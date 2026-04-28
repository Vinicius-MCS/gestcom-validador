import streamlit as st
import pandas as pd
import csv
import os
import re
import tempfile

# ==============================
# CONVERSÃO EXCEL → CSV
# ==============================

def converter_excel_para_csv(caminho_excel):
    try:
        df = pd.read_excel(caminho_excel, dtype=str)
        df = df.applymap(lambda x: str(x) if pd.notnull(x) else "")
        temp_csv = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        df.to_csv(temp_csv.name, sep=';', index=False, encoding='utf-8')
        return temp_csv.name
    except Exception:
        return None

# ==============================
# FUNÇÕES AUXILIARES
# ==============================

def validar_estrutura_basica(linhas, quantidade_colunas, cabecalho_esperado):
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

# ==============================
# VALIDAÇÃO CARGOS
# ==============================

def validar_cargos(linhas):

    erros, avisos = [], []

    cabecalho_esperado = ["codigo_cargo", "nome_cargo"]

    erros += validar_estrutura_basica(linhas, 2, cabecalho_esperado)
    erros += validar_linhas_vazias(linhas)

    codigos, nomes = {}, {}

    for numero_linha, linha in enumerate(linhas[1:], start=2):
        if all(c.strip() == "" for c in linha):
            continue
        
        for j, campo in enumerate(linha):
            if ";" in campo:
                match j:
                    case 0:
                        avisos.append(
                            f"Linha {numero_linha}: codigo_cargo contém caractere ';'."
                        )
                    case 1:
                        avisos.append(
                            f"Linha {numero_linha}: nome_cargo contém caractere ';'."
                        )

        codigo = linha[0].strip() if len(linha) > 0 else ""
        nome = linha[1].strip() if len(linha) > 1 else ""

        if codigo == "":
            erros.append(f"Linha {numero_linha}: codigo_cargo vazio. Use '*'.")
        if nome == "":
            erros.append(f"Linha {numero_linha}: nome_cargo vazio. Use '*'.")

        if codigo not in ["", "*"]:
            codigos.setdefault(codigo, []).append(numero_linha)
        if nome not in ["", "*"]:
            nomes.setdefault(nome, []).append(numero_linha)

    for codigo, linhas_dup in codigos.items():
        if len(linhas_dup) > 1:
            erros.append(f"Linhas {', '.join(map(str, linhas_dup))}: codigo_cargo '{codigo}' está duplicado.")

    for nome, linhas_dup in nomes.items():
        if len(linhas_dup) > 1:
            avisos.append(f"Linhas {', '.join(map(str, linhas_dup))}: nome_cargo '{nome}' está duplicado.")

    return erros, avisos

# ==============================
# VALIDAÇÃO COLABORADORES
# ==============================

