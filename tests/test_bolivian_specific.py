"""
Tests específicos para datos y contexto boliviano
"""
import pytest
from datetime import datetime, timedelta
from src.ml.classifier import TransactionClassifier
from src.ml.forecaster_simple import SimpleExpenseForecaster
from src.dl.pattern_analyzer import PatternAnalyzer


# Marcador para tests bolivianos
pytestmark = pytest.mark.bolivian_data


class TestBolivianTransactionClassifier:
    """Tests del clasificador con datos específicamente bolivianos"""
    
    def setup_method(self):
        """Setup con datos bolivianos realistas"""
        self.classifier = TransactionClassifier()
        
        # Datos de entrenamiento con comercios bolivianos reales
        self.bolivian_training_data = [
            # Supermercados
            {'descripcion': 'KETAL SUPERMERCADO CALACOTO', 'categoria': 'Alimentación'},
            {'descripcion': 'KETAL MIRAFLORES COMPRAS', 'categoria': 'Alimentación'}, 
            {'descripcion': 'HIPERMAXI MEGACENTER IRPAVI', 'categoria': 'Alimentación'},
            {'descripcion': 'HIPERMAXI ZONA SUR', 'categoria': 'Alimentación'},
            {'descripcion': 'HYPERMAXI SAN MIGUEL', 'categoria': 'Alimentación'},
            {'descripcion': 'SUPER NICOLAS CENTRO', 'categoria': 'Alimentación'},
            
            # Farmacias
            {'descripcion': 'FARMACIA CHAVEZ CENTRO', 'categoria': 'Salud'},
            {'descripcion': 'FARMACIA BOLIVIA ZONA SUR', 'categoria': 'Salud'},
            {'descripcion': 'FARMACIAS BOLIVIA MEDICAMENTOS', 'categoria': 'Salud'},
            {'descripcion': 'FARMACIA SAN MARTIN', 'categoria': 'Salud'},
            
            # Transporte
            {'descripcion': 'RADIO TAXI COPACABANA', 'categoria': 'Transporte'},
            {'descripcion': 'TAXI LA PAZ AEROPUERTO', 'categoria': 'Transporte'},
            {'descripcion': 'TELEFERICO LINEA ROJA', 'categoria': 'Transporte'},
            {'descripcion': 'TELEFERICO AMARILLA', 'categoria': 'Transporte'},
            {'descripcion': 'PUMAKATARI TARJETA', 'categoria': 'Transporte'},
            {'descripcion': 'MINI BUS RUTA 273', 'categoria': 'Transporte'},
            
            # Servicios básicos
            {'descripcion': 'DELAPAZ SERVICIO LUZ', 'categoria': 'Servicios Básicos'},
            {'descripcion': 'DELAPAZ ELECTRICIDAD', 'categoria': 'Servicios Básicos'},
            {'descripcion': 'EPSAS AGUA POTABLE', 'categoria': 'Servicios Básicos'},
            {'descripcion': 'ENTEL PLAN CELULAR', 'categoria': 'Servicios Básicos'},
            {'descripcion': 'TIGO RECHARGE SALDO', 'categoria': 'Servicios Básicos'},
            {'descripcion': 'VIVA PLAN POSTPAGO', 'categoria': 'Servicios Básicos'},
            
            # Educación
            {'descripcion': 'UNIVERSIDAD MAYOR SAN ANDRES', 'categoria': 'Educación'},
            {'descripcion': 'UNIVERSIDAD CATOLICA BOLIVIANA', 'categoria': 'Educación'},
            {'descripcion': 'COLEGIO LA SALLE', 'categoria': 'Educación'},
            {'descripcion': 'INSTITUTO TECNOLOGICO', 'categoria': 'Educación'},
            
            # Entretenimiento
            {'descripcion': 'CINE CENTER MIRAFLORES', 'categoria': 'Entretenimiento'},
            {'descripcion': 'MULTICINE ZONA SUR', 'categoria': 'Entretenimiento'},
            {'descripcion': 'NETFLIX SUSCRIPCION', 'categoria': 'Entretenimiento'},
            {'descripcion': 'SPOTIFY PREMIUM', 'categoria': 'Entretenimiento'},
            
            # Finanzas
            {'descripcion': 'BANCO UNION COMISION', 'categoria': 'Finanzas'},
            {'descripcion': 'BANCO MERCANTIL ATM', 'categoria': 'Finanzas'},
            {'descripcion': 'BCP TRANSFERENCIA', 'categoria': 'Finanzas'},
            {'descripcion': 'COOPERATIVA JESUS NAZARENO', 'categoria': 'Finanzas'},
            
            # Vivienda
            {'descripcion': 'ALQUILER DEPARTAMENTO SOPOCACHI', 'categoria': 'Vivienda'},
            {'descripcion': 'INMOBILIARIA CENTRAL', 'categoria': 'Vivienda'},
            {'descripcion': 'CONDOMINIO CUOTAS', 'categoria': 'Vivienda'},
            
            # Ropa y calzado
            {'descripcion': 'GAMARRA ROPA NUEVA', 'categoria': 'Ropa y Calzado'},
            {'descripcion': 'ELOY SALMON TIENDA', 'categoria': 'Ropa y Calzado'},
            {'descripcion': 'MERCADO LANZA ROPA', 'categoria': 'Ropa y Calzado'}
        ]
    
    def test_bolivian_supermarkets_classification(self):
        """Test clasificación de supermercados bolivianos"""
        # Given
        self.classifier.train(self.bolivian_training_data)
        
        # Test cases específicos de supermercados bolivianos
        supermarket_tests = [
            'KETAL ACHUMANI COMPRAS FAMILIARES',
            'HIPERMAXI PRADO PRODUCTOS LIMPIEZA',
            'SUPER NICOLAS ALTO OBRAJES'
        ]
        
        # When/Then
        for merchant in supermarket_tests:
            prediction = self.classifier.predict(merchant)
            
            assert prediction['category'] == 'Alimentación'
            assert prediction['confidence'] > 0.5
    
    def test_bolivian_pharmacies_classification(self):
        """Test clasificación de farmacias bolivianas"""
        # Given
        self.classifier.train(self.bolivian_training_data)
        
        # Test cases de farmacias bolivianas
        pharmacy_tests = [
            'FARMACIA CHAVEZ MEDICINAS GENERICAS',
            'FARMACIAS BOLIVIA VITAMINAS',
            'FARMACIA SAN MARTIN CENTRO'
        ]
        
        # When/Then
        for merchant in pharmacy_tests:
            prediction = self.classifier.predict(merchant)
            
            assert prediction['category'] == 'Salud'
            assert prediction['confidence'] > 0.4
    
    def test_bolivian_transport_classification(self):
        """Test clasificación de transporte boliviano específico"""
        # Given
        self.classifier.train(self.bolivian_training_data)
        
        # Transport específico de La Paz
        transport_tests = [
            'TELEFERICO VERDE BOLETO',
            'PUMAKATARI RECARGA TARJETA',
            'RADIO MOVIL TAXI NOCTURNO'
        ]
        
        # When/Then
        for merchant in transport_tests:
            prediction = self.classifier.predict(merchant)
            
            assert prediction['category'] == 'Transporte'
            assert prediction['confidence'] > 0.3
    
    def test_bolivian_utilities_classification(self):
        """Test servicios públicos bolivianos"""
        # Given  
        self.classifier.train(self.bolivian_training_data)
        
        # Servicios públicos bolivianos
        utility_tests = [
            'DELAPAZ PAGO LUZ FEBRERO',
            'EPSAS SERVICIO AGUA',
            'ENTEL INTERNET FIBRA'
        ]
        
        # When/Then
        for merchant in utility_tests:
            prediction = self.classifier.predict(merchant)
            
            assert prediction['category'] == 'Servicios Básicos'
            assert prediction['confidence'] > 0.3


