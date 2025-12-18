import sys
import os
import tempfile
from pathlib import Path

# Verifica se Streamlit está disponível
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    print("Streamlit não encontrado. Executando em modo CONSOLE.")
    print("Para interface web: pip install streamlit")
    print()

import geopandas as gpd
import pandas as pd
from src import generatesafetymargins as gsm
from src import populationanalysis as pa

# CSS Customizado (apenas para Streamlit)
if STREAMLIT_AVAILABLE:
    CSS = """
    <style>
    /* Hide Streamlit header elements */
    #MainMenu {visibility: hidden;}
    .header {visibility: hidden;}
    .footer {visibility: hidden;}
    .stDeployButton {display: none;}
    [data-testid="collapsedControl"] {display: none;}
    
    /* AL Drones Color Palette */
    :root {
        --aldrones-teal: #054750;
        --aldrones-dark: #1a1a1a;
        --aldrones-yellow: #E0AB25;
        --aldrones-light-teal: #0a6b7a;
    }
    
    /* Main background */
    .stApp { background: #000000; }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(90deg, #054750 0%, #0D0B54 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0rem;
        border-left: 5px solid #E0AB25;
        box-shadow: 0 4px 12px rgba(13, 11, 84, 0.5);
    }
    .main-header h1 { color: #ffffff; font-size: 2rem; font-weight: 700; margin-bottom: 0rem; }
    .main-header p { color: #e0f7fa; font-size: 1rem; margin: 0; }
    
    /* Card styling */
    .info-card {
        background: rgba(5, 71, 80, 0.1);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid rgba(5, 71, 80, 0.3);
        margin: 1rem 0;
        backdrop-filter: blur(10px);
    }
    .info-card h3 { color: #E0AB25; margin-top: 0; }
    .info-card p, .info-card ul { color: #e0e0e0; }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #054750 0%, #0a6b7a 100%);
        color: #ffffff;
        font-weight: 600;
        border: 2px solid transparent;
        padding: 0.75rem 2rem;
        border-radius: 5px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
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
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 2px solid #054750 !important;
        border-radius: 5px;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #E0AB25 !important;
        box-shadow: 0 0 0 2px rgba(224, 171, 37, 0.2) !important;
    }
    
    /* Input labels */
    .stTextInput label, .stNumberInput label, .stSelectbox label {
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
    
    /* Completed step */
    .completed-step {
        display: flex;
        align-items: center;
        background: rgba(224, 171, 37, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border-left: 3px solid #E0AB25;
        margin: 0.5rem 0;
        color: #E0AB25;
        font-size: 0.9rem;
    }
    
    /* Step indicator */
    .step-indicator {
        background: rgba(5, 71, 80, 0.2);
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border-left: 3px solid #E0AB25;
        margin: 1rem 0;
        font-weight: 600;
        color: #E0AB25;
    }
    
    /* Block container */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    /* Section headers */
    h3 { color: #E0AB25 !important; }
    h4 { color: #0a6b7a !important; }
    </style>
    """
    
    def create_header():
        st.markdown("""
        <div class="main-header">
            <div style="display: flex; justify-content: center; align-items: center; gap: 3rem; margin-bottom: 2rem;">
                <img src="https://aldrones.com.br/wp-content/uploads/2021/01/Logo-branca-2.png" alt="AL Drones Logo" style="height: 70px; object-fit: contain;">
                <div style="width: 2px; height: 100px; background: linear-gradient(to bottom, transparent, rgba(255,255,255,0.4), transparent);"></div>
                <img src="https://adtechsd.com.br/wp-content/uploads/2023/03/logo-adtech-mbr-b-2048x780.png" alt="ADTECH Logo" style="height: 70px; object-fit: contain;">
                <div>
                    <h1 style="text-align: center;">Análise da área de Voo para o Harpiah</h1>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def console_mode():
    """Modo console quando Streamlit não está disponível"""
    print("=" * 70)
    print("🚁 AL DRONES - Flight Area Analysis Tool 🚁")
    print("=" * 70)
    print("MODO CONSOLE (Streamlit não instalado)")
    print()
    
    # Solicita arquivo KML
    kml_path = input("📁 Digite o caminho completo do arquivo KML: ").strip().strip('"')
    if not os.path.exists(kml_path):
        print(f"❌ Arquivo não encontrado: {kml_path}")
        input("\nPressione Enter para sair...")
        return
    
    print("\n⚙️  Configurações (pressione Enter para usar padrão):")
    try:
        fg_size = float(input("   Flight Geography Buffer (m) [50]: ") or 50)
        height = float(input("   Altura de voo (m) [100]: ") or 100)
        cv_size = float(input("   Contingency Volume (m) [50]: ") or 50)
        corner_style = input("   Estilo de cantos (square/rounded) [square]: ").lower() or "square"
    except ValueError:
        print("❌ Valores inválidos. Usando padrões.")
        fg_size, height, cv_size, corner_style = 50, 100, 50, "square"
    
    print("\n🚀 Iniciando análise...")
    try:
        output_dir = tempfile.mkdtemp()
        safety_kml_path = os.path.join(output_dir, "safetymargins.kml")
        
        print("📊 1/2 Gerando margens de segurança...")
        gsm.generatesafetymargins(kml_path, safety_kml_path, fg_size, height, cv_size, corner_style)
        
        print("👥 2/2 Analisando densidade populacional...")
        analysis_output_dir = os.path.join(output_dir, "analysis_results")
        os.makedirs(analysis_output_dir, exist_ok=True)
        results = pa.analyzepopulation(safety_kml_path, analysis_output_dir)
        
        print("\n✅ ANÁLISE CONCLUÍDA COM SUCESSO!")
        print("-" * 50)
        fg_density = results.get('Flight Geography', {}).get('densidademedia', 0)
        grb_density = results.get('Ground Risk Buffer', {}).get('densidademedia', 0)
        grb_cells = results.get('Ground Risk Buffer', {}).get('numcellsabove5', 0)
        
        print(f"✈️  Flight Geography: {fg_density:.2f} hab/km²")
        print(f"⚠️  Ground Risk Buffer: {grb_density:.2f} hab/km²")
        print(f"🔴 Células > 5 hab/km²: {grb_cells}")
        
        if grb_cells > 0:
            print(f"\n⚠️  ATENÇÃO: Planejamento de trajetória necessário!")
        
        print(f"\n📁 Mapas salvos em: {analysis_output_dir}")
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ Erro durante processamento: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPressione Enter para sair...")

def streamlit_mode():
    """Modo Streamlit (código original completo)"""
    st.set_page_config(
        page_title="AL Drones - Flight Area Analysis Tool",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.markdown(CSS, unsafe_allow_html=True)
    create_header()
    
    # Inicialização session state
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    if 'kml_uploaded' not in st.session_state:
        st.session_state.kml_uploaded = False
    if 'parameters_set' not in st.session_state:
        st.session_state.parameters_set = False
    
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
    
    # ETAPA 1: Upload KML
    if st.session_state.current_step == 1:
        if st.session_state.kml_uploaded:
            col1, col2 = st.columns([8, 1])
            with col1:
                st.markdown(f"""
                <div class="completed-step">
                    ✅ Etapa 1 concluída - KML carregado: {st.session_state.get('kml_filename', 'arquivo.kml')}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("✏️", key="edit_step1", type="secondary", help="Editar KML"):
                    st.session_state.kml_uploaded = False
                    st.session_state.current_step = 1
                    st.rerun()
        else:
            st.markdown("### Etapa 1: Upload do KML")
            uploaded_file = st.file_uploader("Selecione o arquivo KML de entrada", type="kml", key="kml_input",
                                           on_change=lambda: st.session_state.pop('analysis_results', None))
            
            if uploaded_file:
                st.session_state.uploaded_file = uploaded_file
                st.session_state.kml_filename = uploaded_file.name
                
                if st.button("Próximo: Configurar Parâmetros", type="primary"):
                    st.session_state.kml_uploaded = True
                    st.session_state.current_step = 2
                    st.rerun()
    
    # ETAPA 2: Configurar Parâmetros
    if st.session_state.current_step == 2 and st.session_state.kml_uploaded:
        if st.session_state.parameters_set:
            col1, col2 = st.columns([8, 1])
            with col1:
                st.markdown(f"""
                <div class="completed-step">
                    ✅ Etapa 2 concluída - Parâmetros configurados<br>
                    Altura: {st.session_state.get('height', 0)}m, CV: {st.session_state.get('cv_size', 0)}m
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("✏️", key="edit_step2", type="secondary", help="Editar parâmetros"):
                    st.session_state.parameters_set = False
                    st.session_state.current_step = 2
                    if 'analysis_results' in st.session_state:
                        del st.session_state.analysis_results
                    st.rerun()
        else:
            st.markdown("### Etapa 2: Configuração dos Parâmetros")
            uploaded_file = st.session_state.get('uploaded_file')
            
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".kml") as tmp:
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
                st.markdown("**Parâmetros de Voo**")
                if has_point_or_line and not has_polygon:
                    fg_size = st.number_input("Flight Geography Buffer (m)", min_value=0.0, value=50.0, step=10.0,
                                            help="Buffer para criar a área de voo a partir do ponto/linha")
                else:
                    fg_size = 0.0
                    st.info("Geometria detectada: Polígono (Flight Geography já definido)")
                
                height = st.number_input("Altura de Voo (m)", min_value=0.0, value=100.0, step=10.0,
                                       help="Altura de voo em metros")
            
            with col2:
                st.markdown("**Parâmetros de Buffer**")
                cv_size = st.number_input("Contingency Volume (m)", min_value=0.0, value=50.0, step=10.0,
                                        help="Tamanho do volume de contingência")
                corner_style = st.selectbox("Estilo de Cantos", options=["square", "rounded"], index=0,
                                          help="Estilo dos cantos dos buffers")
                
                grb_preview = gsm.calculategrbsize(height)
                st.info(f"Ground Risk Buffer: {grb_preview:.2f}m | Adjacent Area: 5000m")
            
            if st.button("🚀 Iniciar Análise", type="primary"):
                st.session_state.fg_size = fg_size
                st.session_state.height = height
                st.session_state.cv_size = cv_size
                st.session_state.corner_style = corner_style
                st.session_state.parameters_set = True
                st.session_state.current_step = 3
                st.rerun()
    
    # ETAPA 3: Processamento
    if st.session_state.current_step == 3 and st.session_state.parameters_set:
        if 'analysis_results' not in st.session_state:
            st.markdown("### Etapa 3: Processamento")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                uploaded_file = st.session_state.get('uploaded_file')
                fg_size = st.session_state.get('fg_size')
                height = st.session_state.get('height')
                cv_size = st.session_state.get('cv_size')
                corner_style = st.session_state.get('corner_style')
                
                status_text.markdown('<div class="step-indicator">Gerando margens de segurança...</div>', unsafe_allow_html=True)
                progress_bar.progress(10)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".kml") as tmp_input:
                    tmp_input.write(uploaded_file.getvalue())
                    tmp_input_path = tmp_input.name
                
                output_dir = tempfile.mkdtemp()
                safety_kml_path = os.path.join(output_dir, "safetymargins.kml")
                gsm.generatesafetymargins(input_kml_path=tmp_input_path, output_kml_path=safety_kml_path,
                                        fg_size=fg_size, height=height, cv_size=cv_size, corner_style=corner_style)
                progress_bar.progress(30)
                
                with open(safety_kml_path, 'rb') as f:
                    kml_data = f.read()
                
                status_text.markdown('<div class="step-indicator">Analisando densidade populacional...</div>', unsafe_allow_html=True)
                progress_bar.progress(40)
                
                analysis_output_dir = os.path.join(output_dir, "analysis_results")
                os.makedirs(analysis_output_dir, exist_ok=True)
                results = pa.analyzepopulation(safety_kml_path, analysis_output_dir)
                progress_bar.progress(100)
                status_text.empty()
                
                if results:
                    st.session_state.analysis_results = {
                        'stats': results,
                        'output_dir': analysis_output_dir,
                        'kml_data': kml_data
                    }
                    st.rerun()
                else:
                    st.warning("Nenhum resultado foi gerado.")
                
                if os.path.exists(tmp_input_path):
                    os.unlink(tmp_input_path)
                    
            except Exception as e:
                progress_bar.empty()
                status_text.empty()
                st.error(f"Erro durante o processamento: {str(e)}")
                import traceback
                with st.expander("Ver detalhes do erro"):
                    st.code(traceback.format_exc())
        
        # Resultados
        if 'analysis_results' in st.session_state:
            results = st.session_state.analysis_results['stats']
            analysis_output_dir = st.session_state.analysis_results['output_dir']
            kml_data = st.session_state.analysis_results['kml_data']
            
            st.success("✅ Análise concluída com sucesso!")
            st.markdown("---")
            st.markdown("### Resultados da Análise")
            
            grb_densidade_media = results.get('Ground Risk Buffer', {}).get('densidademedia', 0)
            grb_num_cells_above5 = results.get('Ground Risk Buffer', {}).get('numcellsabove5', 0)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                densidade = grb_densidade_media
                if densidade <= 1:
                    st.markdown(f"""
                    <div style="background: rgba(0, 255, 0, 0.05); padding: 1rem; border-radius: 5px; border-left: 4px solid #00ff00;">
                        <p style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0;">Flight Geography</p>
                        <p style="color: #00ff00; font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">{densidade:.2f}<span style="color: #66ff66; font-size: 1.2rem; font-weight: 600;">hab/km²</span></p>
                        <p style="color: #aaa; font-size: 0.8rem; margin: 0;">Densidade Média no GRB</p>
                        <p style="color: #66ff66; font-size: 0.85rem; margin-top: 0.5rem;">Área Inabitada Confirmada</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: rgba(255, 152, 0, 0.1); padding: 1rem; border-radius: 5px; border-left: 4px solid #ff9800;">
                        <p style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0;">Flight Geography</p>
                        <p style="color: #ff9800; font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">{densidade:.2f}<span style="color: #ffb74d; font-size: 1.2rem; font-weight: 600;">hab/km²</span></p>
                        <p style="color: #aaa; font-size: 0.8rem; margin: 0;">Densidade Média no GRB</p>
                        <p style="color: #ffb74d; font-size: 0.85rem; margin-top: 0.5rem;">Não caracteriza área inabitada</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col2:
                num_cells = grb_num_cells_above5
                if num_cells == 0:
                    st.markdown(f"""
                    <div style="background: rgba(0, 255, 0, 0.05); padding: 1rem; border-radius: 5px; border-left: 4px solid #00ff00;">
                        <p style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0;">Ground Risk Buffer</p>
                        <p style="color: #00ff00; font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">{num_cells}<span style="color: #66ff66; font-size: 1.2rem; font-weight: 600;">células</span></p>
                        <p style="color: #aaa; font-size: 0.8rem; margin: 0;">Células > 5 hab/km²</p>
                        <p style="color: #66ff66; font-size: 0.85rem; margin-top: 0.5rem;">Nenhuma área crítica</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: rgba(255, 0, 0, 0.1); padding: 1rem; border-radius: 5px; border-left: 4px solid #ff0000;">
                        <p style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0;">Ground Risk Buffer</p>
                        <p style="color: #ff0000; font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">{num_cells}<span style="color: #ff6666; font-size: 1.2rem; font-weight: 600;">células</span></p>
                        <p style="color: #aaa; font-size: 0.8rem; margin: 0;">Células > 5 hab/km²</p>
                        <p style="color: #ff6666; font-size: 0.85rem; margin-top: 0.5rem;">Atenção Necessária</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                if 'Adjacent Area' in results:
                    densidade = results['Adjacent Area']['densidademedia']
                    threshold = 50
                    if densidade > threshold:
                        st.markdown(f"""
                        <div style="background: rgba(255, 0, 0, 0.1); padding: 1rem; border-radius: 5px; border-left: 4px solid #ff0000;">
                            <p style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0;">Adjacent Area</p>
                            <p style="color: #ff0000; font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">{densidade:.1f}<span style="color: #ff6666; font-size: 1.2rem; font-weight: 600;">hab/km²</span></p>
                            <p style="color: #aaa; font-size: 0.8rem; margin: 0;">Densidade Média</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: rgba(0, 255, 0, 0.05); padding: 1rem; border-radius: 5px; border-left: 4px solid #00ff00;">
                            <p style="color: #ffffff; font-size: 1.1rem; font-weight: 600; margin: 0;">Adjacent Area</p>
                            <p style="color: #00ff00; font-size: 2.5rem; font-weight: bold; margin: 0.5rem 0;">{densidade:.1f}<span style="color: #66ff66; font-size: 1.2rem; font-weight: 600;">hab/km²</span></p>
                            <p style="color: #aaa; font-size: 0.8rem; margin: 0;">Densidade Média</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            if grb_num_cells_above5 > 0:
                st.markdown("---")
                st.warning(f"""
                ⚠️ **ATENÇÃO** - Planejamento de Trajetória Necessário
                
                Foram identificadas **{grb_num_cells_above5}** células no Ground Risk Buffer com densidade 
                populacional superior a **5 hab/km²**.
                
                **Ações Requeridas:**
                - A trajetória de voo deve ser planejada para **evitar sobrevoar** essas áreas de maior densidade
                - Necessária a criação de **No Fly Zones** sobre as células identificadas
                - Consulte a tabela detalhada abaixo para localizar as células críticas
                """)

def main():
    if not STREAMLIT_AVAILABLE:
        console_mode()
    else:
        streamlit_mode()

if __name__ == "__main__":
    main()
