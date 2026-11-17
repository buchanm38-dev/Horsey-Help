
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Daily Racing Matcher", layout="wide")
st.title("Daily Racing System Matcher")

sample_data = {
    "Race": ["Goodwood 14:25", "Goodwood 14:25", "York 15:00", "York 15:00"],
    "Horse": ["Drumbeat", "Capability Brown", "Progressive Type", "Firm Only"],
    "Age": [2, 2, 3, 4],
    "Trainer": ["Aidan O'Brien", "Aidan O'Brien", "William Haggas", "Unknown"],
    "LastTwo": ["1-1", "2-1", "1-3", "4-5"],
    "Style": ["mid-pack", "tactical", "prominent", "front"],
    "SoftForm": ["Yes", "Yes", "Yes", "No"],
    "ClassDrop": ["No", "No", "Yes", "No"],
    "CourseFit": ["Yes", "Yes", "Yes", "No"]
}

uploaded_file = st.file_uploader("Upload today's runners CSV", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.info("Using sample data")
    df = pd.DataFrame(sample_data)

strong_yards = ["haggas", "balding", "o'brien", "obrien", "aidan", "burke", "gosden", "scott"]

def score_horse(row):
    score = 0
    reasons = []

    lt = str(row.get("LastTwo", "")).lower()
    if any(x in lt for x in ["1-", "2-1", "1-1", "1-2"]):
        score += 30
        reasons.append("Progressive last-two")

    trainer = str(row.get("Trainer", "")).lower()
    if any(y in trainer for y in strong_yards):
        score += 25
        reasons.append("Strong yard")

    style = str(row.get("Style", "")).lower()
    if "mid" in style or "tactical" in style or "handy" in style:
        score += 20
        reasons.append("Tactical/mid-pack style")
    elif "front" in style:
        score -= 10
        reasons.append("Pure front-runner")

    if str(row.get("SoftForm", "")).lower() in ["yes", "y"]:
        score += 15
        reasons.append("Soft/GTS form")

    if str(row.get("ClassDrop", "")).lower() in ["yes", "y"]:
        score += 15
        reasons.append("Class/mark drop")

    if str(row.get("CourseFit", "")).lower() in ["yes", "y"]:
        score += 10
        reasons.append("Course fit")

    return score, "; ".join(reasons) if reasons else "Weak match"

scores = []
reasons_list = []
for index, row in df.iterrows():
    s, r = score_horse(row)
    scores.append(s)
    reasons_list.append(r)

df["Score"] = scores
df["Match Reasons"] = reasons_list
df = df.sort_values(by="Score", ascending=False)

st.subheader("Matches (highest first)")
st.dataframe(df[["Race", "Horse", "Trainer", "Score", "Match Reasons"]], use_container_width=True, hide_index=True)

strong = df[df["Score"] >= 50]
if len(strong) > 0:
    st.success(str(len(strong)) + " strong matches")
else:
    st.warning("No strong matches")
