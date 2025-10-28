"""
Tests para Pattern Analyzer (Deep Learning)
"""
import pytest
import tempfile
import os
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from src.dl.pattern_analyzer import PatternAnalyzer


class TestPatternAnalyzer:
    """Tests para el analizador de patrones con Deep Learning"""
    
    def setup_method(self):
        """Setup para cada test"""
        # Crear archivo temporal para modelo
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.h5')
        self.temp_file.close()
        
        self.analyzer = PatternAnalyzer(model_path=self.temp_file.name)
        
        # Datos de prueba bolivianos
        base_date = datetime(2025, 1, 1)
        self.sample_transactions = []
        
        for i in range(50):  # Suficientes datos para DL
            date = base_date + timedelta(days=i)
            
            # Simular patrones realistas
            is_weekend = date.weekday() >= 5
            amount = 200 + (i % 10) * 50
            if is_weekend:
                amount *= 1.5
            
            self.sample_transactions.append({
                'fecha': date.strftime('%Y-%m-%d'),
                'monto': amount,
                'categoria': 'Alimentación' if i % 2 == 0 else 'Transporte',
                'descripcion': f'MERCHANT {i}',
                'tipo_pago': 'Tarjeta' if i % 3 == 0 else 'Efectivo'
            })
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_train_analyzer_success(self):
        """Test entrenamiento exitoso del analizador"""
        # When
        metrics = self.analyzer.train(self.sample_transactions, epochs=5)  # Pocas épocas para test
        
        # Then
        assert metrics['status'] == 'success'
        assert 'loss' in metrics
        assert 'val_loss' in metrics
        assert 'num_samples' in metrics
        assert 'epochs_trained' in metrics
        assert metrics['num_samples'] == 50
        assert metrics['epochs_trained'] <= 5
        assert isinstance(metrics['loss'], float)
        assert isinstance(metrics['val_loss'], float)
    
    def test_train_analyzer_insufficient_data(self):
        """Test entrenamiento con datos insuficientes"""
        # Given - muy pocos datos
        few_transactions = self.sample_transactions[:5]
        
        # When
        metrics = self.analyzer.train(few_transactions, epochs=2)
        
        # Then
        assert metrics['status'] == 'error'
        assert 'error' in metrics
    
    def test_train_analyzer_empty_data(self):
        """Test entrenamiento con datos vacíos"""
        # When
        metrics = self.analyzer.train([], epochs=1)
        
        # Then
        assert metrics['status'] == 'error'
        assert 'error' in metrics
    
    def test_analyze_patterns_after_training(self):
        """Test análisis de patrones después de entrenar"""
        # Given - entrenar primero
        self.analyzer.train(self.sample_transactions, epochs=3)
        
        # When
        analysis = self.analyzer.analyze_patterns(self.sample_transactions)
        
        # Then
        assert 'pattern_type' in analysis
        assert 'stability_score' in analysis
        assert 'unusual_days' in analysis
        assert 'insights' in analysis
        
        # Verificar tipos válidos
        valid_patterns = ['low_spender', 'moderate_spender', 'high_spender', 'irregular_spender']
        assert analysis['pattern_type'] in valid_patterns
        
        # Verificar rangos válidos
        assert 0 <= analysis['stability_score'] <= 1
        assert analysis['unusual_days'] >= 0
        assert isinstance(analysis['insights'], list)
    
    def test_analyze_patterns_without_training(self):
        """Test análisis sin entrenar el modelo"""
        # When/Then
        with pytest.raises(ValueError, match="Model not trained"):
            self.analyzer.analyze_patterns(self.sample_transactions)
    
    def test_save_and_load_model(self):
        """Test guardar y cargar modelo"""
        # Given - entrenar modelo
        self.analyzer.train(self.sample_transactions, epochs=3)
        
        # When - crear nuevo analizador y cargar
        new_analyzer = PatternAnalyzer(model_path=self.temp_file.name)
        loaded = new_analyzer.load_model()
        
        # Then
        assert loaded is True
        assert new_analyzer.model is not None
        
        # Verificar que puede analizar
        analysis = new_analyzer.analyze_patterns(self.sample_transactions)
        assert 'pattern_type' in analysis
    
    def test_load_nonexistent_model(self):
        """Test cargar modelo inexistente"""
        # Given
        analyzer = PatternAnalyzer(model_path="/path/that/doesnt/exist.h5")
        
        # When/Then
        assert analyzer.load_model() is False
    
    def test_feature_engineering_quality(self):
        """Test calidad de las características generadas"""
        # When
        features = self.analyzer._prepare_features(self.sample_transactions)
        
        # Then
        assert isinstance(features, np.ndarray)
        assert features.shape[0] == len(self.sample_transactions)
        assert features.shape[1] > 0  # Debe tener características
        
        # Verificar que no hay NaN o infinitos
        assert not np.any(np.isnan(features))
        assert not np.any(np.isinf(features))
    
    def test_pattern_classification_logic(self):
        """Test lógica de clasificación de patrones"""
        # Given - crear datos con patrones específicos
        
        # Patrón de gastador alto (>400 por día promedio)
        high_spender_data = []
        for i in range(30):
            high_spender_data.append({
                'fecha': (datetime(2025, 1, 1) + timedelta(days=i)).strftime('%Y-%m-%d'),
                'monto': 500 + i * 10,  # Gastos altos
                'categoria': 'Vivienda',
                'tipo_pago': 'Tarjeta'
            })
        
        # When
        analysis = self.analyzer._classify_spending_pattern(high_spender_data)
        
        # Then
        assert analysis['pattern_type'] == 'high_spender'
    
    def test_stability_score_calculation(self):
        """Test cálculo del score de estabilidad"""
        # Given - datos estables (mismos montos)
        stable_data = []
        for i in range(20):
            stable_data.append({
                'fecha': (datetime(2025, 1, 1) + timedelta(days=i)).strftime('%Y-%m-%d'),
                'monto': 200,  # Siempre el mismo monto
                'categoria': 'Alimentación'
            })
        
        # When
        stability = self.analyzer._calculate_stability_score(stable_data)
        
        # Then
        assert stability >= 0.9  # Muy estable
        
        # Given - datos inestables
        unstable_data = []
        for i in range(20):
            unstable_data.append({
                'fecha': (datetime(2025, 1, 1) + timedelta(days=i)).strftime('%Y-%m-%d'),
                'monto': 100 + (i % 5) * 200,  # Muy variable
                'categoria': 'Alimentación'
            })
        
        # When
        instability = self.analyzer._calculate_stability_score(unstable_data)
        
        # Then
        assert instability < 0.7  # Menos estable
    
    def test_unusual_days_detection(self):
        """Test detección de días inusuales"""
        # Given - datos con algunos días atípicos
        mixed_data = []
        for i in range(30):
            # Mayoría de días normales, algunos atípicos
            amount = 200 if i not in [5, 15, 25] else 1000  # Días 5, 15, 25 son atípicos
            
            mixed_data.append({
                'fecha': (datetime(2025, 1, 1) + timedelta(days=i)).strftime('%Y-%m-%d'),
                'monto': amount,
                'categoria': 'Alimentación'
            })
        
        # When
        unusual_count = self.analyzer._detect_unusual_days(mixed_data)
        
        # Then
        assert unusual_count >= 2  # Debe detectar al menos algunos días atípicos
    
    def test_insights_generation(self):
        """Test generación de insights"""
        # When
        insights = self.analyzer._generate_insights(self.sample_transactions)
        
        # Then
        assert isinstance(insights, list)
        assert len(insights) > 0
        
        for insight in insights:
            assert 'type' in insight
            assert 'message' in insight
            assert 'value' in insight
            assert isinstance(insight['message'], str)
    
    @patch('src.dl.pattern_analyzer.logger')
    def test_logging_during_training(self, mock_logger):
        """Test logging durante entrenamiento"""
        # When
        self.analyzer.train(self.sample_transactions, epochs=2)
        
        # Then
        mock_logger.info.assert_called()


