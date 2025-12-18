"""
AL Drones - Flight Area Analysis Tool
"""

import streamlit as st
import os
import tempfile
from pathlib import Path
import geopandas as gpd
import pandas as pd

# Import from src folder
from src import generate_safety_margins as gsm
from src import population_analysis as pa


# Page configuration
st.set_page_config(
    page_title="AL Drones - Flight Area Analysis Tool",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with AL Drones branding
st.markdown("""
<style>
    /* Hide Streamlit header elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
      
    /* Hide sidebar toggle button */
    [data-testid="collapsedControl"] {display: none;}
    
    /* Hide "Made with Streamlit" footer */
    footer {visibility: hidden;}
    footer:after {
        content:''; 
        visibility: visible;
        display: block;
        position: relative;
        padding: 5px;
        top: 2px;
    }
    
    /* Hide "Created by" link in bottom right (keep "Hosted by") */
    a[href*="~"] {display: none !important;}
    .viewerBadge_container__r5tak {display: none !important;}
    .styles_viewerBadge__CiemY {display: none !important;}
    
    /* AL Drones Color Palette */
    :root {
        --aldrones-teal: #054750;
        --aldrones-dark: #1a1a1a;
        --aldrones-yellow: #E0AB25;
        --aldrones-light-teal: #0a6b7a;
    }
    
    /* Main background */
    .stApp {
        background: #000000;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #054750 0%, #0D0B54 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0rem;
        border-left: 5px solid #E0AB25;
        box-shadow: 0 4px 12px rgba(13, 11, 84, 0.5);
    }
    
    .main-header h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0rem;
    }
    
    .main-header p {
        color: #e0f7fa;
        font-size: 1rem;
        margin: 0;
    }
    
    /* Card styling */
    .info-card {
        background: rgba(5, 71, 80, 0.1);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(5, 71, 80, 0.3);
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    
    .info-card h3 {
        color: #E0AB25;
        margin-top: 0;
    }
    
    .info-card p, .info-card ul {
        color: #e0e0e0;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #054750 0%, #0a6b7a 100%);
        color: #ffffff;
        font-weight: 600;
        border: 2px solid transparent;
        padding: 0.75rem 2rem;
        border-radius: 5px;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #0a6b7a 0%, #E0AB25 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(224, 171, 37, 0.4);
        border-color: #E0AB25;
    }
    
    /* Small edit buttons */
    button[kind="secondary"] {
        padding: 0.3rem 0.8rem !important;
        font-size: 0.85rem !important;
        min-height: 2rem !important;
        background: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: #ffffff !important;
        margin-top: 0.25rem !important;
    }
    
    button[kind="secondary"]:hover {
        background: rgba(224, 171, 37, 0.2) !important;
        border-color: #E0AB25 !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    /* Align completed step with button */
    .completed-step {
        display: flex;
        align-items: center;
    }
    
    /* Input fields */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 2px solid #054750 !important;
        border-radius: 5px;
    }
    
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus {
        border-color: #E0AB25 !important;
        box-shadow: 0 0 0 2px rgba(224, 171, 37, 0.2) !important;
    }
    
    /* Input labels */
    .stTextInput>label,
    .stNumberInput>label,
    .stSelectbox>label {
        color: #E0AB25 !important;
        font-weight: 600;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background-color: #1a1a1a;
        border: 2px dashed #054750;
        border-radius: 8px;
        padding: 1rem;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #E0AB25;
        background-color: rgba(5, 71, 80, 0.1);
    }
    
    .uploadedFile {
        background: rgba(5, 71, 80, 0.2);
        border: 2px solid #054750;
        border-radius: 5px;
    }
    
    /* Success messages */
    .stSuccess {
        background: rgba(224, 171, 37, 0.1);
        border-left: 4px solid #E0AB25;
        color: #E0AB25;
    }
    
    /* Info messages */
    .stInfo {
        background: rgba(5, 71, 80, 0.2);
        border-left: 4px solid #054750;
        color: #e0f7fa;
    }
    
    /* Warning messages */
    .stWarning {
        background: rgba(255, 152, 0, 0.1);
        border-left: 4px solid #ff9800;
        color: #ffb74d;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, #054750 0%, #E0AB25 100%);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(5, 71, 80, 0.1);
        border-radius: 5px;
        color: #E0AB25;
        border: 1px solid #054750;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(5, 71, 80, 0.2);
        border-color: #E0AB25;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #E0AB25;
        font-size: 2rem;
    }
    
    [data-testid="stMetricLabel"] {
        color: #e0e0e0;
    }
    
    /* Tables */
    .dataframe {
        background: rgba(5, 71, 80, 0.1);
        color: #e0e0e0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #888888;
        border-top: 1px solid rgba(5, 71, 80, 0.3);
        margin-top: 3rem;
    }
    
    .footer a {
        color: #E0AB25;
        text-decoration: none;
        transition: color 0.3s;
    }
    
    .footer a:hover {
        color: #054750;
    }
    
    /* Steps indicator */
    .step-indicator {
        background: rgba(5, 71, 80, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border-left: 3px solid #E0AB25;
        margin: 1rem 0;
        font-weight: 600;
        color: #E0AB25;
    }
    
    /* Completed step badge */
    .completed-step {
        background: rgba(224, 171, 37, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border-left: 3px solid #E0AB25;
        margin: 0.5rem 0;
        color: #E0AB25;
        font-size: 0.9rem;
    }

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Section headers */
    h3 {
        color: #E0AB25 !important;
    }
    
    h4 {
        color: #0a6b7a !important;
    }
    
</style>
""", unsafe_allow_html=True)


def create_header():
    """Create application header with logos."""
    st.markdown("""
    <div class="main-header">
        <div style="display: flex; justify-content: center; align-items: center; gap: 3rem; margin-bottom: 2rem;">
            <img src="https://aldrones.com.br/wp-content/uploads/2021/01/Logo-branca-2.png" 
                 alt="AL Drones Logo" 
                 style="height: 70px; object-fit: contain;">
            <div style="width: 2px; height: 100px; background: linear-gradient(to bottom, transparent, rgba(255,255,255,0.4), transparent);"></div>
            <img src="https://adtechsd.com.br/wp-content/uploads/2023/03/logo-adtech-mbr-b-2048x780.png" 
                 alt="ADTECH Logo" 
                 style="height: 70px; object-fit: contain;">
        </div>
        <h1 style="text-align: center;">Análise da Área de Voo para o Harpia</h1>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Main application."""
    # Header
    create_header()
    
    # Initialize session state for steps
    if 'current_step' not in st.session_state:
        st.session_state['current_step'] = 1
    if 'kml_uploaded' not in st.session_state:
        st.session_state['kml_uploaded'] = False
    if 'parameters_set' not in st.session_state:
        st.session_state['parameters_set'] = False
    
    # Main content
    st.markdown("""
    <div class="info-card">
        <h3>Como usar</h3>
        <p>Faça upload de um arquivo KML contendo a geometria do voo (linha ou polígono). 
        A ferramenta irá automaticamente:</p>
        <ul>
            <li>Gerar polígonos com as margens de segurança aplicáveis</li>
            <li>Analisar a densidade populacional na área de interesse utilizando os dados do IBGE 2022</li>
            <li>Gerar mapas e estatísticas detalhadas</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # STEP 1: Upload KML
    if st.session_state['current_step'] >= 1:
        if st.session_state['kml_uploaded']:
            # Show completed step with edit option
            col1, col2 = st.columns([8, 1])
            with col1:
                st.markdown(f"""
                <div class="completed-step">
                    ✓ Etapa 1 concluída: KML carregado ({st.session_state.get('kml_filename', 'arquivo.kml')})
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("✏️", key="edit_step1", type="secondary", help="Editar KML"):
                    st.session_state['kml_uploaded'] = False
                    st.session_state['current_step'] = 1
                    st.rerun()
        else:
            st.markdown("### 📤 Etapa 1: Upload do KML")
            uploaded_file = st.file_uploader(
                "Selecione o arquivo KML de entrada",
                type=['kml'],
                key='kml_input',
                on_change=lambda: st.session_state.pop('analysis_results', None)
            )
            
            if uploaded_file:
                st.session_state['uploaded_file'] = uploaded_file
                st.session_state['kml_filename'] = uploaded_file.name
                
                if st.button("➡️ Próximo: Configurar Parâmetros", type="primary"):
                    st.session_state['kml_uploaded'] = True
                    st.session_state['current_step'] = 2
                    st.rerun()
    
    # STEP 2: Configure Parameters
    if st.session_state['current_step'] >= 2 and st.session_state['kml_uploaded']:
        if st.session_state['parameters_set']:
            # Show completed step with edit option
            col1, col2 = st.columns([8, 1])
            with col1:
                st.markdown(f"""
                <div class="completed-step">
                    ✓ Etapa 2 concluída: Parâmetros configurados (Altura: {st.session_state.get('height', 0)}m, CV: {st.session_state.get('cv_size', 0)}m)
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("✏️", key="edit_step2", type="secondary", help="Editar parâmetros"):
                    st.session_state['parameters_set'] = False
                    st.session_state['current_step'] = 2
                    if 'analysis_results' in st.session_state:
                        del st.session_state['analysis_results']
                    st.rerun()
        else:
            st.markdown("### ⚙️ Etapa 2: Configuração dos Parâmetros")
            
            # Read geometry to check type
            uploaded_file = st.session_state.get('uploaded_file')
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.kml') as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name
                
                gdf_check = gpd.read_file(tmp_path, driver='KML')
                geom_types = gdf_check.geometry.type.unique()
                has_polygon = any(g in ['Polygon', 'MultiPolygon'] for g in geom_types)
                has_point_or_line = any(g in ['Point', 'LineString', 'MultiPoint', 'MultiLineString'] for g in geom_types)
                
                os.unlink(tmp_path)
                
            except Exception as e:
                st.error(f"Erro ao ler KML: {str(e)}")
                has_polygon = False
                has_point_or_line = True
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Parâmetros de Voo")
                
                if has_point_or_line and not has_polygon:
                    fg_size = st.number_input(
                        "Flight Geography Buffer (m)",
                        min_value=0.0,
                        value=50.0,
                        step=10.0,
                        help="Buffer para criar a área de voo a partir do ponto/linha"
                    )
                else:
                    fg_size = 0.0
                    st.info("📍 Geometria detectada: Polígono (Flight Geography já definido)")
                
                height = st.number_input(
                    "Altura de Voo (m)",
                    min_value=0.0,
                    value=100.0,
                    step=10.0,
                    help="Altura de voo em metros"
                )
            
            with col2:
                st.markdown("#### Parâmetros de Buffer")
                cv_size = st.number_input(
                    "Contingency Volume (m)",
                    min_value=0.0,
                    value=50.0,
                    step=10.0,
                    help="Tamanho do volume de contingência"
                )
                
                corner_style = st.selectbox(
                    "Estilo de Cantos",
                    options=['square', 'rounded'],
                    index=0,
                    help="Estilo dos cantos dos buffers"
                )
            
            grb_preview = gsm.calculate_grb_size(height)
            st.info(f"Ground Risk Buffer: {grb_preview:.2f} m | Adjacent Area: 5000m")
            
            if st.button("🚀 Iniciar Análise", type="primary"):
                # Store parameters
                st.session_state['fg_size'] = fg_size
                st.session_state['height'] = height
                st.session_state['cv_size'] = cv_size
                st.session_state['corner_style'] = corner_style
                st.session_state['parameters_set'] = True
                st.session_state['current_step'] = 3
                st.rerun()
    
    # STEP 3: Run Analysis
    if st.session_state['current_step'] >= 3 and st.session_state['parameters_set']:
        if 'analysis_results' not in st.session_state:
            st.markdown("### 📊 Etapa 3: Processamento")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                uploaded_file = st.session_state.get('uploaded_file')
                fg_size = st.session_state.get('fg_size')
                height = st.session_state.get('height')
                cv_size = st.session_state.get('cv_size')
                corner_style = st.session_state.get('corner_style')
                
                # ETAPA 1: Gerar Margens de Segurança
                status_text.markdown('<div class="step-indicator">📍 Gerando margens de segurança...</div>', unsafe_allow_html=True)
                progress_bar.progress(10)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.kml') as tmp_input:
                    tmp_input.write(uploaded_file.getvalue())
                    tmp_input_path = tmp_input.name
                
                output_dir = tempfile.mkdtemp()
                safety_kml_path = os.path.join(output_dir, 'safety_margins.kml')
                
                result_path = gsm.generate_safety_margins(
                    input_kml_path=tmp_input_path,
                    output_kml_path=safety_kml_path,
                    fg_size=fg_size,
                    height=height,
                    cv_size=cv_size,
                    corner_style=corner_style
                )
                
                progress_bar.progress(30)
                
                with open(result_path, 'rb') as f:
                    kml_data = f.read()
                
                # ETAPA 2: Análise Populacional
                status_text.markdown('<div class="step-indicator">📊 Analisando densidade populacional...</div>', unsafe_allow_html=True)
                progress_bar.progress(40)
                
                analysis_output_dir = os.path.join(output_dir, 'analysis_results')
                os.makedirs(analysis_output_dir, exist_ok=True)
                
                results = pa.analyze_population(result_path, analysis_output_dir)
                
                progress_bar.progress(100)
                status_text.empty()
                
                if results:
                    st.session_state['analysis_results'] = {
                        'stats': results,
                        'output_dir': analysis_output_dir,
                        'kml_data': kml_data
                    }
                    st.rerun()
                else:
                    st.warning("⚠️ Nenhum resultado foi gerado.")
                
                if os.path.exists(tmp_input_path):
                    os.unlink(tmp_input_path)
            
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"❌ Erro durante o processamento: {str(e)}")
                import traceback
                with st.expander("Ver detalhes do erro"):
                    st.code(traceback.format_exc())
        
        # Display results if they exist
        if 'analysis_results' in st.session_state:
            results = st.session_state['analysis_results']['stats']
            analysis_output_dir = st.session_state['analysis_results']['output_dir']
            kml_data = st.session_state['analysis_results']['kml_data']
            
            st.success("✅ Análise concluída com sucesso!")
            
            st.markdown("---")
            st.markdown("## 📈 Resultados da Análise")
            
            # Get GRB average density for Flight Geography metric
            grb_densidade_media = results.get('Ground Risk Buffer', {}).get('densidade_media', 0)
            grb_num_cells_above_5 = results.get('Ground Risk Buffer', {}).get('num_cells_above_5', 0)
            
            # Create metrics with updated logic
            col1, col2, col3 = st.columns(3)
            
            # METRIC 1: Flight Geography - Show GRB average density
            with col1:
                densidade = grb_densidade_media
                
                if densidade < 1:
                    st.markdown(f"""
                    <div style="background: rgba(0, 255, 0, 0.05); padding: 1rem; border-radius: 5px; border-left: 4px solid #00ff00;">
                        <p style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0;">Flight Geography</p>
                        <p style="color: #00ff00; font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">
                            ✓ {densidade:.2f} <span style="color: #66ff66; font-size: 1.2rem; font-weight: 600;">hab/km²</span>
                        </p>
                        <p style="color: #aaa; font-size: 0.8rem; margin: 0;">Densidade Média no GRB</p>
                        <p style="color: #66ff66; font-size: 0.85rem; margin-top: 0.5rem;">Área Inóspita Confirmada</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: rgba(255, 152, 0, 0.1); padding: 1rem; border-radius: 5px; border-left: 4px solid #ff9800;">
                        <p style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0;">Flight Geography</p>
                        <p style="color: #ff9800; font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">
                            ⚠️ {densidade:.2f} <span style="color: #ffb74d; font-size: 1.2rem; font-weight: 600;">hab/km²</span>
                        </p>
                        <p style="color: #aaa; font-size: 0.8rem; margin: 0;">Densidade Média no GRB</p>
                        <p style="color: #ffb74d; font-size: 0.85rem; margin-top: 0.5rem;">Não caracteriza área inóspita</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # METRIC 2: Ground Risk Buffer - Show number of cells > 5 hab/km²
            with col2:
                num_cells = grb_num_cells_above_5
                
                if num_cells == 0:
                    st.markdown(f"""
                    <div style="background: rgba(0, 255, 0, 0.05); padding: 1rem; border-radius: 5px; border-left: 4px solid #00ff00;">
                        <p style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0;">Ground Risk Buffer</p>
                        <p style="color: #00ff00; font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">
                            ✓ {num_cells} <span style="color: #66ff66; font-size: 1.2rem; font-weight: 600;">células</span>
                        </p>
                        <p style="color: #aaa; font-size: 0.8rem; margin: 0;">Células > 5 hab/km²</p>
                        <p style="color: #66ff66; font-size: 0.85rem; margin-top: 0.5rem;">Nenhuma área crítica</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: rgba(255, 0, 0, 0.1); padding: 1rem; border-radius: 5px; border-left: 4px solid #ff0000;">
                        <p style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0;">Ground Risk Buffer</p>
                        <p style="color: #ff0000; font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">
                            ⚠️ {num_cells} <span style="color: #ff6666; font-size: 1.2rem; font-weight: 600;">células</span>
                        </p>
                        <p style="color: #aaa; font-size: 0.8rem; margin: 0;">Células > 5 hab/km²</p>
                        <p style="color: #ff6666; font-size: 0.85rem; margin-top: 0.5rem;">Atenção Necessária</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # METRIC 3: Adjacent Area - Keep as is
            with col3:
                if 'Adjacent Area' in results:
                    densidade = results['Adjacent Area']['densidade_media']
                    threshold = 50
                    
                    if densidade > threshold:
                        st.markdown(f"""
                        <div style="background: rgba(255, 0, 0, 0.1); padding: 1rem; border-radius: 5px; border-left: 4px solid #ff0000;">
                            <p style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0;">Adjacent Area</p>
                            <p style="color: #ff0000; font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">
                                ⚠️ {densidade:.1f} <span style="color: #ff6666; font-size: 1.2rem; font-weight: 600;">hab/km²</span>
                            </p>
                            <p style="color: #aaa; font-size: 0.8rem; margin: 0;">Densidade Média</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: rgba(0, 255, 0, 0.05); padding: 1rem; border-radius: 5px; border-left: 4px solid #00ff00;">
                            <p style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0;">Adjacent Area</p>
                            <p style="color: #00ff00; font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">
                                ✓ {densidade:.1f} <span style="color: #66ff66; font-size: 1.2rem; font-weight: 600;">hab/km²</span>
                            </p>
                            <p style="color: #aaa; font-size: 0.8rem; margin: 0;">Densidade Média</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Warning note if cells > 5 hab/km² exist
            if grb_num_cells_above_5 > 0:
                st.markdown("---")
                st.warning(f"""
                ⚠️ **ATENÇÃO - Planejamento de Trajetória Necessário**
                
                Foram identificadas **{grb_num_cells_above_5} célula(s)** no Ground Risk Buffer com densidade populacional superior a 5 hab/km².
                
                **Ações Requeridas:**
                - A trajetória de voo deve ser planejada para evitar sobrevoar essas áreas de maior densidade
                - É necessária a criação de **No Fly Zones** sobre as células identificadas
                - Consulte a tabela detalhada abaixo para localizar as células críticas
                """)

            # Tabela Detalhada de Células do GRB
            if 'Ground Risk Buffer' in results and 'detailed_cells' in results['Ground Risk Buffer']:
                detailed_cells = results['Ground Risk Buffer']['detailed_cells']

                if not detailed_cells.empty:
                    st.markdown("---")
                    st.markdown("## 📋 Células do Ground Risk Buffer")

                    # Estatísticas rápidas
                    total_cells = len(detailed_cells)
                    cells_above_5 = len(detailed_cells[detailed_cells['Densidade_hab_km2'] > 5])
                    cells_above_0 = len(detailed_cells[detailed_cells['Densidade_hab_km2'] > 0])

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total de Células", f"{total_cells}")
                    with col2:
                        st.metric("Células > 0 hab/km²", f"{cells_above_0}")
                    with col3:
                        st.metric("Células > 5 hab/km²", f"{cells_above_5}", 
                                 delta="Críticas" if cells_above_5 > 0 else None,
                                 delta_color="inverse")

                    st.markdown("---")

                    # Filtros
                    st.markdown("### 🔍 Filtrar Células")
                    col1, col2 = st.columns(2)

                    with col1:
                        densidade_filter = st.selectbox(
                            "Filtrar por densidade",
                            options=["Todas as células", "Somente > 0 hab/km²", "Somente > 5 hab/km²"],
                            index=1
                        )

                    with col2:
                        sort_option = st.selectbox(
                            "Ordenar por",
                            options=["Densidade (maior → menor)", "Densidade (menor → maior)", 
                                    "População (maior → menor)", "População (menor → maior)"],
                            index=0
                        )

                    # Aplicar filtros
                    filtered_cells = detailed_cells.copy()

                    if densidade_filter == "Somente > 0 hab/km²":
                        filtered_cells = filtered_cells[filtered_cells['Densidade_hab_km2'] > 0]
                    elif densidade_filter == "Somente > 5 hab/km²":
                        filtered_cells = filtered_cells[filtered_cells['Densidade_hab_km2'] > 5]

                    # Aplicar ordenação
                    if sort_option == "Densidade (maior → menor)":
                        filtered_cells = filtered_cells.sort_values('Densidade_hab_km2', ascending=False)
                    elif sort_option == "Densidade (menor → maior)":
                        filtered_cells = filtered_cells.sort_values('Densidade_hab_km2', ascending=True)
                    elif sort_option == "População (maior → menor)":
                        filtered_cells = filtered_cells.sort_values('Populacao', ascending=False)
                    elif sort_option == "População (menor → maior)":
                        filtered_cells = filtered_cells.sort_values('Populacao', ascending=True)

                    # Formatar a tabela para exibição
                    display_df = filtered_cells.copy()
                    display_df['Densidade_hab_km2'] = display_df['Densidade_hab_km2'].round(2)
                    display_df['Area_km2'] = display_df['Area_km2'].round(4)
                    display_df['Latitude'] = display_df['Latitude'].round(6)
                    display_df['Longitude'] = display_df['Longitude'].round(6)
                    display_df['Populacao'] = display_df['Populacao'].astype(int)

                    # Renomear colunas para português
                    display_df = display_df.rename(columns={
                        'ID_Celula': 'ID Célula',
                        'Populacao': 'População',
                        'Area_km2': 'Área (km²)',
                        'Densidade_hab_km2': 'Densidade (hab/km²)',
                        'Latitude': 'Latitude',
                        'Longitude': 'Longitude'
                    })

                    st.markdown(f"### 📊 Tabela de Células ({len(filtered_cells)} registros)")

                    # Adicionar destaque visual para células críticas
                    def highlight_critical(row):
                        if row['Densidade (hab/km²)'] > 5:
                            return ['background-color: rgba(255, 0, 0, 0.15)'] * len(row)
                        return [''] * len(row)

                    styled_df = display_df.style.apply(highlight_critical, axis=1)
                    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=400)

                    # Legenda
                    st.markdown("""
                    <div style="background: rgba(255, 0, 0, 0.15); padding: 0.5rem; border-radius: 5px; margin-top: 0.5rem;">
                        <small>🔴 Células destacadas em vermelho possuem densidade > 5 hab/km² (área crítica)</small>
                    </div>
                    """, unsafe_allow_html=True)

                    # Botão de download do CSV
                    st.markdown("---")
                    st.markdown("### 📥 Download dos Dados das Células")

                    col1, col2, col3 = st.columns([1, 1, 2])

                    with col1:
                        # Download CSV completo
                        csv_completo = detailed_cells.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download Todas as Células (CSV)",
                            data=csv_completo,
                            file_name='celulas_grb_completo.csv',
                            mime='text/csv',
                            use_container_width=True,
                            help="Baixar todas as células do GRB"
                        )

                    with col2:
                        # Download CSV apenas células > 5
                        if cells_above_5 > 0:
                            cells_critical = detailed_cells[detailed_cells['Densidade_hab_km2'] > 5]
                            csv_critical = cells_critical.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Download Células Críticas (CSV)",
                                data=csv_critical,
                                file_name='celulas_grb_criticas.csv',
                                mime='text/csv',
                                use_container_width=True,
                                help="Baixar apenas células com densidade > 5 hab/km²"
                            )
                        else:
                            st.button(
                                label="📥 Download Células Críticas (CSV)",
                                disabled=True,
                                use_container_width=True,
                                help="Nenhuma célula crítica encontrada"
                            )

                    with col3:
                        st.info(f"💡 **Dica:** Use as coordenadas para criar No Fly Zones no planejamento de voo")

