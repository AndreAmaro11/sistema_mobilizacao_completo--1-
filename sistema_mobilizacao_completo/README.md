# Sistema de Mobilização de Funcionários

Sistema completo de gerenciamento de mobilização de funcionários em formato Kanban visual, com controle por etapas, responsáveis, checklists e alertas automáticos.

## Estrutura do Projeto

Este repositório contém três componentes principais:

1. **Demo** - Versão simplificada do sistema em HTML/CSS/JS puro para demonstração rápida
2. **Backend** - API REST desenvolvida em Flask (Python)
3. **Frontend** - Interface de usuário desenvolvida em React

## Versão de Demonstração (Demo)

A pasta `demo` contém uma versão simplificada do sistema implementada como uma página HTML estática para demonstração rápida.

### Como executar a demo:

1. Navegue até a pasta `demo`
2. Abra o arquivo `index.html` em qualquer navegador moderno

## Sistema Completo

### Backend (Flask)

A pasta `backend` contém a API REST desenvolvida em Flask.

#### Requisitos:

- Python 3.8+
- Flask
- SQLite (desenvolvimento) / PostgreSQL (produção)

#### Instalação:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Execução:

```bash
python src/main.py
```

O backend estará disponível em `http://localhost:5000`.

### Frontend (React)

A pasta `frontend` contém a interface de usuário desenvolvida em React.

#### Requisitos:

- Node.js 16+
- npm ou pnpm

#### Instalação:

```bash
cd frontend
npm install
# ou
pnpm install
```

#### Execução:

```bash
npm run dev
# ou
pnpm run dev
```

O frontend estará disponível em `http://localhost:5173`.

## Funcionalidades Principais

- Quadro Kanban visual com etapas personalizáveis
- Gerenciamento de cards de colaboradores
- Checklists por etapa com itens obrigatórios e opcionais
- Sistema de notificações e alertas automáticos
- Dashboard com indicadores de performance
- Controle de permissões por grupos de usuários

## Documentação

- [Manual do Usuário](manual_usuario.md) - Guia completo para usuários do sistema
- [Plano de Testes](plano_testes.md) - Documentação dos testes realizados no sistema
- [Todo](todo.md) - Lista de tarefas concluídas durante o desenvolvimento

## Credenciais de Teste

Para testar o sistema, utilize as seguintes credenciais:

**Administrador:**
- Email: admin@empresa.com
- Senha: admin123

**Usuário RH:**
- Email: maria.rh@empresa.com
- Senha: senha123

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes.

