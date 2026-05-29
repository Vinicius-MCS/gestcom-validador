import re
from core.schemas import SCHEMAS

# ==========================================
# VALIDAÇÕES ESTRUTURAIS BÁSICAS
# ==========================================

def validar_estrutura_basica(linhas, quantidade_colunas, cabecalho_esperado):
    """Verifica se a quantidade de colunas e os nomes das colunas coincidem com o esperado."""
    erros = []
    cabecalho_recebido = linhas[0]

    if len(cabecalho_recebido) != quantidade_colunas:
        erros.append(
            f"Número de colunas: esperado {quantidade_colunas}, mas encontrado {len(cabecalho_recebido)}."
        )

    for i in range(min(quantidade_colunas, len(cabecalho_recebido))):
        recebido = cabecalho_recebido[i].strip()
        esperado = cabecalho_esperado[i]

        if recebido != esperado:
            erros.append(
                f"Nome da coluna {i+1}: esperado '{esperado}', mas encontrado '{recebido}'."
            )

    return erros


def validar_linhas_vazias(linhas):
    """Identifica linhas vazias no meio do arquivo e excedentes no final."""
    erros = []
    linhas_vazias_meio = []
    linhas_excedentes_final = []
    ultima_linha_com_dados = 0

    for i, linha in enumerate(linhas):
        if any(campo.strip() != "" for campo in linha):
            ultima_linha_com_dados = i

    for i in range(1, len(linhas)):
        linha = linhas[i]

        if all(campo.strip() == "" for campo in linha):
            if i < ultima_linha_com_dados:
                linhas_vazias_meio.append(i + 1)
            else:
                linhas_excedentes_final.append(i + 1)

    if linhas_vazias_meio:
        lista = ", ".join(map(str, linhas_vazias_meio))
        quantidade = len(linhas_vazias_meio)
        if quantidade == 1:
            erros.append(
                f"Foi encontrada 1 linha vazia no meio do arquivo (linha {lista})."
            )
        else:
            erros.append(
                f"Foram encontradas {quantidade} linhas vazias no meio do arquivo (linhas {lista})."
            )

    if linhas_excedentes_final:
        primeira = linhas_excedentes_final[0]
        ultima = linhas_excedentes_final[-1]
        quantidade = len(linhas_excedentes_final)
        if quantidade == 1:
            erros.append(
                f"Foi encontrada 1 linha excedente no final do arquivo (linha {primeira})."
            )
        else:
            erros.append(
                f"Foram encontradas {quantidade} linhas excedentes no final do arquivo (linhas {primeira} a {ultima})."
            )

    return erros


# ==========================================
# MOTOR GENÉRICO DE VALIDAÇÃO DE ARQUIVO
# ==========================================

