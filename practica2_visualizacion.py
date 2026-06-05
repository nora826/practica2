import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

OUTPUT_DIR = "/mnt/user-data/outputs/"

# =============================================================================
# 1. CARGA DE DATOS

perf = pd.read_csv("/mnt/user-data/uploads/Academic_performance_retention_dataset.csv")
mh   = pd.read_csv("/mnt/user-data/uploads/Student_Mental_health.csv")

print(f"Academic Performance: {perf.shape[0]} filas, {perf.shape[1]} columnas")
print(f"Mental Health:{mh.shape[0]} filas, {mh.shape[1]} columnas")


# =============================================================================
# 2. LIMPIEZA - Dataset 1: Academic Performance

perf = perf.dropna(subset=["Student_ID", "Semester_Average_Grade"])

perf["Grade_0_10"] = (perf["Grade_Average"] / 6) * 10

perf["Attendance"] = perf["Attendance"].round(1)

soc_order = {"Low": 1, "Medium": 2, "High": 3}
perf["Soc_Num"] = perf["Socioeconomic_Level"].map(soc_order)

perf["Approval_Ratio"] = (
    perf["Semester_Approved_Units"] / perf["Semester_Enrolled_Units"].replace(0, np.nan)
).round(2)

print("\n✓ Dataset 1 limpio:", perf.shape)


# =============================================================================
# 3. LIMPIEZA - Dataset 2: Student Mental Health

mh = mh.rename(columns={
    "Choose your gender":"Gender",
    "What is your course?":"Course",
    "Your current year of Study":"Year_of_Study",
    "What is your CGPA?":"CGPA",
    "Marital status":"Marital_Status",
    "Do you have Depression?":"Depression",
    "Do you have Anxiety?":"Anxiety",
    "Do you have Panic attack?":"Panic_Attack",
    "Did you seek any specialist for a treatment?": "Treatment"
})

mh = mh.dropna(subset=["Age"])
mh["Age"] = mh["Age"].astype(int)

mh["Year_of_Study"] = mh["Year_of_Study"].str.lower().str.strip()

mh["CGPA"] = mh["CGPA"].str.strip()

for col in ["Depression", "Anxiety", "Panic_Attack", "Treatment"]:
    mh[f"{col}_bin"] = (mh[col] == "Yes").astype(int)

mh["Mental_Risk_Index"] = (
    mh["Depression_bin"] + mh["Anxiety_bin"] + mh["Panic_Attack_bin"]
)
mh["Mental_Risk_Label"] = mh["Mental_Risk_Index"].map({
    0: "Sin riesgo",
    1: "Riesgo bajo",
    2: "Riesgo medio",
    3: "Riesgo alto"
})

cgpa_order = ["0 - 1.99", "2.00 - 2.49", "2.50 - 2.99", "3.00 - 3.49", "3.50 - 4.00"]
mh["CGPA"] = pd.Categorical(mh["CGPA"], categories=cgpa_order, ordered=True)

print("✓ Dataset 2 limpio:", mh.shape)


# =============================================================================
# 4. EXPORTAR CSVs LIMPIOS (para Flourish)

perf_export = perf[[
    "Student_ID","Age","Gender","Marital_Status","Course_Chosen",
    "Application_Mode","Residence_Location","Parental_Education",
    "Parental_Income_Level","Employment_Status","Socioeconomic_Level",
    "Study_Career","Attendance","Grade_0_10","Approval_Ratio",
    "Semester_Average_Grade","Retention","Unemployment_Rate",
    "Inflation_Rate","Regional_GDP","Year","Soc_Num"
]].copy()

mh_export = mh[[
    "Gender","Age","Course","Year_of_Study","CGPA","Marital_Status",
    "Depression","Anxiety","Panic_Attack","Treatment",
    "Depression_bin","Anxiety_bin","Panic_Attack_bin",
    "Mental_Risk_Index","Mental_Risk_Label"
]].copy()
mh_export["CGPA"] = mh_export["CGPA"].astype(str)

perf_export.to_csv(f"{OUTPUT_DIR}academic_performance_clean.csv", index=False)
mh_export.to_csv(f"{OUTPUT_DIR}mental_health_clean.csv", index=False)
print("✓ CSVs limpios exportados")



COLORS = {
    "Sin riesgo":"#4CAF82",
    "Riesgo bajo":"#F5C518",
    "Riesgo medio":"#FF8C42",
    "Riesgo alto":"#E63946",
    "Female": "#7B68EE",
    "Male":"#48CAE4",
    "Low":"#E63946",
    "Medium":"#F5C518",
    "High":"#4CAF82",
}

