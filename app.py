import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

DATA_DIR = Path("data")
DEFAULT_DATA_URL = "https://drive.google.com/drive/folders/1mrygqlHMjH6_Ix_q2uM429hApB1NJBav?usp=drive_link"

# Configuração da página
st.set_page_config(
    page_title="PSH - Programa de Segurança Hídrica",
    page_icon="💧",
    layout="wide"
)


@st.cache_data(show_spinner=False)
def download_data_folder(folder_url: str):
    """Baixa todos os arquivos Excel do Google Drive para a pasta local de dados."""
    import gdown

    DATA_DIR.mkdir(exist_ok=True)
    return gdown.download_folder(
        folder_url,
        output=str(DATA_DIR),
        quiet=True,
        use_cookies=False,
    )


def ensure_data_files(required_files):
    """Garante que os arquivos necessários estão disponíveis localmente."""

    DATA_DIR.mkdir(exist_ok=True)
    missing = [file for file in required_files if not (DATA_DIR / file).exists()]

    if not missing:
        return True

    folder_url = st.secrets.get("DATA_FOLDER_URL", DEFAULT_DATA_URL)
    with st.spinner("Baixando arquivos de dados (Google Drive)..."):
        try:
            download_data_folder(folder_url)
        except Exception as exc:
            st.error(
                "Não foi possível baixar os dados. Verifique o link da pasta ou a conexão de rede."
            )
            st.exception(exc)
            return False

    remaining = [file for file in required_files if not (DATA_DIR / file).exists()]
    if remaining:
        st.error(
            "Arquivos essenciais não foram encontrados após o download: "
            + ", ".join(remaining)
        )
        return False

    return True

# Função para cache de dados
@st.cache_data
def load_data(file_name):
    """Carrega dados com cache para otimização"""
    path = DATA_DIR / file_name
    if not path.exists():
        return None
    if path.exists():
        try:
            return pd.read_excel(path)
        except Exception as e:
            st.error(f"Erro ao carregar {file_name}: {e}")
            return None
    return None

def safe_sum(df, id_list, column_name):
    """Soma segura verificando se coluna existe"""
    if df is None or not id_list:
        return 0
    filtered = df[df['ID'].isin(id_list)]
    if column_name in filtered.columns:
        return filtered[column_name].sum()
    return len(filtered)  # retorna contagem se coluna não existe

def safe_plot_bar(df, id_list, group_col, value_col, title, xlabel, ylabel, 
                  orientation='v', top_n=None):
    """Cria gráfico de barras com verificação de colunas"""
    if df is None or not id_list:
        st.info("Sem dados disponíveis")
        return
    
    filtered = df[df['ID'].isin(id_list)]
    
    if group_col not in filtered.columns or value_col not in filtered.columns:
        st.warning(f"Colunas necessárias não encontradas: {group_col}, {value_col}")
        return
    
    grouped = filtered.groupby(group_col)[value_col].sum().reset_index()
    
    if top_n:
        grouped = grouped.nlargest(top_n, value_col)
    
    if len(grouped) == 0:
        st.info("Sem dados para exibir")
        return
    
    if orientation == 'h':
        fig = px.bar(grouped, x=value_col, y=group_col, orientation='h',
                    title=title, labels={group_col: xlabel, value_col: ylabel})
    else:
        fig = px.bar(grouped, x=group_col, y=value_col,
                    title=title, labels={group_col: xlabel, value_col: ylabel})
    
    st.plotly_chart(fig, use_container_width=True)

required_files = [
    "microbacias_selecionadas_otto.xlsx",
    "altimetria_otto.xlsx",
    "declividade_otto.xlsx",
    "solos_otto.xlsx",
    "caf_otto.xlsx",
    "educacao_otto.xlsx",
    "construcoes_otto.xlsx",
    "imoveiscar_otto.xlsx",
    "nascentes_otto.xlsx",
    "hidrografia_otto.xlsx",
    "sigarh_otto.xlsx",
    "uso_solo_otto.xlsx",
    "conflitosdeuso_otto.xlsx",
]

if not ensure_data_files(required_files):
    st.stop()

# Carregar tabela de microbacias (base para filtros)
microbacias = load_data("microbacias_selecionadas_otto.xlsx")

if microbacias is None:
    st.error("Arquivo microbacias_selecionadas_otto.xlsx não encontrado!")
    st.stop()

