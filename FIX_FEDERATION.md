# 🔧 Arreglar Apollo Federation

## Problema Encontrado

El gateway no puede conectarse al ML service porque **Strawberry GraphQL** necesita configuración especial para **Apollo Federation**.

Error:
```
Error: Couldn't load service definitions for "ML" at http://localhost:5015/graphql: 
request failed, reason: socket hang up
```

---

## ✅ Solución Implementada

### Paso 1: Actualizar requirements.txt

Agregado soporte para Federation:
```python
strawberry-graphql[apollo-federation]==0.219.0
```

### Paso 2: Actualizar schema.py

Cambiado de:
```python
import strawberry
schema = strawberry.Schema(...)
```

A:
```python
from strawberry.federation import Schema
schema = Schema(..., enable_federation_2=True)
```

---

## 🚀 Cómo Aplicar el Fix

### Opción 1: Docker (Recomendado)

```bash
cd ml-service

# 1. Reconstruir con nuevas dependencias
docker-compose down
docker-compose build
docker-compose up

# El servicio ahora será compatible con Apollo Federation
```

### Opción 2: Local

```bash
cd ml-service

# 1. Activar entorno virtual
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instalar nuevas dependencias
pip install strawberry-graphql[apollo-federation]==0.219.0

# 3. Reiniciar servicio
uvicorn src.main:app --reload --port 5015
```

---

## 🧪 Verificar que Funciona

### 1. Verificar ML Service

```bash
# Debe responder con schema de Federation
curl http://localhost:5015/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ _service { sdl } }"}'
```

**Respuesta esperada:**
```json
{
  "data": {
    "_service": {
      "sdl": "type Query { ... }"
    }
  }
}
```

### 2. Descomentar en Gateway

Editar `gateway-service/src/app.module.ts` línea 104:

```typescript
// Cambiar de:
//{ name: 'ML', url: 'http://localhost:5015/graphql' },

// A:
{ name: 'ML', url: 'http://localhost:5015/graphql' },
```

### 3. Reiniciar Gateway

```bash
cd gateway-service
# Ctrl+C para detener
npm run start:dev
```

**El gateway ahora debería iniciar sin errores!** ✅

---

## 📝 Archivos Modificados

1. ✅ `ml-service/requirements.txt` - Agregado federation support
2. ✅ `ml-service/src/graphql/schema.py` - Cambiado a Federation Schema
3. ✅ `gateway-service/src/app.module.ts` - Comentado temporalmente

---

## 🎯 Alternativa: Usar ML Service Standalone

Si no necesitas Apollo Federation (queries unificadas), puedes usar el ML service **directamente**:

```graphql
# Directo a ML Service (sin gateway)
# http://localhost:5015/graphql

mutation {
  classifyTransaction(input: {
    text: "KETAL SUPERMERCADO LA PAZ"
  }) {
    predictedCategory
    confidence
  }
}
```

**Ventajas:**
- ✅ Funciona inmediatamente
- ✅ No necesita gateway
- ✅ Más simple para desarrollo

**Desventajas:**
- ❌ No tiene queries unificadas
- ❌ Debes manejar autenticación manualmente

---

## 💡 Recomendación

Para **desarrollo/testing inicial**:
→ Usa el ML service **standalone** (puerto 5015 directo)

Para **producción**:
→ Aplica el fix de Federation y usa el gateway

---

## 🆘 Si Sigue sin Funcionar

### Debug paso a paso:

```bash
# 1. Verificar que ML service está corriendo
curl http://localhost:5015/health

# 2. Verificar que responde GraphQL
curl http://localhost:5015/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}'

# 3. Verificar Federation
curl http://localhost:5015/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ _service { sdl } }"}'

# 4. Ver logs del ML service
docker-compose logs -f ml-service
```

---

## ✅ Checklist

- [ ] Instalado `strawberry-graphql[apollo-federation]`
- [ ] Actualizado schema.py con Federation Schema
- [ ] Reconstruido Docker image
- [ ] ML service responde a `{ _service { sdl } }`
- [ ] Descomentado en gateway
- [ ] Gateway inicia sin errores

---

¡Listo! 🚀

