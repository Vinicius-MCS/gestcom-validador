import csv
import io
import os
import pandas as pd

def converter_excel_para_linhas(arquivo_input):
    """
    Lê um arquivo Excel (pode ser caminho físico ou bytes/objeto Streamlit)
    e retorna uma lista de listas com os dados, tratando tudo como string.
    """
    try:
        # Lê o Excel em um DataFrame
        df = pd.read_excel(arquivo_input, dtype=str)
        # Substitui valores nulos por strings vazias e garante que tudo é string
        df = df.apply(lambda col: col.map(lambda x: str(x) if pd.notnull(x) else ""))
        
        # Converte para lista de listas, incluindo o cabeçalho
        cabecalho = df.columns.astype(str).tolist()
        linhas = [cabecalho] + df.values.tolist()
        return linhas
    except Exception as e:
        print(f"Erro ao converter Excel: {e}")
        return None

def ler_linhas_csv(conteudo_bytes):
    """
    Tenta decodificar o conteúdo em bytes com múltiplos encodings
    e lê as linhas usando o leitor de CSV.
    """
    encodings = ['utf-8-sig', 'latin-1', 'cp1252']
    for encoding in encodings:
        try:
            texto = conteudo_bytes.decode(encoding)
            # Cria um StringIO para ler como se fosse um arquivo de texto
            buffer = io.StringIO(texto)
            leitor = csv.reader(buffer, delimiter=';')
            return list(leitor)
        except (UnicodeDecodeError, TypeError):
            continue
    raise Exception("Não foi possível ler o arquivo. Encoding inválido.")

def processar_arquivo_para_linhas(arquivo):
    """
    Recebe um arquivo (pode ser o objeto UploadedFile do Streamlit ou um caminho de arquivo)
    e processa o seu conteúdo para retornar uma lista de listas.
    Apenas arquivos .csv são suportados.
    """
    if arquivo is None:
        return None

    # Se for um caminho de arquivo do sistema (string)
    if isinstance(arquivo, str):
        nome_arquivo = arquivo
        is_caminho = True
    else:
        nome_arquivo = arquivo.name
        is_caminho = False

    extensao = os.path.splitext(nome_arquivo)[1].lower()

    if extensao != ".csv":
        # Retorna uma linha especial indicando formato inválido para ser tratada pela engine de validação
        return [["ERRO_FORMATO_INVALIDO"]]

    if is_caminho:
        with open(arquivo, 'rb') as f:
            conteudo_bytes = f.read()
    else:
        conteudo_bytes = arquivo.getvalue()
    
    return ler_linhas_csv(conteudo_bytes)
