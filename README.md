# ⚡ Validador e Higienizador de Arquivos CSV (GestCom)

Aplicação robusta desenvolvida em **Python** com interface interativa em **Streamlit**, projetada para automatizar de forma inteligente a conferência, validação e higienização de arquivos estruturais no formato `.csv` separados por ponto e vírgula (`;`).

O sistema vai além de um validador convencional: ele possui um **motor de auto-correção (Self-Healing Engine)** integrado que corrige inconsistências de formatação comuns, remove sujeiras de exportações do Excel, e prepara os dados de forma transparente, deixando-os prontos para importação direta em bancos de dados ou sistemas oficiais.

---

## 🚀 Funcionalidades Principais

### ⚡ 1. Motor de Auto-Correção (Self-Healing)
* **Preenchimento de Obrigatórios:** Detecta campos obrigatórios vazios e os preenche automaticamente com o caractere curinga de negócio (`*`).
* **Sincronização de CPF/Matrícula (Colaboradores):** Associa automaticamente CPFs ausentes ou marcados com `*` à matrícula correspondente do colaborador.
* **Limpeza e Desduplicação de Objetivos:** Remove espaçamentos e desduplica itens repetidos na lista de metas do campo `objetivos` em Competências por Unidade (ex: `3,  4, 3, 5` -> `3,4,5`), preservando a ordem original.
* **Achatamento de Quebras de Linha:** Detecta quebras de linha físicas (`\n`, `\r`) ou entidades do Excel (`_x000D_`, `_x000A_`) dentro de células e as substitui por espaços simples. Isso evita o desalinhamento de linhas em importadores legados.
* **Proteção contra Delimitador Oculto:** Substitui pontos e vírgulas (`;`) inseridos em campos descritivos textuais por vírgulas (`,`), prevenindo a quebra de colunas na leitura do CSV.
* **Remoção de Duplicidades:** Exclui registros inteiramente idênticos, preservando a integridade referencial.
* **Normalização Dimensional:** Trunca colunas vazias excedentes (comuns em exportações Excel) e descarta linhas vazias no meio ou fim do arquivo de forma automática.

### 🛡️ 2. Proteções de Entrada e Interface
* **Restrição de Formato Estrita:** Apenas arquivos com extensão `.csv` são aceitos tanto na interface gráfica quanto no leitor interno de dados.
* **Validação de Delimitador Mestre:** Identifica de forma cirúrgica se o arquivo está incorretamente separado por vírgula (`,`), tabulação (`Tab`) ou espaços, exibindo uma mensagem informativa orientando o usuário a salvar o CSV com separador ponto e vírgula (`;`).

### 📊 3. Transparência e Dashboard
* **Dashboard de Auto-Correções:** Apresenta em tempo real um log interativo contendo cada correção realizada em cada linha (com referências exatas).
* **Download Imediato:** Disponibiliza para download a planilha higienizada (codificação UTF-8-SIG) pronta para o banco de dados.
* **Painel de Erros Críticos:** Destaca com precisão as inconsistências relacionais ou estruturais que não podem ser auto-corrigidas e exigem ação humana manual.

---

## 📁 Estrutura do Projeto

O projeto adota uma arquitetura limpa e modular baseada no Princípio de Responsabilidade Única (SRP):

```text
gestcom-validador/
│
├── core/
│   ├── engine.py       # Motor principal de validações e auto-correções estruturais/de negócio
│   ├── reader.py       # Conversor seguro de bytes de arquivos para matrizes Python (.csv)
│   └── schemas.py      # Definição estrita das estruturas de dados e regras por arquivo
│
├── validador.py        # Interface interativa moderna em Streamlit e lógica de visualização
├── README.md           # Documentação técnica do sistema
└── requirements.txt    # Bibliotecas de dependência
```

---

## 🛠️ Como Executar

### 1. Requisitos Prévios
Certifique-se de possuir o **Python 3.10+** instalado em sua máquina.

### 2. Instalação e Configuração

Entre na pasta do projeto e instale o Streamlit diretamente:

```bash
pip install streamlit
```
*(Nota: O arquivo `requirements.txt` é mantido na raiz do projeto apenas para facilitar deploys automatizados em nuvem, como o Streamlit Community Cloud ou Docker).*

### 3. Executando o Validador

Inicie o servidor de desenvolvimento local:

```bash
streamlit run validador.py
```

### 4. Acesso ao Sistema
Abra seu navegador favorito e acesse a URL:
```text
http://localhost:8501
```

---

## ⚙️ Esquemas de Arquivos Suportados

A aplicação valida e higieniza 6 esquemas de planilhas organizacionais:
1. **Cargos** (`codigo_cargo`, `nome_cargo`)
2. **Colaboradores** (`cpf`, `nome`, `matricula`, `email`, `codigo_unidade`, `codigo_cargo`)
3. **Unidades** (`codigo_unidade`, `nome_unidade`, `sigla_unidade`, `codigo_unidade_superior`, `cpf_gestor`, `cpf_avaliador_gestor`)
4. **Competências** (`codigo_competencia`, `nome_competencia`, `descricao_competencia`, `codigo_categoria`, `centralidade_geral`)
5. **Categorias** (`codigo_categoria`, `nome_categoria`)
6. **Competências por Unidade** (`codigo_unidade`, `codigo_competencia`, `centralidade_por_unidade`, `codigo_ciclo`, `objetivos`)
