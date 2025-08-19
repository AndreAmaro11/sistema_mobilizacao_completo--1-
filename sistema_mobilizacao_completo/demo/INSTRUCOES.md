# Instruções para o Sistema de Mobilização de Funcionários

## Visão Geral

O Sistema de Mobilização de Funcionários é uma aplicação web para gerenciar o processo de mobilização de colaboradores em formato Kanban. Este documento fornece instruções para usar a versão de demonstração e informações sobre como seria a implementação completa.

## Usando a Versão de Demonstração

### Requisitos

- Navegador web moderno (Chrome, Firefox, Edge ou Safari)

### Execução

1. Abra o arquivo `index.html` em seu navegador
2. A página de login será exibida (ou você será automaticamente redirecionado para o quadro Kanban)
3. Se necessário, insira qualquer email e senha para fazer login

### Funcionalidades Disponíveis

1. **Visualização do Quadro Kanban**
   - O quadro exibe colunas para diferentes etapas do processo
   - Cada coluna contém cards representando colaboradores

2. **Interação com Cards**
   - Clique em um card para ver seus detalhes
   - No modal de detalhes, você pode alternar entre as abas: Detalhes, Checklist e Histórico

3. **Navegação**
   - Use os links no cabeçalho para navegar entre diferentes seções (apenas visual na demo)

## Implementação Completa

A implementação completa do sistema incluiria:

### Backend (Flask/Python)

- APIs RESTful para todas as operações CRUD
- Sistema de autenticação JWT
- Banco de dados PostgreSQL
- Sistema de notificações e alertas
- Controle de permissões por grupos de usuários

### Frontend (React)

- Componentes reutilizáveis
- Gerenciamento de estado com React Context ou Redux
- Drag and drop para movimentação de cards
- Dashboard interativo com gráficos e métricas

### Implantação

- Servidor web Nginx
- Gunicorn para o backend Flask
- Configurações de HTTPS/SSL
- Tarefas cron para verificações periódicas

## Extensões Futuras

- Aplicativo móvel para acesso em dispositivos Android e iOS
- Integração com sistemas de RH e ERP
- Relatórios avançados e exportação de dados
- Sistema de BI para análise de dados do processo

## Suporte

Para suporte ou mais informações, entre em contato com a equipe de desenvolvimento.

