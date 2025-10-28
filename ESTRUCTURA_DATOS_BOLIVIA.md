# 🇧🇴 Estructura de Datos - Contexto Boliviano

## 📊 Estructura Propuesta (Mejorada)

```json
{
  // Identificación
  "id_transaccion": "TXN_001",
  "usuario_id": "USER_123",
  
  // Temporal
  "fecha": "2025-01-15",
  "hora": "09:30:45",
  "timestamp": "2025-01-15T09:30:45-04:00",  // Zona horaria Bolivia
  
  // Transacción
  "descripcion": "MERCADO CENTRAL LA PAZ",
  "monto": 75.50,
  "moneda": "BOB",  // Bolivianos
  "tipo_transaccion": "egreso",  // egreso, ingreso
  
  // Categorización
  "categoria": "Alimentación",
  "subcategoria": "Mercado",
  "etiquetas": ["comestibles", "frutas", "verduras"],  // Tags opcionales
  
  // Método de Pago
  "tipo_pago": "Débito",  // Débito, Crédito, Efectivo, QR, Transferencia
  "banco": "BNB",  // BNB, Banco Sol, Mercantil, Unión, etc.
  "ultimos_4_digitos": "1234",  // Opcional
  
  // Ubicación
  "tipo_comercio": "Físico",  // Físico, Online, App
  "departamento": "La Paz",
  "ciudad": "La Paz",
  "zona": "Centro",  // Opcional
  "comercio_nombre": "Mercado Central",
  
  // Contexto Boliviano
  "es_quincena": true,  // Primera o segunda quincena
  "numero_quincena": 1,  // 1 = primera quincena, 2 = segunda
  "es_aguinaldo": false,
  "es_prima": false,  // Pago de prima
  "es_feriado": false,
  "nombre_feriado": null,  // Ej: "Carnaval", "6 de Agosto"
  
  // Temporal calculado
  "dia_semana": 2,  // 0=Lun, 6=Dom
  "nombre_dia": "Miércoles",
  "semana_mes": 3,  // Tercera semana del mes
  "es_fin_mes": false,
  "es_inicio_mes": true,
  
  // Contexto adicional
  "es_recurrente": false,
  "frecuencia": null,  // "mensual", "semanal", "anual"
  "nota_contexto": "Compra semanal",
  "adjuntos": [],  // URLs de recibos/facturas
  
  // ML/Analytics (calculado)
  "prediccion_categoria": "Alimentación",
  "confianza_prediccion": 0.95,
  "es_anomalia": false,
  "score_anomalia": 0.15,
  
  // Metadata
  "creado_en": "2025-01-15T09:35:00-04:00",
  "actualizado_en": "2025-01-15T09:35:00-04:00",
  "fuente": "manual"  // manual, importacion, scraping, api
}
```

---

## 🏷️ Categorías en Español (Contexto Boliviano)

### Categorías Principales:

```python
CATEGORIAS_BOLIVIA = {
    # Esenciales
    "Alimentación": {
        "subcategorias": [
            "Mercado",
            "Supermercado",
            "Panadería",
            "Restaurante",
            "Comida Rápida",
            "Cafetería",
            "Delivery"
        ],
        "keywords": ["mercado", "super", "ketal", "fidalga", "ic norte", "hipermaxi"]
    },
    
    "Transporte": {
        "subcategorias": [
            "Micro/Minibus",
            "Taxi",
            "Trufi",
            "Teleférico",
            "Combustible",
            "Peaje",
            "Estacionamiento"
        ],
        "keywords": ["taxi", "trufi", "teleferico", "gasolina", "diesel", "ypfb"]
    },
    
    "Vivienda": {
        "subcategorias": [
            "Alquiler",
            "Anticretico",  # Específico de Bolivia
            "Condominio",
            "Reparaciones",
            "Muebles"
        ],
        "keywords": ["alquiler", "anticrético", "condominio"]
    },
    
    "Servicios Básicos": {
        "subcategorias": [
            "Luz (DELAPAZ/ELFEC)",
            "Agua (EPSAS/SAGUAPAC)",
            "Gas",
            "Internet",
            "Telefonía (Entel/Tigo/Viva)"
        ],
        "keywords": ["delapaz", "elfec", "epsas", "entel", "tigo", "viva"]
    },
    
    "Salud": {
        "subcategorias": [
            "Farmacia",
            "Consulta Médica",
            "Laboratorio",
            "Seguro (CNS/Privado)",
            "Óptica"
        ],
        "keywords": ["farmacia", "clinica", "hospital", "laboratorio", "cns"]
    },
    
    "Educación": {
        "subcategorias": [
            "Colegiatura",
            "Universidad",
            "Instituto",
            "Libros",
            "Materiales"
        ],
        "keywords": ["colegio", "universidad", "instituto", "umsa", "ucb"]
    },
    
    "Entretenimiento": {
        "subcategorias": [
            "Cine",
            "Eventos",
            "Deportes",
            "Streaming (Netflix/etc)",
            "Juegos"
        ],
        "keywords": ["cine", "netflix", "spotify", "multicine"]
    },
    
    "Ropa y Calzado": {
        "subcategorias": [
            "Ropa",
            "Calzado",
            "Accesorios"
        ],
        "keywords": ["ropa", "zapatos", "tienda"]
    },
    
    "Tecnología": {
        "subcategorias": [
            "Electrónica",
            "Computadoras",
            "Celulares",
            "Accesorios"
        ],
        "keywords": ["computadora", "celular", "laptop", "electrónica"]
    },
    
    "Finanzas": {
        "subcategorias": [
            "Transferencias",
            "Comisiones Bancarias",
            "Préstamos",
            "Inversiones",
            "Seguros"
        ],
        "keywords": ["transferencia", "banco", "préstamo"]
    },
    
    "Ocio": {
        "subcategorias": [
            "Viajes",
            "Hobbies",
            "Mascotas",
            "Otros"
        ],
        "keywords": ["viaje", "paseo", "mascota"]
    },
    
    "Otros": {
        "subcategorias": ["Sin categoría"]
    }
}
```

