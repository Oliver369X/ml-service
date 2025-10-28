"""
Entrenar modelos con datos bolivianos
"""
import sys
import os
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ml import TransactionClassifier, ExpenseForecaster
from src.dl import PatternAnalyzer
from src.utils.logger import logger


def cargar_datos_bolivia():
    """Cargar datos de ejemplo bolivianos desde CSV"""
    
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'transacciones_bolivia_ejemplo.csv')
    
    if not os.path.exists(csv_path):
        logger.error(f"No se encontró el archivo: {csv_path}")
        return None
    
    df = pd.read_csv(csv_path)
    logger.info(f"✅ Cargados {len(df)} transacciones desde CSV")
    
    return df


def train_classifier_bolivia():
    """Entrenar clasificador con datos bolivianos"""
    logger.info("=" * 60)
    logger.info("🇧🇴 Entrenando Clasificador con Datos Bolivianos")
    logger.info("=" * 60)
    
    # Cargar datos
    df = cargar_datos_bolivia()
    if df is None:
        logger.error("No se pudieron cargar los datos")
        return
    
    # Preparar datos
    texts = df['descripcion'].tolist()
    labels = df['categoria'].tolist()
    
    logger.info(f"📊 Datos de entrenamiento:")
    logger.info(f"   - Total transacciones: {len(texts)}")
    logger.info(f"   - Categorías únicas: {df['categoria'].nunique()}")
    logger.info(f"   - Categorías: {df['categoria'].unique().tolist()}")
    
    # Entrenar
    classifier = TransactionClassifier()
    metrics = classifier.train(texts, labels)
    
    logger.info(f"\n✅ Clasificador entrenado exitosamente!")
    logger.info(f"   📈 Precisión: {metrics['accuracy']:.2%}")
    logger.info(f"   📊 Muestras: {metrics['num_samples']}")
    logger.info(f"   🏷️  Categorías: {metrics['num_categories']}")
    
    # Probar con ejemplos bolivianos
    logger.info("\n🧪 Probando clasificador con ejemplos bolivianos:")
    
    test_cases = [
        "KETAL SUPERMERCADO MIRAFLORES",
        "TAXI LA PAZ SOPOCACHI",
        "MERCADO LANZA FRUTAS",
        "DELAPAZ PAGO LUZ",
        "NETFLIX MENSUALIDAD",
        "ENTEL PLAN CELULAR",
        "FARMACIA CHAVEZ",
        "HIPERMAXI IRPAVI",
        "TELEFERICO ROJO",
        "ALQUILER DEPARTAMENTO"
    ]
    
    for text in test_cases:
        predictions = classifier.predict(text, top_k=2)
        logger.info(f"   '{text}'")
        logger.info(f"      → {predictions[0]['category']} ({predictions[0]['confidence']:.1%})")


def train_forecaster_bolivia():
    """Entrenar predictor con datos bolivianos"""
    logger.info("\n" + "=" * 60)
    logger.info("🇧🇴 Entrenando Predictor de Gastos con Datos Bolivianos")
    logger.info("=" * 60)
    
    # Cargar datos
    df = cargar_datos_bolivia()
    if df is None:
        return
    
    # Convertir a formato requerido
    transactions = []
    for _, row in df.iterrows():
        transactions.append({
            'id': row['id_transaccion'],
            'user_id': 'user_bolivia',
            'amount': row['monto'],
            'date': row['fecha'],
            'category': row['categoria'],
            'description': row['descripcion']
        })
    
    logger.info(f"📊 Datos de entrenamiento:")
    logger.info(f"   - Total transacciones: {len(transactions)}")
    logger.info(f"   - Rango de fechas: {df['fecha'].min()} a {df['fecha'].max()}")
    logger.info(f"   - Monto total: Bs. {df['monto'].sum():,.2f}")
    logger.info(f"   - Promedio diario: Bs. {df['monto'].mean():,.2f}")
    
    # Entrenar
    forecaster = ExpenseForecaster()
    
    try:
        metrics = forecaster.train(transactions)
        
        logger.info(f"\n✅ Predictor entrenado exitosamente!")
        logger.info(f"   📊 Muestras: {metrics['num_samples']}")
        logger.info(f"   📅 Período: {metrics['date_range']['start']} a {metrics['date_range']['end']}")
        
        if metrics.get('mape'):
            logger.info(f"   📈 MAPE: {metrics['mape']:.2%}")
        
        # Probar pronósticos
        logger.info("\n🧪 Generando pronósticos para próximos 3 meses:")
        forecasts = forecaster.forecast_by_month(months=3)
        
        for forecast in forecasts:
            logger.info(f"   📅 {forecast['year']}-{forecast['month']:02d}: Bs. {forecast['predicted_amount']:,.2f}")
            logger.info(f"      Tendencia: {forecast['trend']}")
    
    except Exception as e:
        logger.error(f"❌ Error entrenando predictor: {e}")


