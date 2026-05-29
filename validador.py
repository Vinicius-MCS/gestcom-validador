# pyrefly: ignore [missing-import]
import streamlit as st
import io
import csv
from core.reader import processar_arquivo_para_linhas
from core.engine import (
    validar_arquivo,
    corrigir_e_validar_arquivo,
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

# Helper function to convert list of lists to CSV bytes
def converter_para_csv_bytes(linhas):
    if not linhas:
        return b""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerows(linhas)
    return output.getvalue().encode('utf-8-sig')


# ==========================================
# INTERFACE STREAMLIT
# ==========================================

st.set_page_config(page_title="Validador de Arquivos", layout="centered")
st.title("📄 Validador de Arquivos")

st.subheader("➡️ Upload do arquivo de Cargos")
arquivo_cargos = st.file_uploader(
    "Envie o arquivo de Cargos (apenas .csv separado por ';')",
    type=["csv"],
    key="cargos"
)

st.subheader("➡️ Upload do arquivo de Colaboradores")
arquivo_colaboradores = st.file_uploader(
    "Envie o arquivo de Colaboradores (apenas .csv separado por ';')",
    type=["csv"],
    key="colaboradores"
)

st.subheader("➡️ Upload do arquivo de Unidades")
arquivo_unidades = st.file_uploader(
    "Envie o arquivo de Unidades (apenas .csv separado por ';')",
    type=["csv"],
    key="unidades"
)

st.subheader("➡️ Upload do arquivo de Competências")
arquivo_competencias = st.file_uploader(
    "Envie o arquivo de Competências (apenas .csv separado por ';')",
    type=["csv"],
    key="competencias"
)

st.subheader("➡️ Upload do arquivo de Categorias")
arquivo_categorias = st.file_uploader(
    "Envie o arquivo de Categorias (apenas .csv separado por ';')",
    type=["csv"],
    key="categorias"
)

st.subheader("➡️ Upload do arquivo de Competências por Unidade")
arquivo_competencias_unidades = st.file_uploader(
    "Envie o arquivo de Competências por Unidade (apenas .csv separado por ';')",
    type=["csv"],
    key="competenciasunidades"
)

# ==========================================
# PROCESSAMENTO E VALIDAÇÕES
# ==========================================

if arquivo_cargos or arquivo_colaboradores or arquivo_unidades or arquivo_competencias or arquivo_categorias or arquivo_competencias_unidades:

    # 1. Leitura e parsing dos arquivos em memória
    linhas_cargos_brutas = processar_arquivo_para_linhas(arquivo_cargos)
    linhas_colaboradores_brutas = processar_arquivo_para_linhas(arquivo_colaboradores)
    linhas_unidades_brutas = processar_arquivo_para_linhas(arquivo_unidades)
    linhas_competencias_brutas = processar_arquivo_para_linhas(arquivo_competencias)
    linhas_categorias_brutas = processar_arquivo_para_linhas(arquivo_categorias)
    linhas_competencias_unidades_brutas = processar_arquivo_para_linhas(arquivo_competencias_unidades)

    # 2. Execução da auto-correção e validação individual
    linhas_cargos, erros_cargos, avisos_cargos, correcoes_cargos = (
        corrigir_e_validar_arquivo(linhas_cargos_brutas, "cargos") if linhas_cargos_brutas else (None, [], [], [])
    )
    linhas_colaboradores, erros_colaboradores, avisos_colaboradores, correcoes_colaboradores = (
        corrigir_e_validar_arquivo(linhas_colaboradores_brutas, "colaboradores") if linhas_colaboradores_brutas else (None, [], [], [])
    )
    linhas_unidades, erros_unidades, avisos_unidades, correcoes_unidades = (
        corrigir_e_validar_arquivo(linhas_unidades_brutas, "unidades") if linhas_unidades_brutas else (None, [], [], [])
    )
    linhas_competencias, erros_competencias, avisos_competencias, correcoes_competencias = (
        corrigir_e_validar_arquivo(linhas_competencias_brutas, "competencias") if linhas_competencias_brutas else (None, [], [], [])
    )
    linhas_categorias, erros_categorias, avisos_categorias, correcoes_categorias = (
        corrigir_e_validar_arquivo(linhas_categorias_brutas, "categorias") if linhas_categorias_brutas else (None, [], [], [])
    )
    linhas_competencias_unidades, erros_competencias_unidades, avisos_competencias_unidades, correcoes_competencias_unidades = (
        corrigir_e_validar_arquivo(linhas_competencias_unidades_brutas, "competencias_unidades") if linhas_competencias_unidades_brutas else (None, [], [], [])
    )

    # 3. Extração de chaves/identificadores primários a partir dos dados limpos
    codigos_cargos = extrair_codigos_cargos(linhas_cargos) if linhas_cargos else []
    codigos_unidades = extrair_codigos_unidades(linhas_unidades) if linhas_unidades else []
    cpfs_colaboradores = extrair_cpfs_colaboradores(linhas_colaboradores) if linhas_colaboradores else []
    codigos_competencias = extrair_codigos_competencias(linhas_competencias) if linhas_competencias else []
    codigos_categorias = extrair_codigos_categorias(linhas_categorias) if linhas_categorias else []

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

    # Seção 1: Log de Auto-correções realizadas
    correcoes_totais = []
    if correcoes_cargos:
        correcoes_totais.append(("Cargos 💼", correcoes_cargos))
    if correcoes_colaboradores:
        correcoes_totais.append(("Colaboradores 👥", correcoes_colaboradores))
    if correcoes_unidades:
        correcoes_totais.append(("Unidades 🗄️", correcoes_unidades))
    if correcoes_competencias:
        correcoes_totais.append(("Competências 🎯", correcoes_competencias))
    if correcoes_categorias:
        correcoes_totais.append(("Categorias 📌", correcoes_categorias))
    if correcoes_competencias_unidades:
        correcoes_totais.append(("Competências por Unidade 🗃️", correcoes_competencias_unidades))

    if any(corrs for _, corrs in correcoes_totais):
        st.subheader("⚡ Auto-Correções Realizadas")
        st.success("O motor limpou e ajustou inconsistências de digitação e formatação automaticamente!")
        for titulo, corrs in correcoes_totais:
            if corrs:
                with st.expander(f"📝 {titulo} ({len(corrs)} correções)", expanded=False):
                    for corr in corrs:
                        st.write("•", corr)

    # Seção 2: Grid de Download dos Arquivos Higienizados
    arquivos_enviados = []
    if arquivo_cargos and linhas_cargos:
        arquivos_enviados.append(("💼 Cargos", linhas_cargos, "cargos_higienizado.csv"))
    if arquivo_colaboradores and linhas_colaboradores:
        arquivos_enviados.append(("👥 Colaboradores", linhas_colaboradores, "colaboradores_higienizado.csv"))
    if arquivo_unidades and linhas_unidades:
        arquivos_enviados.append(("🗄️ Unidades", linhas_unidades, "unidades_higienizado.csv"))
    if arquivo_competencias and linhas_competencias:
        arquivos_enviados.append(("🎯 Competências", linhas_competencias, "competencias_higienizado.csv"))
    if arquivo_categorias and linhas_categorias:
        arquivos_enviados.append(("📌 Categorias", linhas_categorias, "categorias_higienizado.csv"))
    if arquivo_competencias_unidades and linhas_competencias_unidades:
        arquivos_enviados.append(("🗃️ Comp. Unidades", linhas_competencias_unidades, "competencias_unidades_higienizado.csv"))

    if arquivos_enviados:
        st.subheader("📥 Download dos Arquivos Higienizados")
        st.info("Baixe abaixo as versões limpas e prontas para importação no banco de dados:")
        
        # Exibe em colunas de até 3 botões por linha
        for i in range(0, len(arquivos_enviados), 3):
            cols = st.columns(min(3, len(arquivos_enviados) - i))
            for idx, (nome, dados, filename) in enumerate(arquivos_enviados[i:i+3]):
                with cols[idx]:
                    st.download_button(
                        label=f"Baixar {nome}",
                        data=converter_para_csv_bytes(dados),
                        file_name=filename,
                        mime="text/csv",
                        key=f"dl_{filename}"
                    )

    # Seção 3: Exibição dos Erros Críticos que Persistem
    if total_erros > 0:
        st.subheader("❌ Erros Críticos Restantes")
        st.error(f"Atenção: Foram encontrados {total_erros} erro(s) crítico(s) que não puderam ser corrigidos automaticamente. Eles exigem ação manual:")

        if erros_estrutura:
            st.markdown("#### Erros Estruturais")

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
            st.markdown("#### Erros de Relacionamento (Integridade Referencial)")

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

    # Seção 4: Avisos
    if len(avisos) > 0:
        st.subheader("⚠️ Avisos")
        st.warning(f"Foram encontrados {len(avisos)} aviso(s) que merecem atenção:")

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
            with st.expander(f"🟡🎯 Avisos no arquivo de Competências ({len(avisos_competencias)})", expanded=False):
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
