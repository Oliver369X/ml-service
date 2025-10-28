# 🧪 Guía de Testing - Integración Completa

## 📋 Pre-requisitos

Asegúrate de tener estos servicios corriendo:

```bash
# Verificar servicios
✅ Auth Service      - http://localhost:5000/graphql
✅ Permissions API   - http://localhost:5005/graphql  
✅ ML Service        - http://localhost:5015/graphql
✅ Gateway           - http://localhost:4000/graphql
```

---

## 🎯 Test 1: Verificar que el ML Service está corriendo

### Paso 1.1: Health Check

```bash
curl http://localhost:5015/health
```

**Resultado esperado:**
```json
{
  "status": "ok",
  "database": "healthy",
  "service": "ml-service",
  "version": "1.0.0"
}
```

### Paso 1.2: Verificar Modelos

```bash
curl http://localhost:5015/models/status
```

**Resultado esperado:**
```json
{
  "classifier": {
    "loaded": true,
    "path": "models/transaction_classifier.pkl"
  },
  "forecaster": {
    "loaded": true,
    "path": "models/expense_forecaster.pkl"
  },
  "pattern_analyzer": {
    "loaded": true,
    "path": "models/pattern_analyzer.h5"
  }
}
```

✅ Si ves `"loaded": false`, entrena los modelos:
```bash
docker-compose exec ml-service python training/train_all.py
```

---

## 🎯 Test 2: ML Service Standalone (Sin Gateway)

### Paso 2.1: GraphQL Playground

Abre http://localhost:5015/graphql

### Paso 2.2: Test Clasificador

```graphql
mutation {
  classifyTransaction(input: {
    text: "KETAL SUPERMERCADO LA PAZ"
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

**Resultado esperado:**
```json
{
  "data": {
    "classifyTransaction": {
      "predictedCategory": "Groceries",
      "confidence": 0.85,
      "alternativeCategories": [
        { "category": "Food", "confidence": 0.10 }
      ]
    }
  }
}
```

### Paso 2.3: Test Forecaster

```graphql
mutation {
  generateForecast(input: {
    months: 2
  }) {
    forecastMonth
    forecastYear
    predictedAmount
    trend
  }
}
```

### Paso 2.4: Test Pattern Analyzer

```graphql
mutation {
  analyzePatterns(input: {
    months: 3
  }) {
    patternType
    stabilityScore
    insights {
      message
      severity
    }
  }
}
```

---

## 🎯 Test 3: Integración con Gateway (SIN Autenticación)

### Paso 3.1: Verificar Gateway

```bash
curl http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}'
```

### Paso 3.2: Introspección

Ver si el Gateway reconoce el ML Service:

```graphql
# En http://localhost:4000/graphql

query {
  __schema {
    types {
      name
    }
  }
}
```

Busca en la respuesta tipos como:
- `Prediction`
- `Forecast`
- `SpendingPattern`

---

## 🎯 Test 4: Integración COMPLETA (Con Autenticación)

### Paso 4.1: Login en Auth Service

```bash
# Primero, crea un usuario o usa uno existente
# Suponiendo que tienes un usuario: admin/admin