def train_pattern_analyzer_bolivia():
    """Entrenar analizador de patrones con datos bolivianos"""
    logger.info("\n" + "=" * 60)
    logger.info("🇧🇴 Entrenando Analizador de Patrones (Deep Learning)")
    logger.info("=" * 60)
    
    # Cargar datos
    df = cargar_datos_bolivia()
    if df is None:
        return
    
    # Convertir a formato requerido
    transactions = []
    for _, row in df.iterrows():
        transactions.append({
            'id': row['id_transaccion'],
            'user_id': 'user_bolivia',
            'amount': row['monto'],
            'date': row['fecha'],
            'category': row['categoria'],
            'description': row['descripcion']
        })
    
    logger.info(f"📊 Datos de entrenamiento:")
    logger.info(f"   - Total transacciones: {len(transactions)}")
    
    # Entrenar
    analyzer = PatternAnalyzer()
    
    try:
        metrics = analyzer.train(transactions, epochs=30)
        
        logger.info(f"\n✅ Analizador de patrones entrenado exitosamente!")
        logger.info(f"   📊 Muestras: {metrics['num_samples']}")
        logger.info(f"   📉 Loss: {metrics['loss']:.4f}")
        logger.info(f"   📉 Val Loss: {metrics['val_loss']:.4f}")
        logger.info(f"   🔄 Épocas: {metrics['epochs_trained']}")
        
        # Analizar patrones
        logger.info("\n🧪 Analizando patrones de gasto:")
        analysis = analyzer.analyze_patterns(transactions)
        
        logger.info(f"   🎯 Tipo de patrón: {analysis['pattern_type']}")
        logger.info(f"   📊 Score de estabilidad: {analysis['stability_score']:.2f}")
        logger.info(f"   ⚠️  Días inusuales: {analysis['unusual_days']}")
        
        logger.info(f"\n   💡 Insights detectados:")
        for insight in analysis['insights'][:3]:  # Mostrar primeros 3
            logger.info(f"      - {insight['message']}")
    
    except Exception as e:
        logger.error(f"❌ Error entrenando analizador: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Entrenar todos los modelos con datos bolivianos"""
    logger.info("🇧🇴 " + "=" * 56)
    logger.info("🇧🇴  ENTRENAMIENTO CON DATOS BOLIVIANOS")
    logger.info("🇧🇴 " + "=" * 56)
    logger.info("")
    
    try:
        # Entrenar todos los modelos
        train_classifier_bolivia()
        train_forecaster_bolivia()
        train_pattern_analyzer_bolivia()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ ¡Todos los modelos entrenados con datos bolivianos!")
        logger.info("=" * 60)
        logger.info("")
        logger.info("📝 Modelos guardados:")
        logger.info("   - models/transaction_classifier.pkl")
        logger.info("   - models/expense_forecaster.pkl")
        logger.info("   - models/pattern_analyzer.h5")
        logger.info("")
        logger.info("🚀 Ahora puedes iniciar el servicio:")
        logger.info("   docker-compose up")
        logger.info("   o")
        logger.info("   uvicorn src.main:app --reload --port 5015")
        logger.info("")
        
    except Exception as e:
        logger.error(f"\n❌ Error en entrenamiento: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