def validar_arquivo(linhas, nome_schema):
    """
    Motor centralizado de validação.
    Lê o esquema definido em core.schemas e executa todas as checagens de linha.
    """
    if not linhas:
        return ["Arquivo está vazio ou não pôde ser lido."], []

    schema = SCHEMAS[nome_schema]
    cabecalho_esperado = schema["cabecalho_esperado"]
    quantidade_colunas = len(cabecalho_esperado)

    erros = []
    avisos = []

    # 1. Validações básicas de estrutura (número de colunas e cabeçalho)
    erros_estrutura = validar_estrutura_basica(linhas, quantidade_colunas, cabecalho_esperado)
    erros += erros_estrutura
    
    # 2. Validações de linhas em branco
    erros += validar_linhas_vazias(linhas)

    # Se houver erro estrutural no cabeçalho ou colunas, paramos aqui para evitar erros de índice (IndexError)
    if erros_estrutura:
        return erros, avisos

    # Mapeamento dinâmico Nome da Coluna -> Índice no cabeçalho do arquivo
    cabecalho_recebido = [col.strip() for col in linhas[0]]
    col_para_idx = {nome: cabecalho_recebido.index(nome) for nome in cabecalho_esperado if nome in cabecalho_recebido}

    # Estruturas para validação de chaves únicas
    duplicados_controle = {}
    for col in schema["erros_duplicados"] + schema["avisos_duplicados"]:
        duplicados_controle[col] = {}

    # Caso específico para Competências por Unidade (Duplicidade composta)
    combinacoes_competencias_unidades = {}

    # 3. Varredura linha por linha
    for numero_linha, linha in enumerate(linhas[1:], start=2):
        # Ignora linhas totalmente vazias (já tratadas no validador de vazias)
        if all(c.strip() == "" for c in linha):
            continue

        # A. Checagem de caractere ';' em qualquer campo
        for j, campo in enumerate(linha):
            if ";" in campo and j < len(cabecalho_esperado):
                col_nome = cabecalho_esperado[j]
                avisos.append(f"Linha {numero_linha}: {col_nome} contém caractere ';'.")

        # Variáveis locais para caso especial de dupla chave
        unidade_val = ""
        competencia_val = ""

        # B. Checagem por coluna esperada
        for col_nome in cabecalho_esperado:
            idx = col_para_idx.get(col_nome)
            if idx is None or idx >= len(linha):
                valor = ""
            else:
                valor = linha[idx].strip()

            # Captura valores para caso especial
            if nome_schema == "competencias_unidades":
                if col_nome == "codigo_unidade":
                    unidade_val = valor
                elif col_nome == "codigo_competencia":
                    competencia_val = valor

            # B.1. Validação de campo obrigatório vazio
            if col_nome in schema["obrigatorios"] and valor == "":
                msg_vazio = schema["obrigatorios"][col_nome]
                erros.append(f"Linha {numero_linha}: {msg_vazio}")

            # B.2. Validação customizada da coluna
            if col_nome in schema["validadores_customizados"]:
                validador_fn = schema["validadores_customizados"][col_nome]
                cust_erros, cust_avis = validador_fn(valor, numero_linha)
                erros += cust_erros
                avisos += cust_avis

            # B.3. Agrupamento para checagem de duplicidade
            if col_nome in duplicados_controle and valor not in ["", "*"]:
                duplicados_controle[col_nome].setdefault(valor, []).append(numero_linha)

        # C. Caso específico: Duplicidade composta em Competências por Unidade
        if nome_schema == "competencias_unidades":
            if unidade_val not in ["", "*"] and competencia_val not in ["", "*"]:
                chave = (unidade_val, competencia_val)
                combinacoes_competencias_unidades.setdefault(chave, []).append(numero_linha)

    # 4. Checagens de Duplicidades ao final da varredura
    for col_nome, registros in duplicados_controle.items():
        msg_template = schema["mensagens_duplicado"].get(col_nome, f"{col_nome} '{{valor}}' está duplicado.")
        
        if col_nome in schema["erros_duplicados"]:
            for valor, lista_linhas in registros.items():
                if len(lista_linhas) > 1:
                    lista_str = ", ".join(map(str, lista_linhas))
                    erros.append(f"Linhas {lista_str}: " + msg_template.format(valor=valor))
                    
        elif col_nome in schema["avisos_duplicados"]:
            for valor, lista_linhas in registros.items():
                if len(lista_linhas) > 1:
                    lista_str = ", ".join(map(str, lista_linhas))
                    avisos.append(f"Linhas {lista_str}: " + msg_template.format(valor=valor))

    # Duplicidade composta Competências por Unidade
    if nome_schema == "competencias_unidades":
        for (unidade, competencia), lista_linhas in combinacoes_competencias_unidades.items():
            if len(lista_linhas) > 1:
                lista_str = ", ".join(map(str, lista_linhas))
                erros.append(
                    f"Linhas {lista_str}: combinação codigo_unidade '{unidade}' + codigo_competencia '{competencia}' está duplicada."
                )

    return erros, avisos


