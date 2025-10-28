"""
Tests para Simple Expense Forecaster
"""
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.ml.forecaster_simple import SimpleExpenseForecaster


class TestSimpleExpenseForecaster:
    """Tests para el predictor de gastos simple"""
    
    def setup_method(self):
        """Setup para cada test"""
        # Crear archivo temporal para modelo
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pkl')
        self.temp_file.close()
        
        self.forecaster = SimpleExpenseForecaster(model_path=self.temp_file.name)
        
        # Datos de prueba con fechas bolivianas
        base_date = datetime(2025, 1, 1)
        self.sample_transactions = [
            {
                'fecha': (base_date + timedelta(days=i)).strftime('%Y-%m-%d'),
                'monto': 50 + (i % 10) * 20,  # Patrón variable
                'categoria': 'Alimentación' if i % 3 == 0 else 'Transporte',
                'descripcion': f'TRANSACCION {i}'
            }
            for i in range(30)  # 30 días de datos
        ]
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_train_forecaster_success_linear(self):
        """Test entrenamiento exitoso con datos suficientes (modelo lineal)"""
        # Given - datos con tendencia
        trending_transactions = []
        base_date = datetime(2025, 1, 1)
        
        for i in range(10):  # Suficientes datos para linear
            trending_transactions.append({
                'fecha': (base_date + timedelta(days=i)).strftime('%Y-%m-%d'),
                'monto': 100 + i * 10,  # Tendencia creciente
                'categoria': 'Alimentación'
            })
        
        # When
        metrics = self.forecaster.train(trending_transactions)
        
        # Then
        assert metrics['status'] == 'success'
        assert metrics['model_type'] == 'linear'
        assert metrics['num_transactions'] == 10
        assert 'mae' in metrics
        assert 'rmse' in metrics
    
    def test_train_forecaster_success_average(self):
        """Test entrenamiento con pocos datos (modelo promedio)"""
        # Given - pocos datos
        few_transactions = [
            {'fecha': '2025-01-01', 'monto': 100, 'categoria': 'Alimentación'},
            {'fecha': '2025-01-02', 'monto': 120, 'categoria': 'Transporte'}
        ]
        
        # When
        metrics = self.forecaster.train(few_transactions)
        
        # Then
        assert metrics['status'] == 'success'
        assert metrics['model_type'] == 'average'
        assert metrics['num_transactions'] == 2
    
    def test_train_forecaster_empty_data(self):
        """Test entrenamiento con datos vacíos"""
        # When
        metrics = self.forecaster.train([])
        
        # Then
        assert metrics['status'] == 'error'
        assert 'error' in metrics
    
    def test_predict_linear_model(self):
        """Test predicción con modelo lineal"""
        # Given - entrenar con datos con tendencia
        trending_transactions = []
        base_date = datetime(2025, 1, 1)
        
        for i in range(15):
            trending_transactions.append({
                'fecha': (base_date + timedelta(days=i)).strftime('%Y-%m-%d'),
                'monto': 100 + i * 5,
                'categoria': 'Alimentación'
            })
        
        self.forecaster.train(trending_transactions)
        
        # When
        predictions = self.forecaster.predict(days_ahead=7)
        
        # Then
        assert len(predictions) == 7
        
        for prediction in predictions:
            assert 'date' in prediction
            assert 'predicted_amount' in prediction
            assert 'category' in prediction
            assert 'confidence_interval' in prediction
            assert prediction['predicted_amount'] >= 0
            assert 'lower' in prediction['confidence_interval']
            assert 'upper' in prediction['confidence_interval']
    
    def test_predict_average_model(self):
        """Test predicción con modelo promedio"""
        # Given - entrenar con pocos datos
        few_transactions = [
            {'fecha': '2025-01-01', 'monto': 100, 'categoria': 'Alimentación'},
            {'fecha': '2025-01-02', 'monto': 200, 'categoria': 'Transporte'}
        ]
        
        self.forecaster.train(few_transactions)
        
        # When
        predictions = self.forecaster.predict(days_ahead=5)
        
        # Then
        assert len(predictions) == 5
        
        # Verificar que usa el promedio
        expected_avg = 150  # (100 + 200) / 2
        for prediction in predictions:
            assert prediction['predicted_amount'] == expected_avg
    
    def test_predict_without_training(self):
        """Test predicción sin entrenar"""
        # When/Then
        with pytest.raises(ValueError, match="Model not trained"):
            self.forecaster.predict(days_ahead=7)
    
    def test_save_and_load_model(self):
        """Test guardar y cargar modelo"""
        # Given - entrenar modelo
        self.forecaster.train(self.sample_transactions)
        
        # When - guardar y cargar
        new_forecaster = SimpleExpenseForecaster(model_path=self.temp_file.name)
        loaded = new_forecaster.load_model()
        
        # Then
        assert loaded is True
        assert new_forecaster.model is not None
        
        # Verificar que puede predecir
        predictions = new_forecaster.predict(days_ahead=3)
        assert len(predictions) == 3
    
    def test_load_nonexistent_model(self):
        """Test cargar modelo inexistente"""
        # Given
        forecaster = SimpleExpenseForecaster(model_path="/path/that/doesnt/exist.pkl")
        
        # When/Then
        assert forecaster.load_model() is False
    
    def test_predict_future_dates(self):
        """Test que las predicciones son para fechas futuras"""
        # Given
        self.forecaster.train(self.sample_transactions)
        
        # When
        predictions = self.forecaster.predict(days_ahead=5)
        
        # Then
        today = datetime.now().date()
        
        for i, prediction in enumerate(predictions):
            pred_date = datetime.strptime(prediction['date'], '%Y-%m-%d').date()
            expected_date = today + timedelta(days=i+1)
            assert pred_date == expected_date
    
    def test_confidence_intervals_valid(self):
        """Test que los intervalos de confianza son válidos"""
        # Given
        self.forecaster.train(self.sample_transactions)
        
        # When
        predictions = self.forecaster.predict(days_ahead=3)
        
        # Then
        for prediction in predictions:
            ci = prediction['confidence_interval']
            predicted = prediction['predicted_amount']
            
            assert ci['lower'] <= predicted <= ci['upper']
            assert ci['lower'] >= 0  # No gastos negativos
    
    def test_predict_specific_category(self):
        """Test predicción para categoría específica"""
        # Given
        self.forecaster.train(self.sample_transactions)
        
        # When
        predictions = self.forecaster.predict(days_ahead=3, category='Alimentación')
        
        # Then
        for prediction in predictions:
            assert prediction['category'] == 'Alimentación'
    
    @patch('src.ml.forecaster_simple.logger')
    def test_logging_during_operations(self, mock_logger):
        """Test que se logea correctamente"""
        # When
        self.forecaster.train(self.sample_transactions)
        self.forecaster.predict(days_ahead=1)
        
        # Then
        mock_logger.info.assert_called()