def validar_colaboradores(linhas):

    erros, avisos = [], []

    cabecalho_esperado = ["cpf", "nome", "matricula", "email", "codigo_unidade", "codigo_cargo"]

    erros += validar_estrutura_basica(linhas, 6, cabecalho_esperado)
    erros += validar_linhas_vazias(linhas)

    cpfs, nomes, matriculas, emails = {}, {}, {}, {}

    for numero_linha, linha in enumerate(linhas[1:], start=2):
        if all(c.strip() == "" for c in linha):
            continue
        
        for j, campo in enumerate(linha):
            if ";" in campo:
                match j:
                    case 0:
                        avisos.append(
                            f"Linha {numero_linha}: cpf contém caractere ';'."
                        )
                    case 1:
                        avisos.append(
                            f"Linha {numero_linha}: nome contém caractere ';'."
                        )
                    case 2:
                        avisos.append(
                            f"Linha {numero_linha}: matricula contém caractere ';'."
                        )
                    case 3:
                        avisos.append(
                            f"Linha {numero_linha}: email contém caractere ';'."
                        )
                    case 4:
                        avisos.append(
                            f"Linha {numero_linha}: codigo_unidade contém caractere ';'."
                        )
                    case 5:
                        avisos.append(
                            f"Linha {numero_linha}: codigo_cargo contém caractere ';'."
                        )

        cpf = linha[0].strip() if len(linha) > 0 else ""
        nome = linha[1].strip() if len(linha) > 1 else ""
        matricula = linha[2].strip() if len(linha) > 2 else ""
        email = linha[3].strip() if len(linha) > 3 else ""
        unidade = linha[4].strip() if len(linha) > 4 else ""
        cargo = linha[5].strip() if len(linha) > 5 else ""

        if cpf == "" or cpf == "*":
            erros.append(f"Linha {numero_linha}: cpf deve ter o mesmo valor de matricula.")
        if nome == "":
            erros.append(f"Linha {numero_linha}: nome vazio. Use '*'.")
        if matricula == "":
            erros.append(f"Linha {numero_linha}: matricula vazio. Use '*'.")
        if email == "":
            erros.append(f"Linha {numero_linha}: email vazio. Use '*'.")
        if unidade == "":
            erros.append(f"Linha {numero_linha}: codigo_unidade vazio. Use '*'.")
        if cargo == "":
            erros.append(f"Linha {numero_linha}: codigo_cargo vazio. Use '*'.")

        if cpf not in ["", "*"]:
            cpfs.setdefault(cpf, []).append(numero_linha)
        if nome not in ["", "*"]:
            nomes.setdefault(nome, []).append(numero_linha)
        if matricula not in ["", "*"]:
            matriculas.setdefault(matricula, []).append(numero_linha)
        if email not in ["", "*"]:
            emails.setdefault(email, []).append(numero_linha)

    for cpf, linhas_dup in cpfs.items():
        if len(linhas_dup) > 1:
            erros.append(f"Linhas {', '.join(map(str, linhas_dup))}: cpf '{cpf}' está duplicado.")

    for nome, linhas_dup in nomes.items():
        if len(linhas_dup) > 1:
            avisos.append(f"Linhas {', '.join(map(str, linhas_dup))}: nome '{nome}' está duplicado.")

    for matricula, linhas_dup in matriculas.items():
        if len(linhas_dup) > 1:
            avisos.append(f"Linhas {', '.join(map(str, linhas_dup))}: matricula '{matricula}' está duplicado.")

    for email, linhas_dup in emails.items():
        if len(linhas_dup) > 1:
            avisos.append(f"Linhas {', '.join(map(str, linhas_dup))}: email '{email}' está duplicado.")

    return erros, avisos

# ==============================
# VALIDAÇÃO UNIDADES
# ==============================

def validar_unidades(linhas):

    erros, avisos = [], []

    cabecalho_esperado = ["codigo_unidade", "nome_unidade", "sigla_unidade", "codigo_unidade_superior", "cpf_gestor", "cpf_avaliador_gestor"]

    erros += validar_estrutura_basica(linhas, 6, cabecalho_esperado)
    erros += validar_linhas_vazias(linhas)

    codigos, nomes, siglas = {}, {}, {}

    for numero_linha, linha in enumerate(linhas[1:], start=2):
        if all(c.strip() == "" for c in linha):
            continue
        
        for j, campo in enumerate(linha):
            if ";" in campo:
                match j:
                    case 0:
                        avisos.append(
                            f"Linha {numero_linha}: codigo_unidade contém caractere ';'."
                        )
                    case 1:
                        avisos.append(
                            f"Linha {numero_linha}: nome_unidade contém caractere ';'."
                        )
                    case 2:
                        avisos.append(
                            f"Linha {numero_linha}: sigla_unidade contém caractere ';'."
                        )
                    case 3:
                        avisos.append(
                            f"Linha {numero_linha}: codigo_unidade_superior contém caractere ';'."
                        )
                    case 4:
                        avisos.append(
                            f"Linha {numero_linha}: cpf_gestor contém caractere ';'."
                        )
                    case 5:
                        avisos.append(
                            f"Linha {numero_linha}: cpf_avaliador_gestor contém caractere ';'."
                        )

        codigo = linha[0].strip() if len(linha) > 0 else ""
        nome = linha[1].strip() if len(linha) > 1 else ""
        sigla = linha[2].strip() if len(linha) > 2 else ""
        codigo_sup = linha[3].strip() if len(linha) > 3 else ""
        cpf_gestor = linha[4].strip() if len(linha) > 4 else ""
        cpf_avaliador_gestor = linha[5].strip() if len(linha) > 5 else ""

        if codigo == "":
            erros.append(f"Linha {numero_linha}: codigo_unidade vazio. Use '*'.")
        if nome == "":
            erros.append(f"Linha {numero_linha}: nome_unidade vazio. Use '*'.")
        if sigla == "":
            erros.append(f"Linha {numero_linha}: sigla_unidade vazio. Use '*'.")
        if codigo_sup == "":
            erros.append(f"Linha {numero_linha}: codigo_unidade_superior vazio. Use '*'.")
        if cpf_gestor == "":
            erros.append(f"Linha {numero_linha}: cpf_gestor vazio. Use '*'.")
        if cpf_avaliador_gestor == "":
            erros.append(f"Linha {numero_linha}: cpf_avaliador_gestor vazio. Use '*'.")

        if codigo not in ["", "*"]:
            codigos.setdefault(codigo, []).append(numero_linha)
        if nome not in ["", "*"]:
            nomes.setdefault(nome, []).append(numero_linha)
        if sigla not in ["", "*"]:
            siglas.setdefault(sigla, []).append(numero_linha)

    for codigo, linhas_dup in codigos.items():
        if len(linhas_dup) > 1:
            erros.append(f"Linhas {', '.join(map(str, linhas_dup))}: codigo_unidade '{codigo}' está duplicado.")
    
    for nome, linhas_dup in nomes.items():
        if len(linhas_dup) > 1:
            avisos.append(f"Linhas {', '.join(map(str, linhas_dup))}: nome_unidade '{nome}' está duplicado.")
    
    for sigla, linhas_dup in siglas.items():
        if len(linhas_dup) > 1:
            avisos.append(f"Linhas {', '.join(map(str, linhas_dup))}: sigla_unidade '{sigla}' está duplicado.")

    return erros, avisos

