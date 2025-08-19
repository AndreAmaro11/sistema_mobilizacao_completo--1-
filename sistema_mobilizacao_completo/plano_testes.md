# Plano de Testes - Sistema de Mobilização de Funcionários

## 1. Introdução

Este documento descreve o plano de testes para o Sistema de Mobilização de Funcionários. O objetivo é garantir que todas as funcionalidades estejam operando corretamente, que o sistema seja estável e que atenda aos requisitos especificados.

## 2. Escopo dos Testes

Os testes abrangem todas as funcionalidades do sistema, incluindo:

- Autenticação e controle de acesso
- Gerenciamento de cards no quadro Kanban
- Movimentação entre etapas
- Gerenciamento de checklists
- Sistema de notificações e alertas
- Dashboard e relatórios
- Responsividade e usabilidade da interface

## 3. Tipos de Testes

### 3.1 Testes de Unidade
- Verificação de componentes individuais do sistema
- Testes de funções e métodos isolados
- Validação de regras de negócio específicas

### 3.2 Testes de Integração
- Verificação da comunicação entre componentes
- Testes de fluxos completos entre frontend e backend
- Validação de integrações entre módulos

### 3.3 Testes Funcionais
- Verificação de funcionalidades completas do sistema
- Testes de fluxos de usuário end-to-end
- Validação de requisitos funcionais

### 3.4 Testes de Usabilidade
- Verificação da experiência do usuário
- Testes de responsividade em diferentes dispositivos
- Validação de acessibilidade

### 3.5 Testes de Desempenho
- Verificação de tempos de resposta
- Testes de carga e estresse
- Validação de limites do sistema

## 4. Casos de Teste

### 4.1 Autenticação e Controle de Acesso

| ID | Descrição | Passos | Resultado Esperado |
|----|-----------|--------|-------------------|
| AUTH-01 | Login com credenciais válidas | 1. Acessar página de login<br>2. Inserir email e senha válidos<br>3. Clicar em "Entrar" | Usuário é autenticado e redirecionado para o dashboard |
| AUTH-02 | Login com credenciais inválidas | 1. Acessar página de login<br>2. Inserir email e senha inválidos<br>3. Clicar em "Entrar" | Mensagem de erro é exibida |
| AUTH-03 | Logout | 1. Clicar no menu do usuário<br>2. Clicar em "Sair" | Usuário é deslogado e redirecionado para a página de login |
| AUTH-04 | Acesso a rota protegida sem autenticação | 1. Tentar acessar uma rota protegida sem estar autenticado | Redirecionamento para a página de login |
| AUTH-05 | Verificação de permissões por grupo | 1. Logar com usuário de grupo específico<br>2. Tentar acessar funcionalidades restritas a outros grupos | Acesso negado para funcionalidades não permitidas |

### 4.2 Gerenciamento de Cards

| ID | Descrição | Passos | Resultado Esperado |
|----|-----------|--------|-------------------|
| CARD-01 | Criação de novo card | 1. Clicar em "Novo Card"<br>2. Preencher formulário<br>3. Clicar em "Criar" | Card é criado e aparece na primeira etapa |
| CARD-02 | Edição de card existente | 1. Clicar em um card<br>2. Editar informações<br>3. Salvar alterações | Card é atualizado com novas informações |
| CARD-03 | Visualização de detalhes do card | 1. Clicar em um card | Modal com detalhes do card é exibido |
| CARD-04 | Filtro de cards | 1. Usar campo de pesquisa<br>2. Aplicar filtros | Apenas cards que correspondem aos critérios são exibidos |
| CARD-05 | Ordenação de cards | 1. Clicar em opções de ordenação | Cards são reordenados conforme critério selecionado |

### 4.3 Movimentação entre Etapas

| ID | Descrição | Passos | Resultado Esperado |
|----|-----------|--------|-------------------|
| ETAPA-01 | Movimentação de card entre etapas | 1. Abrir detalhes do card<br>2. Selecionar nova etapa<br>3. Confirmar movimentação | Card é movido para a nova etapa |
| ETAPA-02 | Verificação de permissões para movimentação | 1. Tentar mover card com usuário sem permissão | Operação é negada |
| ETAPA-03 | Registro de histórico de movimentação | 1. Mover card entre etapas<br>2. Verificar histórico | Movimentação é registrada no histórico |
| ETAPA-04 | Atualização de prazo ao mudar de etapa | 1. Mover card para nova etapa | Prazo é recalculado conforme configuração da etapa |
| ETAPA-05 | Criação de checklist ao mudar de etapa | 1. Mover card para nova etapa | Checklist da nova etapa é criado para o card |

### 4.4 Gerenciamento de Checklists

