#!/usr/bin/env python3
"""
Script para executar todos os testes do Sistema de Mobilização.
Este script executa os testes de API e UI e gera um relatório.
"""

import os
import sys
import time
import subprocess
import datetime
import json
import unittest
from unittest import TextTestRunner, TestSuite, TestLoader
from io import StringIO

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Importar testes
try:
    from test_api import TestAPI
    from test_ui import TestUI
except ImportError as e:
    print(f"Erro ao importar testes: {e}")
    print("Executando testes como módulos separados...")

def check_services():
    """Verifica se os serviços necessários estão rodando"""
    print("Verificando serviços...")
    
    # Verificar backend
    try:
        import requests
        response = requests.get("http://localhost:5000/api/etapas")
        if response.status_code == 200:
            print("✅ Backend está rodando")
            backend_ok = True
        else:
            print("❌ Backend está rodando, mas retornou status code:", response.status_code)
            backend_ok = False
    except Exception as e:
        print(f"❌ Backend não está rodando: {e}")
        backend_ok = False
    
    # Verificar frontend
    try:
        response = requests.get("http://localhost:5173")
        if response.status_code == 200:
            print("✅ Frontend está rodando")
            frontend_ok = True
        else:
            print("❌ Frontend está rodando, mas retornou status code:", response.status_code)
            frontend_ok = False
    except Exception as e:
        print(f"❌ Frontend não está rodando: {e}")
        frontend_ok = False
    
    return backend_ok, frontend_ok

def run_api_tests():
    """Executa os testes de API"""
    print("\n=== Executando testes de API ===\n")
    
    try:
        # Criar suite de testes
        loader = TestLoader()
        suite = loader.loadTestsFromTestCase(TestAPI)
        
        # Executar testes
        result = TextTestRunner(verbosity=2).run(suite)
        
        return result.wasSuccessful(), result
    except NameError:
        # Executar como módulo separado
        result = subprocess.run([sys.executable, "test_api.py"], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("ERROS:", result.stderr)
        
        return result.returncode == 0, None

def run_ui_tests():
    """Executa os testes de UI"""
    print("\n=== Executando testes de UI ===\n")
    
    try:
        # Criar suite de testes
        loader = TestLoader()
        suite = loader.loadTestsFromTestCase(TestUI)
        
        # Executar testes
        result = TextTestRunner(verbosity=2).run(suite)
        
        return result.wasSuccessful(), result
    except NameError:
        # Executar como módulo separado
        result = subprocess.run([sys.executable, "test_ui.py"], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("ERROS:", result.stderr)
        
        return result.returncode == 0, None

def generate_report(api_success, ui_success, api_result=None, ui_result=None):
    """Gera um relatório de testes"""
    print("\n=== Gerando relatório de testes ===\n")
    
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "summary": {
            "api_tests": "PASSOU" if api_success else "FALHOU",
            "ui_tests": "PASSOU" if ui_success else "FALHOU",
            "overall": "PASSOU" if (api_success and ui_success) else "FALHOU"
        },
        "details": {
            "api_tests": {},
            "ui_tests": {}
        }
    }
    
    # Adicionar detalhes se disponíveis
    if api_result:
        report["details"]["api_tests"] = {
            "tests_run": api_result.testsRun,
            "errors": len(api_result.errors),
            "failures": len(api_result.failures),
            "skipped": len(api_result.skipped) if hasattr(api_result, 'skipped') else 0
        }
    
    if ui_result:
        report["details"]["ui_tests"] = {
            "tests_run": ui_result.testsRun,
            "errors": len(ui_result.errors),
            "failures": len(ui_result.failures),
            "skipped": len(ui_result.skipped) if hasattr(ui_result, 'skipped') else 0
        }
    
    # Salvar relatório em arquivo
    report_file = os.path.join(os.path.dirname(__file__), "test_report.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    # Gerar relatório em formato texto
    report_text = f"""
=== RELATÓRIO DE TESTES ===
Data/Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

RESUMO:
- Testes de API: {report['summary']['api_tests']}
- Testes de UI: {report['summary']['ui_tests']}
- Resultado geral: {report['summary']['overall']}

DETALHES:
- Testes de API:
  - Testes executados: {report['details']['api_tests'].get('tests_run', 'N/A')}
  - Erros: {report['details']['api_tests'].get('errors', 'N/A')}
  - Falhas: {report['details']['api_tests'].get('failures', 'N/A')}
  - Pulados: {report['details']['api_tests'].get('skipped', 'N/A')}

- Testes de UI:
  - Testes executados: {report['details']['ui_tests'].get('tests_run', 'N/A')}
  - Erros: {report['details']['ui_tests'].get('errors', 'N/A')}
  - Falhas: {report['details']['ui_tests'].get('failures', 'N/A')}
  - Pulados: {report['details']['ui_tests'].get('skipped', 'N/A')}

Relatório completo salvo em: {report_file}
"""
    
    print(report_text)
    
    # Salvar relatório em formato texto
    report_text_file = os.path.join(os.path.dirname(__file__), "test_report.txt")
    with open(report_text_file, "w") as f:
        f.write(report_text)
    
    return report_file, report_text_file

def main():
    """Função principal"""
    print("=== TESTES DO SISTEMA DE MOBILIZAÇÃO ===")
    print(f"Data/Hora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar serviços
    backend_ok, frontend_ok = check_services()
    
    if not backend_ok:
        print("\n⚠️ Backend não está rodando. Testes de API serão pulados.")
        api_success = False
        api_result = None
    else:
        # Executar testes de API
        api_success, api_result = run_api_tests()
    
    if not frontend_ok:
        print("\n⚠️ Frontend não está rodando. Testes de UI serão pulados.")
        ui_success = False
        ui_result = None
    else:
        # Executar testes de UI
        ui_success, ui_result = run_ui_tests()
    
    # Gerar relatório
    report_file, report_text_file = generate_report(api_success, ui_success, api_result, ui_result)
    
    # Exibir resultado final
    if api_success and ui_success:
        print("\n✅ TODOS OS TESTES PASSARAM!")
    else:
        print("\n❌ ALGUNS TESTES FALHARAM!")
    
    print(f"Relatório salvo em: {report_file} e {report_text_file}")

if __name__ == "__main__":
    main()