# ==============================
# VALIDAÇÃO COMPETÊNCIAS
# ==============================

def validar_competencias(linhas):

    erros, avisos = [], []

    cabecalho_esperado = ["codigo_competencia", "nome_competencia", "descricao_competencia", "codigo_categoria", "centralidade_geral"]

    erros += validar_estrutura_basica(linhas, 5, cabecalho_esperado)
    erros += validar_linhas_vazias(linhas)

    codigos, nomes, descricoes = {}, {}, {}

    for numero_linha, linha in enumerate(linhas[1:], start=2):
        if all(c.strip() == "" for c in linha):
            continue
        
        for j, campo in enumerate(linha):
            if ";" in campo:
                match j:
                    case 0:
                        avisos.append(
                            f"Linha {numero_linha}: codigo_competencia contém caractere ';'."
                        )
                    case 1:
                        avisos.append(
                            f"Linha {numero_linha}: nome_competencia contém caractere ';'."
                        )
                    case 2:
                        avisos.append(
                            f"Linha {numero_linha}: descricao_competencia contém caractere ';'."
                        )
                    case 3:
                        avisos.append(
                            f"Linha {numero_linha}: codigo_categoria contém caractere ';'."
                        )
                    case 4:
                        avisos.append(
                            f"Linha {numero_linha}: centralidade_geral contém caractere ';'."
                        )

        codigo = linha[0].strip() if len(linha) > 0 else ""
        nome = linha[1].strip() if len(linha) > 1 else ""
        descricao = linha[2].strip() if len(linha) > 2 else ""
        categoria = linha[3].strip() if len(linha) > 3 else ""
        centralidade = linha[4].strip() if len(linha) > 4 else ""

        if codigo == "":
            erros.append(f"Linha {numero_linha}: codigo_competencia vazio. Use '*'.")
        if nome == "":
            erros.append(f"Linha {numero_linha}: nome_competencia vazio. Use '*'.")
        if descricao == "":
            erros.append(f"Linha {numero_linha}: descricao_competencia vazio. Use '*'.")
        if categoria == "":
            erros.append(f"Linha {numero_linha}: codigo_categoria vazio. Use '*'.")
        if centralidade == "":
            erros.append(f"Linha {numero_linha}: centralidade_geral vazio. Use '*'.")

        if codigo not in ["", "*"]:
            codigos.setdefault(codigo, []).append(numero_linha)
        if nome not in ["", "*"]:
            nomes.setdefault(nome, []).append(numero_linha)
        if descricao not in ["", "*"]:
            descricoes.setdefault(descricao, []).append(numero_linha)
        if centralidade not in ["", "*", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
            erros.append(f"Linha {numero_linha}: centralidade_geral '{centralidade}' inválido.")

    for codigo, linhas_dup in codigos.items():
        if len(linhas_dup) > 1:
            erros.append(f"Linhas {', '.join(map(str, linhas_dup))}: codigo_competencia '{codigo}' está duplicado.")
            
    for nome, linhas_dup in nomes.items():
        if len(linhas_dup) > 1:
            avisos.append(f"Linhas {', '.join(map(str, linhas_dup))}: nome_competencia '{nome}' está duplicado.")

    for descricao, linhas_dup in descricoes.items():
        if len(linhas_dup) > 1:
            avisos.append(f"Linhas {', '.join(map(str, linhas_dup))}: descricao_competencia '{descricao}' está duplicado.")

    return erros, avisos

# ==============================
# VALIDAÇÃO CATEGORIAS 
# ==============================

def validar_categorias(linhas):

    erros, avisos = [], []

    cabecalho_esperado = ["codigo_categoria", "nome_categoria"]

    erros += validar_estrutura_basica(linhas, 2, cabecalho_esperado)
    erros += validar_linhas_vazias(linhas)

    codigos, nomes = {}, {}

    for numero_linha, linha in enumerate(linhas[1:], start=2):
        if all(c.strip() == "" for c in linha):
            continue
        
        for j, campo in enumerate(linha):
            if ";" in campo:
                match j:
                    case 0:
                        avisos.append(
                            f"Linha {numero_linha}: codigo_categoria contém caractere ';'."
                        )
                    case 1:
                        avisos.append(
                            f"Linha {numero_linha}: nome_categoria contém caractere ';'."
                        )

        codigo = linha[0].strip() if len(linha) > 0 else ""
        nome = linha[1].strip() if len(linha) > 1 else ""

        if codigo == "":
            erros.append(f"Linha {numero_linha}: codigo_categoria vazio. Use '*'.")
        if nome == "":
            erros.append(f"Linha {numero_linha}: nome_categoria vazio. Use '*'.")

        if codigo not in ["", "*"]:
            codigos.setdefault(codigo, []).append(numero_linha)
        if nome not in ["", "*"]:
            nomes.setdefault(nome, []).append(numero_linha)

    for codigo, linhas_dup in codigos.items():
        if len(linhas_dup) > 1:
            erros.append(f"Linhas {', '.join(map(str, linhas_dup))}: codigo_categoria '{codigo}' está duplicado.")
            
    for nome, linhas_dup in nomes.items():
        if len(linhas_dup) > 1:
            avisos.append(f"Linhas {', '.join(map(str, linhas_dup))}: nome_categoria '{nome}' está duplicado.")

    return erros, avisos

# ====================================
# VALIDAÇÃO COMPETÊNCIAS POR UNIDADES
# ====================================

def validar_competencias_unidades(linhas):

    erros, avisos = [], []
    padrao = re.compile(r'^\d+(?:[,#]\d+)*$')

    cabecalho_esperado = ["codigo_unidade", "codigo_competencia", "centralidade_por_unidade", "codigo_ciclo", "objetivos"]

    erros += validar_estrutura_basica(linhas, 5, cabecalho_esperado)
    erros += validar_linhas_vazias(linhas)

    combinacoes = {}

    for numero_linha, linha in enumerate(linhas[1:], start=2):

        if all(c.strip() == "" for c in linha):
            continue
        
        for j, campo in enumerate(linha):
            if ";" in campo:
                match j:
                    case 0:
                        avisos.append(
                            f"Linha {numero_linha}: codigo_unidade contém caractere ';'."
                        )
                    case 1:
                        avisos.append(
                            f"Linha {numero_linha}: codigo_competencia contém caractere ';'."
                        )
                    case 2:
                        avisos.append(
                            f"Linha {numero_linha}: centralidade_por_unidade contém caractere ';'."
                        )
                    case 3:
                        avisos.append(
                            f"Linha {numero_linha}: codigo_ciclo contém caractere ';'."
                        )

        unidade = linha[0].strip() if len(linha) > 0 else ""
        competencia = linha[1].strip() if len(linha) > 1 else ""
        centralidade = linha[2].strip() if len(linha) > 2 else ""
        ciclo = linha[3].strip() if len(linha) > 3 else ""
        objetivos = linha[4].strip() if len(linha) > 4 else ""

        if unidade == "":
            erros.append(f"Linha {numero_linha}: codigo_categoria vazio. Use '*'.")
        if competencia == "":
            erros.append(f"Linha {numero_linha}: nome_categoria vazio. Use '*'.")
        if centralidade == "":
            erros.append(f"Linha {numero_linha}: centralidade_por_unidade vazio. Use '*'.")
        if ciclo == "":
            erros.append(f"Linha {numero_linha}: codigo_ciclo vazio. Use '*'.")
        if objetivos == "":
            erros.append(f"Linha {numero_linha}: objetivos vazio. Use '*'.")

        objetivos = str(objetivos).strip()

        if re.match(r'^\d+\.\d+$', objetivos):
            objetivos = objetivos.replace('.', ',')

        if not padrao.match(objetivos) and objetivos not in ["-"]:
            erros.append(f"Linha {numero_linha}: objetivos '{objetivos}' inválido. Use números separados por ',' ou '#' sem espaços.")

        numeros = re.split(r'[,#]', objetivos)

        if len(numeros) > 5:
            erros.append(f"Linha {numero_linha}: objetivos '{objetivos}' possui mais de 5 números.")
        if len(numeros) != len(set(numeros)):
            avisos.append(f"Linha {numero_linha}: objetivos '{objetivos}' possui números duplicados.")
            
        if unidade not in ["", "*"] and competencia not in ["", "*"]:
            chave = (unidade, competencia)
            combinacoes.setdefault(chave, []).append(numero_linha)
        if centralidade not in ["", "*", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]:
            erros.append(f"Linha {numero_linha}: centralidade_por_unidade '{centralidade}' inválido.")

    for (unidade, competencia), linhas_dup in combinacoes.items():
        if len(linhas_dup) > 1:
            erros.append(
                f"Linhas {', '.join(map(str, linhas_dup))}: "
                f"combinação codigo_unidade '{unidade}' + codigo_competencia '{competencia}' está duplicada."
            )

    return erros, avisos

# ==============================
# RELACIONAMENTOS
# ==============================

def extrair_codigos_cargos(linhas):
    codigos = set()

    for linha in linhas[1:]:
        if len(linha) > 0:
            codigo = linha[0].strip()
            if codigo not in ["", "*"]:
                codigos.add(codigo)

    return codigos

def extrair_cpfs_colaboradores(linhas):
    cpfs = set()

    for linha in linhas[1:]:
        if len(linha) > 0:
            cpf = linha[0].strip()
            if cpf not in ["", "*"]:
                cpfs.add(cpf)

    return cpfs

def extrair_codigos_unidades(linhas):
    codigos = set()

    for linha in linhas[1:]:
        if len(linha) > 0:
            codigo = linha[0].strip()
            if codigo not in ["", "*"]:
                codigos.add(codigo)

    return codigos

def extrair_codigos_competencias(linhas):
    codigos = set()

    for linha in linhas[1:]:
        if len(linha) > 0:
            codigo = linha[0].strip()
            if codigo not in ["", "*"]:
                codigos.add(codigo)

    return codigos

def extrair_codigos_categorias(linhas):
    categorias = set()

    for linha in linhas[1:]:
        if len(linha) > 0:
            categoria = linha[0].strip()
            if categoria not in ["", "*"]:
                categorias.add(categoria)

    return categorias

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

        if unidade not in["", "*"] and unidade not in codigos_unidades:
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

        if competencia not in ["","*"] and competencia not in codigos_competencias:
            erros.append(
                f"Linha {numero_linha}: codigo_competencia '{competencia}' não existe em codigo_competencia no arquivo de Competencias."
            )

    return erros

# ==============================
# INTERFACE STREAMLIT
# ==============================

st.set_page_config(page_title="Validador de Arquivos", layout="centered")
st.title("📄 Validador de Arquivos")

st.subheader("➡️ Upload do arquivo de Cargos")
arquivo_cargos = st.file_uploader(
    "Envie o arquivo de Cargos",
    type=["csv", "xls", "xlsx"],
    key="cargos"
)

st.subheader("➡️ Upload do arquivo de Colaboradores")
arquivo_colaboradores = st.file_uploader(
    "Envie o arquivo de Colaboradores",
    type=["csv", "xls", "xlsx"],
    key="colaboradores"
)

st.subheader("➡️ Upload do arquivo de Unidades")
arquivo_unidades = st.file_uploader(
    "Envie o arquivo de Unidades",
    type=["csv", "xls", "xlsx"],
    key="unidades"
)

st.subheader("➡️ Upload do arquivo de Competências")
arquivo_competencias = st.file_uploader(
    "Envie o arquivo de Competências",
    type=["csv", "xls", "xlsx"],
    key="competencias"
)

st.subheader("➡️ Upload do arquivo de Categorias")
arquivo_categorias = st.file_uploader(
    "Envie o arquivo de Categorias",
    type=["csv", "xls", "xlsx"],
    key="categorias"
)

st.subheader("➡️ Upload do arquivo de Competências por Unidade")
arquivo_competencias_unidades = st.file_uploader(
    "Envie o arquivode Competências por Unidade",
    type=["csv", "xls", "xlsx"],
    key="competenciasunidades"
)

if arquivo_cargos or arquivo_colaboradores or arquivo_unidades or arquivo_competencias or arquivo_categorias or arquivo_competencias_unidades:

    def salvar_temp(arquivo):
        extensao = os.path.splitext(arquivo.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=extensao) as temp:
            temp.write(arquivo.getbuffer())
            return temp.name

    caminho_cargos = salvar_temp(arquivo_cargos) if arquivo_cargos else None
    caminho_colaboradores = salvar_temp(arquivo_colaboradores) if arquivo_colaboradores else None
    caminho_unidades = salvar_temp(arquivo_unidades) if arquivo_unidades else None
    caminho_competencias = salvar_temp(arquivo_competencias) if arquivo_competencias else None
    caminho_categorias = salvar_temp(arquivo_categorias) if arquivo_categorias else None
    caminho_competencias_unidades = salvar_temp(arquivo_competencias_unidades) if arquivo_competencias_unidades else None

    if caminho_cargos and caminho_cargos.endswith((".xls", ".xlsx")):
        caminho_cargos = converter_excel_para_csv(caminho_cargos)

    if caminho_colaboradores and caminho_colaboradores.endswith((".xls", ".xlsx")):
        caminho_colaboradores = converter_excel_para_csv(caminho_colaboradores)

    if caminho_unidades and caminho_unidades.endswith((".xls", ".xlsx")):
        caminho_unidades = converter_excel_para_csv(caminho_unidades)

    if caminho_competencias and caminho_competencias.endswith((".xls", ".xlsx")):
        caminho_competencias = converter_excel_para_csv(caminho_competencias)

    if caminho_categorias and caminho_categorias.endswith((".xls", ".xlsx")):
        caminho_categorias = converter_excel_para_csv(caminho_categorias)

    if caminho_competencias_unidades and caminho_competencias_unidades.endswith((".xls", ".xlsx")):
        caminho_competencias_unidades = converter_excel_para_csv(caminho_competencias_unidades)

    def ler_linhas(caminho):
        encodings = ['utf-8-sig', 'latin-1', 'cp1252']
        for encoding in encodings:
            try:
                with open(caminho, 'r', encoding=encoding) as arq:
                    leitor = csv.reader(arq, delimiter=';')
                    return list(leitor)
            except UnicodeDecodeError:
                continue
        raise Exception("Não foi possível ler o arquivo. Encoding inválido.")

    linhas_cargos = ler_linhas(caminho_cargos) if caminho_cargos else None
    linhas_colaboradores = ler_linhas(caminho_colaboradores) if caminho_colaboradores else None
    linhas_unidades = ler_linhas(caminho_unidades) if caminho_unidades else None
    linhas_competencias = ler_linhas(caminho_competencias) if caminho_competencias else None
    linhas_categorias = ler_linhas(caminho_categorias) if caminho_categorias else None
    linhas_competencias_unidades = ler_linhas(caminho_competencias_unidades) if caminho_competencias_unidades else None

    codigos_cargos = extrair_codigos_cargos(linhas_cargos) if linhas_cargos else []
    codigos_unidades = extrair_codigos_unidades(linhas_unidades) if linhas_unidades else []
    cpfs_colaboradores = extrair_cpfs_colaboradores(linhas_colaboradores) if linhas_colaboradores else []
    codigos_competencias = extrair_codigos_competencias(linhas_competencias) if linhas_competencias else []
    codigos_categorias = extrair_codigos_categorias(linhas_categorias) if linhas_categorias else []

    erros_cargos, avisos_cargos = validar_cargos(linhas_cargos) if linhas_cargos else ([], [])
    erros_colaboradores, avisos_colaboradores = validar_colaboradores(linhas_colaboradores) if linhas_colaboradores else ([], [])
    erros_unidades, avisos_unidades = validar_unidades(linhas_unidades) if linhas_unidades else ([], [])
    erros_competencias, avisos_competencias = validar_competencias(linhas_competencias) if linhas_competencias else ([], [])
    erros_categorias, avisos_categorias = validar_categorias(linhas_categorias) if linhas_categorias else ([], [])
    erros_competencias_unidades, avisos_competencias_unidades = validar_competencias_unidades(linhas_competencias_unidades) if linhas_competencias_unidades else ([], [])

    erros_estrutura = (erros_cargos 
                       + erros_colaboradores 
                       + erros_unidades 
                       + erros_competencias 
                       + erros_categorias 
                       + erros_competencias_unidades)
    
    avisos = (avisos_cargos
              + avisos_colaboradores
              + avisos_unidades
              + avisos_competencias
              + avisos_categorias
              + avisos_competencias_unidades)

    erros_relacao_cargos = []
    erros_relacao_unidades_colaboradores = []
    erros_relacao_cpfs = []
    erros_autorrelacao_unidades = []
    erros_relacao_categorias = []
    erros_relacao_unidades_competencias = []
    erros_relacao_competencias = []

    if linhas_cargos and linhas_colaboradores:
        erros_relacao_cargos = validar_relacionamento_cargos(codigos_cargos, linhas_colaboradores)

    if linhas_unidades and linhas_colaboradores:
        erros_relacao_unidades_colaboradores = validar_relacionamento_unidades_colaboradores(codigos_unidades, linhas_colaboradores)
        erros_relacao_cpfs = validar_relacionamento_cpfs(cpfs_colaboradores, linhas_unidades)

    if linhas_unidades:
        erros_autorrelacao_unidades = validar_autorrelacionamento_unidades(codigos_unidades, linhas_unidades)

    if linhas_competencias and linhas_categorias:
        erros_relacao_categorias = validar_relacionamento_categorias(codigos_categorias, linhas_competencias)

    if linhas_unidades and linhas_competencias_unidades:
        erros_relacao_unidades_competencias = validar_relacionamento_unidades_competencias(codigos_unidades, linhas_competencias_unidades)

    if linhas_competencias and linhas_competencias_unidades:
        erros_relacao_competencias = validar_relacionamento_competencias(codigos_competencias, linhas_competencias_unidades)
        
    erros_relacao = (erros_relacao_cargos 
                     + erros_relacao_unidades_colaboradores 
                     + erros_relacao_cpfs 
                     + erros_autorrelacao_unidades 
                     + erros_relacao_categorias
                     + erros_relacao_unidades_competencias
                     + erros_relacao_competencias)

    total_erros = (len(erros_estrutura) + len(erros_relacao))

    if total_erros > 0:

        st.error(f"Foram encontrados {total_erros} erro(s). Veja detalhes abaixo:")

        if erros_estrutura:

            st.subheader("​❌​​ Erros de Estrutura")

            if erros_cargos:
                with st.expander(f"​🔴💼​​ Erros no arquivo de Cargos ({len(erros_cargos)})", expanded=False):
                    for erro in erros_cargos:
                        st.write("•", erro)

            if erros_colaboradores:
                with st.expander(f"🔴👥​​ Erros no arquivo de Colaboradores ({len(erros_colaboradores)})", expanded=False):
                    for erro in erros_colaboradores:
                        st.write("•", erro)

            if erros_unidades:
                with st.expander(f"​🔴🗄️ Erros no arquivo de Unidades ({len(erros_unidades)})", expanded=False):
                    for erro in erros_unidades:
                        st.write("•", erro)

            if erros_competencias:
                with st.expander(f"🔴🎯​ Erros no arquivo de Competências ({len(erros_competencias)})", expanded=False):
                    for erro in erros_competencias:
                        st.write("•", erro)

            if erros_categorias:
                with st.expander(f"​🔴📌​ Erros no arquivo de Categorias ({len(erros_categorias)})", expanded=False):
                    for erro in erros_categorias:
                        st.write("•", erro)

            if erros_competencias_unidades:
                with st.expander(f"🔴🗃️​ Erros no arquivo de Competências por Unidade ({len(erros_competencias_unidades)})", expanded=False):
                    for erro in erros_competencias_unidades:
                        st.write("•", erro)         

        if erros_relacao:

            st.subheader("​❌​ Erros de Relacionamento")

            if erros_relacao_cargos:
                with st.expander(f"🔴​​🔗​ Colaboradores → Cargos ({len(erros_relacao_cargos)})", expanded=False):
                    for erro in erros_relacao_cargos:
                        st.write("•", erro)

            if erros_relacao_unidades_colaboradores:
                with st.expander(f"🔴​​🔗​ Colaboradores → Unidades ({len(erros_relacao_unidades_colaboradores)})", expanded=False):
                    for erro in erros_relacao_unidades_colaboradores:
                        st.write("•", erro)

            if erros_relacao_cpfs:
                with st.expander(f"🔴​​🔗​ Unidades → Colaboradores ({len(erros_relacao_cpfs)})", expanded=False):
                    for erro in erros_relacao_cpfs:
                        st.write("•", erro)

            if erros_autorrelacao_unidades:
                with st.expander(f"🔴​​🔗​ Unidades (Autorrelação) ({len(erros_autorrelacao_unidades)})", expanded=False):
                    for erro in erros_autorrelacao_unidades:
                        st.write("•", erro)

            if erros_relacao_categorias:
                with st.expander(f"🔴​​🔗​ Competências → Categorias ({len(erros_relacao_categorias)})", expanded=False):
                    for erro in erros_relacao_categorias:
                        st.write("•", erro)

            if erros_relacao_unidades_competencias:
                with st.expander(f"🔴​​🔗​ Competências por Unidade → Unidades ({len(erros_relacao_unidades_competencias)})", expanded=False):
                    for erro in erros_relacao_unidades_competencias:
                        st.write("•", erro)

            if erros_relacao_competencias:
                with st.expander(f"🔴​​🔗​ Competências por Unidade → Competências ({len(erros_relacao_competencias)})", expanded=False):
                    for erro in erros_relacao_competencias:
                        st.write("•", erro)

    if len(avisos) > 0:

        st.warning(f"Foram encontrados {len(avisos)} aviso(s). Veja detalhes abaixo:")

        st.subheader("⚠️​ Avisos")

        if avisos_cargos:
            with st.expander(f"​🟡​💼​​ Avisos no arquivo de Cargos ({len(avisos_cargos)})", expanded=False):
                for aviso in avisos_cargos:
                    st.write("•", aviso)

        if avisos_colaboradores:
            with st.expander(f"​🟡👥​ Avisos no arquivo de Colaboradores ({len(avisos_colaboradores)})", expanded=False):
                for aviso in avisos_colaboradores:
                    st.write("•", aviso)

        if avisos_unidades:
            with st.expander(f"🟡🗄️ Avisos no arquivo de Unidades ({len(avisos_unidades)})", expanded=False):
                for aviso in avisos_unidades:
                    st.write("•", aviso)

        if avisos_competencias:
            with st.expander(f"🟡🎯 Avisos no aquivo de Competências ({len(avisos_competencias)})", expanded=False):
                for aviso in avisos_competencias:
                    st.write("•", aviso)

        if avisos_categorias:
            with st.expander(f"🟡📌 Avisos no arquivo de Categorias ({len(avisos_categorias)})", expanded=False):
                for aviso in avisos_categorias:
                    st.write("•", aviso)

        if avisos_competencias_unidades:
            with st.expander(f"🟡🗃️ Avisos no arquivo de Competências por Unidades ({len(avisos_competencias_unidades)})", expanded=False):
                for aviso in avisos_competencias_unidades:
                    st.write("•", aviso)

    else:
        st.success("Arquivos válidos e relacionamento consistente! ✅")
