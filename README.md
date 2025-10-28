# 🤖 ML/DL Microservicio - Finanzas Personales

Microservicio de Machine Learning y Deep Learning para análisis financiero inteligente.

## 🎯 Características

### Machine Learning:
1. **Clasificador de Transacciones**: Clasifica automáticamente transacciones en categorías
2. **Predicción de Gastos Futuros**: Pronostica gastos usando modelos de series temporales

### Deep Learning:
1. **Análisis de Patrones**: Detecta patrones de gasto usando redes neuronales

## 🛠️ Tecnologías

- **Python 3.11**
- **FastAPI** - Framework web
- **Strawberry GraphQL** - API GraphQL
- **PostgreSQL** - Base de datos
- **Scikit-learn** - Machine Learning
- **TensorFlow** - Deep Learning
- **Prophet** - Forecasting
- **Docker** - Contenedorización

## 🚀 Instalación

### Opción 1: Con Docker (Recomendado)

```bash
# 1. Copiar variables de entorno
cp .env.example .env

# 2. Levantar servicios
docker-compose up --build

# El servicio estará disponible en http://localhost:5015/graphql
```

### Opción 2: Local

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 4. Levantar PostgreSQL
docker-compose up postgres-ml -d

# 5. Ejecutar migraciones
alembic upgrade head

# 6. Entrenar modelos iniciales
python training/train_all.py

# 7. Iniciar servidor
uvicorn src.main:app --reload --port 5015
```

## 📊 Endpoints

- **GraphQL Playground**: http://localhost:5015/graphql
- **Health Check**: http://localhost:5015/health
- **Docs**: http://localhost:5015/docs

## 🔧 Uso

### Clasificar una transacción

```graphql
mutation {
  classifyTransaction(input: {
    text: "Uber del trabajo a casa"
    amount: 15.50
  }) {
    predictedCategory
    confidence
    alternativeCategories {
      category
      confidence
    }
  }
}
```

### Generar pronósticos

```graphql
mutation {
  generateForecast(input: {
    months: 3
  }) {
    forecastMonth
    forecastYear
    predictedAmount
    confidenceInterval {
      lower
      upper
    }
    trend
  }
}
```

### Analizar patrones

```graphql
query {
  analyzePatterns(months: 6) {
    patternType
    insights
    trends
  }
}
```

## 🏗️ Estructura del Proyecto

```
ml-service/
├── src/
│   ├── main.py              # Entry point
│   ├── config.py            # Configuración
│   ├── graphql/             # GraphQL layer
│   ├── database/            # Database models
│   ├── ml/                  # ML models
│   ├── dl/                  # DL models
│   ├── services/            # Business logic
│   └── utils/               # Utilities
├── models/                  # Trained models
├── training/                # Training scripts
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## 🔗 Integración con Gateway

Este servicio se integra con el Apollo Gateway. El gateway maneja la autenticación JWT y pasa el `userId` en los headers.

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=src
```

## 📝 Variables de Entorno

Ver `.env.example` para todas las variables disponibles.

**IMPORTANTE**: `JWT_SECRET` debe ser el mismo en todos los microservicios.

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu feature branch
3. Commit tus cambios
4. Push al branch
5. Abre un Pull Request

