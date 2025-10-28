# 📘 Guía de Uso - ML Service

## 🚀 Inicio Rápido

### 1. Levantar el servicio con Docker

```bash
cd ml-service

# Copiar variables de entorno
cp .env.example .env

# Levantar PostgreSQL y ML Service
docker-compose up --build
```

El servicio estará disponible en: http://localhost:5015/graphql

### 2. Opción Local (sin Docker)

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables de entorno
cp .env.example .env

# Levantar PostgreSQL
docker-compose up postgres-ml -d

# Entrenar modelos iniciales
python training/train_all.py

# Iniciar servidor
uvicorn src.main:app --reload --port 5015
```

---

## 📊 Endpoints Disponibles

| Endpoint | Descripción |
|----------|-------------|
| `GET /` | Info del servicio |
| `GET /health` | Health check |
| `GET /models/status` | Estado de modelos ML |
| `POST /graphql` | GraphQL API |

---

## 🎯 Ejemplos de Uso GraphQL

### 1. Clasificar una Transacción

```graphql
mutation {
  classifyTransaction(input: {
    text: "Uber del trabajo a casa"
    amount: 15.50
  }) {
    id
    predictedCategory
    confidence
    alternativeCategories {
      category
      confidence
    }
  }
}
```

**Respuesta:**
```json
{
  "data": {
    "classifyTransaction": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "predictedCategory": "Transport",
      "confidence": 0.95,
      "alternativeCategories": [
        {
          "category": "Other",
          "confidence": 0.03
        }
      ]
    }
  }
}
```

### 2. Generar Pronósticos de Gastos

```graphql
mutation {
  generateForecast(input: {
    months: 3
  }) {
    id
    forecastMonth
    forecastYear
    predictedAmount
    confidenceInterval {
      lower
      upper
      confidence
    }
    trend
  }
}
```

**Respuesta:**
```json
{
  "data": {
    "generateForecast": [
      {
        "id": "...",
        "forecastMonth": 11,
        "forecastYear": 2025,
        "predictedAmount": 1250.75,
        "confidenceInterval": {
          "lower": 1100.50,
          "upper": 1400.00,
          "confidence": 0.95
        },
        "trend": "increasing"
      },
      {
        "id": "...",
        "forecastMonth": 12,
        "forecastYear": 2025,
        "predictedAmount": 1380.25,
        "confidenceInterval": {
          "lower": 1200.00,
          "upper": 1550.00,
          "confidence": 0.95
        },
        "trend": "increasing"
      }
    ]
  }
}
```

### 3. Analizar Patrones de Gasto

```graphql
mutation {
  analyzePatterns(input: {
    months: 6
  }) {
    userId
    patternType
    patterns {
      type
      description
      impact
    }
    insights {
      category
      message
      severity
    }
    stabilityScore
    unusualDays
  }
}
```

**Respuesta:**
```json
{
  "data": {
    "analyzePatterns": {
      "userId": "123",
      "patternType": "consistent_spender",
      "patterns": [
        {
          "type": "weekend_spender",
          "description": "Gastas significativamente más los fines de semana",
          "impact": "high"
        }
      ],
      "insights": [
        {
          "category": "spending_summary",
          "message": "Promedio diario de gastos: $85.50",
          "severity": "INFO"
        },
        {
          "category": "top_spending",
          "message": "Tu mayor gasto es en Food: $450.00",
          "severity": "INFO"
        }
      ],
      "stabilityScore": 0.75,
      "unusualDays": 3
    }
  }
}
```

### 4. Consultar Predicciones Anteriores

```graphql
query {
  predictions(limit: 10) {
    id
    inputText
    predictedCategory
    confidence
    createdAt
  }
}
```

### 5. Consultar Pronósticos Guardados

```graphql
query {
  forecasts {
    forecastMonth
    forecastYear
    predictedAmount
    trend
  }
}
```

---

## 🔗 Uso a través del Gateway

Una vez integrado con el gateway (puerto 4000), puedes hacer queries unificadas:

```graphql
# A través del gateway: http://localhost:4000/graphql

