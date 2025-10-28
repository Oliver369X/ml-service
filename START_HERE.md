# 🚀 ML Service - Inicio Rápido

## ⚡ Opción 1: Docker (Recomendado)

```bash
cd ml-service

# 1. Copiar variables de entorno
cp .env.example .env

# 2. Levantar todo con Docker
docker-compose up --build

# El servicio estará en: http://localhost:5015/graphql
```

Eso es todo! El servicio incluye:
- ✅ PostgreSQL
- ✅ ML Service
- ✅ GraphQL Playground
- ✅ Modelos entrenados automáticamente

---

## 💻 Opción 2: Local (Para Desarrollo)

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Variables de entorno
cp .env.example .env

# 4. Levantar PostgreSQL
docker-compose up postgres-ml -d

# 5. Entrenar modelos
python training/train_all.py

# 6. Iniciar servidor
uvicorn src.main:app --reload --port 5015
```

---

## 🧪 Probar el Servicio

### 1. Health Check

```bash
curl http://localhost:5015/health
```

### 2. GraphQL Playground

Abrir en navegador: http://localhost:5015/graphql

### 3. Clasificar una transacción

```graphql
mutation {
  classifyTransaction(input: {
    text: "Uber ride to work"
  }) {
    predictedCategory
    confidence
  }
}
```

### 4. Generar pronósticos

```graphql
mutation {
  generateForecast(input: {
    months: 3
  }) {
    forecastMonth
    forecastYear
    predictedAmount
  }
}
```

---

## 🔗 Integrar con Gateway

```bash
# El ML Service ya está registrado en el gateway
cd ../gateway-service

# Asegúrate de que JWT_SECRET sea el mismo
export JWT_SECRET=WERWRWERWERW

# Inicia el gateway
npm run start:dev

# Ahora puedes hacer queries unificadas en:
# http://localhost:4000/graphql
```

---

## 📚 Próximos Pasos

1. **Leer:** [USAGE_GUIDE.md](./USAGE_GUIDE.md) - Guía completa de uso
2. **Explorar:** GraphQL Playground en http://localhost:5015/graphql
3. **Personalizar:** Entrenar modelos con tus propios datos
4. **Monitorear:** Health checks y métricas

---

## ⚠️ Problemas Comunes

### No se conecta a la base de datos
```bash
# Verificar PostgreSQL
docker-compose ps
docker-compose logs postgres-ml
```

### Modelos no funcionan
```bash
# Re-entrenar modelos
python training/train_all.py
```

### Gateway no encuentra el servicio
```bash
# Verificar que esté corriendo
curl http://localhost:5015/health

# Verificar en gateway que esté en subgraphs
# gateway-service/src/app.module.ts línea 104
```

---

## 🎯 ¿Todo listo?

Ahora tienes un microservicio completo de ML/DL funcionando! 🎉

**Características:**
- ✅ Clasificación automática de transacciones
- ✅ Predicción de gastos futuros
- ✅ Análisis de patrones con Deep Learning
- ✅ GraphQL API
- ✅ Dockerizado
- ✅ Integrado con Gateway

**Disfruta!** 🚀

