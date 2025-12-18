# Evolução de Software 2025.2 – Cherry  
Análise de Code Smells com Modelos de Linguagem

## Visão geral
Este repositório contém os artefatos desenvolvidos para a Atividade 2 da disciplina **Evolução de Software** da Universidade Federal de Sergipe. O objetivo do projeto é analisar a evolução de code smells ao longo das releases do projeto open source **Cherry Studio**, utilizando modelos de linguagem como apoio à identificação automática de problemas estruturais no código.

A análise considera uma amostra representativa de 30% das releases do projeto, selecionadas de forma sistemática e cronológica, permitindo observar tendências de melhoria ou degradação da qualidade interna do software ao longo do tempo.

Vídeo explicativo sobre os conceitos e a abordagem utilizada:  
https://youtu.be/DcEwFfjL-Wk

## Projeto analisado
O projeto analisado é o **Cherry Studio**, um software open source voltado para produtividade e organização de conteúdos, desenvolvido com tecnologias do ecossistema web moderno.

Repositório oficial do projeto:  
https://github.com/CherryHQ/cherry-studio

## Objetivos do trabalho
- Analisar a evolução de code smells ao longo das releases do projeto Cherry  
- Comparar o comportamento de diferentes modelos de linguagem na identificação de code smells  
- Avaliar a efetividade desses modelos como ferramentas de apoio à engenharia de software  
- Discutir o impacto das decisões de design na evolução do projeto  

## Code smells considerados
A análise é baseada exclusivamente no catálogo do **Refactoring Guru**, considerando as seguintes categorias.

### Bloaters
- Long Method  
- Large Class  
- Primitive Obsession  
- Long Parameter List  
- Data Clumps  

### Object Orientation Abusers
- Alternative Classes with Different Interfaces  
- Refused Bequest  
- Switch Statements  
- Temporary Field  

### Change Preventers
- Divergent Change  
- Parallel Inheritance Hierarchies  
- Shotgun Surgery  

### Dispensables
- Comments  
- Duplicate Code  
- Data Class  
- Dead Code  
- Lazy Class  
- Speculative Generality  

### Couplers
- Feature Envy  
- Inappropriate Intimacy  
- Incomplete Library Class  
- Message Chains  
- Middle Man  

## Modelos de linguagem utilizados
Os seguintes modelos foram empregados na análise:

- microsoft/Phi-3-mini-4k-instruct  
- Qwen/Qwen2.5-0.5B-Instruct  
- Qwen/Qwen2.5-3B-Instruct  

A execução foi realizada em ambiente Google Colab com GPU Tesla T4.

## Estrutura do repositório
```bash
Evolucao_Software_2025-2_Cherry_Atividade2
│
├─ scripts
│ └─ export_releases_csv.py
│
├─ data
│ └─ arquivos CSV com todas as releases e amostra de 30%
│
├─ prompt
│ └─ code_smells_prompt.txt
│
├─ analises
│ ├─ qwen_resultados.csv
│ ├─ qwen3b_resultados.csv
│ └─ phi3_resultados.csv
│
└─ README.md
```

## Metodologia resumida
1. Coleta de todas as releases do projeto Cherry via API do GitHub  
2. Seleção de uma amostra sistemática correspondente a 30% das versões  
3. Definição de um prompt padronizado baseado no Refactoring Guru  
4. Execução da análise com diferentes modelos de linguagem  
5. Geração de resultados no formato CSV  
6. Análise comparativa e interpretação dos dados obtidos  

## Execução do script de coleta de releases

### Pré requisitos
- Python 3.10 ou superior  
- Biblioteca requests  
- Token de acesso ao GitHub configurado como variável de ambiente  

### Criação do ambiente virtual
```bash
python -m venv .venv
````

### Ativação do ambiente
Windows PowerShell
```bash
.venv\Scripts\activate
````

Linux ou macOS
```bash
source .venv/bin/activate
````

### Instalação das dependências
```bash
pip install requests
````

### Configuração do token do GitHub
Windows PowerShell
```bash
$env:GITHUB_TOKEN="SEU_TOKEN_AQUI"
````

### Execução do script
Windows PowerShell
```bash
python scripts/export_releases_csv.py CherryHQ cherry-studio 0.3
````


## Resultados
Os resultados são apresentados em arquivos CSV contendo:
- Identificação da release  
- Descrição da release  
- Categoria do code smell  
- Tipo específico do code smell  
- Justificativa baseada exclusivamente no código analisado  

Esses dados permitiram a geração de gráficos temporais, distribuição por categorias e heatmaps, evidenciando diferenças significativas entre os modelos analisados.

## Conclusão resumida
Os resultados demonstram que:
- O Microsoft Phi-3 apresentou alta sensibilidade, atuando como um auditor rigoroso  
- O Qwen-3B foi mais conservador, mas forneceu análises mais contextuais quando detectou problemas  
- Não existe um modelo único ideal, mas perfis complementares dependendo do objetivo da análise  

O estudo confirma o potencial dos modelos de linguagem como ferramentas de apoio à engenharia de software, especialmente em análises evolutivas de larga escala.

## Autores
Bruno Amancio Ferreira  
Géssica Kelly de Souza Santos  
Iago Humberto da Rosa Normandia  
Leticia da Mata Cavalcanti  
Maria Fernanda da Mota Diniz  
Pedro Henrique Gomes dos Santos  
Sâmmya Emanuelle Guimarães de Oliveira  
Wenderson Luiz Portela da Silva  

Universidade Federal de Sergipe  
Disciplina Evolução de Software  
Ano 2025