| ID | Descrição | Passos | Resultado Esperado |
|----|-----------|--------|-------------------|
| CHECK-01 | Marcação de item como concluído | 1. Abrir detalhes do card<br>2. Marcar item do checklist | Item é marcado como concluído e progresso é atualizado |
| CHECK-02 | Desmarcação de item concluído | 1. Abrir detalhes do card<br>2. Desmarcar item do checklist | Item é desmarcado e progresso é atualizado |
| CHECK-03 | Verificação de itens obrigatórios | 1. Tentar finalizar etapa sem concluir itens obrigatórios | Operação é negada com mensagem de erro |
| CHECK-04 | Cálculo de progresso do checklist | 1. Marcar/desmarcar itens do checklist | Percentual de progresso é atualizado corretamente |
| CHECK-05 | Adição de observações em itens | 1. Adicionar observação a um item do checklist | Observação é salva e exibida |

### 4.5 Sistema de Notificações e Alertas

| ID | Descrição | Passos | Resultado Esperado |
|----|-----------|--------|-------------------|
| NOTIF-01 | Exibição de notificações não lidas | 1. Logar no sistema com usuário que possui notificações | Contador de notificações não lidas é exibido |
| NOTIF-02 | Marcação de notificação como lida | 1. Abrir dropdown de notificações<br>2. Marcar notificação como lida | Notificação é removida da lista e contador é atualizado |
| NOTIF-03 | Marcação de todas notificações como lidas | 1. Abrir dropdown de notificações<br>2. Clicar em "Marcar todas como lidas" | Todas notificações são marcadas como lidas |
| NOTIF-04 | Geração de notificação de prazo vencido | 1. Executar verificação de prazos com card vencido | Notificação é gerada para o responsável |
| NOTIF-05 | Geração de notificação de movimentação | 1. Mover card entre etapas | Notificação é gerada para o responsável da etapa de destino |

### 4.6 Dashboard e Relatórios

| ID | Descrição | Passos | Resultado Esperado |
|----|-----------|--------|-------------------|
| DASH-01 | Exibição de indicadores gerais | 1. Acessar dashboard | Indicadores gerais são exibidos corretamente |
| DASH-02 | Filtro de indicadores por período | 1. Selecionar período no dashboard | Indicadores são atualizados conforme período selecionado |
| DASH-03 | Exibição de cards atrasados | 1. Acessar seção de cards atrasados | Lista de cards com prazo vencido é exibida |
| DASH-04 | Exibição de estatísticas por etapa | 1. Visualizar gráfico de estatísticas por etapa | Dados são exibidos corretamente por etapa |
| DASH-05 | Exportação de relatórios | 1. Clicar em exportar relatório | Relatório é gerado e baixado |

### 4.7 Responsividade e Usabilidade

| ID | Descrição | Passos | Resultado Esperado |
|----|-----------|--------|-------------------|
| UI-01 | Visualização em desktop | 1. Acessar sistema em desktop | Interface é exibida corretamente |
| UI-02 | Visualização em tablet | 1. Acessar sistema em tablet | Interface se adapta ao tamanho da tela |
| UI-03 | Visualização em smartphone | 1. Acessar sistema em smartphone | Interface se adapta ao tamanho da tela |
| UI-04 | Navegação por teclado | 1. Navegar usando apenas teclado | Todos elementos são acessíveis via teclado |
| UI-05 | Feedback visual de ações | 1. Realizar ações no sistema | Feedback visual é fornecido para cada ação |

## 5. Ambiente de Testes

### 5.1 Configuração de Ambiente
- Backend: Flask rodando em localhost:5000
- Frontend: React rodando em localhost:5173
- Banco de dados: SQLite local

### 5.2 Ferramentas de Teste
- Testes manuais via navegador
- Postman para testes de API
- Chrome DevTools para inspeção e debugging
- React Developer Tools para debugging de componentes

## 6. Critérios de Aceitação

- Todos os casos de teste críticos devem passar
- Nenhum erro crítico ou bloqueante deve estar presente
- Tempo de resposta deve ser aceitável (< 2 segundos para operações comuns)
- Interface deve ser responsiva em todos os dispositivos testados
- Todas as funcionalidades devem operar conforme especificado nos requisitos

## 7. Relatório de Testes

Os resultados dos testes serão documentados em um relatório separado, incluindo:
- Status de cada caso de teste (Passou/Falhou)
- Descrição de problemas encontrados
- Capturas de tela de erros
- Recomendações para correções

## 8. Plano de Correção

Para cada problema identificado, será criado um plano de correção incluindo:
- Descrição do problema
- Severidade e prioridade
- Passos para reprodução
- Solução proposta
- Responsável pela correção
- Prazo para correção

