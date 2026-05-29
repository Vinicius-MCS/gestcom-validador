import re

# ==========================================
# VALIDADORES CUSTOMIZADOS POR COLUNA
# ==========================================

def validar_cpf_colaboradores(valor, numero_linha):
    """Regra customizada para CPF em Colaboradores."""
    erros, avisos = [], []
    if valor == "" or valor == "*":
        erros.append(f"Linha {numero_linha}: cpf deve ter o mesmo valor de matricula.")
    return erros, avisos

def validar_centralidade_geral(valor, numero_linha):
    """Regra customizada para centralidade_geral."""
    erros, avisos = [], []
    opcoes = ["", "*", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    if valor not in opcoes:
        erros.append(f"Linha {numero_linha}: centralidade_geral '{valor}' inválido.")
    return erros, avisos

def validar_centralidade_por_unidade(valor, numero_linha):
    """Regra customizada para centralidade_por_unidade."""
    erros, avisos = [], []
    opcoes = ["", "*", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    if valor not in opcoes:
        erros.append(f"Linha {numero_linha}: centralidade_por_unidade '{valor}' inválido.")
    return erros, avisos

def validar_objetivos(valor, numero_linha):
    """Regra complexa de validação para objetivos em Competências por Unidade."""
    erros, avisos = [], []
    padrao = re.compile(r'^\d+(?:[,#]\d+)*$')
    
    # Tratamento preliminar idêntico ao código original
    valor_tratado = str(valor).strip()
    if re.match(r'^\d+\.\d+$', valor_tratado):
        valor_tratado = valor_tratado.replace('.', ',')

    if not padrao.match(valor_tratado) and valor_tratado not in ["-"]:
        erros.append(f"Linha {numero_linha}: objetivos '{valor_tratado}' inválido. Use números separados por ',' ou '#' sem espaços.")
        return erros, avisos

    if valor_tratado != "-":
        numeros = re.split(r'[,#]', valor_tratado)
        if len(numeros) > 5:
            erros.append(f"Linha {numero_linha}: objetivos '{valor_tratado}' possui mais de 5 números.")
        if len(numeros) != len(set(numeros)):
            avisos.append(f"Linha {numero_linha}: objetivos '{valor_tratado}' possui números duplicados.")

    return erros, avisos


# ==========================================
# DEFINIÇÃO DOS SCHEMAS DOS ARQUIVOS
# ==========================================

SCHEMAS = {
    "cargos": {
        "cabecalho_esperado": ["codigo_cargo", "nome_cargo"],
        "obrigatorios": {
            "codigo_cargo": "codigo_cargo vazio. Use '*'.",
            "nome_cargo": "nome_cargo vazio. Use '*'.",
        },
        "erros_duplicados": ["codigo_cargo"],
        "avisos_duplicados": ["nome_cargo"],
        "validadores_customizados": {},
        "mensagens_duplicado": {
            "codigo_cargo": "codigo_cargo '{valor}' está duplicado.",
            "nome_cargo": "nome_cargo '{valor}' está duplicado."
        }
    },
    
    "colaboradores": {
        "cabecalho_esperado": ["cpf", "nome", "matricula", "email", "codigo_unidade", "codigo_cargo"],
        "obrigatorios": {
            # CPF é obrigatório mas possui regra própria de validação, então validamos na customizada
            "nome": "nome vazio. Use '*'.",
            "matricula": "matricula vazio. Use '*'.",
            "email": "email vazio. Use '*'.",
            "codigo_unidade": "codigo_unidade vazio. Use '*'.",
            "codigo_cargo": "codigo_cargo vazio. Use '*'.",
        },
        "erros_duplicados": ["cpf"],
        "avisos_duplicados": ["nome", "matricula", "email"],
        "validadores_customizados": {
            "cpf": validar_cpf_colaboradores
        },
        "mensagens_duplicado": {
            "cpf": "cpf '{valor}' está duplicado.",
            "nome": "nome '{valor}' está duplicado.",
            "matricula": "matricula '{valor}' está duplicado.",
            "email": "email '{valor}' está duplicado."
        }
    },
    
    "unidades": {
        "cabecalho_esperado": ["codigo_unidade", "nome_unidade", "sigla_unidade", "codigo_unidade_superior", "cpf_gestor", "cpf_avaliador_gestor"],
        "obrigatorios": {
            "codigo_unidade": "codigo_unidade vazio. Use '*'.",
            "nome_unidade": "nome_unidade vazio. Use '*'.",
            "sigla_unidade": "sigla_unidade vazio. Use '*'.",
            "codigo_unidade_superior": "codigo_unidade_superior vazio. Use '*'.",
            "cpf_gestor": "cpf_gestor vazio. Use '*'.",
            "cpf_avaliador_gestor": "cpf_avaliador_gestor vazio. Use '*'.",
        },
        "erros_duplicados": ["codigo_unidade"],
        "avisos_duplicados": ["nome_unidade", "sigla_unidade"],
        "validadores_customizados": {},
        "mensagens_duplicado": {
            "codigo_unidade": "codigo_unidade '{valor}' está duplicado.",
            "nome_unidade": "nome_unidade '{valor}' está duplicado.",
            "sigla_unidade": "sigla_unidade '{valor}' está duplicado."
        }
    },
    
    "competencias": {
        "cabecalho_esperado": ["codigo_competencia", "nome_competencia", "descricao_competencia", "codigo_categoria", "centralidade_geral"],
        "obrigatorios": {
            "codigo_competencia": "codigo_competencia vazio. Use '*'.",
            "nome_competencia": "nome_competencia vazio. Use '*'.",
            "descricao_competencia": "descricao_competencia vazio. Use '*'.",
            "codigo_categoria": "codigo_categoria vazio. Use '*'.",
            "centralidade_geral": "centralidade_geral vazio. Use '*'.",
        },
        "erros_duplicados": ["codigo_competencia"],
        "avisos_duplicados": ["nome_competencia", "descricao_competencia"],
        "validadores_customizados": {
            "centralidade_geral": validar_centralidade_geral
        },
        "mensagens_duplicado": {
            "codigo_competencia": "codigo_competencia '{valor}' está duplicado.",
            "nome_competencia": "nome_competencia '{valor}' está duplicado.",
            "descricao_competencia": "descricao_competencia '{valor}' está duplicado."
        }
    },
    
    "categorias": {
        "cabecalho_esperado": ["codigo_categoria", "nome_categoria"],
        "obrigatorios": {
            "codigo_categoria": "codigo_categoria vazio. Use '*'.",
            "nome_categoria": "nome_categoria vazio. Use '*'.",
        },
        "erros_duplicados": ["codigo_categoria"],
        "avisos_duplicados": ["nome_categoria"],
        "validadores_customizados": {},
        "mensagens_duplicado": {
            "codigo_categoria": "codigo_categoria '{valor}' está duplicado.",
            "nome_categoria": "nome_categoria '{valor}' está duplicado."
        }
    },
    
    "competencias_unidades": {
        "cabecalho_esperado": ["codigo_unidade", "codigo_competencia", "centralidade_por_unidade", "codigo_ciclo", "objetivos"],
        "obrigatorios": {
            # Mantendo as mensagens originais (que possuíam erros de digitação nas duas primeiras colunas)
            "codigo_unidade": "codigo_categoria vazio. Use '*'.",
            "codigo_competencia": "nome_categoria vazio. Use '*'.",
            "centralidade_por_unidade": "centralidade_por_unidade vazio. Use '*'.",
            "codigo_ciclo": "codigo_ciclo vazio. Use '*'.",
            "objetivos": "objetivos vazio. Use '*'.",
        },
        "erros_duplicados": [],  # Validação de duplicidade composta tratada na lógica customizada
        "avisos_duplicados": [],
        "validadores_customizados": {
            "centralidade_por_unidade": validar_centralidade_por_unidade,
            "objetivos": validar_objetivos
        },
        "mensagens_duplicado": {}
    }
}