# Tests específicos para patrones bolivianos
class TestPatternAnalyzerBolivianPatterns:
    """Tests con patrones de gasto bolivianos específicos"""
    
    def test_quincena_pattern_detection(self):
        """Test detección de patrón de quincena boliviano"""
        analyzer = PatternAnalyzer()
        
        # Simular patrón de quincena (gastos altos días 15 y 30)
        quincena_data = []
        base_date = datetime(2025, 1, 1)
        
        for i in range(60):  # 2 meses
            date = base_date + timedelta(days=i)
            day = date.day
            
            # Gastos altos en quincenas
            amount = 500 if day in [15, 30] else 150
            
            quincena_data.append({
                'fecha': date.strftime('%Y-%m-%d'),
                'monto': amount,
                'categoria': 'Alimentación',
                'es_quincena': day in [15, 30]
            })
        
        # Entrenar y analizar
        metrics = analyzer.train(quincena_data, epochs=5)
        assert metrics['status'] == 'success'
        
        analysis = analyzer.analyze_patterns(quincena_data)
        
        # Debe detectar que hay días inusuales (las quincenas)
        assert analysis['unusual_days'] >= 2
    
    def test_weekend_spending_pattern(self):
        """Test patrón de gastos de fin de semana"""
        analyzer = PatternAnalyzer()
        
        # Simular más gastos en fines de semana
        weekend_data = []
        base_date = datetime(2025, 1, 1)  # Miércoles
        
        for i in range(28):  # 4 semanas
            date = base_date + timedelta(days=i)
            is_weekend = date.weekday() >= 5
            
            # Más gastos en fin de semana
            amount = 400 if is_weekend else 200
            
            weekend_data.append({
                'fecha': date.strftime('%Y-%m-%d'),
                'monto': amount,
                'categoria': 'Entretenimiento' if is_weekend else 'Alimentación',
                'dia_semana': date.weekday()
            })
        
        # Entrenar
        metrics = analyzer.train(weekend_data, epochs=3)
        assert metrics['status'] == 'success'
        
        # Analizar
        analysis = analyzer.analyze_patterns(weekend_data)
        insights = analysis['insights']
        
        # Debe generar algún insight relevante
        assert len(insights) > 0
    
    def test_seasonal_bolivian_expenses(self):
        """Test gastos estacionales bolivianos (carnaval, año escolar, etc.)"""
        analyzer = PatternAnalyzer()
        
        # Simular gastos especiales en fechas bolivianas
        seasonal_data = []
        base_date = datetime(2025, 1, 1)
        
        for i in range(90):  # 3 meses
            date = base_date + timedelta(days=i)
            
            # Gastos especiales
            special_amount = 0
            if date.month == 2:  # Carnaval
                special_amount = 300
            elif date.month == 3:  # Inicio clases
                special_amount = 200
            
            base_amount = 180
            total_amount = base_amount + special_amount
            
            seasonal_data.append({
                'fecha': date.strftime('%Y-%m-%d'),
                'monto': total_amount,
                'categoria': 'Entretenimiento' if special_amount > 0 else 'Alimentación'
            })
        
        # Entrenar
        metrics = analyzer.train(seasonal_data, epochs=5)
        assert metrics['status'] == 'success'
        
        # Verificar que puede procesar patrones estacionales
        analysis = analyzer.analyze_patterns(seasonal_data)
        assert analysis['pattern_type'] in ['moderate_spender', 'high_spender']


if __name__ == '__main__':
    pytest.main([__file__])
