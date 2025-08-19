from src.models.mobilizacao import db, Usuario, Grupo, EtapaProcesso, ChecklistEtapa, CardMobilizacao
from datetime import datetime, date

def criar_dados_iniciais():
    """Cria dados iniciais se o banco estiver vazio"""
    
    # Verificar se já existem dados
    if Usuario.query.first() is not None:
        return
    
    print("Criando dados iniciais...")
    
    # Criar grupos
    grupos_data = [
        {'nome': 'Administrador', 'descricao': 'Administradores do sistema'},
        {'nome': 'RH', 'descricao': 'Recursos Humanos'},
        {'nome': 'Requisição', 'descricao': 'Responsáveis por requisições de pessoal'},
        {'nome': 'Treinamento', 'descricao': 'Equipe de treinamento'},
        {'nome': 'TI', 'descricao': 'Tecnologia da Informação'},
        {'nome': 'Segurança', 'descricao': 'Segurança do trabalho'},
        {'nome': 'Operações', 'descricao': 'Operações e produção'}
    ]
    
    grupos = {}
    for grupo_data in grupos_data:
        grupo = Grupo(**grupo_data)
        db.session.add(grupo)
        grupos[grupo_data['nome']] = grupo
    
    db.session.flush()
    
    # Criar usuário administrador
    admin = Usuario(
        nome='Administrador',
        email='admin@empresa.com',
        ativo=True
    )
    admin.set_senha('admin123')
    admin.grupos.append(grupos['Administrador'])
    admin.grupos.append(grupos['RH'])
    db.session.add(admin)
    db.session.flush()
    
    # Criar outros usuários
    usuarios_data = [
        {
            'nome': 'Maria Silva',
            'email': 'maria.rh@empresa.com',
            'senha': 'senha123',
            'grupos': ['RH', 'Requisição']
        },
        {
            'nome': 'João Santos',
            'email': 'joao.treinamento@empresa.com',
            'senha': 'senha123',
            'grupos': ['Treinamento']
        },
        {
            'nome': 'Ana Costa',
            'email': 'ana.ti@empresa.com',
            'senha': 'senha123',
            'grupos': ['TI']
        },
        {
            'nome': 'Carlos Oliveira',
            'email': 'carlos.seguranca@empresa.com',
            'senha': 'senha123',
            'grupos': ['Segurança']
        },
        {
            'nome': 'Fernanda Lima',
            'email': 'fernanda.operacoes@empresa.com',
            'senha': 'senha123',
            'grupos': ['Operações']
        }
    ]
    
    for usuario_data in usuarios_data:
        usuario = Usuario(
            nome=usuario_data['nome'],
            email=usuario_data['email'],
            ativo=True,
            criado_por=admin.id
        )
        usuario.set_senha(usuario_data['senha'])
        
        for nome_grupo in usuario_data['grupos']:
            if nome_grupo in grupos:
                usuario.grupos.append(grupos[nome_grupo])
        
        db.session.add(usuario)
    
    db.session.flush()
    
    # Criar etapas do processo
    etapas_data = [
        {
            'nome': 'Requisição de Pessoas',
            'descricao': 'Solicitação e aprovação de nova contratação',
            'ordem': 1,
            'prazo_dias': 3,
            'dias_alerta_inatividade': 2,
            'dono_email': 'maria.rh@empresa.com',
            'grupos': ['RH', 'Requisição', 'Administrador']
        },
        {
            'nome': 'Admissão',
            'descricao': 'Processo de admissão e documentação',
            'ordem': 2,
            'prazo_dias': 5,
            'dias_alerta_inatividade': 3,
            'dono_email': 'maria.rh@empresa.com',
            'grupos': ['RH', 'Administrador']
        },
        {
            'nome': 'Treinamento',
            'descricao': 'Treinamento inicial e integração',
            'ordem': 3,
            'prazo_dias': 7,
            'dias_alerta_inatividade': 4,
            'dono_email': 'joao.treinamento@empresa.com',
            'grupos': ['Treinamento', 'Administrador']
        },
        {
            'nome': 'Postagem de Documentos',
            'descricao': 'Organização e arquivo de documentos',
            'ordem': 4,
            'prazo_dias': 2,
            'dias_alerta_inatividade': 1,
            'dono_email': 'maria.rh@empresa.com',
            'grupos': ['RH', 'Administrador']
        },
        {
            'nome': 'Retirada de Crachá',
            'descricao': 'Confecção e entrega de crachá',
            'ordem': 5,
            'prazo_dias': 3,
            'dias_alerta_inatividade': 2,
            'dono_email': 'carlos.seguranca@empresa.com',
            'grupos': ['Segurança', 'Administrador']
        },
        {
            'nome': 'Entrega de EPI',
            'descricao': 'Entrega de equipamentos de proteção individual',
            'ordem': 6,
            'prazo_dias': 2,
            'dias_alerta_inatividade': 1,
            'dono_email': 'carlos.seguranca@empresa.com',
            'grupos': ['Segurança', 'Administrador']
        },
        {
            'nome': 'Início das Atividades',
            'descricao': 'Início efetivo das atividades laborais',
            'ordem': 7,
            'prazo_dias': 1,
            'dias_alerta_inatividade': 1,
            'dono_email': 'fernanda.operacoes@empresa.com',
            'grupos': ['Operações', 'Administrador']
        }
    ]
    
    etapas = {}
    for etapa_data in etapas_data:
        grupos_etapa = etapa_data.pop('grupos')
        etapa = EtapaProcesso(**etapa_data)
        
        # Associar grupos
        for nome_grupo in grupos_etapa:
            if nome_grupo in grupos:
                etapa.grupos_permitidos.append(grupos[nome_grupo])
        
        db.session.add(etapa)
        etapas[etapa_data['nome']] = etapa
    
    db.session.flush()
    
    # Criar checklists para cada etapa
    checklists_data = {
        'Requisição de Pessoas': [
            {'tarefa': 'Validar necessidade da vaga', 'obrigatorio': True, 'ordem': 1},
            {'tarefa': 'Aprovar orçamento', 'obrigatorio': True, 'ordem': 2},
            {'tarefa': 'Definir perfil do candidato', 'obrigatorio': True, 'ordem': 3},
            {'tarefa': 'Publicar vaga', 'obrigatorio': False, 'ordem': 4}
        ],
        'Admissão': [
            {'tarefa': 'Coletar documentos pessoais', 'obrigatorio': True, 'ordem': 1},
            {'tarefa': 'Realizar exame médico', 'obrigatorio': True, 'ordem': 2},
            {'tarefa': 'Preencher ficha de admissão', 'obrigatorio': True, 'ordem': 3},
            {'tarefa': 'Configurar acesso ao sistema', 'obrigatorio': True, 'ordem': 4},
            {'tarefa': 'Cadastrar no sistema de folha', 'obrigatorio': True, 'ordem': 5}
        ],
        'Treinamento': [
            {'tarefa': 'Apresentar empresa e cultura', 'obrigatorio': True, 'ordem': 1},
            {'tarefa': 'Treinamento de segurança', 'obrigatorio': True, 'ordem': 2},
            {'tarefa': 'Treinamento específico da função', 'obrigatorio': True, 'ordem': 3},
            {'tarefa': 'Avaliar conhecimento adquirido', 'obrigatorio': True, 'ordem': 4}
        ],
        'Postagem de Documentos': [
            {'tarefa': 'Organizar documentos físicos', 'obrigatorio': True, 'ordem': 1},
            {'tarefa': 'Digitalizar documentos', 'obrigatorio': True, 'ordem': 2},
            {'tarefa': 'Arquivar no sistema', 'obrigatorio': True, 'ordem': 3}
        ],
        'Retirada de Crachá': [
            {'tarefa': 'Tirar foto para crachá', 'obrigatorio': True, 'ordem': 1},
            {'tarefa': 'Confeccionar crachá', 'obrigatorio': True, 'ordem': 2},
            {'tarefa': 'Entregar crachá ao colaborador', 'obrigatorio': True, 'ordem': 3}
        ],
        'Entrega de EPI': [
            {'tarefa': 'Avaliar EPIs necessários', 'obrigatorio': True, 'ordem': 1},
            {'tarefa': 'Separar EPIs do estoque', 'obrigatorio': True, 'ordem': 2},
            {'tarefa': 'Entregar e orientar uso', 'obrigatorio': True, 'ordem': 3},
            {'tarefa': 'Registrar entrega', 'obrigatorio': True, 'ordem': 4}
        ],
        'Início das Atividades': [
            {'tarefa': 'Apresentar ao supervisor direto', 'obrigatorio': True, 'ordem': 1},
            {'tarefa': 'Mostrar local de trabalho', 'obrigatorio': True, 'ordem': 2},
            {'tarefa': 'Iniciar atividades', 'obrigatorio': True, 'ordem': 3}
        ]
    }
    
    for nome_etapa, checklist_items in checklists_data.items():
        if nome_etapa in etapas:
            etapa = etapas[nome_etapa]
            for item_data in checklist_items:
                checklist_item = ChecklistEtapa(
                    etapa_id=etapa.id,
                    **item_data
                )
                db.session.add(checklist_item)
    
    db.session.flush()
    
    # Criar alguns cards de exemplo
    cards_exemplo = [
        {
            'nome_colaborador': 'Pedro Oliveira',
            'cpf': '123.456.789-00',
            'cargo': 'Desenvolvedor',
            'salario': 6000.00,
            'centro_custo': 'TI',
            'data_admissao': date(2024, 2, 1),
            'etapa_atual_id': etapas['Admissão'].id,
            'status_etapa': 'EM_ANDAMENTO',
            'observacoes': 'Contratação urgente para projeto especial'
        },
        {
            'nome_colaborador': 'Ana Martins',
            'cpf': '987.654.321-00',
            'cargo': 'Analista de RH',
            'salario': 4500.00,
            'centro_custo': 'RH',
            'data_admissao': date(2024, 2, 15),
            'etapa_atual_id': etapas['Treinamento'].id,
            'status_etapa': 'NAO_INICIADO',
            'observacoes': 'Substituição de funcionário que se desligou'
        },
        {
            'nome_colaborador': 'Carlos Santos',
            'cpf': '456.789.123-00',
            'cargo': 'Operador de Máquina',
            'salario': 3200.00,
            'centro_custo': 'Produção',
            'data_admissao': date(2024, 1, 20),
            'etapa_atual_id': etapas['Entrega de EPI'].id,
            'status_etapa': 'EM_ANDAMENTO',
            'observacoes': 'Experiência anterior em metalúrgica'
        },
        {
            'nome_colaborador': 'Fernanda Costa',
            'cpf': '789.123.456-00',
            'cargo': 'Assistente Administrativo',
            'salario': 2800.00,
            'centro_custo': 'Administrativo',
            'data_admissao': date(2024, 2, 10),
            'etapa_atual_id': etapas['Requisição de Pessoas'].id,
            'status_etapa': 'FINALIZADO',
            'observacoes': 'Primeira experiência profissional'
        }
    ]
    
    for card_data in cards_exemplo:
        card = CardMobilizacao(
            **card_data,
            criado_por=admin.id,
            atualizado_por=admin.id
        )
        db.session.add(card)
    
    # Commit todas as mudanças
    db.session.commit()
    print("Dados iniciais criados com sucesso!")
    print("Usuário admin: admin@empresa.com / admin123")
    print("Outros usuários: [nome]@empresa.com / senha123")