class TestBolivianSpendingPatterns:
    """Test patrones de gasto específicos de Bolivia"""
    
    def setup_method(self):
        """Setup con patrones bolivianos"""
        self.analyzer = PatternAnalyzer()
        
    def test_aguinaldo_spending_pattern(self):
        """Test patrón de gastos con aguinaldo (diciembre/enero)"""
        # Given - simular patrón de aguinaldo
        aguinaldo_data = []
        base_date = datetime(2024, 12, 1)
        
        for i in range(90):  # Dic-Ene-Feb
            date = base_date + timedelta(days=i)
            
            # Gastos más altos en diciembre (aguinaldo) y enero (regalos/vacaciones)
            if date.month == 12:
                base_amount = 800  # Aguinaldo
            elif date.month == 1:
                base_amount = 600  # Post aguinaldo
            else:
                base_amount = 300  # Normal
            
            aguinaldo_data.append({
                'fecha': date.strftime('%Y-%m-%d'),
                'monto': base_amount + (i % 5) * 50,
                'categoria': 'Entretenimiento' if date.month == 12 else 'Alimentación',
                'es_aguinaldo': date.month == 12
            })
        
        # When
        metrics = self.analyzer.train(aguinaldo_data, epochs=3)
        
        # Then
        assert metrics['status'] == 'success'
        
        analysis = self.analyzer.analyze_patterns(aguinaldo_data)
        assert analysis['pattern_type'] in ['high_spender', 'moderate_spender']
    
    def test_quincena_spending_pattern(self):
        """Test patrón de quincena boliviano (días 15 y 30)"""
        # Given
        quincena_data = []
        base_date = datetime(2025, 1, 1)
        
        for i in range(60):  # 2 meses
            date = base_date + timedelta(days=i)
            day = date.day
            
            # Gastos altos en quincenas (día 15 y fin de mes)
            if day in [15] or day >= 28:
                amount = 600
            else:
                amount = 200
            
            quincena_data.append({
                'fecha': date.strftime('%Y-%m-%d'),
                'monto': amount,
                'categoria': 'Alimentación',
                'es_quincena': day in [15] or day >= 28
            })
        
        # When
        metrics = self.analyzer.train(quincena_data, epochs=3)
        analysis = self.analyzer.analyze_patterns(quincena_data)
        
        # Then
        # Debe detectar días inusuales (las quincenas)
        assert analysis['unusual_days'] >= 3
    
    def test_carnival_spending_spike(self):
        """Test pico de gastos en carnaval (febrero/marzo)"""
        # Given
        carnival_data = []
        base_date = datetime(2025, 1, 1)
        
        for i in range(90):  # Ene-Mar
            date = base_date + timedelta(days=i)
            
            # Pico de gastos en febrero (carnaval)
            if date.month == 2:
                amount = 500  # Gastos de carnaval
            else:
                amount = 250
            
            carnival_data.append({
                'fecha': date.strftime('%Y-%m-%d'),
                'monto': amount,
                'categoria': 'Entretenimiento' if date.month == 2 else 'Alimentación'
            })
        
        # When
        metrics = self.analyzer.train(carnival_data, epochs=3)
        analysis = self.analyzer.analyze_patterns(carnival_data)
        
        # Then
        insights = analysis['insights']
        assert len(insights) > 0


