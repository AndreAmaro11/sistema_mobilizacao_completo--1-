# Manual do Usuário - Sistema de Mobilização de Funcionários

## Sumário

1. [Introdução](#1-introdução)
2. [Acesso ao Sistema](#2-acesso-ao-sistema)
3. [Interface Principal](#3-interface-principal)
4. [Quadro Kanban](#4-quadro-kanban)
5. [Gerenciamento de Cards](#5-gerenciamento-de-cards)
6. [Checklists](#6-checklists)
7. [Notificações e Alertas](#7-notificações-e-alertas)
8. [Dashboard](#8-dashboard)
9. [Administração do Sistema](#9-administração-do-sistema)
10. [Solução de Problemas](#10-solução-de-problemas)

## 1. Introdução

O Sistema de Mobilização de Funcionários é uma ferramenta completa para gerenciar o processo de mobilização de colaboradores em formato Kanban. O sistema permite o controle por etapas, atribuição de responsáveis, gerenciamento de checklists e alertas automáticos para prazos e pendências.

### 1.1 Principais Funcionalidades

- Quadro Kanban visual com etapas personalizáveis
- Gerenciamento de cards de colaboradores
- Checklists por etapa com itens obrigatórios e opcionais
- Sistema de notificações e alertas automáticos
- Dashboard com indicadores de performance
- Controle de permissões por grupos de usuários

## 2. Acesso ao Sistema

### 2.1 Requisitos Mínimos

- Navegador web atualizado (Chrome, Firefox, Edge ou Safari)
- Conexão com a internet
- Credenciais de acesso fornecidas pelo administrador

### 2.2 Login

1. Acesse o sistema através da URL fornecida pelo administrador
2. Na tela de login, insira seu email e senha
3. Clique no botão "Entrar"

![Tela de Login](imagens/tela_login.png)

### 2.3 Recuperação de Senha

1. Na tela de login, clique em "Esqueceu sua senha?"
2. Insira seu email cadastrado
3. Siga as instruções enviadas para seu email

## 3. Interface Principal

Após fazer login, você será direcionado para a interface principal do sistema, que consiste em:

### 3.1 Cabeçalho

- **Logo e Título**: Identificação do sistema
- **Navegação**: Botões para alternar entre Kanban e Dashboard
- **Barra de Pesquisa**: Busca rápida de colaboradores
- **Filtros**: Opções para filtrar cards por diferentes critérios
- **Botão Novo Card**: Cria um novo card de colaborador
- **Notificações**: Exibe alertas e notificações pendentes
- **Menu do Usuário**: Acesso ao perfil e opção de logout

### 3.2 Área Principal

A área principal exibe o conteúdo selecionado na navegação:
- Quadro Kanban (padrão)
- Dashboard de indicadores

## 4. Quadro Kanban

O quadro Kanban é a visualização principal do sistema, organizado em colunas que representam as etapas do processo de mobilização.

### 4.1 Estrutura do Quadro

- **Colunas**: Representam as etapas do processo (ex: "To do", "On Hold", "Blocked", etc.)
- **Cards**: Representam os colaboradores em processo de mobilização
- **Indicadores Visuais**: Cores e badges que indicam status, prioridade e alertas

### 4.2 Navegação no Quadro

- **Rolagem Horizontal**: Navegue entre as colunas arrastando horizontalmente
- **Rolagem Vertical**: Navegue entre os cards de uma coluna arrastando verticalmente
- **Filtros**: Use os filtros no cabeçalho para mostrar apenas cards específicos

## 5. Gerenciamento de Cards

### 5.1 Criação de Card

1. Clique no botão "Novo Card" no cabeçalho
2. Preencha os dados do colaborador no formulário:
   - Nome do colaborador
   - CPF
   - Cargo
   - Salário
   - Centro de custo
   - Data de admissão
   - Observações
3. Clique em "Criar" para adicionar o card ao quadro

### 5.2 Visualização de Card

1. Clique em um card no quadro Kanban
2. Um modal será aberto com todos os detalhes do card:
   - Informações do colaborador
   - Etapa atual
   - Responsável atual
   - Histórico de movimentações
   - Checklist da etapa atual
   - Prazos e alertas

### 5.3 Edição de Card

1. Abra o card clicando nele no quadro Kanban
2. Clique no botão "Editar" no modal
3. Faça as alterações necessárias
4. Clique em "Salvar" para confirmar as alterações

### 5.4 Movimentação de Card

#### 5.4.1 Movimentação via Drag and Drop

1. Clique e segure o card que deseja mover
2. Arraste-o para a coluna de destino
3. Solte o card na nova coluna
4. Confirme a movimentação na janela de confirmação

#### 5.4.2 Movimentação via Modal

1. Abra o card clicando nele no quadro Kanban
2. Clique no botão "Mover" no modal
3. Selecione a etapa de destino no dropdown
4. Adicione um motivo para a movimentação (opcional)
5. Clique em "Confirmar" para mover o card

### 5.5 Exclusão de Card

1. Abra o card clicando nele no quadro Kanban
2. Clique no botão "Excluir" no modal
3. Confirme a exclusão na janela de confirmação

## 6. Checklists

Cada etapa do processo possui um checklist específico que deve ser preenchido para o card.

### 6.1 Visualização do Checklist

1. Abra o card clicando nele no quadro Kanban
2. Na seção "Checklist", você verá todos os itens da etapa atual

### 6.2 Preenchimento do Checklist

1. Marque a caixa de seleção ao lado de cada item concluído
2. Itens obrigatórios são marcados com um asterisco (*)
3. Adicione observações aos itens clicando no ícone de comentário
4. O progresso do checklist é atualizado automaticamente

### 6.3 Regras do Checklist

- Itens obrigatórios devem ser concluídos para avançar o card para a próxima etapa
- Itens não obrigatórios são recomendados, mas não bloqueiam a movimentação
- Ao mover um card para uma nova etapa, o checklist da etapa anterior é arquivado e um novo checklist é criado

## 7. Notificações e Alertas

O sistema possui um mecanismo de notificações e alertas para manter os usuários informados sobre prazos e pendências.

### 7.1 Tipos de Notificações

- **Prazo Vencido**: Alerta quando o prazo de um card foi ultrapassado
- **Prazo Próximo**: Aviso quando um card está próximo de vencer (2 dias)
- **Card Inativo**: Alerta quando um card está sem atualizações por um período configurável
- **Checklist Pendente**: Aviso quando há itens obrigatórios pendentes no checklist
- **Card Movido**: Notificação quando um card é movido para uma etapa sob sua responsabilidade

### 7.2 Visualização de Notificações

1. Clique no ícone de sino no cabeçalho
2. Um dropdown será aberto com todas as notificações não lidas
3. Clique em uma notificação para ver mais detalhes
4. Clique no ícone de check para marcar como lida

### 7.3 Configuração de Notificações

1. Acesse seu perfil através do menu do usuário
2. Na seção "Notificações", configure suas preferências:
   - Quais tipos de notificações deseja receber
   - Se deseja receber notificações por email
   - Frequência de notificações

## 8. Dashboard

O Dashboard fornece uma visão geral do processo de mobilização com indicadores e gráficos.

### 8.1 Indicadores Principais

- **Total de Cards**: Número total de colaboradores em processo de mobilização
- **Cards por Etapa**: Distribuição de cards em cada etapa do processo
- **Tempo Médio**: Tempo médio de permanência em cada etapa
- **Cards Atrasados**: Número de cards com prazo vencido
- **Eficiência do Processo**: Percentual de cards que seguem o fluxo sem atrasos

### 8.2 Gráficos e Visualizações

- **Gráfico de Distribuição**: Visualização da distribuição de cards por etapa
- **Gráfico de Tendência**: Evolução do número de cards ao longo do tempo
- **Mapa de Calor**: Identificação de gargalos no processo
- **Tabela de Cards Atrasados**: Lista detalhada de cards com prazo vencido

### 8.3 Filtros do Dashboard

- **Período**: Selecione o período de análise (dia, semana, mês, trimestre, ano)
- **Departamento**: Filtre por centro de custo ou departamento
- **Responsável**: Filtre por responsável atual
- **Etapa**: Filtre por etapa específica

## 9. Administração do Sistema

Esta seção é destinada aos usuários com perfil de administrador.

### 9.1 Gerenciamento de Usuários

1. Acesse o menu "Administração" > "Usuários"
2. Visualize a lista de usuários cadastrados
3. Para adicionar um novo usuário:
   - Clique em "Novo Usuário"
   - Preencha os dados do usuário
   - Atribua grupos de permissão
   - Clique em "Salvar"
4. Para editar um usuário existente:
   - Clique no ícone de edição ao lado do usuário
   - Faça as alterações necessárias
   - Clique em "Salvar"

### 9.2 Gerenciamento de Etapas

1. Acesse o menu "Administração" > "Etapas"
2. Visualize a lista de etapas configuradas
3. Para adicionar uma nova etapa:
   - Clique em "Nova Etapa"
   - Defina o nome e a cor da etapa
   - Configure o prazo padrão
   - Defina o responsável padrão
   - Clique em "Salvar"
4. Para editar uma etapa existente:
   - Clique no ícone de edição ao lado da etapa
   - Faça as alterações necessárias
   - Clique em "Salvar"

### 9.3 Gerenciamento de Checklists

1. Acesse o menu "Administração" > "Checklists"
2. Selecione a etapa para configurar seu checklist
3. Para adicionar um novo item:
   - Clique em "Novo Item"
   - Defina o texto do item
   - Marque se é obrigatório
   - Defina a ordem de exibição
   - Clique em "Salvar"
4. Para editar um item existente:
   - Clique no ícone de edição ao lado do item
   - Faça as alterações necessárias
   - Clique em "Salvar"

### 9.4 Gerenciamento de Permissões

1. Acesse o menu "Administração" > "Permissões"
2. Visualize os grupos de permissão configurados
3. Para adicionar um novo grupo:
   - Clique em "Novo Grupo"
   - Defina o nome do grupo
   - Configure as permissões por recurso e operação
   - Clique em "Salvar"
4. Para editar um grupo existente:
   - Clique no ícone de edição ao lado do grupo
   - Faça as alterações necessárias
   - Clique em "Salvar"

## 10. Solução de Problemas

### 10.1 Problemas de Login

- **Senha incorreta**: Utilize a opção "Esqueceu sua senha?" na tela de login
- **Conta bloqueada**: Entre em contato com o administrador do sistema
- **Erro de conexão**: Verifique sua conexão com a internet e tente novamente

### 10.2 Problemas com Cards

- **Não consigo mover um card**: Verifique se todos os itens obrigatórios do checklist estão concluídos
- **Card não aparece no quadro**: Verifique se há filtros ativos no cabeçalho
- **Não consigo editar um card**: Verifique se você tem permissão para editar cards nesta etapa

### 10.3 Problemas com Notificações

- **Não recebo notificações por email**: Verifique suas configurações de notificação no perfil
- **Notificações atrasadas**: O sistema verifica notificações periodicamente, pode haver um pequeno atraso

### 10.4 Suporte Técnico

Para problemas não resolvidos com as soluções acima, entre em contato com o suporte técnico:

- **Email**: suporte@mobilizacao.exemplo.com.br
- **Telefone**: (XX) XXXX-XXXX
- **Horário de atendimento**: Segunda a sexta, das 8h às 18h