# Tests con datos bolivianos realistas
class TestForecasterBolivianData:
    """Tests con datos bolivianos específicos"""
    
    def test_bolivian_spending_patterns(self):
        """Test con patrones de gasto bolivianos típicos"""
        forecaster = SimpleExpenseForecaster()
        
        # Datos realistas bolivianos (en bolivianos)
        bolivian_transactions = []
        base_date = datetime(2025, 1, 1)
        
        # Patrón típico: gastos más altos en fin de semana, quincenas
        for i in range(30):
            date = base_date + timedelta(days=i)
            is_weekend = date.weekday() >= 5
            is_quincena = date.day in [15, 30]
            
            base_amount = 150  # Bs por día típico
            multiplier = 1.0
            
            if is_weekend:
                multiplier *= 1.5  # Más gastos fin de semana
            if is_quincena:
                multiplier *= 2.0  # Gastos de quincena
            
            bolivian_transactions.append({
                'fecha': date.strftime('%Y-%m-%d'),
                'monto': base_amount * multiplier,
                'categoria': 'Alimentación' if i % 2 == 0 else 'Transporte'
            })
        
        # Entrenar y predecir
        metrics = forecaster.train(bolivian_transactions)
        assert metrics['status'] == 'success'
        
        predictions = forecaster.predict(days_ahead=15)
        assert len(predictions) == 15
        
        # Verificar rangos realistas para Bolivia
        for prediction in predictions:
            amount = prediction['predicted_amount']
            assert 50 <= amount <= 1000  # Rangos razonables en Bs
    
    def test_monthly_salary_pattern(self):
        """Test patrón de gastos con salario mensual boliviano"""
        forecaster = SimpleExpenseForecaster()
        
        # Simular patrón: gastos altos al inicio del mes, bajos al final
        monthly_transactions = []
        base_date = datetime(2025, 1, 1)
        
        for i in range(60):  # 2 meses
            date = base_date + timedelta(days=i)
            day_of_month = date.day
            
            # Más gastos al inicio del mes (días 1-10)
            if day_of_month <= 10:
                amount = 300
            elif day_of_month <= 20:
                amount = 200
            else:
                amount = 100
            
            monthly_transactions.append({
                'fecha': date.strftime('%Y-%m-%d'),
                'monto': amount,
                'categoria': 'Alimentación'
            })
        
        # Entrenar
        metrics = forecaster.train(monthly_transactions)
        assert metrics['status'] == 'success'
        
        # Predecir próximos 30 días
        predictions = forecaster.predict(days_ahead=30)
        assert len(predictions) == 30


if __name__ == '__main__':
    pytest.main([__file__])
