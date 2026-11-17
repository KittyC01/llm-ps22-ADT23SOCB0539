
import streamlit as st
import pandas as pd
import json
import random
import re
from groq import Groq

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="FlashcardAI",
    page_icon="📚",
    layout="centered"
)


# ---------------- CUSTOM DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background: #101827;
    color: #F1F5F9;
}

.block-container {
    max-width: 900px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4, p, label, li {
    color: #F1F5F9 !important;
}

.main-title {
    text-align: center;
    font-size: 44px;
    font-weight: 800;
    color: #A5A0FF !important;
    letter-spacing: -1px;
}

.subtitle {
    text-align: center;
    color: #AAB5C5 !important;
    font-size: 16px;
    margin-bottom: 30px;
}

.stTextArea textarea {
    background: #1E293B !important;
    color: #FFFFFF !important;
    border: 1px solid #475569 !important;
    border-radius: 12px !important;
}

.stTextArea textarea::placeholder {
    color: #AAB5C5 !important;
}

.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input {
    background: #1E293B !important;
    color: #FFFFFF !important;
    border-color: #475569 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #1E293B;
    border: 1px solid #475569;
    border-radius: 18px;
    padding: 20px;
}

.question {
    font-size: 25px;
    font-weight: 700;
    color: #FFFFFF !important;
    line-height: 1.5;
}

.answer {
    font-size: 19px;
    color: #C7D2FE !important;
    line-height: 1.7;
    padding-bottom: 20px;
    margin-bottom: 10px;
}

.stButton > button {
    background: #635BDB;
    color: white !important;
    border: 1px solid #7770E8;
    border-radius: 10px;
    font-weight: 600;
    min-height: 44px;
}

.stButton > button:hover {
    background: #4F46C5;
    border-color: #A5A0FF;
}

.stButton > button:disabled {
    background: #334155;
    color: #94A3B8 !important;
}

.stDownloadButton > button {
    background: #635BDB;
    color: white !important;
    border-radius: 10px;
    border: none;
    min-height: 45px;
}

.stDownloadButton > button:hover {
    background: #4F46C5;
}

[data-testid="stDataEditor"] {
    background: #1E293B;
}

[data-testid="stProgressBar"] > div > div {
    background: #7770E8;
}

hr {
    border-color: #334155;
}

[data-testid="stCaptionContainer"] {
    color: #AAB5C5 !important;
}

.stAlert {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)


# ---------------- GROQ CONNECTION ----------------

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL = "openai/gpt-oss-20b"

# ---------------- SESSION STATE ----------------

if "flashcards" not in st.session_state:
    st.session_state.flashcards = None

if "index" not in st.session_state:
    st.session_state.index = 0

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# ---------------- JSON CLEANING ----------------

def extract_json(content):

    if not content or not content.strip():
        raise ValueError("The AI returned an empty response.")

    content = content.strip()

    # Remove Markdown code fences if present
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    # Extract JSON object
    start = content.find("{")
    end = content.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("The AI did not return valid JSON.")

    content = content[start:end + 1]

    return json.loads(content)


# ---------------- GENERATE FLASHCARDS ----------------

def generate_flashcards(notes, difficulty, count):

    prompt = f"""
You are an educational flashcard generator.

Create exactly {count} question-answer flashcards
using ONLY the supplied study notes.

Difficulty: {difficulty}

Difficulty guidelines:
Easy: Definitions and basic recall.
Medium: Explanations, understanding and comparisons.
Hard: Application, analysis and reasoning.

Requirements:
1. Questions must be accurate and relevant.
2. Do not introduce facts absent from the notes.
3. Avoid unnecessary repetition.
4. Answers must be clear and concise.
5. Return a valid JSON object only.
6. Do not include Markdown or explanations outside JSON.

Required format:
{{
  "flashcards": [
    {{
      "question": "Question here",
      "answer": "Answer here"
    }}
  ]
}}

Study notes:
{notes}
"""

    # Retry once if the response is malformed
    for attempt in range(2):

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2
        )

        content = response.choices[0].message.content

        try:
            result = extract_json(content)

            cards = result["flashcards"]

            if not isinstance(cards, list) or len(cards) == 0:
                raise ValueError("No flashcards were generated.")

            df = pd.DataFrame(cards)

            if not {"question", "answer"}.issubset(df.columns):
                raise ValueError("Flashcards have an incorrect format.")

            df = df[["question", "answer"]].dropna()

            df["question"] = df["question"].astype(str)
            df["answer"] = df["answer"].astype(str)

            df = df[
                (df["question"].str.strip() != "") &
                (df["answer"].str.strip() != "")
            ]

            if df.empty:
                raise ValueError("No valid flashcards were generated.")

            return df.reset_index(drop=True)

        except (ValueError, KeyError, TypeError, json.JSONDecodeError):
            if attempt == 1:
                raise ValueError(
                    "AI returned an invalid response twice. Please try again."
                )


