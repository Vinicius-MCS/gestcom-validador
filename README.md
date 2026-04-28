# Validador de Arquivos

Aplicação desenvolvida em Python com interface em Streamlit, criada para automatizar a conferência de arquivos `.csv`, `.xls` ou `.xlsx` utilizados em processos internos.
O sistema realiza verificações estruturais e de conteúdo, identificando erros e avisos, permitindo corrigir inconsistências antes do uso dos arquivos em sistemas oficiais ou bases de dados.

## Objetivo - Garantir que os dados estejam:
- No formato correto  
- Com cabeçalhos padronizados  
- Sem campos obrigatórios vazios  
- Sem duplicidades indevidas  
- Com relacionamentos válidos entre arquivos  
- Dentro das regras de negócio definidas  

## Como Executar

### 1. Clone ou baixe o projeto

```bash
git clone https://github.com/camilapenha/gestcom-validador/
cd validador
```

### 2. Instale as dependências

```bash
pip install streamlit pandas
```

### 3. Execute a aplicação

```bash
streamlit run validador.py
```

### 4. Acesse no navegador

```text
http://localhost:8501
```

---

## Estrutura do Projeto

```text
validador/
│── validador.py
│── README.md
│── requirements.txt
```