# Verificar colunas essenciais
required_cols = ['ID', 'Bacia', 'Manancial']
missing_cols = [col for col in required_cols if col not in microbacias.columns]
if missing_cols:
    st.error(f"Colunas faltando em microbacias: {missing_cols}")
    st.write("Colunas disponíveis:", list(microbacias.columns))
    st.stop()

# Header
st.title("🌊 PROGRAMA DE SEGURANÇA HÍDRICA")
st.markdown("### Painel Interativo de Diagnóstico Territorial")

# Sidebar com filtros
with st.sidebar:
    st.markdown("### 🎛️ Filtros")
    
    # Filtro de Bacia
    bacias = sorted(microbacias['Bacia'].dropna().unique())
    selected_bacia = st.multiselect("Bacia", bacias, default=bacias[:1] if bacias else [])
    
    # Filtrar microbacias baseado na bacia
    if selected_bacia:
        filtered_mb = microbacias[microbacias['Bacia'].isin(selected_bacia)]
    else:
        filtered_mb = microbacias
    
    # Filtro de Manancial
    mananciais = sorted(filtered_mb['Manancial'].dropna().unique())
    selected_manancial = st.multiselect("Manancial", mananciais)
    
    if selected_manancial:
        filtered_mb = filtered_mb[filtered_mb['Manancial'].isin(selected_manancial)]
    
    # IDs selecionados
    selected_ids = filtered_mb['ID'].tolist()
    
    st.markdown("---")
    st.info(f"**{len(selected_ids)}** microbacias selecionadas")

# Tabs principais
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Geral", 
    "🌍 Meio Físico",
    "👥 Socioeconômico",
    "💧 Outorgas",
    "🌱 Uso do Solo"
])

with tab1:
    st.markdown("### Visão Geral")
    
    # Métricas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Microbacias", len(filtered_mb))
    
    with col2:
        # Tentar diferentes nomes de coluna para área
        area_col = None
        for col_name in ['Area_ha', 'area_ha', 'AREA_HA', 'Area']:
            if col_name in filtered_mb.columns:
                area_col = col_name
                break
        
        if area_col:
            total_area = filtered_mb[area_col].sum() / 1000
            st.metric("Área (k ha)", f"{total_area:.1f}K")
        else:
            st.metric("Área", "N/D")
    
    with col3:
        nascentes_df = load_data("nascentes_otto.xlsx")
        if nascentes_df is not None and selected_ids and 'ID' in nascentes_df.columns:
            total_nascentes = nascentes_df[nascentes_df['ID'].isin(selected_ids)].shape[0]
            st.metric("Nascentes", f"{total_nascentes:,}")
        else:
            st.metric("Nascentes", "N/D")
    
    with col4:
        caf_df = load_data("caf_otto.xlsx")
        if caf_df is not None and selected_ids and 'ID' in caf_df.columns:
            caf_filtered = caf_df[caf_df['ID'].isin(selected_ids)]
            # Contar registros ao invés de somar
            total_caf = len(caf_filtered)
            st.metric("CAF", f"{total_caf:,}")
        else:
            st.metric("CAF", "N/D")
    
    # Info sobre dados
    st.markdown("### 📋 Informações")
    with st.expander("Ver detalhes das microbacias selecionadas"):
        st.dataframe(filtered_mb, use_container_width=True)

with tab2:
    st.markdown("### Análise do Meio Físico")
    
    col1, col2 = st.columns(2)
    
    with col1:
        alt_df = load_data("altimetria_otto.xlsx")
        safe_plot_bar(alt_df, selected_ids, 'ClAlt', 'area_ha',
                     'Área por Classe de Altitude',
                     'Classe de Altitude', 'Área (ha)')
    
    with col2:
        dec_df = load_data("declividade_otto.xlsx")
        safe_plot_bar(dec_df, selected_ids, 'ClDec', 'area_ha',
                     'Área por Classe de Declividade',
                     'Classe de Declividade', 'Área (ha)')
    
    # Solos
    st.markdown("### Classes de Solo")
    solo_df = load_data("solos_otto.xlsx")
    safe_plot_bar(solo_df, selected_ids, 'Cl_solos', 'area_ha',
                 'Top 10 Classes de Solo por Área',
                 'Classe de Solo', 'Área (ha)', 
                 orientation='h', top_n=10)