query {
  me {
    # Auth Service
    id
    username
    email
    
    # Permissions API
    permissions
  }
  
  # ML Service
  predictions(limit: 5) {
    predictedCategory
    confidence
  }
  
  forecasts {
    forecastMonth
    forecastYear
    predictedAmount
  }
}
```

---

## 🔐 Autenticación

### Standalone (Desarrollo)

El servicio puede funcionar sin autenticación para desarrollo:

```bash
# Simplemente no envíes headers de autenticación
curl -X POST http://localhost:5015/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}'
```

### A través del Gateway (Producción)

El gateway maneja la autenticación JWT:

```bash
# 1. Login en auth-service
curl -X POST http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { login(username: \"user\", password: \"pass\") { token } }"
  }'

# 2. Usar token en requests
curl -X POST http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "query": "mutation { classifyTransaction(input: {text: \"Uber ride\"}) { predictedCategory } }"
  }'
```

---

## 🧪 Testing

### Test Unitarios

```bash
pytest tests/
```

### Test de Integración

```bash
# 1. Levantar servicio
docker-compose up -d

# 2. Ejecutar tests
pytest tests/integration/

# 3. Detener servicio
docker-compose down
```

### Test Manual con GraphQL Playground

1. Abrir http://localhost:5015/graphql
2. Probar las mutations y queries de ejemplo
3. Ver la documentación auto-generada en el panel derecho

---

## 📝 Logs

Los logs se muestran en formato JSON para fácil análisis:

```bash
# Ver logs del servicio
docker-compose logs -f ml-service

# Filtrar por nivel
docker-compose logs -f ml-service | grep ERROR
```

---

## 🔧 Troubleshooting

### El servicio no inicia

```bash
# Verificar logs
docker-compose logs ml-service

# Verificar PostgreSQL
docker-compose logs postgres-ml

# Reiniciar servicios
docker-compose restart
```

### Modelos no entrenados

```bash
# Entrenar modelos manualmente
docker-compose exec ml-service python training/train_all.py
```

### Error de conexión a base de datos

```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps

# Verificar variables de entorno
docker-compose exec ml-service env | grep DATABASE
```

### Gateway no puede conectar al ML Service

```bash
# Verificar que el servicio esté corriendo
curl http://localhost:5015/health

# Verificar que el schema GraphQL sea válido
curl http://localhost:5015/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}'
```

---

## 📊 Monitoreo

### Health Check

```bash
curl http://localhost:5015/health
```

### Status de Modelos

```bash
curl http://localhost:5015/models/status
```

### Métricas de Base de Datos

```sql
-- Conectar a PostgreSQL
docker-compose exec postgres-ml psql -U mluser -d mldb

-- Ver estadísticas
SELECT 
  'predictions' as table_name, 
  COUNT(*) as count 
FROM ml_predictions
UNION ALL
SELECT 
  'forecasts', 
  COUNT(*) 
FROM forecasts
UNION ALL
SELECT 
  'patterns', 
  COUNT(*) 
FROM spending_patterns;
```

---

## 🚀 Deployment

### Variables de Entorno Importantes

```bash
# Producción
ENV=production
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@host:port/db

# JWT Secret (DEBE SER EL MISMO que auth-service)
JWT_SECRET=your-secret-key

# URLs de servicios
EXPENSES_SERVICE_URL=http://expenses-service:5010
```

### Docker Compose Producción

```yaml
version: '3.8'

services:
  ml-service:
    image: your-registry/ml-service:latest
    environment:
      ENV: production
      DATABASE_URL: ${DATABASE_URL}
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "5015:5015"
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5015/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

---

## 💡 Mejores Prácticas

1. **Re-entrenar modelos periódicamente** con datos reales
2. **Monitorear la confianza** de las predicciones
3. **Recolectar feedback** de usuarios para mejorar modelos
4. **Usar cache** para predicciones frecuentes
5. **Escalar horizontalmente** si es necesario

---

## 🆘 Soporte

Para problemas o preguntas:
1. Revisar logs: `docker-compose logs -f ml-service`
2. Verificar health check: `curl http://localhost:5015/health`
3. Consultar documentación del código
4. Revisar GitHub Issues

