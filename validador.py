# pyrefly: ignore [missing-import]
import streamlit as st
from core.reader import processar_arquivo_para_linhas
from core.engine import (
    validar_arquivo,
    extrair_codigos_cargos,
    extrair_cpfs_colaboradores,
    extrair_codigos_unidades,
    extrair_codigos_competencias,
    extrair_codigos_categorias,
    validar_relacionamento_cargos,
    validar_relacionamento_unidades_colaboradores,
    validar_relacionamento_cpfs,
    validar_autorrelacionamento_unidades,
    validar_relacionamento_categorias,
    validar_relacionamento_unidades_competencias,
    validar_relacionamento_competencias
)

# ==========================================
# INTERFACE STREAMLIT
# ==========================================

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

# ==========================================
# PROCESSAMENTO E VALIDAÇÕES
# ==========================================

if arquivo_cargos or arquivo_colaboradores or arquivo_unidades or arquivo_competencias or arquivo_categorias or arquivo_competencias_unidades:

    # 1. Leitura e parsing dos arquivos em memória
    linhas_cargos = processar_arquivo_para_linhas(arquivo_cargos)
    linhas_colaboradores = processar_arquivo_para_linhas(arquivo_colaboradores)
    linhas_unidades = processar_arquivo_para_linhas(arquivo_unidades)
    linhas_competencias = processar_arquivo_para_linhas(arquivo_competencias)
    linhas_categorias = processar_arquivo_para_linhas(arquivo_categorias)
    linhas_competencias_unidades = processar_arquivo_para_linhas(arquivo_competencias_unidades)

    # 2. Extração de chaves/identificadores primários para integridade referencial
    codigos_cargos = extrair_codigos_cargos(linhas_cargos) if linhas_cargos else []
    codigos_unidades = extrair_codigos_unidades(linhas_unidades) if linhas_unidades else []
    cpfs_colaboradores = extrair_cpfs_colaboradores(linhas_colaboradores) if linhas_colaboradores else []
    codigos_competencias = extrair_codigos_competencias(linhas_competencias) if linhas_competencias else []
    codigos_categorias = extrair_codigos_categorias(linhas_categorias) if linhas_categorias else []

    # 3. Execução das validações de arquivo individuais baseadas nos Schemas
    erros_cargos, avisos_cargos = validar_arquivo(linhas_cargos, "cargos") if linhas_cargos else ([], [])
    erros_colaboradores, avisos_colaboradores = validar_arquivo(linhas_colaboradores, "colaboradores") if linhas_colaboradores else ([], [])
    erros_unidades, avisos_unidades = validar_arquivo(linhas_unidades, "unidades") if linhas_unidades else ([], [])
    erros_competencias, avisos_competencias = validar_arquivo(linhas_competencias, "competencias") if linhas_competencias else ([], [])
    erros_categorias, avisos_categorias = validar_arquivo(linhas_categorias, "categorias") if linhas_categorias else ([], [])
    erros_competencias_unidades, avisos_competencias_unidades = validar_arquivo(linhas_competencias_unidades, "competencias_unidades") if linhas_competencias_unidades else ([], [])

    # Consolidação de erros estruturais e avisos
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

    # 4. Execução das validações de relacionamento cruzado
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

    # ==========================================
    # APRESENTAÇÃO DOS RESULTADOS (UI)
    # ==========================================

    if total_erros > 0:
        st.error(f"Foram encontrados {total_erros} erro(s). Veja detalhes abaixo:")

        if erros_estrutura:
            st.subheader("❌ Erros de Estrutura")

            if erros_cargos:
                with st.expander(f"🔴💼 Erros no arquivo de Cargos ({len(erros_cargos)})", expanded=False):
                    for erro in erros_cargos:
                        st.write("•", erro)

            if erros_colaboradores:
                with st.expander(f"🔴👥 Erros no arquivo de Colaboradores ({len(erros_colaboradores)})", expanded=False):
                    for erro in erros_colaboradores:
                        st.write("•", erro)

            if erros_unidades:
                with st.expander(f"🔴🗄️ Erros no arquivo de Unidades ({len(erros_unidades)})", expanded=False):
                    for erro in erros_unidades:
                        st.write("•", erro)

            if erros_competencias:
                with st.expander(f"🔴🎯 Erros no arquivo de Competências ({len(erros_competencias)})", expanded=False):
                    for erro in erros_competencias:
                        st.write("•", erro)

            if erros_categorias:
                with st.expander(f"🔴📌 Erros no arquivo de Categorias ({len(erros_categorias)})", expanded=False):
                    for erro in erros_categorias:
                        st.write("•", erro)

            if erros_competencias_unidades:
                with st.expander(f"🔴🗃️ Erros no arquivo de Competências por Unidade ({len(erros_competencias_unidades)})", expanded=False):
                    for erro in erros_competencias_unidades:
                        st.write("•", erro)         

        if erros_relacao:
            st.subheader("❌ Erros de Relacionamento")

            if erros_relacao_cargos:
                with st.expander(f"🔴🔗 Colaboradores → Cargos ({len(erros_relacao_cargos)})", expanded=False):
                    for erro in erros_relacao_cargos:
                        st.write("•", erro)

            if erros_relacao_unidades_colaboradores:
                with st.expander(f"🔴🔗 Colaboradores → Unidades ({len(erros_relacao_unidades_colaboradores)})", expanded=False):
                    for erro in erros_relacao_unidades_colaboradores:
                        st.write("•", erro)

            if erros_relacao_cpfs:
                with st.expander(f"🔴🔗 Unidades → Colaboradores ({len(erros_relacao_cpfs)})", expanded=False):
                    for erro in erros_relacao_cpfs:
                        st.write("•", erro)

            if erros_autorrelacao_unidades:
                with st.expander(f"🔴🔗 Unidades (Autorrelação) ({len(erros_autorrelacao_unidades)})", expanded=False):
                    for erro in erros_autorrelacao_unidades:
                        st.write("•", erro)

            if erros_relacao_categorias:
                with st.expander(f"🔴🔗 Competências → Categorias ({len(erros_relacao_categorias)})", expanded=False):
                    for erro in erros_relacao_categorias:
                        st.write("•", erro)

            if erros_relacao_unidades_competencias:
                with st.expander(f"🔴🔗 Competências por Unidade → Unidades ({len(erros_relacao_unidades_competencias)})", expanded=False):
                    for erro in erros_relacao_unidades_competencias:
                        st.write("•", erro)

            if erros_relacao_competencias:
                with st.expander(f"🔴🔗 Competências por Unidade → Competências ({len(erros_relacao_competencias)})", expanded=False):
                    for erro in erros_relacao_competencias:
                        st.write("•", erro)

    if len(avisos) > 0:
        st.warning(f"Foram encontrados {len(avisos)} aviso(s). Veja detalhes abaixo:")
        st.subheader("⚠️ Avisos")

        if avisos_cargos:
            with st.expander(f"🟡💼 Avisos no arquivo de Cargos ({len(avisos_cargos)})", expanded=False):
                for aviso in avisos_cargos:
                    st.write("•", aviso)

        if avisos_colaboradores:
            with st.expander(f"🟡👥 Avisos no arquivo de Colaboradores ({len(avisos_colaboradores)})", expanded=False):
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

    if total_erros == 0 and len(avisos) == 0:
        st.success("Arquivos válidos e relacionamento consistente! ✅")
