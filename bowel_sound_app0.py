# bowel_sound_app.py
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# -----------------------------
# App Configuration
# -----------------------------
st.set_page_config(page_title="GI Acoustic Monitoring System", layout="wide")

st.title("🩺 Gastrointestinal Acoustic Monitoring System")
st.subheader("Automated Bowel Sound Analysis Interface")
st.markdown("---")

st.caption(
    "Designed as a bedside support tool for residents, physicians, and nurses to help "
    "structure GI acoustic assessment. Demo only – not a medical device."
)

# -----------------------------
# Right person: intended user role
# -----------------------------
st.sidebar.header("User Role")
user_role = st.sidebar.radio(
    "Who is using this tool?",
    ["Resident", "Physician", "Nurse"],
    index=0,
)

# -----------------------------
# Helper functions
# -----------------------------
def bmi_category(bmi: float | None) -> str:
    if bmi is None:
        return "N/A"
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


# 9-region list (anatomy convention)
REGIONS = [
    "Right hypochondrium", "Epigastric region", "Left hypochondrium",
    "Right lumbar", "Umbilical region", "Left lumbar",
    "Right iliac region", "Hypogastrium", "Left iliac region",
]

# Map region → cell in diagram grid
CELL = {
    "Right hypochondrium": (0, 0), "Epigastric region": (1, 0), "Left hypochondrium": (2, 0),
    "Right lumbar": (0, 1),        "Umbilical region": (1, 1),  "Left lumbar": (2, 1),
    "Right iliac region": (0, 2),  "Hypogastrium": (1, 2),      "Left iliac region": (2, 2),
}

def recommend_region(bmi: float | None, body_type: str) -> str:
    """
    Simple heuristic (demo only, not medical advice).
    """
    if bmi is None:
        return "Right iliac region" if body_type == "Mesomorph" else "Umbilical region"

    cat = bmi_category(bmi)

    if body_type == "Ectomorph":
        return "Umbilical region"

    if body_type == "Mesomorph":
        if cat in ["Underweight", "Normal"]:
            return "Right iliac region"
        return "Right hypochondrium"

    if body_type == "Endomorph":
        if cat in ["Overweight", "Obese"]:
            return "Right hypochondrium"
        return "Left hypochondrium"

    return "Umbilical region"

def draw_abdomen_diagram(selected_region: str):
    """Draw a clean 3x3 abdomen diagram and mark the sensor location."""
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 3)
    ax.invert_yaxis()
    ax.axis("off")

    # Grid lines
    for i in range(4):
        ax.plot([i, i], [0, 3], lw=1, alpha=0.6)
        ax.plot([0, 3], [i, i], lw=1, alpha=0.6)

    # Labels
    for name, (x, y) in CELL.items():
        ax.text(x + 0.5, y + 0.5, name, ha="center", va="center", fontsize=10, wrap=True)

    # Highlight + sensor
    sx, sy = CELL.get(selected_region, (1, 1))
    ax.add_patch(plt.Rectangle((sx, sy), 1, 1, fill=False, lw=3))
    ax.add_patch(plt.Circle((sx + 0.5, sy + 0.5), 0.08))
    ax.text(sx + 0.5, sy + 0.25, "Sensor", ha="center", va="center", fontsize=9)

    return fig


# -----------------------------
# SECTION 1: Patient Details
# -----------------------------
st.header("1️⃣ Patient Details")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Patient Name")
    patient_id = st.text_input("Patient ID")
    treatment_room = st.text_input("Treatment Room No.")
    sex = st.selectbox("Sex", ["Male", "Female", "Other"])

with col2:
    age = st.number_input("Age", min_value=0, max_value=120)
    date = st.date_input("Date", datetime.now())
    clinical_notes = st.text_area("Clinical Notes / Comments")

st.markdown("---")


# -----------------------------
# -----------------------------
# SECTION 2: Physiological Data & Conceptual Sensor Placement
# -----------------------------
st.header("2️⃣ Physiological Data & Conceptual Recommended Sensor Placement")

col3, col4 = st.columns(2)

with col3:
    height = st.number_input("Height (cm)", min_value=0.0)
    weight = st.number_input("Weight (kg)", min_value=0.0)
    bmi = round(weight / ((height / 100) ** 2), 2) if height > 0 else None

    st.metric("Calculated BMI", bmi if bmi is not None else "N/A")
    st.caption(
        f"BMI Category: **{bmi_category(bmi)}**" if bmi is not None else "BMI Category: **N/A**"
    )

    body_type = st.selectbox("Body Type", ["Ectomorph", "Mesomorph", "Endomorph"])
    suggested_region = recommend_region(bmi, body_type)

with col4:
    st.markdown("**Conceptual Recommended Sensor Region**")

    st.markdown(
        f"<div style='font-size:20px; font-weight:600; color:#1f77b4;'>"
        f"📍 {suggested_region}</div>",
        unsafe_allow_html=True,
    )

    with st.expander("Why this region was suggested?"):
        st.write(
            f"- **Body type:** `{body_type}`\n"
            f"- **BMI:** `{bmi if bmi is not None else 'N/A'}` → **{bmi_category(bmi)}**\n"
            f"- **Heuristic overview:**\n"
            f"  • Lean / ectomorph → central (*Umbilical region*)\n"
            f"  • Normal BMI → RLQ (*Right iliac region*)\n"
            f"  • Higher BMI → upper quadrant (*Right hypochondrium*)\n\n"
            f"🔎 Simple conceptual rule — not a clinical guideline."
        )

    if st.checkbox("Show placement diagram", value=True):
        fig = draw_abdomen_diagram(suggested_region)
        st.pyplot(fig)

st.markdown("---")


# -----------------------------
# SECTION 3: Diagnostic Recommendations
# -----------------------------
st.header("3️⃣ Diagnostic Recommendations")

col5, col6 = st.columns(2)

with col5:
    diagnosis = st.radio(
        "Overall impression of bowel activity",
        ["Normal ✅", "Abnormal ⚠️"],
    )

    # Manual acoustic metrics
    cpm = st.text_input("CPM:")
    sn_ratio = st.text_input("S–N Ratio:")
    ssi = st.text_input("SSI:")

with col6:
    clinical_info = st.text_area(
        "Clinical Info",
        "E.g., type of surgery, postop day, bowel movement status, ileus suspicion, analgesia, etc.",
    )
    recommended_lab = st.text_input(
        "Recommended Lab / Imaging",
        "E.g., Electrolytes, Imaging, Blood Count",
    )

st.markdown("---")


# -----------------------------
# Download + Status
# -----------------------------
report_text = f"""
GI Acoustic Monitoring Report (Demo)

User role: {user_role}
Date: {date}
Patient: {name or 'N/A'} (ID: {patient_id or 'N/A'})
Sex: {sex}, Age: {age if age else 'N/A'}
Room: {treatment_room or 'N/A'}

BMI: {bmi if bmi is not None else 'N/A'} ({bmi_category(bmi)})
Body type: {body_type}
Conceptual recommended sensor region: {suggested_region}

Diagnosis impression: {diagnosis}
CPM: {cpm or 'N/A'}
S–N Ratio: {sn_ratio or 'N/A'}
SSI: {ssi or 'N/A'}

Clinical info:
{clinical_info or 'N/A'}

Suggested labs / imaging:
{recommended_lab or 'N/A'}

Note: This report is generated from a research prototype UI and is not a medical record.
"""

st.download_button("📄 Download Report", report_text, file_name="GI_Report.txt")
st.success("✅ Data captured. Review before making any clinical decisions.")

st.caption(
    "⚠️ Prototype only — not intended for diagnosis or medical decision-making."
)