curl -X POST http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { login(input: { username: \"admin\", password: \"admin\" }) { token user { id username } } }"
  }'
```

**Guarda el token de la respuesta:**
```json
{
  "data": {
    "login": {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "user": {
        "id": "507f1f77bcf86cd799439011",
        "username": "admin"
      }
    }
  }
}
```

### Paso 4.2: Usar ML Service a través del Gateway

```bash
# Reemplaza <TOKEN> con tu token real

curl -X POST http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "query": "mutation { classifyTransaction(input: { text: \"KETAL SUPERMERCADO\" }) { predictedCategory confidence } }"
  }'
```

**Resultado esperado:**
```json
{
  "data": {
    "classifyTransaction": {
      "predictedCategory": "Groceries",
      "confidence": 0.85
    }
  }
}
```

✅ **Si funciona:** El ML Service está correctamente integrado!

---

## 🎯 Test 5: Query Unificada (Todos los Servicios)

Esta es la prueba definitiva - obtener datos de múltiples servicios en una sola query:

```graphql
# En http://localhost:4000/graphql con Authorization Header

query PerfilFinancieroCompleto {
  # Auth Service
  me {
    id
    username
    email
    
    # Permissions API
    permissions
  }
  
  # ML Service - Predicciones
  predictions(limit: 5) {
    id
    inputText
    predictedCategory
    confidence
    createdAt
  }
  
  # ML Service - Pronósticos
  forecasts {
    forecastMonth
    forecastYear
    predictedAmount
    trend
  }
  
  # ML Service - Patrones
  latestPatternAnalysis {
    patternType
    stabilityScore
    insights {
      message
    }
  }
}
```

**Si esta query funciona:** ¡ÉXITO TOTAL! 🎉

---

## 🎯 Test 6: Testing con cURL Completo

### Script de Testing Automatizado

```bash
#!/bin/bash
# test_integration.sh

echo "🧪 Testing ML Service Integration"
echo "=================================="

# Variables
GATEWAY_URL="http://localhost:4000/graphql"
ML_URL="http://localhost:5015/graphql"
TOKEN=""  # Se llenará después del login

# Test 1: Health Check
echo -e "\n✅ Test 1: Health Check"
curl -s http://localhost:5015/health | jq

# Test 2: Login
echo -e "\n✅ Test 2: Login"
LOGIN_RESPONSE=$(curl -s -X POST $GATEWAY_URL \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { login(input: { username: \"admin\", password: \"admin\" }) { token } }"
  }')

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.data.login.token')
echo "Token obtenido: ${TOKEN:0:20}..."

# Test 3: Clasificar Transacción
echo -e "\n✅ Test 3: Clasificar Transacción"
curl -s -X POST $GATEWAY_URL \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "mutation { classifyTransaction(input: { text: \"KETAL SUPERMERCADO LA PAZ\" }) { predictedCategory confidence } }"
  }' | jq

# Test 4: Generar Pronóstico
echo -e "\n✅ Test 4: Generar Pronóstico"
curl -s -X POST $GATEWAY_URL \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "mutation { generateForecast(input: { months: 2 }) { forecastMonth predictedAmount } }"
  }' | jq

# Test 5: Query Unificada
echo -e "\n✅ Test 5: Query Unificada"
curl -s -X POST $GATEWAY_URL \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "query { me { username } predictions(limit: 3) { predictedCategory } }"
  }' | jq

echo -e "\n🎉 Testing Complete!"
```

**Ejecutar:**
```bash
chmod +x test_integration.sh
./test_integration.sh
```

---

## 🎯 Test 7: Verificar Headers (Debug)

Para ver que el Gateway está enviando los headers correctamente:

### Agregar logging temporal en ML Service

Edita `ml-service/src/main.py` y agrega:

```python
@app.middleware("http")
async def log_headers(request: Request, call_next):
    logger.info(f"Headers received: {dict(request.headers)}")
    response = await call_next(request)
    return response
```

Luego verifica los logs:
```bash
docker-compose logs -f ml-service | grep "Headers received"
```

Deberías ver:
```
userid: 507f1f77bcf86cd799439011
permissions: admin,user
authorization: Bearer eyJhbG...
```

---

## 🔍 Troubleshooting

### ❌ Error: "User not authenticated"

**Causa:** El Gateway no está enviando el userId en headers

**Solución:**
1. Verifica que el token JWT sea válido
2. Verifica que JWT_SECRET sea el mismo en todos los servicios
3. Verifica los logs del gateway

```bash
cd gateway-service
npm run start:dev
# Buscar errores de JWT
```

### ❌ Error: "Cannot query field 'predictions'"

**Causa:** El Gateway no reconoce el ML Service

**Solución:**
1. Verifica que el ML Service esté corriendo
2. Verifica que esté en app.module.ts del gateway
3. Reinicia el gateway

```bash
cd gateway-service
# Ctrl+C para detener
npm run start:dev
```

### ❌ Error: "Classifier not trained"

**Causa:** Los modelos no están entrenados

**Solución:**
```bash
docker-compose exec ml-service python training/train_all.py
```

### ❌ Error: Connection refused

**Causa:** Algún servicio no está corriendo

**Solución:**
```bash
# Verificar todos los servicios
docker-compose ps
curl http://localhost:5000/graphql  # Auth
curl http://localhost:5005/graphql  # Perms
curl http://localhost:5015/graphql  # ML
curl http://localhost:4000/graphql  # Gateway
```

---

## ✅ Checklist de Integración

- [ ] ML Service corriendo en puerto 5015
- [ ] PostgreSQL conectado (health check OK)
- [ ] Modelos entrenados (models/status OK)
- [ ] GraphQL Playground funciona standalone
- [ ] Gateway reconoce ML Service (introspection)
- [ ] Login funciona y retorna token
- [ ] ML mutations funcionan con token
- [ ] Headers llegan correctamente (userId, permissions)
- [ ] Query unificada funciona
- [ ] Sin errores en logs

---

## 🎉 Resultados Esperados

Si todos los tests pasan:

✅ **ML Service funcionando** standalone  
✅ **Gateway integrado** correctamente  
✅ **Autenticación** funcionando  
✅ **Headers propagados** correctamente  
✅ **Queries unificadas** exitosas  

**¡Sistema completo funcionando!** 🚀

---

## 📊 Próximos Pasos

1. ✅ Entrenar modelos con datos reales bolivianos
2. ✅ Adaptar categorías a español
3. ✅ Agregar contexto boliviano (quincena, aguinaldo)
4. ✅ Implementar feedback loop
5. ✅ Monitoreo y métricas

---

**¿Listo para adaptar a contexto boliviano?** 🇧🇴

