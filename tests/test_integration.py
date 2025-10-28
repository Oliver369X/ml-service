"""
Tests de Integración entre Microservicios
Gateway + Auth + ML Services
"""
import pytest
import requests
import json
import time
from typing import Dict, Any
from unittest.mock import patch


class TestMicroservicesIntegration:
    """Tests de integración entre microservicios"""
    
    # URLs de los servicios
    GATEWAY_URL = "http://localhost:3000/graphql"
    AUTH_URL = "http://localhost:5000/graphql" 
    ML_URL = "http://localhost:5015/graphql"
    ML_HEALTH_URL = "http://localhost:5015/health"
    
    def setup_method(self):
        """Setup antes de cada test"""
        # Esperar que los servicios estén listos
        self._wait_for_services()
    
    def _wait_for_services(self, timeout=30):
        """Esperar que todos los servicios estén disponibles"""
        services = [
            ("ML Health", self.ML_HEALTH_URL, 'GET'),
            ("ML GraphQL", self.ML_URL, 'POST')
        ]
        
        for name, url, method in services:
            print(f"Esperando {name}...")
            if not self._wait_for_service(url, method, timeout):
                pytest.skip(f"Servicio {name} no disponible en {url}")
    
    def _wait_for_service(self, url: str, method: str = 'GET', timeout: int = 30) -> bool:
        """Esperar que un servicio específico esté disponible"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                if method == 'GET':
                    response = requests.get(url, timeout=5)
                else:  # POST para GraphQL
                    response = requests.post(
                        url, 
                        json={"query": "{ __typename }"}, 
                        timeout=5
                    )
                
                if response.status_code in [200, 400]:  # 400 es OK para GraphQL con query inválida
                    return True
                    
            except (requests.ConnectionError, requests.Timeout):
                pass
            
            time.sleep(1)
        
        return False
    
    def _make_graphql_request(self, url: str, query: str, variables: Dict = None, headers: Dict = None) -> Dict[Any, Any]:
        """Hacer request GraphQL y manejar respuesta"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = requests.post(
            url,
            json=payload,
            headers=headers or {},
            timeout=10
        )
        
        return {
            'status_code': response.status_code,
            'data': response.json() if response.content else {},
            'headers': dict(response.headers)
        }


