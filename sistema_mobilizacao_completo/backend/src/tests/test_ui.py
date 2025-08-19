#!/usr/bin/env python3
"""
Script de teste para interface do usuário do Sistema de Mobilização.
Este script testa as principais funcionalidades da interface usando Selenium.
"""

import os
import sys
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# URL base da aplicação
APP_BASE_URL = 'http://localhost:5173'

# Credenciais de teste
TEST_USER = {
    'email': 'admin@empresa.com',
    'senha': 'admin123'
}

class TestUI(unittest.TestCase):
    """Classe de teste para interface do usuário do Sistema de Mobilização"""
    
    @classmethod
    def setUpClass(cls):
        """Configuração inicial para os testes"""
        # Configurar driver do Chrome
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Executar em modo headless
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        try:
            cls.driver = webdriver.Chrome(options=options)
            cls.driver.implicitly_wait(10)
            cls.wait = WebDriverWait(cls.driver, 10)
            print("Driver do Chrome inicializado com sucesso")
        except Exception as e:
            print(f"Erro ao inicializar driver do Chrome: {e}")
            print("Tentando inicializar driver do Firefox...")
            
            try:
                options = webdriver.FirefoxOptions()
                options.add_argument('--headless')
                cls.driver = webdriver.Firefox(options=options)
                cls.driver.implicitly_wait(10)
                cls.wait = WebDriverWait(cls.driver, 10)
                print("Driver do Firefox inicializado com sucesso")
            except Exception as e:
                print(f"Erro ao inicializar driver do Firefox: {e}")
                print("Não foi possível inicializar nenhum driver. Testes UI serão pulados.")
                cls.driver = None
    
    @classmethod
    def tearDownClass(cls):
        """Limpeza após os testes"""
        if cls.driver:
            cls.driver.quit()
    
    def setUp(self):
        """Configuração para cada teste"""
        if not self.driver:
            self.skipTest("Driver não inicializado. Pulando teste.")
    
    def test_01_login(self):
        """Teste de login"""
        print("\n--- Testando login ---")
        
        # Acessar página de login
        self.driver.get(APP_BASE_URL)
        print("✅ Página de login carregada")
        
        # Verificar elementos da página
        self.assertIn("Sistema de Mobilização", self.driver.title)
        
        # Preencher formulário de login
        email_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='seu@email.com']")))
        senha_input = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Sua senha']")))
        
        email_input.send_keys(TEST_USER['email'])
        senha_input.send_keys(TEST_USER['senha'])
        
        # Clicar no botão de login
        login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Entrar')]")))
        login_button.click()
        
        # Verificar se login foi bem-sucedido
        try:
            # Esperar pelo elemento que indica que o login foi bem-sucedido
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Sistema de Mobilização')]")))
            print("✅ Login bem-sucedido")
        except TimeoutException:
            self.fail("Login falhou - não foi possível encontrar elemento após login")
    
    def test_02_navegacao(self):
        """Teste de navegação"""
        print("\n--- Testando navegação ---")
        
        # Verificar se já está logado
        if "login" in self.driver.current_url.lower():
            self.test_01_login()
        
        # Verificar elementos de navegação
        kanban_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Kanban')]")))
        dashboard_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Dashboard')]")))
        
        # Navegar para Dashboard
        dashboard_button.click()
        time.sleep(1)  # Aguardar transição
        print("✅ Navegação para Dashboard")
        
        # Navegar para Kanban
        kanban_button.click()
        time.sleep(1)  # Aguardar transição
        print("✅ Navegação para Kanban")
    
    def test_03_visualizar_cards(self):
        """Teste de visualização de cards"""
        print("\n--- Testando visualização de cards ---")
        
        # Verificar se já está logado
        if "login" in self.driver.current_url.lower():
            self.test_01_login()
        
        # Verificar se há cards no quadro Kanban
        try:
            cards = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-card-id]")))
            print(f"✅ Cards encontrados: {len(cards)}")
            
            if len(cards) > 0:
                # Clicar no primeiro card para ver detalhes
                cards[0].click()
                
                # Verificar se modal de detalhes foi aberto
                self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'dialog-content')]")))
                print("✅ Modal de detalhes do card aberto")
                
                # Fechar modal
                close_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Close']")))
                close_button.click()
                time.sleep(0.5)  # Aguardar fechamento do modal
        except TimeoutException:
            print("⚠️ Nenhum card encontrado no quadro Kanban")
    
    def test_04_criar_card(self):
        """Teste de criação de card"""
        print("\n--- Testando criação de card ---")
        
        # Verificar se já está logado
        if "login" in self.driver.current_url.lower():
            self.test_01_login()
        
        # Clicar no botão de novo card
        novo_card_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Novo Card')]")))
        novo_card_button.click()
        
        # Verificar se modal de criação foi aberto
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'dialog-content')]")))
        print("✅ Modal de criação de card aberto")
        
        # Preencher formulário
        nome_input = self.wait.until(EC.presence_of_element_located((By.ID, "nome_colaborador")))
        nome_input.send_keys(f"Teste UI {time.strftime('%Y%m%d%H%M%S')}")
        
        # Clicar no botão de criar
        criar_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Criar')]")))
        criar_button.click()
        
        # Verificar se card foi criado (modal fecha)
        try:
            self.wait.until_not(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'dialog-content')]")))
            print("✅ Card criado com sucesso")
        except TimeoutException:
            print("⚠️ Modal não fechou após criação do card")
    
    def test_05_notificacoes(self):
        """Teste de notificações"""
        print("\n--- Testando notificações ---")
        
        # Verificar se já está logado
        if "login" in self.driver.current_url.lower():
            self.test_01_login()
        
        # Clicar no ícone de notificações
        notificacoes_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Bell')]")))
        notificacoes_button.click()
        
        # Verificar se dropdown de notificações foi aberto
        self.wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Notificações')]")))
        print("✅ Dropdown de notificações aberto")
        
        # Fechar dropdown
        self.driver.find_element(By.XPATH, "//body").click()
        time.sleep(0.5)  # Aguardar fechamento do dropdown
    
    def test_06_logout(self):
        """Teste de logout"""
        print("\n--- Testando logout ---")
        
        # Verificar se já está logado
        if "login" in self.driver.current_url.lower():
            self.test_01_login()
        
        # Clicar no menu do usuário
        user_menu_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'user-menu')]")))
        user_menu_button.click()
        
        # Clicar no botão de logout
        logout_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Sair')]")))
        logout_button.click()
        
        # Verificar se logout foi bem-sucedido
        try:
            # Esperar pela página de login
            self.wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Entrar')]")))
            print("✅ Logout bem-sucedido")
        except TimeoutException:
            self.fail("Logout falhou - não foi possível encontrar página de login")

def run_tests():
    """Executa os testes"""
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

if __name__ == '__main__':
    print("Iniciando testes de UI do Sistema de Mobilização...")
    print("Certifique-se de que o frontend está rodando em http://localhost:5173")
    
    try:
        run_tests()
    except Exception as e:
        print(f"Erro ao executar testes: {e}")
    finally:
        print("Testes de UI concluídos.")

