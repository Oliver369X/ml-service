"""
Train all ML/DL models with sample data
Run this script to initialize models before first use
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ml import TransactionClassifier, ExpenseForecaster
from src.dl import PatternAnalyzer
from src.utils.logger import logger
from datetime import datetime, timedelta
import random


def generate_sample_transactions(num_samples=500):
    """Generate sample transaction data for training"""
    
    categories = ['Food', 'Transport', 'Bills', 'Entertainment', 'Groceries', 'Shopping', 'Health']
    
    # Category keywords for generating realistic descriptions
    category_keywords = {
        'Food': ['restaurant', 'cafe', 'pizza', 'burger', 'lunch', 'dinner', 'breakfast'],
        'Transport': ['uber', 'taxi', 'bus', 'metro', 'gas', 'parking'],
        'Bills': ['rent', 'electricity', 'water', 'internet', 'phone', 'insurance'],
        'Entertainment': ['netflix', 'spotify', 'cinema', 'concert', 'game'],
        'Groceries': ['supermarket', 'walmart', 'grocery', 'market'],
        'Shopping': ['amazon', 'clothing', 'shoes', 'electronics', 'store'],
        'Health': ['pharmacy', 'doctor', 'gym', 'medicine']
    }
    
    transactions = []
    texts = []
    labels = []
    
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(num_samples):
        category = random.choice(categories)
        keyword = random.choice(category_keywords[category])
        
        # Generate description
        description = f"{keyword} payment"
        if random.random() > 0.5:
            description += f" at {keyword} place"
        
        # Generate amount
        amount = random.uniform(10, 200)
        
        # Generate date
        date = start_date + timedelta(days=random.randint(0, 365))
        
        transactions.append({
            'id': str(i),
            'user_id': 'sample-user',
            'amount': amount,
            'date': date.isoformat(),
            'category': category,
            'description': description
        })
        
        texts.append(description)
        labels.append(category)
    
    return transactions, texts, labels


def train_classifier():
    """Train transaction classifier"""
    logger.info("=" * 50)
    logger.info("Training Transaction Classifier")
    logger.info("=" * 50)
    
    # Generate training data
    _, texts, labels = generate_sample_transactions(500)
    
    # Train
    classifier = TransactionClassifier()
    metrics = classifier.train(texts, labels)
    
    logger.info(f"✅ Classifier trained successfully!")
    logger.info(f"   Accuracy: {metrics['accuracy']:.2%}")
    logger.info(f"   Samples: {metrics['num_samples']}")
    logger.info(f"   Categories: {metrics['num_categories']}")
    logger.info(f"   Categories list: {', '.join(metrics['categories'])}")
    
    # Test
    test_texts = [
        "Uber ride to airport",
        "Pizza dinner",
        "Monthly rent payment",
        "Netflix subscription"
    ]
    
    logger.info("\nTesting classifier:")
    for text in test_texts:
        predictions = classifier.predict(text, top_k=2)
        logger.info(f"  '{text}' → {predictions[0]['category']} ({predictions[0]['confidence']:.2%})")


def train_forecaster():
    """Train expense forecaster"""
    logger.info("\n" + "=" * 50)
    logger.info("Training Expense Forecaster")
    logger.info("=" * 50)
    
    # Generate training data
    transactions, _, _ = generate_sample_transactions(500)
    
    # Train
    forecaster = ExpenseForecaster()
    
    try:
        metrics = forecaster.train(transactions)
        
        logger.info(f"✅ Forecaster trained successfully!")
        logger.info(f"   Samples: {metrics['num_samples']}")
        logger.info(f"   Date range: {metrics['date_range']['start']} to {metrics['date_range']['end']}")
        
        if metrics.get('mape'):
            logger.info(f"   MAPE: {metrics['mape']:.2%}")
        if metrics.get('rmse'):
            logger.info(f"   RMSE: {metrics['rmse']:.2f}")
        
        # Test
        logger.info("\nTesting forecaster:")
        forecasts = forecaster.forecast_by_month(months=3)
        for forecast in forecasts:
            logger.info(f"  {forecast['year']}-{forecast['month']:02d}: ${forecast['predicted_amount']:.2f}")
    
    except Exception as e:
        logger.error(f"❌ Error training forecaster: {e}")
        logger.info("Forecaster will use default predictions")


def train_pattern_analyzer():
    """Train pattern analyzer"""
    logger.info("\n" + "=" * 50)
    logger.info("Training Pattern Analyzer")
    logger.info("=" * 50)
    
    # Generate training data
    transactions, _, _ = generate_sample_transactions(500)
    
    # Train
    analyzer = PatternAnalyzer()
    
    try:
        metrics = analyzer.train(transactions, epochs=30)
        
        logger.info(f"✅ Pattern analyzer trained successfully!")
        logger.info(f"   Samples: {metrics['num_samples']}")
        logger.info(f"   Loss: {metrics['loss']:.4f}")
        logger.info(f"   Val Loss: {metrics['val_loss']:.4f}")
        logger.info(f"   Epochs: {metrics['epochs_trained']}")
        
        # Test
        logger.info("\nTesting pattern analyzer:")
        analysis = analyzer.analyze_patterns(transactions[-100:])  # Last 100 transactions
        logger.info(f"  Pattern type: {analysis['pattern_type']}")
        logger.info(f"  Stability score: {analysis['stability_score']:.2f}")
        logger.info(f"  Unusual days: {analysis['unusual_days']}")
        logger.info(f"  Patterns detected: {len(analysis['patterns'])}")
        logger.info(f"  Insights: {len(analysis['insights'])}")
    
    except Exception as e:
        logger.error(f"❌ Error training pattern analyzer: {e}")
        logger.info("Pattern analyzer will use rule-based analysis")


def main():
    """Main training script"""
    logger.info("🚀 Starting ML/DL Models Training")
    logger.info("This may take a few minutes...\n")
    
    try:
        # Train all models
        train_classifier()
        train_forecaster()
        train_pattern_analyzer()
        
        logger.info("\n" + "=" * 50)
        logger.info("✅ All models trained successfully!")
        logger.info("=" * 50)
        logger.info("\nYou can now start the ML service:")
        logger.info("  uvicorn src.main:app --reload --port 5015")
        
    except Exception as e:
        logger.error(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