class TestBolivianForecasting:
    """Test forecasting con patrones bolivianos"""
    
    def test_salary_based_forecasting(self):
        """Test forecasting basado en patrón de salarios bolivianos"""
        forecaster = SimpleExpenseForecaster()
        
        # Given - patrón típico de salario mensual boliviano
        salary_data = []
        base_date = datetime(2025, 1, 1)
        
        for i in range(60):  # 2 meses
            date = base_date + timedelta(days=i)
            day_of_month = date.day
            
            # Patrón típico: gastos altos inicio de mes, bajos al final
            if day_of_month <= 5:
                amount = 400  # Pago de servicios y compras grandes
            elif day_of_month <= 15:
                amount = 250  # Gastos normales
            elif day_of_month <= 25:
                amount = 200  # Reduciendo gastos
            else:
                amount = 150  # Ahorrando para próximo mes
            
            salary_data.append({
                'fecha': date.strftime('%Y-%m-%d'),
                'monto': amount,
                'categoria': 'Alimentación'
            })
        
        # When
        metrics = forecaster.train(salary_data)
        predictions = forecaster.predict(days_ahead=30)
        
        # Then
        assert metrics['status'] == 'success'
        assert len(predictions) == 30
        
        # Verificar rangos realistas para Bolivia
        for prediction in predictions:
            amount = prediction['predicted_amount']
            assert 100 <= amount <= 600  # Rango realista en Bs
    
    def test_seasonal_bolivian_forecasting(self):
        """Test forecasting con patrones estacionales bolivianos"""
        forecaster = SimpleExpenseForecaster()
        
        # Given - datos con estacionalidad boliviana
        seasonal_data = []
        base_date = datetime(2025, 1, 1)
        
        for i in range(365):  # 1 año completo
            date = base_date + timedelta(days=i)
            month = date.month
            
            # Patrones estacionales bolivianos
            base_amount = 250
            
            if month in [12, 1]:  # Aguinaldo y año nuevo
                multiplier = 1.8
            elif month == 2:  # Carnaval
                multiplier = 1.5
            elif month in [3, 4]:  # Inicio clases
                multiplier = 1.3
            elif month in [6, 7]:  # Vacaciones de invierno
                multiplier = 1.2
            else:
                multiplier = 1.0
            
            seasonal_data.append({
                'fecha': date.strftime('%Y-%m-%d'),
                'monto': base_amount * multiplier,
                'categoria': 'Alimentación'
            })
        
        # When
        metrics = forecaster.train(seasonal_data)
        
        # Then
        assert metrics['status'] == 'success'
        assert metrics['num_transactions'] == 365


