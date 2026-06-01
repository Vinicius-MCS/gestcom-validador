import csv
import io
import os

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
