# 🌊 BI - Programa de Segurança Hídrica do Paraná

Painel interativo de diagnóstico territorial para o Programa de Segurança Hídrica do Paraná (PSH).

## 📋 Sobre

O Programa de Segurança Hídrica do Paraná (PSH) é uma iniciativa do Governo do Estado, coordenada pela Secretaria de Estado do Planejamento (SEPL), com participação de diversos órgãos estaduais.

Este aplicativo BI permite visualizar e analisar dados territoriais de microbacias selecionadas, incluindo:

- **Meio Físico**: Altimetria, declividade, solos
- **Socioeconômico**: CAF, educação, construções, imóveis rurais
- **Outorgas de Água**: Nascentes, hidrografia, vazões
- **Uso do Solo**: Classes de uso e conflitos em APP
- **Pecuária**: Bovinos, suínos, bubalinos, aves

## 🚀 Como Usar

### Instalação

```bash
pip install -r requirements.txt
```

### Executar

```bash
streamlit run app.py
```

## 📊 Estrutura de Dados

O aplicativo utiliza a tabela `microbacias_selecionadas_otto.xlsx` como base para os filtros, usando as seguintes chaves:

- **ID**: Identificador único da microbacia
- **Bacia**: Bacia hidrográfica
- **Manancial**: Nome do manancial
- **Nº Manancial**: Número do manancial
- **Nome Manancial**: Nome completo do manancial

Todas as outras tabelas usam a coluna **ID** como chave de relacionamento.

## 📁 Arquivos de Dados

Os dados são baixados automaticamente da pasta do Google Drive: `https://drive.google.com/drive/folders/1mrygqlHMjH6_Ix_q2uM429hApB1NJBav?usp=drive_link`.

Para ambientes onde o link precise ser alterado, defina `DATA_FOLDER_URL` em `st.secrets` para apontar para outra pasta pública do Google Drive.

Os arquivos ficam organizados localmente na pasta `data/` com os seguintes nomes:

- `microbacias_selecionadas_otto.xlsx` - Tabela base com filtros
- `altimetria_otto.xlsx` - Classes de altitude
- `declividade_otto.xlsx` - Classes de declividade
- `solos_otto.xlsx` - Classes de solo
- `caf_otto.xlsx` - Cadastro Ambiental Florestal
- `educacao_otto.xlsx` - Gestores e escolaridade
- `construcoes_otto.xlsx` - Edificações
- `imoveiscar_otto.xlsx` - Imóveis rurais (CAR)
- `nascentes_otto.xlsx` - Nascentes
- `hidrografia_otto.xlsx` - Rede hidrográfica
- `uso_solo_otto.xlsx` - Uso e cobertura do solo
- `conflitosdeuso_otto.xlsx` - Conflitos em APP
- `bovinos_otto.xlsx` - Rebanho bovino
- `suínos_otto.xlsx` - Rebanho suíno
- `bubalinos_otto.xlsx` - Rebanho bubalino
- `aves_otto.xlsx` - Criação de aves
- `agrotóxicos_otto.xlsx` - Aplicações de agrotóxicos

## 🎯 Funcionalidades

- **Filtros dinâmicos**: Por bacia e manancial
- **Visualizações interativas**: Gráficos Plotly responsivos
- **Abas organizadas**: Conteúdo dividido por tema
- **Cache otimizado**: Carregamento rápido dos dados
- **Layout responsivo**: Adaptável a diferentes telas

## 🛠️ Tecnologias

- **Streamlit**: Framework para aplicações web
- **Pandas**: Manipulação de dados
- **Plotly**: Visualizações interativas
- **OpenPyXL**: Leitura de arquivos Excel

## 📝 Notas

- O aplicativo foi otimizado para performance
- Os dados são carregados com cache para evitar reprocessamento
- Apenas os top 10 itens são exibidos em alguns gráficos para clareza visual

## 🏢 Instituições

**IDR-Paraná** - Instituto de Desenvolvimento Rural do Paraná - IAPAR-EMATER

**Governo do Estado do Paraná**
- Secretaria de Estado do Planejamento (SEPL)
- Secretaria da Agricultura e do Abastecimento (SEAB)
- Secretaria do Desenvolvimento Sustentável (SEDEST)
- Instituto Água e Terra (IAT)
- Agência de Defesa Agropecuária do Paraná (ADAPAR)