def corrigir_e_validar_arquivo(linhas, nome_schema):
    """
    Higieniza e corrige automaticamente o conteúdo do arquivo com base nas regras do esquema,
    registrando todas as correções efetuadas. Em seguida, roda as validações sobre o dado limpo.
    
    Retorna:
        linhas_corrigidas (list[list[str]]): A matriz de dados higienizada.
        erros (list[str]): Erros críticos que restaram após a correção.
        avisos (list[str]): Avisos de formatação/duplicação.
        correcoes (list[str]): Log descritivo de todas as auto-correções aplicadas.
    """
    if not linhas:
        return [], ["Arquivo está vazio ou não pôde ser lido."], [], []

    schema = SCHEMAS[nome_schema]
    cabecalho_esperado = schema["cabecalho_esperado"]
    quantidade_colunas = len(cabecalho_esperado)

    correcoes = []
    
    cabecalho_original = linhas[0]
    
    # Tratamento de erro de formato inválido
    if len(linhas) == 1 and cabecalho_original[0] == "ERRO_FORMATO_INVALIDO":
        return [], ["Erro de Formato: Apenas arquivos no formato .csv são aceitos. Por favor, envie apenas arquivos no formato .csv."], [], []

    # Tratamento de erro de delimitador incorreto
    if len(cabecalho_original) == 1 and quantidade_colunas > 1:
        primeira_celula = cabecalho_original[0]
        if "," in primeira_celula or "\t" in primeira_celula or " " in primeira_celula:
            provavel = "vírgula ','" if "," in primeira_celula else "tabulação (Tab)" if "\t" in primeira_celula else "espaço ' '"
            return [], [
                f"Erro de Delimitador: O arquivo parece estar separado por {provavel} em vez de ponto e vírgula ';'. Certifique-se de salvar o arquivo como CSV delimitado por ponto e vírgula."
            ], [], []

    # 1. Higienização estrutural preliminar: Truncar colunas excedentes e remover vazias
    linhas_normalizadas = []
    linhas_vazias_removidas = []
    
    # Verifica se o cabeçalho original possui colunas excedentes
    if len(cabecalho_original) > quantidade_colunas:
        excedente_count = len(cabecalho_original) - quantidade_colunas
        correcoes.append(f"Foram removidas {excedente_count} coluna(s) excedente(s) vazias no final do arquivo.")

    # Processamos o cabeçalho normalizado
    cabecalho_recebido = [col.strip() for col in cabecalho_original[:quantidade_colunas]]
    linhas_normalizadas.append(cabecalho_recebido)
    
    for numero_linha, linha in enumerate(linhas[1:], start=2):
        # Trata as células limpando espaços
        linha_limpa_campos = [campo.strip() for campo in linha]
        
        # Checamos se a linha está inteiramente vazia
        if all(campo == "" for campo in linha_limpa_campos):
            linhas_vazias_removidas.append(numero_linha)
        else:
            # Normaliza o tamanho da linha para corresponder exatamente ao esperado
            linha_normalizada = list(linha_limpa_campos)
            if len(linha_normalizada) > quantidade_colunas:
                linha_normalizada = linha_normalizada[:quantidade_colunas]
            else:
                while len(linha_normalizada) < quantidade_colunas:
                    linha_normalizada.append("")
            linhas_normalizadas.append(linha_normalizada)
            
    if linhas_vazias_removidas:
        if len(linhas_vazias_removidas) == 1:
            correcoes.append(f"Foi removida 1 linha totalmente vazia (linha {linhas_vazias_removidas[0]}).")
        else:
            lista_str = ", ".join(map(str, sorted(linhas_vazias_removidas)))
            correcoes.append(f"Foram removidas {len(linhas_vazias_removidas)} linhas totalmente vazias (linhas {lista_str}).")

    # 2. Validações básicas de estrutura de cabeçalho sobre os dados normalizados
    erros_estrutura = validar_estrutura_basica(linhas_normalizadas, quantidade_colunas, cabecalho_esperado)
    if erros_estrutura:
        # Se mesmo após a normalização dimensional houver erros (ex: nome de coluna incorreto),
        # paramos aqui para evitar mapeamentos errôneos
        return linhas, erros_estrutura, [], []

    # Mapeamento dinâmico Nome da Coluna -> Índice
    col_para_idx = {nome: cabecalho_recebido.index(nome) for nome in cabecalho_esperado if nome in cabecalho_recebido}

    # 3. Correções de regras de negócio linha a linha
    linhas_corrigidas = [cabecalho_recebido]
    
    for numero_linha, linha in enumerate(linhas_normalizadas[1:], start=2):
        linha_limpa = list(linha) # as células já estão tratadas na etapa 1
        
        # Sanitização geral: quebras de linha (\n, \r, _x000D_, _x000A_) e conflitos de delimitador (';' -> ',')
        for idx in range(len(linha_limpa)):
            valor_original = linha_limpa[idx]
            
            valor_limpo = valor_original.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ')
            valor_limpo = valor_limpo.replace('_x000D_', ' ').replace('_x000A_', ' ')
            
            # Substitui ';' por ',' para evitar conflitos de quebra de delimitador no CSV final
            valor_limpo = valor_limpo.replace(';', ',')
            
            valor_limpo = " ".join(valor_limpo.split())
            
            if valor_limpo != valor_original:
                linha_limpa[idx] = valor_limpo
                col_nome = cabecalho_recebido[idx] if idx < len(cabecalho_recebido) else f"coluna {idx+1}"
                
                # Constrói mensagem de log detalhada
                mensagens_log = []
                if '\r' in valor_original or '\n' in valor_original or '_x000' in valor_original:
                    mensagens_log.append("removida quebra de linha")
                if ';' in valor_original:
                    mensagens_log.append("substituído ';' por ',' para evitar conflito de delimitador")
                
                msg_desc = " e ".join(mensagens_log) if mensagens_log else "caracteres especiais higienizados"
                correcoes.append(f"Linha {numero_linha}: {msg_desc} no campo '{col_nome}'.")
        
        # A. Caso específico: CPF em Colaboradores
        if nome_schema == "colaboradores":
            cpf_idx = col_para_idx.get("cpf")
            mat_idx = col_para_idx.get("matricula")
            if cpf_idx is not None and mat_idx is not None:
                cpf_val = linha_limpa[cpf_idx]
                mat_val = linha_limpa[mat_idx]
                if cpf_val in ["", "*"] and mat_val not in ["", "*"]:
                    linha_limpa[cpf_idx] = mat_val
                    correcoes.append(f"Linha {numero_linha}: CPF estava vazio/'*' e foi preenchido com a matrícula '{mat_val}' automaticamente.")

        # B. Caso específico: Objetivos em Competências por Unidade
        if nome_schema == "competencias_unidades":
            obj_idx = col_para_idx.get("objetivos")
            if obj_idx is not None:
                obj_val = linha_limpa[obj_idx]
                if obj_val not in ["", "*", "-"]:
                    # Limpa todos os espaços
                    obj_limpo = "".join(obj_val.split())
                    # Converte float de ponto para vírgula
                    if re.match(r'^\d+\.\d+$', obj_limpo):
                        obj_limpo = obj_limpo.replace('.', ',')
                    
                    # Remove números duplicados mantendo a ordem de inserção original
                    if any(sep in obj_limpo for sep in [',', '#']):
                        sep = '#' if '#' in obj_limpo else ','
                        partes = obj_limpo.split(sep)
                        unicos = []
                        for p in partes:
                            if p and p not in unicos:
                                unicos.append(p)
                        obj_limpo = sep.join(unicos)
                    
                    if obj_limpo != obj_val:
                        linha_limpa[obj_idx] = obj_limpo
                        correcoes.append(f"Linha {numero_linha}: objetivos formatado de '{obj_val}' para '{obj_limpo}'.")

        # C. Preenchimento de campos obrigatórios com '*' se vazios
        for col_nome, idx in col_para_idx.items():
            if col_nome in schema["obrigatorios"]:
                valor_atual = linha_limpa[idx]
                if valor_atual == "":
                    linha_limpa[idx] = "*"
                    correcoes.append(f"Linha {numero_linha}: campo obrigatório '{col_nome}' estava vazio e foi preenchido com '*' automaticamente.")

        linhas_corrigidas.append(linha_limpa)

    # 4. Remoção de duplicidades exatas
    linhas_unicas = [linhas_corrigidas[0]]
    vistas = set()
    linhas_duplicadas_removidas = []
    
    for numero_linha, linha in enumerate(linhas_corrigidas[1:], start=2):
        linha_tupla = tuple(linha)
        if linha_tupla in vistas:
            linhas_duplicadas_removidas.append(numero_linha)
        else:
            vistas.add(linha_tupla)
            linhas_unicas.append(linha)
            
    if linhas_duplicadas_removidas:
        if len(linhas_duplicadas_removidas) == 1:
            correcoes.append(f"Foi removida 1 linha duplicada idêntica (linha {linhas_duplicadas_removidas[0]}).")
        else:
            lista_str = ", ".join(map(str, sorted(linhas_duplicadas_removidas)))
            correcoes.append(f"Foram removidas {len(linhas_duplicadas_removidas)} linhas duplicadas idênticas (linhas {lista_str}).")

    # 5. Executar validação sobre as linhas finais higienizadas
    erros, avisos = validar_arquivo(linhas_unicas, nome_schema)

    return list(linhas_unicas), erros, avisos, correcoes


