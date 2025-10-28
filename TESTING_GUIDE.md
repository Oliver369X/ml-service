# 🧪 Guía de Testing - ML Service

Guía completa para ejecutar y mantener tests del ML Service con datos bolivianos.

## 📋 Índice

- [Configuración Inicial](#configuración-inicial)
- [Tipos de Tests](#tipos-de-tests)
- [Ejecutar Tests](#ejecutar-tests)
- [Tests Específicos Bolivianos](#tests-específicos-bolivianos)
- [Tests de Integración](#tests-de-integración)
- [Cobertura de Código](#cobertura-de-código)
- [CI/CD](#cicd)

---

## ⚙️ Configuración Inicial

### 1. Instalar Dependencias de Testing

```bash
# En ml-service/
pip install -r requirements-test.txt
```

### 2. Variables de Entorno para Tests

```bash
# En .env.test
ENV=test
LOG_LEVEL=ERROR
DATABASE_URL=postgresql://mluser:mlpassword@localhost:5433/ml_test_db
```

### 3. Configurar Base de Datos de Test

```bash
# Crear DB separada para tests
docker exec ml-postgres psql -U mluser -c "CREATE DATABASE ml_test_db;"
```

---

## 📝 Tipos de Tests

### 🔸 Tests Unitarios (`unit`)
- **Clasificador**: `test_classifier.py`
- **Forecaster**: `test_forecaster.py`  
- **Pattern Analyzer**: `test_pattern_analyzer.py`

### 🔸 Tests de Integración (`integration`)
- **Servicios**: `test_integration.py`
- **GraphQL Federation**: Gateway ↔ ML Service

### 🔸 Tests Bolivianos (`bolivian_data`)
- **Datos específicos**: `test_bolivian_specific.py`
- **Comercios bolivianos**: KETAL, Hipermaxi, etc.
- **Patrones locales**: Quincena, aguinaldo, carnaval

---

## 🚀 Ejecutar Tests

### Usando Script Python (Recomendado)

```bash
# Tests básicos
python run_tests.py

# Solo tests unitarios
python run_tests.py --unit

# Solo tests de integración
python run_tests.py --integration

# Solo tests bolivianos
python run_tests.py --bolivian

# Con cobertura
python run_tests.py --coverage

# Tests rápidos (skip lentos)
python run_tests.py --fast

# Archivo específico
python run_tests.py --file test_classifier.py
```

### Usando Pytest Directamente

```bash
# Todos los tests
pytest tests/ -v

# Por marcadores
pytest -m unit -v
pytest -m integration -v
pytest -m bolivian_data -v

# Tests específicos
pytest tests/test_classifier.py::TestTransactionClassifier::test_train_classifier_success -v

# Con cobertura
pytest --cov=src --cov-report=html tests/
```

---

## 🇧🇴 Tests Específicos Bolivianos

### Comercios Incluidos

**Supermercados:**
- KETAL (Miraflores, Calacoto, Zona Sur)
- Hipermaxi (Megacenter, Irpavi)
- IC Norte

**Transporte:**
- Teleférico (Roja, Amarilla, Verde)
- Radio Taxi, Pumakatari
- Minibuses

**Servicios:**
- DELAPAZ (electricidad)
- EPSAS (agua)
- ENTEL, TIGO, VIVA

**Bancos:**
- Banco Unión, BCP, Mercantil Santa Cruz
- Cooperativas

### Patrones Bolivianos Probados

```python
# Patrón de Quincena
test_quincena_spending_pattern()
# Gastos altos días 15 y 30

# Patrón de Aguinaldo  
test_aguinaldo_spending_pattern()
# Gastos altos en diciembre/enero

# Carnaval
test_carnival_spending_spike()
# Pico de gastos en febrero
```

### Ejecutar Solo Tests Bolivianos

```bash
# Todos los tests bolivianos
pytest -m bolivian_data -v

# Test específico de comercios
pytest tests/test_bolivian_specific.py::TestBolivianTransactionClassifier -v

# Test de patrones estacionales
pytest tests/test_bolivian_specific.py::TestBolivianSpendingPatterns -v
```

---

## 🔗 Tests de Integración

### Prerequisitos

Los servicios deben estar ejecutándose:

```bash
# ML Service
docker-compose up ml-service

# Opcional: Gateway (para tests completos)
cd ../gateway-service
npm run start:dev
```

### Tests Disponibles

```bash
# Tests directos al ML Service
pytest tests/test_integration.py::TestMLServiceDirect -v

# Tests de comunicación entre servicios
pytest tests/test_integration.py::TestServiceCommunication -v

# Tests del Gateway (requiere gateway corriendo)
pytest tests/test_integration.py::TestGatewayIntegration -v
```

### Verificar Servicios

```bash
# Health check ML Service
curl http://localhost:5015/health

# GraphQL ML Service
curl -X POST http://localhost:5015/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __typename }"}'
```

---

## 📊 Cobertura de Código

### Generar Reporte

```bash
# HTML (recomendado)
pytest --cov=src --cov-report=html tests/

# Ver en navegador
open htmlcov/index.html
```

### Objetivos de Cobertura

- **Mínimo**: 70%
- **Objetivo**: 85%
- **Crítico**: 95% (clasificador)

### Archivos Excluidos

- Tests (`tests/`)
- Migraciones (`migrations/`)
- Configuración (`config.py`)

---

## 🎯 Ejemplos de Uso

### Test Clasificador con Datos Bolivianos

```python
def test_ketal_classification():
    classifier = TransactionClassifier()
    
    # Entrenar con datos bolivianos
    training_data = [
        {'descripcion': 'KETAL MIRAFLORES', 'categoria': 'Alimentación'},
        {'descripcion': 'HIPERMAXI ZONA SUR', 'categoria': 'Alimentación'}
    ]
    
    classifier.train(training_data)
    
    # Predecir
    prediction = classifier.predict("KETAL CALACOTO COMPRAS")
    
    assert prediction['category'] == 'Alimentación'
    assert prediction['confidence'] > 0.7
```

### Test Integración GraphQL

```python
def test_classify_via_graphql():
    mutation = '''
    mutation {
        classifyTransaction(input: {
            text: "KETAL SUPERMERCADO MIRAFLORES"
        }) {
            predictedCategory
            confidence
        }
    }
    '''
    
    response = requests.post(
        "http://localhost:5015/graphql",
        json={"query": mutation}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['data']['classifyTransaction']['predictedCategory'] == 'Alimentación'
```

---

## 🔍 Debugging Tests

### Tests Fallando

```bash
# Modo debug con más información
pytest tests/test_classifier.py -vv -s --tb=long

# Parar en el primer fallo
pytest tests/ -x

# Solo re-ejecutar tests fallidos
pytest --lf
```

### Logs Durante Tests

```bash
# Mostrar logs de la aplicación
pytest tests/ -s --log-cli-level=INFO

# Solo errores
pytest tests/ --log-cli-level=ERROR
```

---

## 🚀 CI/CD (Futuro)

### GitHub Actions (ejemplo)

```yaml
name: ML Service Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

---

## 📈 Métricas y KPIs

### Métricas de Calidad

- **Cobertura de código**: > 70%
- **Tests pasando**: 100%
- **Tiempo de ejecución**: < 2 minutos
- **Tests bolivianos**: > 20 casos

### Monitoreo

```bash
# Estadísticas de tests
pytest --collect-only tests/ | grep "test session"

# Tiempo de ejecución
pytest tests/ --durations=10
```

---

## ❓ FAQ

### ¿Por qué fallan los tests de integración?

1. **Servicios no corriendo**: Verificar `docker-compose up`
2. **Puertos ocupados**: Cambiar puertos en docker-compose
3. **Modelos no entrenados**: Ejecutar `python training/train_bolivia.py`

### ¿Cómo agregar nuevos comercios bolivianos?

1. Editar `test_bolivian_specific.py`
2. Agregar a `bolivian_training_data`
3. Crear test específico

### ¿Los tests modifican la base de datos?

No. Los tests usan:
- Base de datos separada (`ml_test_db`)
- Archivos temporales para modelos
- Mocks para servicios externos

---

## 🎉 ¡Ejecutar Tests Ahora!

```bash
# Quick start
cd ml-service/
python run_tests.py --bolivian --coverage

# Ver resultados en navegador
open htmlcov/index.html
```

---

**¡Tests exitosos = ML Service confiable para Bolivia! 🇧🇴✨**
