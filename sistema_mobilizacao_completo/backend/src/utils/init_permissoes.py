from src.models.mobilizacao import db, Grupo
from src.models.permissoes import Permissao, TipoPermissao, RecursoSistema, permissao_grupo

def inicializar_permissoes():
    """
    Inicializa as permissões padrão do sistema e associa aos grupos.
    """
    print("Inicializando permissões do sistema...")
    
    # Verificar se já existem permissões
    if Permissao.query.first() is not None:
        print("Permissões já inicializadas.")
        return
    
    # Criar permissões para cada recurso e tipo
    permissoes = {}
    
    for recurso in RecursoSistema:
        for tipo in TipoPermissao:
            descricao = f"Permite {tipo.value} {recurso.value}"
            permissao = Permissao(
                tipo=tipo.value,
                recurso=recurso.value,
                descricao=descricao
            )
            db.session.add(permissao)
            permissoes[f"{tipo.value}_{recurso.value}"] = permissao
    
    db.session.flush()
    
    # Associar permissões aos grupos
    grupos = {grupo.nome: grupo for grupo in Grupo.query.all()}
    
    # Administrador tem todas as permissões
    if 'Administrador' in grupos:
        for permissao in permissoes.values():
            grupos['Administrador'].permissoes.append(permissao)
    
    # RH pode gerenciar cards e visualizar dashboard
    if 'RH' in grupos:
        grupos['RH'].permissoes.append(permissoes['visualizar_card'])
        grupos['RH'].permissoes.append(permissoes['criar_card'])
        grupos['RH'].permissoes.append(permissoes['editar_card'])
        grupos['RH'].permissoes.append(permissoes['mover_card'])
        grupos['RH'].permissoes.append(permissoes['visualizar_dashboard'])
        grupos['RH'].permissoes.append(permissoes['visualizar_relatorio'])
    
    # Requisição pode criar cards
    if 'Requisição' in grupos:
        grupos['Requisição'].permissoes.append(permissoes['visualizar_card'])
        grupos['Requisição'].permissoes.append(permissoes['criar_card'])
        grupos['Requisição'].permissoes.append(permissoes['editar_card'])
    
    # Treinamento pode visualizar e editar cards
    if 'Treinamento' in grupos:
        grupos['Treinamento'].permissoes.append(permissoes['visualizar_card'])
        grupos['Treinamento'].permissoes.append(permissoes['editar_card'])
        grupos['Treinamento'].permissoes.append(permissoes['mover_card'])
    
    # TI pode visualizar cards e configurações
    if 'TI' in grupos:
        grupos['TI'].permissoes.append(permissoes['visualizar_card'])
        grupos['TI'].permissoes.append(permissoes['visualizar_configuracao'])
        grupos['TI'].permissoes.append(permissoes['editar_configuracao'])
    
    # Segurança pode visualizar e editar cards
    if 'Segurança' in grupos:
        grupos['Segurança'].permissoes.append(permissoes['visualizar_card'])
        grupos['Segurança'].permissoes.append(permissoes['editar_card'])
        grupos['Segurança'].permissoes.append(permissoes['mover_card'])
    
    # Operações pode visualizar e editar cards
    if 'Operações' in grupos:
        grupos['Operações'].permissoes.append(permissoes['visualizar_card'])
        grupos['Operações'].permissoes.append(permissoes['editar_card'])
        grupos['Operações'].permissoes.append(permissoes['mover_card'])
    
    db.session.commit()
    print("Permissões inicializadas com sucesso!")
    
    # Listar permissões por grupo
    for nome_grupo, grupo in grupos.items():
        permissoes_grupo = [f"{p.tipo}_{p.recurso}" for p in grupo.permissoes]
        print(f"Grupo {nome_grupo}: {len(permissoes_grupo)} permissões")
        if len(permissoes_grupo) > 0:
            print(f"  - {', '.join(permissoes_grupo)}")

