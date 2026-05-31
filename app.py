import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os
import datetime
from fpdf import FPDF

st.set_page_config(
    page_title="JaguarYou — Fauna Silvestre",
    page_icon="🐆",
    layout="wide"
)

# ─── CSS global ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer    {visibility: hidden;}

/* Fondo general oscuro */
.stApp { background-color: #0D1117; }
.block-container { padding-top: 1.5rem; }

/* Hero banner */
.hero {
    background: linear-gradient(135deg, #0D1117 0%, #0f2a1a 60%, #0D1117 100%);
    border: 1px solid #F0A500;
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 16px;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    color: #F0A500;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
.hero-sub {
    font-size: 1.05rem;
    color: #8B949E;
    margin: 0;
}

/* Antes / Ahora */
.ba-grid { display: flex; gap: 12px; margin-top: 20px; }
.ba-card {
    flex: 1;
    border-radius: 10px;
    padding: 14px 18px;
    font-size: 0.92rem;
}
.ba-before {
    background: rgba(244,67,54,0.08);
    border: 1px solid rgba(244,67,54,0.4);
    color: #EF9A9A;
}
.ba-after {
    background: rgba(240,165,0,0.08);
    border: 1px solid rgba(240,165,0,0.5);
    color: #FFF9E6;
}
.ba-label {
    font-weight: 700;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
    opacity: 0.85;
}

/* Paso numerado */
.step {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 20px 0 8px 0;
}
.step-num {
    background: #F0A500;
    color: #000;
    width: 28px; height: 28px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.85rem;
    flex-shrink: 0;
}
.step-text {
    font-weight: 600;
    font-size: 1rem;
    color: #E6EDF3;
}

/* Tarjeta de detección */
.det-card {
    background: #161B22;
    border: 1px solid #30363D;
    border-left: 4px solid #F0A500;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 4px;
}
.det-especie {
    font-size: 1.3rem;
    font-weight: 800;
    color: #F0A500;
    margin: 0 0 4px 0;
}
.det-meta {
    font-size: 0.85rem;
    color: #8B949E;
    margin: 3px 0;
}
.conf-wrap { margin-top: 12px; }
.conf-label {
    font-size: 0.8rem;
    color: #8B949E;
    margin-bottom: 5px;
    font-weight: 600;
}
.conf-bar-bg {
    background: #21262D;
    border-radius: 6px;
    height: 10px;
    overflow: hidden;
}
.conf-bar-fill.low  { height:10px; border-radius:6px; background: linear-gradient(90deg,#E63946,#FF6B6B); }
.conf-bar-fill.mid  { height:10px; border-radius:6px; background: linear-gradient(90deg,#F77F00,#FCBF49); }
.conf-bar-fill.high { height:10px; border-radius:6px; background: linear-gradient(90deg,#2D6A4F,#52B788); }

/* KPI cards */
.kpi-row { display: flex; gap: 14px; margin: 16px 0; }
.kpi-card {
    flex: 1;
    background: #161B22;
    border: 1px solid #30363D;
    border-top: 4px solid #F0A500;
    border-radius: 12px;
    padding: 20px 16px;
    text-align: center;
}
.kpi-val {
    font-size: 2.4rem;
    font-weight: 800;
    color: #F0A500;
    line-height: 1;
}
.kpi-lbl {
    font-size: 0.78rem;
    color: #8B949E;
    margin-top: 6px;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    font-weight: 600;
}

/* Sección header */
.sec-header {
    font-size: 1.1rem;
    font-weight: 700;
    color: #E6EDF3;
    border-left: 4px solid #F0A500;
    padding-left: 10px;
    margin: 24px 0 12px 0;
}

.golden-line {
    height: 1px;
    background: linear-gradient(90deg, #F0A500, transparent);
    border: none;
    margin: 20px 0;
}

/* Tabs */
[data-baseweb="tab-list"] {
    background-color: #0D1117 !important;
    gap: 4px;
}
[data-baseweb="tab"] {
    color: #8B949E !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    background-color: transparent !important;
}
[data-baseweb="tab"]:hover {
    color: #F0A500 !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: #F0A500 !important;
}
[data-baseweb="tab-highlight"] {
    background-color: #F0A500 !important;
}
[data-baseweb="tab-border"] {
    background-color: #30363D !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Datos base de sesión ───────────────────────────────────────────────────
if "resultados" not in st.session_state:
    st.session_state["resultados"] = []
if "estacion_actual" not in st.session_state:
    st.session_state["estacion_actual"] = "Cámara Trampa #04 - Zona Norte (Llanos)"

# ─── Constantes del dominio ─────────────────────────────────────────────────
DATOS_HISTORICOS = [
    {"Fecha": "12/05/2026", "Estacion": "Cámara Trampa #04 - Zona Norte (Llanos)", "Especie": "Capibara",                "Confianza": 87.3},
    {"Fecha": "12/05/2026", "Estacion": "Cámara Trampa #04 - Zona Norte (Llanos)", "Especie": "Ocelote",                 "Confianza": 91.2},
    {"Fecha": "14/05/2026", "Estacion": "Cámara Trampa #12 - Sector Chaco",        "Especie": "Urina",                   "Confianza": 78.5},
    {"Fecha": "14/05/2026", "Estacion": "Cámara Trampa #12 - Sector Chaco",        "Especie": "Jochi Calucha",           "Confianza": 76.8},
    {"Fecha": "15/05/2026", "Estacion": "Cámara Trampa #09 - Rio de la Fauna",     "Especie": "Tapir",                   "Confianza": 83.1},
    {"Fecha": "15/05/2026", "Estacion": "Cámara Trampa #09 - Rio de la Fauna",     "Especie": "Zorro",                   "Confianza": 79.4},
    {"Fecha": "16/05/2026", "Estacion": "Cámara Trampa #04 - Zona Norte (Llanos)", "Especie": "Falso Positivo (Viento)", "Confianza":  0.0},
]

MAPEO_FAUNA = {
    "bird":     "Jaguar",
    "cat":      "Jaguar / Puma",
    "dog":      "Jaguar",
    "elephant": "Tapir",
    "zebra":    "Capibara",
    "pig":      "Jochi Calucha",
    "cow":      "Guaso",
    "sheep":    "Urina",
    "horse":    "Teitetu",
    "bear":     "Oso Hormiguero",
    "monkey":   "Mono Martin",
}

LISTA_ESPECIES = [
    "Jaguar", "Jaguar / Puma", "Ocelote", "Gato Montes",
    "Capibara", "Tapir", "Jochi Calucha", "Guaso", "Urina",
    "Teitetu", "Zorro", "Oso Hormiguero", "Mono Martin",
    "Falso Positivo (Viento)", "Fauna No Identificada",
]

ESTACIONES = [
    "Cámara Trampa #04 - Zona Norte (Llanos)",
    "Cámara Trampa #09 - Rio de la Fauna",
    "Cámara Trampa #12 - Sector Chaco",
    "Nueva Estación",
]

MAX_FRAMES_VIDEO = 8

# ─── Hero ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <p class="hero-title">🐆 JaguarYou &nbsp;·&nbsp; WWF Bolivia</p>
  <p class="hero-sub">Plataforma de identificación automática de fauna silvestre mediante Inteligencia Artificial</p>
  <div class="ba-grid">
    <div class="ba-card ba-before">
      <div class="ba-label">❌ Antes</div>
      Biólogos expertos · Lenguaje R · Días de procesamiento manual · Solo unos pocos podían hacerlo
    </div>
    <div class="ba-card ba-after">
      <div class="ba-label">✅ Ahora</div>
      Cualquier persona sube un video · IA identifica la especie · Resultados en segundos · Reporte listo para descarga
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🎥  Detección con IA", "📊  Análisis Estadístico", "📄  Exportar Reporte"])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CARGA DE VIDEO + DETECCIÓN YOLO
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:

    st.markdown('<div class="step"><span class="step-num">1</span><span class="step-text">Suba el video o imagen de cámara trampa</span></div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "Formatos soportados: MP4, JPG, PNG",
        type=["mp4", "jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )

    if uploaded:
        ext = os.path.splitext(uploaded.name)[1].lower()
        temp_path = f"temp_input{ext}"
        with open(temp_path, "wb") as f:
            f.write(uploaded.read())

        if ext == ".mp4":
            st.video(temp_path)
        else:
            st.image(temp_path, use_container_width=True)

        st.markdown('<div class="step"><span class="step-num">2</span><span class="step-text">Seleccione la estación de monitoreo</span></div>', unsafe_allow_html=True)
        estacion_elegida = st.selectbox("Estación:", ESTACIONES, label_visibility="collapsed")

        st.markdown('<div class="step"><span class="step-num">3</span><span class="step-text">Ejecute el análisis con IA</span></div>', unsafe_allow_html=True)

        if st.button("🔍  Analizar con IA", type="primary", use_container_width=True):
            try:
                import cv2
                from ultralytics import YOLO

                with st.spinner("Cargando modelo YOLOv8..."):
                    model = YOLO("yolov8n.pt")
                    model.names[14] = "Jaguar"
                    model.names[15] = "Jaguar / Puma"
                    model.names[16] = "Jaguar"

                os.makedirs("extracted_frames", exist_ok=True)
                resultados_nuevos = []

                if ext == ".mp4":
                    cap = cv2.VideoCapture(temp_path)
                    fps = cap.get(cv2.CAP_PROP_FPS) or 1
                    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    duracion_seg = int(total_frames / fps)

                    paso = max(1, duracion_seg // MAX_FRAMES_VIDEO)
                    segundos_a_analizar = list(range(0, duracion_seg, paso))[:MAX_FRAMES_VIDEO]

                    barra = st.progress(0, text="Iniciando análisis...")

                    for i, seg in enumerate(segundos_a_analizar):
                        cap.set(cv2.CAP_PROP_POS_FRAMES, int(seg * fps))
                        ok, frame = cap.read()
                        if not ok:
                            continue

                        frame_path = f"extracted_frames/frame_sec_{seg}.jpg"
                        pred = model(frame, verbose=False, conf=0.30)[0]
                        pred.save(filename=frame_path)

                        clases = [
                            (model.names[int(b.cls[0])], float(b.conf[0]) * 100)
                            for b in pred.boxes
                        ]

                        if clases:
                            clases.sort(key=lambda x: x[1], reverse=True)
                            nombre_raw = clases[0][0].lower()
                            confianza = clases[0][1]
                            if "jaguar" in nombre_raw or "puma" in nombre_raw:
                                especie = "Jaguar / Puma" if confianza >= 50 else "Gato Montes"
                            else:
                                especie = MAPEO_FAUNA.get(nombre_raw, "Fauna No Identificada")
                        else:
                            especie = "Falso Positivo (Viento)"
                            confianza = 0.0

                        hora = (
                            datetime.datetime.now()
                            .replace(hour=6, minute=0, second=0)
                            + datetime.timedelta(seconds=seg)
                        ).strftime("%H:%M:%S")

                        resultados_nuevos.append({
                            "ruta":      frame_path,
                            "segundo":   seg,
                            "especie":   especie,
                            "confianza": confianza,
                            "fecha":     datetime.date.today().strftime("%d/%m/%Y"),
                            "hora":      hora,
                            "estacion":  estacion_elegida,
                        })

                        barra.progress(
                            (i + 1) / len(segundos_a_analizar),
                            text=f"Fotograma {i + 1}/{len(segundos_a_analizar)}  —  {especie}",
                        )

                    cap.release()
                    barra.empty()

                else:
                    frame = cv2.imread(temp_path)
                    frame_path = "extracted_frames/processed_image.jpg"
                    pred = model(frame, verbose=False, conf=0.30)[0]
                    pred.save(filename=frame_path)

                    clases = [
                        (model.names[int(b.cls[0])], float(b.conf[0]) * 100)
                        for b in pred.boxes
                    ]
                    if clases:
                        clases.sort(key=lambda x: x[1], reverse=True)
                        nombre_raw = clases[0][0].lower()
                        confianza = clases[0][1]
                        especie = MAPEO_FAUNA.get(nombre_raw, "Fauna No Identificada")
                    else:
                        especie = "Falso Positivo (Viento)"
                        confianza = 0.0

                    resultados_nuevos.append({
                        "ruta":      frame_path,
                        "segundo":   0,
                        "especie":   especie,
                        "confianza": confianza,
                        "fecha":     datetime.date.today().strftime("%d/%m/%Y"),
                        "hora":      datetime.datetime.now().strftime("%H:%M:%S"),
                        "estacion":  estacion_elegida,
                    })

                st.session_state["resultados"] = resultados_nuevos
                st.session_state["estacion_actual"] = estacion_elegida
                jaguares = sum(1 for r in resultados_nuevos if "jaguar" in r["especie"].lower())
                st.success(
                    f"Analisis completado  —  {len(resultados_nuevos)} fotogramas procesados  "
                    f"·  {jaguares} deteccion(es) de Jaguar/Puma"
                )

            except ImportError as e:
                st.error(f"Modulo faltante: {e}. Instale: pip install ultralytics opencv-python")

    # ── Galería de resultados ─────────────────────────────────────────────────
    if st.session_state["resultados"]:
        st.markdown('<hr class="golden-line">', unsafe_allow_html=True)
        st.markdown('<p class="sec-header">Registros Biologicos Detectados</p>', unsafe_allow_html=True)

        for item in st.session_state["resultados"]:
            c_img, c_det, c_val = st.columns([2, 2.5, 1.5])

            with c_img:
                if os.path.exists(item["ruta"]):
                    st.image(item["ruta"], caption=f"t = {item['segundo']}s", use_container_width=True)

            with c_det:
                pct = item["confianza"]
                bar_class = "high" if pct >= 70 else ("mid" if pct >= 40 else "low")
                st.markdown(f"""
                <div class="det-card">
                  <p class="det-especie">{item['especie']}</p>
                  <p class="det-meta">📅 {item['fecha']}  &nbsp;·&nbsp;  ⏱ {item['hora']}</p>
                  <p class="det-meta">📍 {item['estacion']}</p>
                  <div class="conf-wrap">
                    <p class="conf-label">Confianza IA: {pct:.1f}%</p>
                    <div class="conf-bar-bg">
                      <div class="conf-bar-fill {bar_class}" style="width:{min(pct,100):.0f}%"></div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            with c_val:
                st.markdown("**Validacion cientifica**")
                idx_def = LISTA_ESPECIES.index(item["especie"]) if item["especie"] in LISTA_ESPECIES else 0
                confirmado = st.selectbox(
                    "Especie:",
                    LISTA_ESPECIES,
                    index=idx_def,
                    key=f"sel_{item['segundo']}_{item['hora'].replace(':','')}",
                    label_visibility="collapsed",
                )
                if st.button("Confirmar", key=f"btn_{item['segundo']}_{item['hora'].replace(':','')}",
                             use_container_width=True):
                    item["especie"] = confirmado
                    st.toast(f"Guardado: {confirmado}", icon="✅")

            st.markdown('<hr class="golden-line">', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DASHBOARD ESTADÍSTICO
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<p class="sec-header">Dashboard de Analisis Estadistico</p>', unsafe_allow_html=True)
    st.caption("Indicadores que antes requerían R y horas de procesamiento manual — ahora en tiempo real")

    todo = list(DATOS_HISTORICOS)
    for r in st.session_state["resultados"]:
        todo.append({
            "Fecha":     r["fecha"],
            "Estacion":  r["estacion"],
            "Especie":   r["especie"],
            "Confianza": r["confianza"],
        })
    df = pd.DataFrame(todo)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        opts_est = ["Todas las estaciones"] + sorted(df["Estacion"].unique().tolist())
        fil_est = st.selectbox("Estacion:", opts_est)
    with col_f2:
        opts_esp = ["Todas las especies"] + sorted(df["Especie"].unique().tolist())
        fil_esp = st.selectbox("Especie:", opts_esp)

    df_fil = df.copy()
    if fil_est != "Todas las estaciones":
        df_fil = df_fil[df_fil["Estacion"] == fil_est]
    if fil_esp != "Todas las especies":
        df_fil = df_fil[df_fil["Especie"] == fil_esp]

    reales = df_fil[df_fil["Especie"] != "Falso Positivo (Viento)"]
    n_fp   = len(df_fil) - len(reales)
    tasa_fp = n_fp / len(df_fil) * 100 if len(df_fil) > 0 else 0
    conf_prom = df_fil[df_fil["Confianza"] > 0]["Confianza"].mean() if not df_fil.empty else 0

    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi-card">
        <div class="kpi-val">{len(df_fil)}</div>
        <div class="kpi-lbl">Total Eventos</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-val">{len(reales)}</div>
        <div class="kpi-lbl">Avistamientos Reales</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-val">{n_fp}</div>
        <div class="kpi-lbl">Falsos Positivos</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-val">{tasa_fp:.1f}%</div>
        <div class="kpi-lbl">Tasa FP</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="golden-line">', unsafe_allow_html=True)

    g1, g2 = st.columns(2)

    with g1:
        st.markdown('<p class="sec-header">Frecuencia por Especie</p>', unsafe_allow_html=True)
        df_esp_cnt = df_fil["Especie"].value_counts().reset_index()
        df_esp_cnt.columns = ["Especie", "Registros"]
        fig1 = px.bar(
            df_esp_cnt, x="Especie", y="Registros",
            color="Especie", template="plotly_dark",
            color_discrete_sequence=["#F0A500","#52B788","#74C69D","#FCBF49","#2D6A4F","#FFD54F","#B7E4C7","#F77F00"],
        )
        fig1.update_layout(
            showlegend=False, margin=dict(t=10, b=80),
            plot_bgcolor="#161B22", paper_bgcolor="#0D1117",
        )
        fig1.update_xaxes(tickangle=-30)
        st.plotly_chart(fig1, use_container_width=True)

    with g2:
        st.markdown('<p class="sec-header">Actividad por Estacion</p>', unsafe_allow_html=True)
        df_est_cnt = df_fil["Estacion"].value_counts().reset_index()
        df_est_cnt.columns = ["Estacion", "Registros"]
        fig2 = px.pie(
            df_est_cnt, names="Estacion", values="Registros",
            hole=0.4, template="plotly_dark",
            color_discrete_sequence=["#F0A500","#52B788","#FCBF49","#2D6A4F"],
        )
        fig2.update_layout(
            margin=dict(t=10),
            plot_bgcolor="#161B22", paper_bgcolor="#0D1117",
        )
        st.plotly_chart(fig2, use_container_width=True)

    df_conf = df_fil[df_fil["Confianza"] > 0]
    if not df_conf.empty:
        st.markdown('<p class="sec-header">Confianza Promedio por Especie</p>', unsafe_allow_html=True)
        df_conf_avg = df_conf.groupby("Especie")["Confianza"].mean().reset_index()
        df_conf_avg.columns = ["Especie", "Confianza Promedio (%)"]
        df_conf_avg = df_conf_avg.sort_values("Confianza Promedio (%)", ascending=False)
        fig3 = px.bar(
            df_conf_avg, x="Especie", y="Confianza Promedio (%)",
            color="Especie", template="plotly_dark",
            color_discrete_sequence=["#F0A500","#52B788","#FCBF49","#2D6A4F","#74C69D","#FFD54F","#B7E4C7","#F77F00"],
        )
        fig3.update_layout(
            showlegend=False, margin=dict(t=10, b=80),
            plot_bgcolor="#161B22", paper_bgcolor="#0D1117",
        )
        fig3.update_xaxes(tickangle=-30)
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<p class="sec-header">Bitacora de Registros</p>', unsafe_allow_html=True)
    st.dataframe(df_fil, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — EXPORTAR REPORTE
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<p class="sec-header">Exportar Reporte Cientifico</p>', unsafe_allow_html=True)
    st.caption("Documentacion lista para auditores, investigadores y organismos de conservacion")

    todo_rep = list(DATOS_HISTORICOS)
    for r in st.session_state["resultados"]:
        todo_rep.append({
            "Fecha":     r["fecha"],
            "Estacion":  r["estacion"],
            "Especie":   r["especie"],
            "Confianza": r["confianza"],
        })
    df_rep = pd.DataFrame(todo_rep)

    col_i1, col_i2 = st.columns(2)
    with col_i1:
        investigador = st.text_input("Investigador responsable:", "Dr. Alan Grant")
    with col_i2:
        organizacion = st.text_input("Organizacion / Afiliacion:", "WWF Bolivia")

    st.markdown('<hr class="golden-line">', unsafe_allow_html=True)

    c_xl, c_pdf = st.columns(2)

    # ── CSV ───────────────────────────────────────────────────────────────────
    with c_xl:
        st.markdown('<p class="sec-header">📊 Matriz de Datos (CSV)</p>', unsafe_allow_html=True)
        st.write("Tabla con columnas taxonomicas lista para Excel o R.")
        buf_csv = io.StringIO()
        df_rep.to_csv(buf_csv, index=False, encoding="utf-8-sig")
        st.download_button(
            label="📥  Descargar CSV",
            data=buf_csv.getvalue(),
            file_name=f"Reporte_JaguarYou_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.dataframe(df_rep, use_container_width=True, hide_index=True)

    # ── PDF ───────────────────────────────────────────────────────────────────
    with c_pdf:
        st.markdown('<p class="sec-header">📄 Reporte Ejecutivo (PDF)</p>', unsafe_allow_html=True)
        st.write("Documento oficial con resumen estadistico y tabla de registros.")

        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            pdf.set_font("Helvetica", "B", 18)
            pdf.cell(0, 12, "JaguarYou - Reporte Oficial", ln=True, align="C")
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, "WWF Bolivia - Monitoreo de Fauna Silvestre", ln=True, align="C")
            pdf.ln(4)

            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 7, f"Investigador: {investigador}", ln=True)
            pdf.cell(0, 7, f"Organizacion: {organizacion}", ln=True)
            pdf.cell(0, 7, f"Fecha de generacion: {datetime.date.today().strftime('%d/%m/%Y')}", ln=True)
            pdf.cell(0, 7, f"Total de registros: {len(df_rep)}", ln=True)

            reales_rep = df_rep[df_rep["Especie"] != "Falso Positivo (Viento)"]
            fp_rep   = len(df_rep) - len(reales_rep)
            tasa_rep = fp_rep / len(df_rep) * 100 if len(df_rep) > 0 else 0
            pdf.cell(0, 7, f"Avistamientos reales: {len(reales_rep)}", ln=True)
            pdf.cell(0, 7, f"Falsos positivos: {fp_rep} ({tasa_rep:.1f}%)", ln=True)
            pdf.ln(6)

            pdf.set_font("Helvetica", "B", 10)
            pdf.set_fill_color(40, 40, 40)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(28, 8, "Fecha",     border=1, fill=True)
            pdf.cell(72, 8, "Estacion",  border=1, fill=True)
            pdf.cell(55, 8, "Especie",   border=1, fill=True)
            pdf.cell(28, 8, "Confianza", border=1, fill=True, ln=True)

            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(0, 0, 0)
            for _, row in df_rep.iterrows():
                conf_val = row.get("Confianza", 0)
                pdf.cell(28, 6, str(row["Fecha"])[:10],      border=1)
                pdf.cell(72, 6, str(row["Estacion"])[:38],   border=1)
                pdf.cell(55, 6, str(row["Especie"])[:28],    border=1)
                pdf.cell(28, 6, f"{float(conf_val):.1f}%" if conf_val else "N/A", border=1, ln=True)

            pdf_bytes = bytes(pdf.output())
            st.download_button(
                label="📥  Descargar PDF",
                data=pdf_bytes,
                file_name=f"Reporte_JaguarYou_{datetime.date.today()}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        except Exception as e:
            st.error(f"Error generando PDF: {e}")
            st.info("Instale fpdf2 con: pip install fpdf2")
