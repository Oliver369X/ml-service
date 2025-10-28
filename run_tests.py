#!/usr/bin/env python3
"""
Script para ejecutar tests del ML Service
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Ejecutar comando y manejar errores"""
    print(f"\n🔄 {description}...")
    print(f"Ejecutando: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Éxito")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Error")
        print(f"Código de salida: {e.returncode}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def check_dependencies():
    """Verificar que las dependencias de testing estén instaladas"""
    required_packages = ['pytest', 'requests', 'pytest-cov']
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"⚠️  Faltan dependencias: {', '.join(missing)}")
        print("Instala con: pip install -r requirements-test.txt")
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Ejecutar tests del ML Service')
    parser.add_argument('--unit', action='store_true', help='Solo tests unitarios')
    parser.add_argument('--integration', action='store_true', help='Solo tests de integración')
    parser.add_argument('--bolivian', action='store_true', help='Solo tests con datos bolivianos')
    parser.add_argument('--coverage', action='store_true', help='Generar reporte de cobertura')
    parser.add_argument('--verbose', '-v', action='store_true', help='Output detallado')
    parser.add_argument('--fast', action='store_true', help='Skip tests lentos')
    parser.add_argument('--file', help='Ejecutar archivo específico')
    
    args = parser.parse_args()
    
    # Verificar dependencias
    if not check_dependencies():
        sys.exit(1)
    
    # Cambiar al directorio del ML service
    os.chdir(Path(__file__).parent)
    
    # Construir comando pytest
    cmd = ['python', '-m', 'pytest']
    
    # Agregar opciones específicas
    if args.unit:
        cmd.extend(['-m', 'unit'])
    elif args.integration:
        cmd.extend(['-m', 'integration'])
    elif args.bolivian:
        cmd.extend(['-m', 'bolivian_data'])
    
    if args.fast:
        cmd.extend(['-m', 'not slow'])
    
    if args.coverage:
        cmd.extend(['--cov=src', '--cov-report=html', '--cov-report=term'])
    
    if args.verbose:
        cmd.append('-vv')
    
    if args.file:
        cmd.append(f'tests/{args.file}')
    else:
        cmd.append('tests/')
    
    # Mostrar información inicial
    print("🧪 ML Service - Test Runner")
    print("=" * 50)
    print(f"Directorio: {os.getcwd()}")
    print(f"Comando: {' '.join(cmd)}")
    
    # Ejecutar tests
    success = run_command(cmd, "Ejecutando tests")
    
    if success:
        print("\n✅ Todos los tests completados exitosamente!")
        if args.coverage:
            print("📊 Reporte de cobertura generado en: htmlcov/index.html")
    else:
        print("\n❌ Algunos tests fallaron")
        sys.exit(1)


if __name__ == '__main__':
    main()