# ==========================================
# EXTRAÇÃO DE IDENTIFICADORES (CHAVES PRIMÁRIAS)
# ==========================================

def extrair_identificadores(linhas):
    """Extrai os identificadores únicos da primeira coluna (índice 0) ignorando cabeçalhos, vazios e '*'."""
    if not linhas or len(linhas) <= 1:
        return set()
    identificadores = set()
    for linha in linhas[1:]:
        if len(linha) > 0:
            valor = linha[0].strip()
            if valor not in ["", "*"]:
                identificadores.add(valor)
    return identificadores

def extrair_codigos_cargos(linhas):
    return extrair_identificadores(linhas)

def extrair_cpfs_colaboradores(linhas):
    return extrair_identificadores(linhas)

def extrair_codigos_unidades(linhas):
    return extrair_identificadores(linhas)

def extrair_codigos_competencias(linhas):
    return extrair_identificadores(linhas)

def extrair_codigos_categorias(linhas):
    return extrair_identificadores(linhas)


# ==========================================
# VALIDAÇÕES DE RELACIONAMENTO (INTEGRIDADE REFERENCIAL)
# ==========================================

def validar_relacionamento_cargos(codigos_cargos, linhas_colaboradores):
    erros = []
    for numero_linha, linha in enumerate(linhas_colaboradores[1:], start=2):
        if all(c.strip() == "" for c in linha):
            continue
        cargo = linha[5].strip() if len(linha) > 5 else ""
        if cargo not in ["", "*"] and cargo not in codigos_cargos:
            erros.append(
                f"Linha {numero_linha}: codigo_cargo '{cargo}' não existe em codigo_unidade no arquivo de Cargos."
            )
    return erros


