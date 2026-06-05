# Rendimiento académico y salud mental
### Práctica II — Visualización de Datos · UOC · 2026
**Nora Mendoza**

---

## Descripción

Este proyecto analiza la relación entre el rendimiento académico, la salud mental y el nivel socioeconómico en estudiantes universitarios, a partir de dos datasets de Kaggle.

La visualización responde cuatro preguntas clave:
- ¿Los estudiantes con ansiedad o depresión obtienen peores notas?
- ¿Influye el nivel socioeconómico en el rendimiento?
- ¿La asistencia está relacionada con las notas?
- ¿Hay diferencias de riesgo mental por género y año de estudio?

---

## Estructura del repositorio

```
├── data/
│   ├── academic_performance_clean.csv   # Dataset 1 limpio (494 registros)
│   └── mental_health_clean.csv          # Dataset 2 limpio (100 registros)
├── visualizations/
│   ├── viz1_cgpa_vs_salud_mental.html   # CGPA según condición mental
│   ├── viz2_riesgo_heatmap.html         # Heatmap riesgo por género y curso
│   ├── viz3_socioeconomico_notas.html   # Nivel socioeconómico vs nota
│   ├── viz4_asistencia_scatter.html     # Asistencia vs rendimiento
│   └── viz5_perfiles_riesgo.html        # Perfiles combinados
├── practica2_visualizacion.py           # Script de limpieza y generación
├── requirements.txt                     # Dependencias Python
├── LICENSE                              # Licencia MIT
└── README.md
```

---

## Datos

| Dataset | Fuente | Registros | Variables |
|---|---|---|---|
| Student Performance and Socioeconomic Dataset | [Kaggle](https://www.kaggle.com/datasets/waqi786/student-performance-and-socioeconomic-dataset) | 494 | 25 |
| Student Mental Health | [Kaggle](https://www.kaggle.com/datasets/shariful07/student-mental-health) | 100 | 11 |

### Proceso de limpieza (Python / pandas)
- Eliminación de nulos (8 filas sin Student_ID, 2 sin nota semestral, 1 sin edad)
- Normalización de `Grade_Average` a escala 0–10
- Estandarización de columnas (`Year_of_Study`, `CGPA`)
- Creación de nuevas variables:
  - `Mental_Risk_Index` (0–3): suma de depresión + ansiedad + pánico
  - `Approval_Ratio`: asignaturas aprobadas / matriculadas

---

## Tecnologías utilizadas

- **Python 3.12** — limpieza y preparación de datos
- **pandas** — manipulación de datos
- **Plotly** — visualizaciones interactivas (HTML)
- **statsmodels** — línea de tendencia (OLS)




## Vídeo explicativo

**[Ver vídeo en YouTube](https://youtube.com/.)**

---

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