TEMPLATE = "plotly_white"
FONT= dict(family="Arial, sans-serif", size=13, color="#333333")


# =============================================================================

def viz1_cgpa_vs_mental():
    conditions = {
        "Depresión": "Depression_bin",
        "Ansiedad":  "Anxiety_bin",
        "Pánico":    "Panic_Attack_bin"
    }
    
    frames = []
    for label, col in conditions.items():
        grp = (
            mh.groupby([col, "CGPA"], observed=True)
            .size()
            .reset_index(name="count")
        )
        grp["Condición"] = label
        grp["Tiene"] = grp[col].map({1: "Sí", 0: "No"})
        frames.append(grp)
    
    df_plot = pd.concat(frames)
    
    df_plot["pct"] = df_plot.groupby(["Condición","Tiene"])["count"].transform(
        lambda x: (x / x.sum() * 100).round(1)
    )
    
    fig = px.bar(
        df_plot,
        x="Tiene",
        y="pct",
        color="CGPA",
        facet_col="Condición",
        barmode="stack",
        category_orders={"CGPA": cgpa_order},
        color_discrete_sequence=px.colors.sequential.Viridis,
        labels={"pct": "% estudiantes", "Tiene": "¿Tiene la condición?"},
        title="<b>¿Afecta la salud mental al rendimiento académico?</b><br>"
              "<sup>Distribución del CGPA según presencia de depresión, ansiedad y pánico</sup>",
        template=TEMPLATE
    )
    fig.update_layout(
        font=FONT,
        legend_title="CGPA",
        bargap=0.3,
        height=480,
        plot_bgcolor="white",
        yaxis_ticksuffix="%"
    )
    fig.write_html(f"{OUTPUT_DIR}viz1_cgpa_vs_salud_mental.html")
    print("exportada")

viz1_cgpa_vs_mental()


# =============================================================================

def viz2_riesgo_heatmap():
    grp = (
        mh.groupby(["Gender","Year_of_Study"])["Mental_Risk_Index"]
        .mean()
        .round(2)
        .reset_index()
    )
    
    pivot = grp.pivot(index="Gender", columns="Year_of_Study", values="Mental_Risk_Index")
    
    col_order = ["year 1","year 2","year 3","year 4"]
    pivot = pivot.reindex(columns=[c for c in col_order if c in pivot.columns])
    pivot.columns = [c.replace("year","Año") for c in pivot.columns]
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale="RdYlGn_r",
        zmin=0, zmax=3,
        text=pivot.values.round(2),
        texttemplate="%{text}",
        colorbar=dict(
            title="Índice<br>riesgo<br>(0–3)",
            tickvals=[0,1,2,3],
            ticktext=["Sin riesgo","Bajo","Medio","Alto"]
        )
    ))
    
    fig.update_layout(
        title="<b>Índice de riesgo mental por género y curso</b><br>"
              "<sup>Promedio de condiciones de salud mental (depresión + ansiedad + pánico)</sup>",
        font=FONT,
        template=TEMPLATE,
        height=350,
        xaxis_title="Año de estudio",
        yaxis_title="Género"
    )
    fig.write_html(f"{OUTPUT_DIR}viz2_riesgo_heatmap.html")
    print("exportada")

viz2_riesgo_heatmap()


# =============================================================================

def viz3_socioeconomico_notas():
    fig = px.box(
        perf,
        x="Socioeconomic_Level",
        y="Grade_0_10",
        color="Gender",
        category_orders={
            "Socioeconomic_Level": ["Low","Medium","High"],
            "Gender": ["Female","Male"]
        },
        color_discrete_map={"Female": COLORS["Female"], "Male": COLORS["Male"]},
        points="outliers",
        labels={
            "Grade_0_10": "Nota media (0–10)",
            "Socioeconomic_Level": "Nivel socioeconómico",
            "Gender": "Género"
        },
        title="<b>Nivel socioeconómico y rendimiento académico</b><br>"
              "<sup>Distribución de notas por nivel socioeconómico y género</sup>",
        template=TEMPLATE
    )
    fig.update_layout(
        font=FONT,
        height=480,
        boxgap=0.3,
        plot_bgcolor="white"
    )
    fig.add_hline(
        y=perf["Grade_0_10"].mean(),
        line_dash="dot",
        line_color="gray",
        annotation_text=f"Media global: {perf['Grade_0_10'].mean():.1f}",
        annotation_position="top right"
    )
    fig.write_html(f"{OUTPUT_DIR}viz3_socioeconomico_notas.html")
    print("exportada")