def validar_relacionamento_unidades_colaboradores(codigos_unidades, linhas_colaboradores):
    erros = []
    for numero_linha, linha in enumerate(linhas_colaboradores[1:], start=2):
        if all(c.strip() == "" for c in linha):
            continue
        unidade = linha[4].strip() if len(linha) > 4 else ""
        if unidade not in ["", "*"] and unidade not in codigos_unidades:
            erros.append(
                f"Linha {numero_linha}: codigo_unidade '{unidade}' não existe em codigo_unidade no arquivo de Unidades."
            )
    return erros


def validar_relacionamento_cpfs(cpfs_colaboradores, linhas_unidades):
    erros = []
    for numero_linha, linha in enumerate(linhas_unidades[1:], start=2):
        if all(c.strip() == "" for c in linha):
            continue
        cpf_gestor = linha[4].strip() if len(linha) > 4 else ""
        cpf_avaliador = linha[5].strip() if len(linha) > 5 else ""

        if cpf_gestor not in ["", "*"] and cpf_gestor not in cpfs_colaboradores:
            erros.append(
                f"Linha {numero_linha}: cpf_gestor '{cpf_gestor}' não existe em cpf no arquivo de Colaboradores."
            )
        if cpf_avaliador not in ["", "*"] and cpf_avaliador not in cpfs_colaboradores:
            erros.append(
                f"Linha {numero_linha}: cpf_avaliador_gestor '{cpf_avaliador}' não existe em cpf no arquivo de Colaboradores."
            )
    return erros


def validar_autorrelacionamento_unidades(codigos_unidades, linhas_unidades):
    erros = []
    for numero_linha, linha in enumerate(linhas_unidades[1:], start=2):
        if all(c.strip() == "" for c in linha):
            continue
        codigo_sup = linha[3].strip() if len(linha) > 3 else ""
        if codigo_sup not in ["", "*"] and codigo_sup not in codigos_unidades:
            erros.append(
                f"Linha {numero_linha}: codigo_unidade_superior '{codigo_sup}' não existe em codigo_unidade no arquivo de Unidades."
            )
    return erros


def validar_relacionamento_categorias(codigos_categorias, linhas_competencias):
    erros = []
    for numero_linha, linha in enumerate(linhas_competencias[1:], start=2):
        if all(c.strip() == "" for c in linha):
            continue
        categoria = linha[3].strip() if len(linha) > 3 else ""
        if categoria not in ["", "*"] and categoria not in codigos_categorias:
            erros.append(
                f"Linha {numero_linha}: codigo_categoria '{categoria}' não existe em codigo_categoria no arquivo de Categorias."
            )
    return erros


def validar_relacionamento_unidades_competencias(codigos_unidades, linhas_competencias_unidades):
    erros = []
    for numero_linha, linha in enumerate(linhas_competencias_unidades[1:], start=2):
        if all(c.strip() == "" for c in linha):
            continue
        unidade = linha[0].strip() if len(linha) > 0 else ""
        if unidade not in ["", "*"] and unidade not in codigos_unidades:
            erros.append(
                f"Linha {numero_linha}: codigo_unidade '{unidade}' não existe em codigo_unidade no arquivo de Unidades."
            )
    return erros


def validar_relacionamento_competencias(codigos_competencias, linhas_competencias_unidades):
    erros = []
    for numero_linha, linha in enumerate(linhas_competencias_unidades[1:], start=2):
        if all(c.strip() == "" for c in linha):
            continue
        competencia = linha[1].strip() if len(linha) > 1 else ""
        if competencia not in ["", "*"] and competencia not in codigos_competencias:
            erros.append(
                f"Linha {numero_linha}: codigo_competencia '{competencia}' não existe em codigo_competencia no arquivo de Competencias."
            )
    return erros
