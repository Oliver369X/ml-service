#!/bin/bash

# Script de inicio rápido para ML Service Boliviano
# Para Windows: usar Git Bash o ejecutar comandos manualmente

echo "🇧🇴 =========================================="
echo "🇧🇴  ML SERVICE - BOLIVIA"
echo "🇧🇴 =========================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Paso 1: Verificando archivos...${NC}"
if [ ! -f "data/transacciones_bolivia_ejemplo.csv" ]; then
    echo "❌ No se encontró archivo de datos bolivianos"
    exit 1
fi
echo "✅ Archivos de datos encontrados"

echo ""
echo -e "${YELLOW}Paso 2: Creando directorio de modelos...${NC}"
mkdir -p models
echo "✅ Directorio models/ creado"

echo ""
echo -e "${YELLOW}Paso 3: Entrenando modelos con datos bolivianos...${NC}"
python training/train_bolivia.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ ¡Modelos entrenados exitosamente!${NC}"
else
    echo ""
    echo "❌ Error entrenando modelos"
    exit 1
fi

echo ""
echo -e "${YELLOW}Paso 4: Iniciando servicio...${NC}"
echo ""
echo "Opciones:"
echo "  A) Docker:  docker-compose up"
echo "  B) Local:   uvicorn src.main:app --reload --port 5015"
echo ""
echo -e "${GREEN}🎉 Todo listo!${NC}"
echo ""
echo "Accede al servicio en:"
echo "  📊 GraphQL Playground: http://localhost:5015/graphql"
echo "  ✅ Health Check: http://localhost:5015/health"
echo "  📝 Models Status: http://localhost:5015/models/status"
echo ""
echo "Prueba clasificar una transacción boliviana:"
echo "  mutation {"
echo "    classifyTransaction(input: {"
echo "      text: \"KETAL SUPERMERCADO LA PAZ\""
echo "    }) {"
echo "      predictedCategory"
echo "      confidence"
echo "    }"
echo "  }"
echo ""

