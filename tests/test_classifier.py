"""
Tests para Transaction Classifier
"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from src.ml.classifier import TransactionClassifier


class TestTransactionClassifier:
    """Tests para el clasificador de transacciones"""
    
    def setup_method(self):
        """Setup para cada test"""
        # Crear archivo temporal para modelo
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pkl')
        self.temp_file.close()
        
        self.classifier = TransactionClassifier(model_path=self.temp_file.name)
        
        # Datos de prueba bolivianos
        self.sample_transactions = [
            {'descripcion': 'KETAL SUPERMERCADO MIRAFLORES', 'categoria': 'Alimentación'},
            {'descripcion': 'TAXI LA PAZ SOPOCACHI', 'categoria': 'Transporte'},
            {'descripcion': 'MERCADO LANZA VERDURAS', 'categoria': 'Alimentación'},
            {'descripcion': 'FARMACIA CHAVEZ MEDICINAS', 'categoria': 'Salud'},
            {'descripcion': 'TELEFERICO ROJO BOLETO', 'categoria': 'Transporte'},
            {'descripcion': 'HIPERMAXI IRPAVI COMPRAS', 'categoria': 'Alimentación'},
            {'descripcion': 'DELAPAZ PAGO LUZ FEBRERO', 'categoria': 'Servicios Básicos'},
            {'descripcion': 'ENTEL PLAN CELULAR MARZO', 'categoria': 'Servicios Básicos'},
            {'descripcion': 'ALQUILER DEPARTAMENTO SOPOCACHI', 'categoria': 'Vivienda'},
            {'descripcion': 'NETFLIX SUSCRIPCION MENSUAL', 'categoria': 'Entretenimiento'}
        ]
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_train_classifier_success(self):
        """Test entrenamiento exitoso del clasificador"""
        # When
        metrics = self.classifier.train(self.sample_transactions)
        
        # Then
        assert metrics['status'] == 'success'
        assert metrics['accuracy'] > 0.5  # Al menos 50% de precisión
        assert metrics['num_samples'] == 10
        assert len(metrics['categories']) >= 5
        assert 'Alimentación' in metrics['categories']
        assert 'Transporte' in metrics['categories']
    
    def test_train_classifier_empty_data(self):
        """Test entrenamiento con datos vacíos"""
        # When
        metrics = self.classifier.train([])
        
        # Then
        assert metrics['status'] == 'error'
        assert 'error' in metrics
    
    def test_predict_bolivian_transactions(self):
        """Test predicción con transacciones bolivianas"""
        # Given - entrenar primero
        self.classifier.train(self.sample_transactions)
        
        # When - predecir transacciones bolivianas típicas
        test_cases = [
            ('KETAL ZONA SUR', 'Alimentación'),
            ('TAXI RADIO MOVIL', 'Transporte'),
            ('FARMACIA BOLIVIA', 'Salud'),
            ('IC NORTE ALQUILER', 'Vivienda')
        ]
        
        for text, expected_category in test_cases:
            prediction = self.classifier.predict(text)
            
            # Then
            assert 'category' in prediction
            assert 'confidence' in prediction
            assert 'alternatives' in prediction
            assert prediction['confidence'] > 0
            assert prediction['confidence'] <= 1
            assert len(prediction['alternatives']) > 0
    
    def test_predict_without_training(self):
        """Test predicción sin entrenar el modelo"""
        # When/Then
        with pytest.raises(ValueError, match="Model not trained"):
            self.classifier.predict("TEST TRANSACTION")
    
    def test_save_and_load_model(self):
        """Test guardar y cargar modelo"""
        # Given - entrenar modelo
        self.classifier.train(self.sample_transactions)
        original_prediction = self.classifier.predict("KETAL SUPERMERCADO")
        
        # When - crear nuevo clasificador y cargar modelo
        new_classifier = TransactionClassifier(model_path=self.temp_file.name)
        loaded = new_classifier.load_model()
        
        # Then
        assert loaded is True
        new_prediction = new_classifier.predict("KETAL SUPERMERCADO")
        assert new_prediction['category'] == original_prediction['category']
    
    def test_load_nonexistent_model(self):
        """Test cargar modelo que no existe"""
        # Given
        classifier = TransactionClassifier(model_path="/path/that/doesnt/exist.pkl")
        
        # When/Then
        assert classifier.load_model() is False
    
    def test_predict_confidence_ranges(self):
        """Test que las confidencias están en rango válido"""
        # Given
        self.classifier.train(self.sample_transactions)
        
        # When
        prediction = self.classifier.predict("KETAL SUPERMERCADO")
        
        # Then
        assert 0 <= prediction['confidence'] <= 1
        
        for alt in prediction['alternatives']:
            assert 0 <= alt['confidence'] <= 1
            assert 'category' in alt
    
    @patch('src.ml.classifier.logger')
    def test_logging_during_training(self, mock_logger):
        """Test que se logea correctamente durante entrenamiento"""
        # When
        self.classifier.train(self.sample_transactions)
        
        # Then
        mock_logger.info.assert_called()
        
    def test_categories_bolivianas_coverage(self):
        """Test cobertura de categorías bolivianas importantes"""
        # Given - expandir datos de entrenamiento
        bolivian_transactions = self.sample_transactions + [
            {'descripcion': 'UNIVERSIDAD MAYOR SAN ANDRES', 'categoria': 'Educación'},
            {'descripcion': 'CINE CENTER MIRAFLORES', 'categoria': 'Entretenimiento'},
            {'descripcion': 'GAMARRA ROPA NUEVA', 'categoria': 'Ropa y Calzado'},
            {'descripcion': 'BANCO UNION COMISION', 'categoria': 'Finanzas'}
        ]
        
        # When
        metrics = self.classifier.train(bolivian_transactions)
        
        # Then - verificar categorías bolivianas importantes
        expected_categories = {
            'Alimentación', 'Transporte', 'Salud', 'Vivienda', 
            'Servicios Básicos', 'Entretenimiento', 'Educación'
        }
        
        found_categories = set(metrics['categories'])
        overlap = expected_categories.intersection(found_categories)
        
        assert len(overlap) >= 5, f"Faltan categorías importantes. Encontradas: {found_categories}"


# Tests de integración con datos reales
class TestClassifierIntegration:
    """Tests de integración del clasificador"""
    
    def test_real_bolivian_merchant_names(self):
        """Test con nombres reales de comercios bolivianos"""
        classifier = TransactionClassifier()
        
        # Datos de entrenamiento más realistas
        training_data = [
            {'descripcion': 'KETAL SUPERMERCADO CALACOTO', 'categoria': 'Alimentación'},
            {'descripcion': 'HIPERMAXI MEGACENTER', 'categoria': 'Alimentación'},
            {'descripcion': 'FARMACIA FARMACIAS BOLIVIA', 'categoria': 'Salud'},
            {'descripcion': 'RADIO TAXI AEROPUERTO', 'categoria': 'Transporte'},
            {'descripcion': 'TELEFERICO LINEA ROJA', 'categoria': 'Transporte'},
            {'descripcion': 'DELAPAZ SERVICIO LUZ', 'categoria': 'Servicios Básicos'},
            {'descripcion': 'COOPERATIVA JESUS NAZARENO', 'categoria': 'Finanzas'},
            {'descripcion': 'UNIVERSIDAD CATOLICA BOLIVIANA', 'categoria': 'Educación'}
        ]
        
        # Entrenar
        metrics = classifier.train(training_data)
        assert metrics['status'] == 'success'
        
        # Probar predicciones con variaciones realistas
        test_cases = [
            'KETAL MIRAFLORES COMPRAS',
            'HIPERMAXI ZONA SUR',
            'FARMACIA CHAVEZ MEDICAMENTOS',
            'RADIO MOVIL TAXI SERVICIO'
        ]
        
        for merchant in test_cases:
            prediction = classifier.predict(merchant)
            assert prediction['confidence'] > 0.2  # Confianza mínima razonable
            assert prediction['category'] in metrics['categories']


if __name__ == '__main__':
    pytest.main([__file__])