# ---------------- APPLICATION HEADER ----------------

st.markdown(
    '<div class="main-title">📚 FlashcardAI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Turn your study notes into smart flashcards.</div>',
    unsafe_allow_html=True
)

st.divider()



# ---------------- INPUT SECTION ----------------

st.subheader("Create Your Flashcards 📝 ")

notes = st.text_area(
    "Paste your study notes",
    height=180,
    placeholder="Paste your chapter notes or study material here"
)

col1, col2 = st.columns(2)

with col1:
    difficulty = st.selectbox(
        "Choose Difficulty",
        ["Easy", "Medium", "Hard"]
    )

with col2:
    count = st.number_input(
        "Number of Flashcards",
        min_value=1,
        max_value=30,
        value=10
    )

if st.button("✨ Generate Flashcards", use_container_width=True):

    if not notes.strip():
        st.warning("Please enter your study notes first.")

    else:
        try:
            with st.spinner("Creating your flashcards..."):

                df = generate_flashcards(
                    notes,
                    difficulty,
                    count
                )

                st.session_state.flashcards = df
                st.session_state.index = 0
                st.session_state.show_answer = False

            st.success(
                f"{len(df)} flashcards generated successfully!"
            )

        except Exception as e:
            st.error(f"Generation failed: {e}")


# ---------------- FLASHCARD DISPLAY ----------------

if st.session_state.flashcards is not None:

    df = st.session_state.flashcards

    st.divider()
    st.subheader("Your Flashards!")

    total = len(df)
    index = st.session_state.index

    st.progress((index + 1) / total)

    st.caption(f"Card {index + 1} of {total}")

    current = df.iloc[index]

    with st.container(border=True):

        st.markdown("##### QUESTION")

        st.markdown(
            f'<div class="Question">{current["question"]}</div>',
            unsafe_allow_html=True
        )

        st.divider()

        if st.session_state.show_answer:

            st.markdown("##### ANSWER")

            st.markdown(
                f'<div class="Answer">{current["answer"]}</div>',
                unsafe_allow_html=True
            )

    # Show / Hide Answer

    if st.button(
        "Hide Answer" if st.session_state.show_answer
        else "Show Answer",
        use_container_width=True
    ):
        st.session_state.show_answer = (
            not st.session_state.show_answer
        )
        st.rerun()

    # Navigation

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "⬅ Previous",
            disabled=(index == 0),
            use_container_width=True
        ):
            st.session_state.index -= 1
            st.session_state.show_answer = False
            st.rerun()

    with col2:
        if st.button(
            "🔀 Shuffle",
            use_container_width=True
        ):
            st.session_state.flashcards = df.sample(
                frac=1
            ).reset_index(drop=True)

            st.session_state.index = 0
            st.session_state.show_answer = False
            st.rerun()

    with col3:
        if st.button(
            "Next ➡",
            disabled=(index == total - 1),
            use_container_width=True
        ):
            st.session_state.index += 1
            st.session_state.show_answer = False
            st.rerun()

    # ---------------- EDIT FLASHCARDS ----------------

    st.divider()
    st.subheader("✏️ Edit Your Flashcards")

    st.caption("You can directly edit questions and answers below.")

    edited_df = st.data_editor(
        st.session_state.flashcards,
        use_container_width=True,
        num_rows="dynamic",
        key="flashcard_editor"
    )

    st.session_state.flashcards = edited_df

    # ---------------- CSV DOWNLOAD ----------------

    st.divider()
    st.subheader("📥 Export Your Flashcards")

    csv = edited_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇ Download Flashcards as CSV",
        data=csv,
        file_name="FlashcardAI.csv",
        mime="text/csv",
        use_container_width=True
    )

st.divider()

st.markdown(
    "<center style='color:#98A2B3'>📚 FlashcardAI | Smart Study Made Simple </center>",
    unsafe_allow_html=True
)