viz3_socioeconomico_notas()


# =============================================================================

def viz4_asistencia_scatter():
    fig = px.scatter(
        perf,
        x="Attendance",
        y="Grade_0_10",
        color="Study_Career",
        trendline="ols",
        trendline_scope="overall",
        opacity=0.65,
        hover_data={
            "Student_ID": True,
            "Socioeconomic_Level": True,
            "Employment_Status": True,
            "Attendance": ":.1f",
            "Grade_0_10": ":.2f"
        },
        labels={
            "Attendance": "Asistencia (%)",
            "Grade_0_10": "Nota media (0–10)",
            "Study_Career": "Área de estudio"
        },
        title="<b>Asistencia y rendimiento académico</b><br>"
              "<sup>¿Los estudiantes que más asisten obtienen mejores notas?</sup>",
        template=TEMPLATE
    )
    fig.update_layout(font=FONT, height=500)
    fig.write_html(f"{OUTPUT_DIR}viz4_asistencia_scatter.html")
    print("exportada")

viz4_asistencia_scatter()


# =============================================================================

def viz5_perfiles_riesgo():
    risk_gender = (
        mh.groupby(["Gender","Mental_Risk_Label"])
        .size()
        .reset_index(name="count")
    )
    risk_gender["pct"] = risk_gender.groupby("Gender")["count"].transform(
        lambda x: (x / x.sum() * 100).round(1)
    )
    

  
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            "Distribución de riesgo mental por género",
            "Nota media por área y modalidad de estudio"
        ),
        horizontal_spacing=0.15
    )
    
    
    risk_order = ["Sin riesgo","Riesgo bajo","Riesgo medio","Riesgo alto"]
    for risk in risk_order:
        subset = risk_gender[risk_gender["Mental_Risk_Label"] == risk]
        fig.add_trace(go.Bar(
            name=risk,
            x=subset["Gender"],
            y=subset["pct"],
            marker_color=COLORS[risk],
            legendgroup=risk,
            showlegend=True,
            text=subset["pct"].astype(str) + "%",
            textposition="inside"
        ), row=1, col=1)
    
    grp2 = (
        perf.groupby(["Study_Career","Application_Mode"])["Grade_0_10"]
        .mean()
        .round(2)
        .reset_index()
    )
    mode_colors = {"Online": "#7B68EE", "In-person": "#48CAE4", "Referral": "#F5C518"}
    for mode in grp2["Application_Mode"].unique():
        sub = grp2[grp2["Application_Mode"] == mode]
        fig.add_trace(go.Bar(
            name=mode,
            x=sub["Study_Career"],
            y=sub["Grade_0_10"],
            marker_color=mode_colors.get(mode, "#ccc"),
            legendgroup=mode,
            legendgrouptitle_text="Modalidad" if mode == list(mode_colors.keys())[0] else "",
            showlegend=True,
            text=sub["Grade_0_10"].astype(str),
            textposition="outside"
        ), row=1, col=2)
    
    fig.update_layout(
        title_text="<b>Perfiles de riesgo y rendimiento</b><br>"
                   "<sup>Salud mental por género · Nota media por área y modalidad</sup>",
        barmode="stack",
        font=FONT,
        template=TEMPLATE,
        height=500,
        legend=dict(
            groupclick="toggleitem",
            tracegroupgap=20
        )
    )
    fig.update_yaxes(ticksuffix="%", row=1, col=1)
    fig.update_yaxes(title_text="Nota (0–10)", row=1, col=2)
    
    fig.write_html(f"{OUTPUT_DIR}viz5_perfiles_riesgo.html")
    print("exportada")

viz5_perfiles_riesgo()


# =============================================================================
print("\n" + "="*55)
print("ARCHIVOS GENERADOS EN /mnt/user-data/outputs/")
print("="*55)
files = [
    "academic_performance_clean.csv→ CSV limpio dataset 1",
    "mental_health_clean.csv→ CSV limpio dataset 2",
    "viz1_cgpa_vs_salud_mental.html→ CGPA según condición mental",
    "viz2_riesgo_heatmap.html→ Heatmap riesgo por género/curso",
    "viz3_socioeconomico_notas.html→ Box plot nivel socioeconómico",
    "viz4_asistencia_scatter.html→ Scatter asistencia vs nota",
    "viz5_perfiles_riesgo.html→ Perfiles combinados",
]
for f in files:
    print(f"{f}")
