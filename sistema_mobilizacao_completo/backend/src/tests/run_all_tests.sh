#!/bin/bash

# Script para executar todos os testes do Sistema de Mobilização
# Este script inicia os serviços necessários, executa os testes e gera um relatório

# Diretórios
BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FRONTEND_DIR="$(cd "$BACKEND_DIR/../sistema_mobilizacao_frontend" && pwd)"
TESTS_DIR="$BACKEND_DIR/src/tests"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para exibir mensagem com timestamp
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Função para exibir mensagem de erro
error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERRO:${NC} $1"
}

# Função para exibir mensagem de sucesso
success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCESSO:${NC} $1"
}

# Função para exibir mensagem de aviso
warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] AVISO:${NC} $1"
}

# Função para verificar se um processo está rodando
is_running() {
    local port=$1
    nc -z localhost $port > /dev/null 2>&1
    return $?
}

# Função para iniciar o backend
start_backend() {
    log "Iniciando backend..."
    
    # Verificar se já está rodando
    if is_running 5000; then
        warning "Backend já está rodando na porta 5000"
        return 0
    fi
    
    # Ativar ambiente virtual
    cd "$BACKEND_DIR" || { error "Diretório do backend não encontrado"; return 1; }
    
    # Iniciar backend em background
    log "Executando backend em background..."
    source venv/bin/activate
    python src/main.py > backend.log 2>&1 &
    BACKEND_PID=$!
    
    # Verificar se iniciou corretamente
    sleep 3
    if ! is_running 5000; then
        error "Falha ao iniciar backend"
        cat backend.log
        return 1
    fi
    
    success "Backend iniciado com PID $BACKEND_PID"
    return 0
}

# Função para iniciar o frontend
start_frontend() {
    log "Iniciando frontend..."
    
    # Verificar se já está rodando
    if is_running 5173; then
        warning "Frontend já está rodando na porta 5173"
        return 0
    fi
    
    # Iniciar frontend em background
    cd "$FRONTEND_DIR" || { error "Diretório do frontend não encontrado"; return 1; }
    
    log "Executando frontend em background..."
    pnpm run dev -- --host > frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    # Verificar se iniciou corretamente
    sleep 5
    if ! is_running 5173; then
        error "Falha ao iniciar frontend"
        cat frontend.log
        return 1
    fi
    
    success "Frontend iniciado com PID $FRONTEND_PID"
    return 0
}

# Função para parar serviços
stop_services() {
    log "Parando serviços..."
    
    # Parar backend
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        log "Backend parado (PID $BACKEND_PID)"
    fi
    
    # Parar frontend
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        log "Frontend parado (PID $FRONTEND_PID)"
    fi
    
    # Garantir que as portas estão liberadas
    for port in 5000 5173; do
        if is_running $port; then
            warning "Porta $port ainda está em uso. Tentando matar processo..."
            pid=$(lsof -t -i:$port)
            if [ -n "$pid" ]; then
                kill -9 $pid 2>/dev/null
                log "Processo na porta $port encerrado (PID $pid)"
            fi
        fi
    done
}

# Função para executar testes
run_tests() {
    log "Executando testes..."
    
    # Ir para diretório de testes
    cd "$TESTS_DIR" || { error "Diretório de testes não encontrado"; return 1; }
    
    # Instalar dependências de teste se necessário
    if ! pip list | grep -q "selenium"; then
        log "Instalando dependências de teste..."
        pip install selenium requests
    fi
    
    # Executar testes
    log "Executando script de testes..."
    python run_tests.py
    
    # Verificar resultado
    if [ $? -eq 0 ]; then
        success "Testes concluídos com sucesso"
        return 0
    else
        error "Alguns testes falharam"
        return 1
    fi
}

# Função principal
main() {
    log "=== INICIANDO TESTES DO SISTEMA DE MOBILIZAÇÃO ==="
    
    # Configurar trap para garantir que os serviços serão parados
    trap stop_services EXIT
    
    # Iniciar serviços
    start_backend || { error "Falha ao iniciar backend. Abortando testes."; exit 1; }
    start_frontend || { warning "Falha ao iniciar frontend. Testes de UI serão pulados."; }
    
    # Executar testes
    run_tests
    TEST_RESULT=$?
    
    # Exibir resultado final
    if [ $TEST_RESULT -eq 0 ]; then
        success "=== TODOS OS TESTES PASSARAM ==="
    else
        error "=== ALGUNS TESTES FALHARAM ==="
    fi
    
    log "Relatório de testes disponível em: $TESTS_DIR/test_report.txt"
    
    return $TEST_RESULT
}

# Executar função principal
main