with tab3:
    st.markdown("### Análise Socioeconômica")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        caf_df = load_data("caf_otto.xlsx")
        if caf_df is not None and selected_ids and 'ID' in caf_df.columns:
            total_caf = len(caf_df[caf_df['ID'].isin(selected_ids)])
            st.metric("Total CAF", f"{total_caf:,}")
        else:
            st.metric("Total CAF", "N/D")
    
    with col2:
        edu_df = load_data("educacao_otto.xlsx")
        if edu_df is not None and selected_ids and 'ID' in edu_df.columns:
            total_edu = len(edu_df[edu_df['ID'].isin(selected_ids)])
            st.metric("Gestores/Escolas", total_edu)
        else:
            st.metric("Gestores/Escolas", "N/D")
    
    with col3:
        const_df = load_data("construcoes_otto.xlsx")
        if const_df is not None and selected_ids and 'ID' in const_df.columns:
            total_const = len(const_df[const_df['ID'].isin(selected_ids)])
            st.metric("Construções", f"{total_const:,}")
        else:
            st.metric("Construções", "N/D")
    
    # Imóveis por módulo rural
    st.markdown("### Imóveis Rurais (CAR)")
    imoveis_df = load_data("imoveiscar_otto.xlsx")
    
    if imoveis_df is not None and selected_ids and 'ID' in imoveis_df.columns:
        imoveis_filtered = imoveis_df[imoveis_df['ID'].isin(selected_ids)]
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'clas_mod' in imoveis_filtered.columns:
                # Tentar encontrar coluna de área
                area_cols = ['num_area', 'area_ha', 'Area_ha', 'AREA_HA']
                area_col = next((col for col in area_cols if col in imoveis_filtered.columns), None)
                
                if area_col:
                    safe_plot_bar(imoveis_df, selected_ids, 'clas_mod', area_col,
                                'Área Total por Classe de Módulo Rural',
                                'Classe', 'Área')
                else:
                    st.info("Coluna de área não encontrada")
        
        with col2:
            if 'clas_mod' in imoveis_filtered.columns:
                mod_count = imoveis_filtered['clas_mod'].value_counts().reset_index()
                mod_count.columns = ['clas_mod', 'count']
                fig = px.bar(mod_count, x='clas_mod', y='count',
                           title='Número de Imóveis por Classe',
                           labels={'clas_mod': 'Classe', 'count': 'Quantidade'})
                st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.markdown("### Outorgas de Água")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nascentes_df = load_data("nascentes_otto.xlsx")
        if nascentes_df is not None and selected_ids and 'ID' in nascentes_df.columns:
            total_nasc = len(nascentes_df[nascentes_df['ID'].isin(selected_ids)])
            st.metric("Nascentes", f"{total_nasc:,}")
        else:
            st.metric("Nascentes", "N/D")
    
    with col2:
        hidro_df = load_data("hidrografia_otto.xlsx")
        if hidro_df is not None and selected_ids and 'ID' in hidro_df.columns:
            hidro_filtered = hidro_df[hidro_df['ID'].isin(selected_ids)]
            length_cols = ['Length_km', 'length_km', 'comprimento_km', 'Comprimento']
            length_col = next((col for col in length_cols if col in hidro_filtered.columns), None)
            
            if length_col:
                total_km = hidro_filtered[length_col].sum()
                st.metric("Drenagem (km)", f"{total_km:,.1f}")
            else:
                st.metric("Drenagem (km)", "N/D")
        else:
            st.metric("Drenagem (km)", "N/D")
    
    with col3:
        # Outorgas (SIGARH)
        sigarh_df = load_data("sigarh_otto.xlsx")
        if sigarh_df is not None and selected_ids and 'ID' in sigarh_df.columns:
            total_outorgas = len(sigarh_df[sigarh_df['ID'].isin(selected_ids)])
            st.metric("Outorgas", total_outorgas)
        else:
            st.metric("Outorgas", "N/D")

with tab5:
    st.markdown("### Uso do Solo")
    
    uso_df = load_data("uso_solo_otto.xlsx")
    
    col1, col2 = st.columns(2)
    
    with col1:
        safe_plot_bar(uso_df, selected_ids, 'Classe_de_Uso_do_Solo', 'Area_ha',
                     'Área por Classe de Uso do Solo',
                     'Classe', 'Área (ha)', orientation='h')
    
    with col2:
        conf_df = load_data("conflitosdeuso_otto.xlsx")
        safe_plot_bar(conf_df, selected_ids, 'Classe_de_Uso_do_Solo', 'Area_ha',
                     'Conflitos de Uso em APP',
                     'Classe', 'Área (ha)')

# Footer
st.markdown("---")
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown("**IDR-Paraná** | Instituto de Desenvolvimento Rural do Paraná - IAPAR-EMATER")
with col2:
    if st.button("🔄 Recarregar Dados"):
        st.cache_data.clear()
        st.rerun()