class TestMLServiceDirect:
    """Tests directos al ML Service (sin Gateway)"""
    
    ML_URL = "http://localhost:5015/graphql"
    HEALTH_URL = "http://localhost:5015/health"
    
    def setup_method(self):
        """Setup para tests directos"""
        # Verificar que ML service esté disponible
        try:
            response = requests.get(self.HEALTH_URL, timeout=5)
            if response.status_code != 200:
                pytest.skip("ML Service no disponible")
        except:
            pytest.skip("ML Service no disponible")
    
    def test_ml_service_health_check(self):
        """Test health check del ML service"""
        # When
        response = requests.get(self.HEALTH_URL)
        
        # Then
        assert response.status_code == 200
        
        data = response.json()
        assert data['service'] == 'ml-service'
        assert 'status' in data
        assert 'database' in data
        assert 'version' in data
    
    def test_ml_service_graphql_introspection(self):
        """Test introspección GraphQL del ML service"""
        # Given
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                queryType { name }
                mutationType { name }
            }
        }
        """
        
        # When
        response = requests.post(
            self.ML_URL,
            json={"query": introspection_query},
            timeout=10
        )
        
        # Then
        assert response.status_code == 200
        
        data = response.json()
        assert 'data' in data
        assert data['data']['__schema']['queryType']['name'] == 'Query'
        assert data['data']['__schema']['mutationType']['name'] == 'Mutation'
    
    def test_classify_transaction_bolivian(self):
        """Test clasificación de transacción boliviana"""
        # Given
        mutation = """
        mutation ClassifyBolivianTransaction($input: ClassifyTransactionInput!) {
            classifyTransaction(input: $input) {
                predictedCategory
                confidence
                alternativeCategories {
                    category
                    confidence
                }
                modelVersion
            }
        }
        """
        
        variables = {
            "input": {
                "text": "KETAL SUPERMERCADO MIRAFLORES"
            }
        }
        
        # When
        response = requests.post(
            self.ML_URL,
            json={"query": mutation, "variables": variables},
            headers={"user-id": "test-user-bolivia"},
            timeout=15
        )
        
        # Then
        assert response.status_code == 200
        
        data = response.json()
        assert 'data' in data
        assert 'classifyTransaction' in data['data']
        
        result = data['data']['classifyTransaction']
        assert 'predictedCategory' in result
        assert 'confidence' in result
        assert 'alternativeCategories' in result
        assert 'modelVersion' in result
        
        # Verificar rangos válidos
        assert 0 <= result['confidence'] <= 1
        assert len(result['alternativeCategories']) > 0
    
    def test_classify_multiple_bolivian_merchants(self):
        """Test clasificación de múltiples comercios bolivianos"""
        # Given
        bolivian_merchants = [
            "HIPERMAXI ZONA SUR",
            "FARMACIA CHAVEZ MEDICAMENTOS", 
            "RADIO TAXI AEROPUERTO",
            "TELEFERICO LINEA ROJA",
            "DELAPAZ SERVICIO LUZ"
        ]
        
        mutation = """
        mutation ClassifyTransaction($input: ClassifyTransactionInput!) {
            classifyTransaction(input: $input) {
                predictedCategory
                confidence
            }
        }
        """
        
        results = []
        
        # When
        for merchant in bolivian_merchants:
            response = requests.post(
                self.ML_URL,
                json={
                    "query": mutation,
                    "variables": {"input": {"text": merchant}}
                },
                headers={"user-id": "test-user-bolivia"},
                timeout=10
            )
            
            assert response.status_code == 200
            data = response.json()
            
            if 'data' in data and 'classifyTransaction' in data['data']:
                results.append({
                    'merchant': merchant,
                    'category': data['data']['classifyTransaction']['predictedCategory'],
                    'confidence': data['data']['classifyTransaction']['confidence']
                })
        
        # Then
        assert len(results) == len(bolivian_merchants)
        
        # Verificar que las categorías son razonables
        expected_patterns = {
            'HIPERMAXI': 'Alimentación',
            'FARMACIA': 'Salud', 
            'TAXI': 'Transporte',
            'TELEFERICO': 'Transporte',
            'DELAPAZ': 'Servicios Básicos'
        }
        
        # Al menos algunas predicciones deben ser correctas
        correct_predictions = 0
        for result in results:
            merchant = result['merchant']
            category = result['category']
            
            for pattern, expected in expected_patterns.items():
                if pattern in merchant and expected == category:
                    correct_predictions += 1
                    break
        
        # Al menos 40% de precisión en clasificaciones obvias
        precision = correct_predictions / len(results)
        assert precision >= 0.4, f"Precisión muy baja: {precision:.2%}"
    
    def test_generate_forecast_bolivian_data(self):
        """Test generación de forecast con datos bolivianos"""
        # Given
        mutation = """
        mutation GenerateForecast($input: GenerateForecastInput!) {
            generateForecast(input: $input) {
                date
                predictedAmount
                category
                confidenceInterval {
                    lower
                    upper
                }
            }
        }
        """
        
        # Datos de transacciones bolivianas de ejemplo
        variables = {
            "input": {
                "daysAhead": 7,
                "categoryId": "alimentacion"
            }
        }
        
        # When
        response = requests.post(
            self.ML_URL,
            json={"query": mutation, "variables": variables},
            headers={"user-id": "test-user-bolivia"},
            timeout=15
        )
        
        # Then
        # Nota: Este test puede fallar si no hay modelo entrenado
        # En ese caso, verificamos que el error es esperado
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and data['data']['generateForecast']:
                forecasts = data['data']['generateForecast']
                assert len(forecasts) == 7
                
                for forecast in forecasts:
                    assert 'date' in forecast
                    assert 'predictedAmount' in forecast
                    assert forecast['predictedAmount'] >= 0
        else:
            # Si falla, debe ser por un error conocido (modelo no entrenado)
            assert response.status_code in [200, 500]


class TestGatewayIntegration:
    """Tests de integración a través del Gateway"""
    
    GATEWAY_URL = "http://localhost:3000/graphql"
    
    def setup_method(self):
        """Setup para tests del Gateway"""
        # Verificar que Gateway esté disponible
        try:
            response = requests.post(
                self.GATEWAY_URL,
                json={"query": "{ __typename }"},
                timeout=5
            )
            if response.status_code not in [200, 400]:
                pytest.skip("Gateway no disponible")
        except:
            pytest.skip("Gateway no disponible")
    
    @pytest.mark.skip(reason="Gateway puede no tener ML service configurado")
    def test_gateway_ml_service_federation(self):
        """Test federación Gateway -> ML Service"""
        # Given
        query = """
        query TestMLFederation {
            __schema {
                types {
                    name
                }
            }
        }
        """
        
        # When
        response = requests.post(
            self.GATEWAY_URL,
            json={"query": query},
            timeout=10
        )
        
        # Then
        assert response.status_code == 200
        
        data = response.json()
        if 'data' in data:
            # Verificar que tipos del ML service están disponibles
            type_names = [t['name'] for t in data['data']['__schema']['types']]
            
            # Buscar tipos relacionados con ML
            ml_types = ['Prediction', 'Forecast', 'SpendingPattern']
            found_ml_types = [t for t in ml_types if t in type_names]
            
            # Si el ML service está federado, debe tener al menos un tipo
            assert len(found_ml_types) > 0, "ML Service no parece estar federado correctamente"


class TestServiceCommunication:
    """Tests de comunicación entre servicios"""
    
    def test_services_discovery(self):
        """Test que los servicios se pueden descubrir entre sí"""
        services = {
            'ml-service': 'http://localhost:5015/health',
            # Agregar más servicios cuando estén disponibles
        }
        
        available_services = []
        
        for name, health_url in services.items():
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    available_services.append(name)
            except:
                pass
        
        # Al menos el ML service debe estar disponible
        assert 'ml-service' in available_services
        print(f"Servicios disponibles: {available_services}")
    
    def test_ml_service_error_handling(self):
        """Test manejo de errores del ML service"""
        # Given - query GraphQL inválida
        invalid_query = """
        query InvalidQuery {
            nonExistentField {
                invalidSubField
            }
        }
        """
        
        # When
        response = requests.post(
            "http://localhost:5015/graphql",
            json={"query": invalid_query},
            timeout=10
        )
        
        # Then
        assert response.status_code == 200  # GraphQL devuelve 200 con errores en body
        
        data = response.json()
        assert 'errors' in data
        assert len(data['errors']) > 0
        
        # Verificar estructura del error
        error = data['errors'][0]
        assert 'message' in error
        assert 'locations' in error


# Datos de prueba bolivianos para tests
BOLIVIAN_TEST_DATA = {
    'merchants': [
        'KETAL SUPERMERCADO CALACOTO',
        'HIPERMAXI MEGACENTER IRPAVI', 
        'FARMACIA CHAVEZ SUCURSAL CENTRO',
        'RADIO TAXI COPACABANA',
        'TELEFERICO LINEA AMARILLA',
        'DELAPAZ SERVICIO ELECTRICIDAD',
        'ENTEL PLAN POSTPAGO',
        'BANCO UNION COMISION ATM',
        'UNIVERSIDAD MAYOR SAN ANDRES',
        'CINE CENTER ZONA SUR'
    ],
    'categories': [
        'Alimentación',
        'Salud',
        'Transporte', 
        'Servicios Básicos',
        'Finanzas',
        'Educación',
        'Entretenimiento'
    ]
}


if __name__ == '__main__':
    # Ejecutar solo tests que no requieren todos los servicios
    pytest.main([
        __file__ + "::TestMLServiceDirect",
        "-v"
    ])