# Test de datos de mercados bolivianos específicos
BOLIVIAN_MARKET_DATA = {
    'la_paz_markets': [
        'MERCADO LANZA VERDURAS FRESCAS',
        'MERCADO RODRIGUEZ FRUTAS',
        'MERCADO CAMACHO CARNE',
        'FERIA 16 JULIO ROPA'
    ],
    'cochabamba_markets': [
        'MERCADO LA CANCHA ABARROTES',
        'MERCADO QUILLACOLLO',
        'FERIA COCHABAMBA'
    ],
    'santa_cruz_markets': [
        'MERCADO MUTUALISTA',
        'MERCADO LOS POZOS',
        'FERIA BARRIO LINDO'
    ]
}


class TestBolivianMarketClassification:
    """Test clasificación específica de mercados bolivianos"""
    
    def test_traditional_markets_classification(self):
        """Test clasificación de mercados tradicionales"""
        classifier = TransactionClassifier()
        
        # Training data con mercados
        market_training = [
            {'descripcion': 'MERCADO LANZA VERDURAS', 'categoria': 'Alimentación'},
            {'descripcion': 'MERCADO RODRIGUEZ FRUTAS', 'categoria': 'Alimentación'},
            {'descripcion': 'MERCADO CAMACHO CARNE', 'categoria': 'Alimentación'},
            {'descripcion': 'FERIA 16 JULIO ROPA', 'categoria': 'Ropa y Calzado'},
            {'descripcion': 'MERCADO LA CANCHA', 'categoria': 'Alimentación'}
        ]
        
        # Train
        metrics = classifier.train(market_training)
        assert metrics['status'] == 'success'
        
        # Test con variaciones de mercados
        test_markets = [
            'MERCADO LANZA PAPA CHUÑO',
            'FERIA 16 JULIO ZAPATOS',
            'MERCADO RODRIGUEZ PLATANOS'
        ]
        
        for market in test_markets:
            prediction = classifier.predict(market)
            assert prediction['confidence'] > 0.3
            assert prediction['category'] in ['Alimentación', 'Ropa y Calzado']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
