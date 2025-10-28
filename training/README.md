# 🎓 Model Training

Scripts para entrenar los modelos de ML/DL.

## Entrenamiento Inicial

Para entrenar todos los modelos con datos de ejemplo:

```bash
python training/train_all.py
```

Esto generará:
- `models/transaction_classifier.pkl` - Clasificador de transacciones
- `models/expense_forecaster.pkl` - Predictor de gastos
- `models/pattern_analyzer.h5` - Analizador de patrones (+ archivos auxiliares)

## Entrenamiento Individual

### Clasificador de Transacciones
```python
from src.ml import TransactionClassifier

texts = ["Uber ride", "Pizza dinner", "Rent payment"]
labels = ["Transport", "Food", "Bills"]

classifier = TransactionClassifier()
classifier.train(texts, labels)
```

### Predictor de Gastos
```python
from src.ml import ExpenseForecaster

transactions = [
    {'date': '2025-01-01', 'amount': 50.0},
    {'date': '2025-01-02', 'amount': 75.0},
    # ... más transacciones
]

forecaster = ExpenseForecaster()
forecaster.train(transactions)
```

### Analizador de Patrones
```python
from src.dl import PatternAnalyzer

transactions = [
    {
        'id': '1',
        'date': '2025-01-01',
        'amount': 50.0,
        'category': 'Food'
    },
    # ... más transacciones
]

analyzer = PatternAnalyzer()
analyzer.train(transactions, epochs=50)
```

## Mejora Continua

Los modelos pueden ser re-entrenados periódicamente con datos reales para mejorar su precisión:

1. Exportar transacciones reales de la base de datos
2. Entrenar los modelos con estos datos
3. Los modelos se guardan automáticamente al finalizar el entrenamiento

## Notas

- Los modelos entrenados se guardan en la carpeta `models/`
- El primer entrenamiento usa datos sintéticos
- En producción, re-entrena con datos reales mensualmente

