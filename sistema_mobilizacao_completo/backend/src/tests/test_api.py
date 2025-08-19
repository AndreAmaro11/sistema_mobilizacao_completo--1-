#!/usr/bin/env python3
"""
Script de teste automatizado para API do Sistema de Mobilização.
Este script testa as principais funcionalidades da API.
"""

import os
import sys
import unittest
import json
import requests
from datetime import datetime, timedelta

# URL base da API
API_BASE_URL = 'http://localhost:5000/api'

# Credenciais de teste
TEST_USER = {
    'email': 'admin@empresa.com',
    'senha': 'admin123'
}

class TestAPI(unittest.TestCase):
    """Classe de teste para API do Sistema de Mobilização"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        # Fazer login e obter token
        response = requests.post(f"{API_BASE_URL}/auth/login", json=TEST_USER)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.token = data['data']['token']
        
        # Configurar headers com token
        self.headers = {
            'Authorization': f"Bearer {self.token}",
            'Content-Type': 'application/json'
        }
    
    def test_01_auth(self):
        """Teste de autenticação"""
        print("\n--- Testando autenticação ---")
        
        # Teste de login com credenciais válidas
        response = requests.post(f"{API_BASE_URL}/auth/login", json=TEST_USER)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('token', data['data'])
        print("✅ Login com credenciais válidas: OK")
        
        # Teste de login com credenciais inválidas
        invalid_user = {
            'email': 'invalid@example.com',
            'senha': 'wrongpassword'
        }
        response = requests.post(f"{API_BASE_URL}/auth/login", json=invalid_user)
        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertFalse(data['success'])
        print("✅ Login com credenciais inválidas: OK")
        
        # Teste de obtenção de dados do usuário atual
        response = requests.get(f"{API_BASE_URL}/auth/me", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['email'], TEST_USER['email'])
        print("✅ Obtenção de dados do usuário atual: OK")
    
    def test_02_etapas(self):
        """Teste de gerenciamento de etapas"""
        print("\n--- Testando gerenciamento de etapas ---")
        
        # Teste de listagem de etapas
        response = requests.get(f"{API_BASE_URL}/etapas", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
        self.assertGreater(len(data['data']), 0)
        print(f"✅ Listagem de etapas: OK ({len(data['data'])} etapas encontradas)")
        
        # Guardar ID da primeira etapa para testes posteriores
        self.etapa_id = data['data'][0]['id']
        
        # Teste de obtenção de etapa específica
        response = requests.get(f"{API_BASE_URL}/etapas/{self.etapa_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['id'], self.etapa_id)
        print(f"✅ Obtenção de etapa específica: OK (Etapa: {data['data']['nome']})")
        
        # Teste de obtenção de checklist da etapa
        response = requests.get(f"{API_BASE_URL}/etapas/{self.etapa_id}/checklist", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        print(f"✅ Obtenção de checklist da etapa: OK ({len(data['data'])} itens encontrados)")
    
    def test_03_cards(self):
        """Teste de gerenciamento de cards"""
        print("\n--- Testando gerenciamento de cards ---")
        
        # Teste de listagem de cards
        response = requests.get(f"{API_BASE_URL}/cards", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
        print(f"✅ Listagem de cards: OK ({len(data['data'])} cards encontrados)")
        
        # Teste de criação de card
        novo_card = {
            'nome_colaborador': f"Teste Automatizado {datetime.now().strftime('%Y%m%d%H%M%S')}",
            'cpf': '123.456.789-00',
            'cargo': 'Analista de Testes',
            'salario': 5000.00,
            'centro_custo': 'TI',
            'data_admissao': datetime.now().strftime('%Y-%m-%d'),
            'observacoes': 'Card criado por teste automatizado'
        }
        response = requests.post(f"{API_BASE_URL}/cards", json=novo_card, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data['success'])
        self.card_id = data['data']['id']
        print(f"✅ Criação de card: OK (ID: {self.card_id})")
        
        # Teste de obtenção de card específico
        response = requests.get(f"{API_BASE_URL}/cards/{self.card_id}", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['id'], self.card_id)
        print(f"✅ Obtenção de card específico: OK")
        
        # Teste de atualização de card
        card_atualizado = {
            'nome_colaborador': f"Teste Atualizado {datetime.now().strftime('%Y%m%d%H%M%S')}",
            'observacoes': 'Card atualizado por teste automatizado'
        }
        response = requests.put(f"{API_BASE_URL}/cards/{self.card_id}", json=card_atualizado, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['observacoes'], card_atualizado['observacoes'])
        print(f"✅ Atualização de card: OK")
        
        # Teste de movimentação de card
        # Primeiro, obter ID da próxima etapa
        response = requests.get(f"{API_BASE_URL}/etapas", headers=self.headers)
        etapas = response.json()['data']
        if len(etapas) > 1:
            # Encontrar etapa diferente da atual
            etapa_atual_id = data['data']['etapa_atual']['id']
            for etapa in etapas:
                if etapa['id'] != etapa_atual_id:
                    nova_etapa_id = etapa['id']
                    break
            
            # Mover card para nova etapa
            movimento = {
                'etapa_destino_id': nova_etapa_id,
                'motivo': 'Movimentação por teste automatizado'
            }
            response = requests.put(f"{API_BASE_URL}/cards/{self.card_id}/mover", json=movimento, headers=self.headers)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['etapa_atual']['id'], nova_etapa_id)
            print(f"✅ Movimentação de card: OK")
        else:
            print("⚠️ Movimentação de card: Pulado (necessário mais de uma etapa)")
    
    def test_04_checklist(self):
        """Teste de gerenciamento de checklist"""
        print("\n--- Testando gerenciamento de checklist ---")
        
        # Obter card e seus itens de checklist
        response = requests.get(f"{API_BASE_URL}/cards/{self.card_id}", headers=self.headers)
        data = response.json()
        card = data['data']
        
        # Verificar se há itens de checklist
        if 'checklist' in card and len(card['checklist']) > 0:
            checklist_item_id = card['checklist'][0]['id']
            
            # Teste de atualização de item de checklist
            item_atualizado = {
                'concluido': True,
                'observacoes': 'Item concluído por teste automatizado'
            }
            response = requests.put(
                f"{API_BASE_URL}/cards/{self.card_id}/checklist/{checklist_item_id}", 
                json=item_atualizado, 
                headers=self.headers
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data['success'])
            self.assertTrue(data['data']['concluido'])
            print(f"✅ Atualização de item de checklist: OK")
        else:
            print("⚠️ Atualização de item de checklist: Pulado (nenhum item encontrado)")
    
    def test_05_notificacoes(self):
        """Teste de gerenciamento de notificações"""
        print("\n--- Testando gerenciamento de notificações ---")
        
        # Teste de contagem de notificações
        response = requests.get(f"{API_BASE_URL}/notificacoes/contagem", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('nao_lidas', data['data'])
        print(f"✅ Contagem de notificações: OK ({data['data']['nao_lidas']} não lidas)")
        
        # Teste de listagem de notificações
        response = requests.get(f"{API_BASE_URL}/notificacoes", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
        print(f"✅ Listagem de notificações: OK ({len(data['data'])} notificações encontradas)")
        
        # Teste de verificação de prazos
        response = requests.post(f"{API_BASE_URL}/notificacoes/verificar-prazos", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        print(f"✅ Verificação de prazos: OK")
        
        # Teste de verificação de checklist
        response = requests.post(f"{API_BASE_URL}/notificacoes/verificar-checklist", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        print(f"✅ Verificação de checklist: OK")
    
    def test_06_dashboard(self):
        """Teste de dashboard"""
        print("\n--- Testando dashboard ---")
        
        # Teste de obtenção de indicadores
        response = requests.get(f"{API_BASE_URL}/dashboard/indicadores", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('total_cards', data['data'])
        print(f"✅ Obtenção de indicadores: OK (Total de cards: {data['data']['total_cards']})")
        
        # Teste de obtenção de cards atrasados
        response = requests.get(f"{API_BASE_URL}/dashboard/cards-atrasados", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
        print(f"✅ Obtenção de cards atrasados: OK ({len(data['data'])} cards atrasados)")
        
        # Teste de obtenção de estatísticas por período
        params = {
            'periodo': 'mes',
            'data_inicio': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'data_fim': datetime.now().strftime('%Y-%m-%d')
        }
        response = requests.get(f"{API_BASE_URL}/dashboard/estatisticas-periodo", params=params, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        print(f"✅ Obtenção de estatísticas por período: OK")
    
    def test_07_permissoes(self):
        """Teste de gerenciamento de permissões"""
        print("\n--- Testando gerenciamento de permissões ---")
        
        # Teste de listagem de tipos de permissões
        response = requests.get(f"{API_BASE_URL}/permissoes/tipos", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('tipos', data['data'])
        self.assertIn('recursos', data['data'])
        print(f"✅ Listagem de tipos de permissões: OK")
        
        # Teste de verificação de permissão
        permissao = {
            'tipo': 'visualizar',
            'recurso': 'card'
        }
        response = requests.post(f"{API_BASE_URL}/permissoes/verificar", json=permissao, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('tem_permissao', data['data'])
        print(f"✅ Verificação de permissão: OK (Tem permissão: {data['data']['tem_permissao']})")
        
        # Teste de listagem de permissões do usuário
        response = requests.get(f"{API_BASE_URL}/permissoes/minhas", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('permissoes', data['data'])
        print(f"✅ Listagem de permissões do usuário: OK ({len(data['data']['permissoes'])} permissões encontradas)")
    
    def test_08_usuarios(self):
        """Teste de gerenciamento de usuários"""
        print("\n--- Testando gerenciamento de usuários ---")
        
        # Teste de listagem de usuários
        response = requests.get(f"{API_BASE_URL}/usuarios", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
        self.assertGreater(len(data['data']), 0)
        print(f"✅ Listagem de usuários: OK ({len(data['data'])} usuários encontrados)")
        
        # Teste de listagem de grupos
        response = requests.get(f"{API_BASE_URL}/usuarios/grupos", headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIsInstance(data['data'], list)
        self.assertGreater(len(data['data']), 0)
        print(f"✅ Listagem de grupos: OK ({len(data['data'])} grupos encontrados)")

def run_tests():
    """Executa os testes"""
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == '__main__':
    print("Iniciando testes da API do Sistema de Mobilização...")
    print("Certifique-se de que o backend está rodando em http://localhost:5000")
    run_tests()