---

## 🏦 Bancos Bolivianos

```python
BANCOS_BOLIVIA = [
    "BNB",           # Banco Nacional de Bolivia
    "Banco Sol",
    "Banco Unión",
    "Banco Mercantil Santa Cruz",
    "Banco Bisa",
    "Banco Económico",
    "Banco Ganadero",
    "Banco FIE",
    "Banco Fortaleza",
    "Banco Pyme Ecofuturo",
    "Banco Los Andes ProCredit",
    "Citibank",
    "Banco Solidario",
    "Efectivo",
    "Otro"
]
```

---

## 📍 Departamentos de Bolivia

```python
DEPARTAMENTOS = [
    "La Paz",
    "Santa Cruz",
    "Cochabamba",
    "Oruro",
    "Potosí",
    "Chuquisaca",
    "Tarija",
    "Beni",
    "Pando"
]
```

---

## 📅 Contexto Temporal Boliviano

### Feriados Nacionales
```python
FERIADOS_BOLIVIA = {
    "01-01": "Año Nuevo",
    "01-22": "Día del Estado Plurinacional",
    "02-21": "Carnaval (variable)",
    "03-23": "Día del Mar",
    "04-14": "Viernes Santo (variable)",
    "05-01": "Día del Trabajo",
    "06-21": "Año Nuevo Aymara",
    "08-06": "Día de la Independencia",
    "11-02": "Día de Todos los Santos",
    "12-25": "Navidad"
}
```

### Quincenas
```python
def calcular_quincena(fecha):
    """
    Determina si es primera o segunda quincena
    Primera quincena: días 1-15
    Segunda quincena: días 16-fin de mes
    """
    dia = fecha.day
    return 1 if dia <= 15 else 2

def es_periodo_pago(fecha):
    """
    Detecta períodos típicos de pago en Bolivia
    - Primera quincena: 5-10 del mes
    - Segunda quincena: 20-25 del mes
    """
    dia = fecha.day
    return (5 <= dia <= 10) or (20 <= dia <= 25)
```

---

## 💡 Features para ML (Contexto Boliviano)

### Features calculados útiles:

```python
# Temporales
- dia_semana (0-6)
- es_fin_semana
- semana_mes (1-5)
- quincena (1-2)
- mes (1-12)
- es_inicio_mes (primeros 5 días)
- es_fin_mes (últimos 5 días)

# Contexto laboral boliviano
- es_quincena_pago (días 5-10 o 20-25)
- es_periodo_aguinaldo (diciembre)
- es_periodo_prima (junio/julio)
- dias_desde_ultimo_pago

# Económicos
- monto_normalizado (por ciudad/región)
- monto_vs_promedio_categoria
- porcentaje_ingreso_mensual

# Ubicación
- departamento_economico (La Paz, Sta Cruz, Cbba más caros)
- es_zona_central
- es_area_metropolitana

# Patrones
- frecuencia_comercio (cuántas veces compra ahí)
- patron_horario (mañana/tarde/noche)
- patron_semanal
```

---

## 🎯 Recomendaciones

### ✅ Lo que está bien en tu estructura:
1. **es_quincena** - Súper importante en Bolivia (salarios)
2. **es_aguinaldo** - Contexto cultural clave
3. **departamento** - Útil para análisis regional
4. **tipo_comercio** - Físico vs Online (tendencia creciente)

### 💡 Mejoras sugeridas:
1. Agregar **numero_quincena** (1 o 2) además del booleano
2. Agregar **es_prima** (otro pago anual importante)
3. Agregar **ciudad** y opcionalmente **zona**
4. Agregar **tipo_transaccion** (ingreso/egreso)
5. Agregar **es_recurrente** para gastos fijos
6. Agregar **timestamp** con zona horaria de Bolivia

### 🚀 Features avanzadas opcionales:
1. **comercio_nombre** - Para análisis de frecuencia
2. **etiquetas** - Tags libres para el usuario
3. **adjuntos** - URLs de recibos/facturas digitales
4. **fuente** - Saber si es manual, importado, etc.

---

## 📦 Formato de Archivo para Entrenar

### JSON Lines (.jsonl)
```json
{"id_transaccion": "TXN_001", "fecha": "2025-01-15", "descripcion": "KETAL", "monto": 150.0, "categoria": "Alimentación"}
{"id_transaccion": "TXN_002", "fecha": "2025-01-16", "descripcion": "TAXI", "monto": 15.0, "categoria": "Transporte"}
```

### CSV
```csv
id_transaccion,fecha,descripcion,monto,categoria,departamento
TXN_001,2025-01-15,KETAL SUPERMERCADO,150.00,Alimentación,La Paz
TXN_002,2025-01-16,TAXI LA PAZ,15.00,Transporte,La Paz
```

---

¿Procedemos a actualizar el código con esta estructura boliviana? 🇧🇴

