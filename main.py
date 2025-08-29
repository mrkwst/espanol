import streamlit as st
import random
import json
import unicodedata
import pandas as pd

# Load JSON
with open("verbs.json", "r", encoding="utf-8") as f:
    verbs_data = json.load(f)

# Initialize session state
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.questions = []
    st.session_state.input_text = ""
    st.session_state.show_conjugation = False
    st.session_state.include_vosotros = True

# Sidebar for quiz settings
with st.sidebar:
    selected_verbs = st.multiselect(
        "Select verbs:",
        list(verbs_data["irregulars"].keys()) + ["hablar", "comer", "vivir"]
    )
    selected_tenses = st.multiselect(
        "Select tenses:",
        ["present", "preterite", "imperfect", "future"]  # ✅ Added future
    )
    show_vosotros = st.checkbox("Include vosotros?", value=True)
    if st.button("Start Quiz"):
        st.session_state.questions = []
        st.session_state.include_vosotros = show_vosotros
        for verb in selected_verbs:
            for tense in selected_tenses:
                for pronoun in ["yo", "tú", "él/ella", "nosotros", "vosotros", "ellos/ellas/ustedes"]:
                    if pronoun == "vosotros" and not show_vosotros:
                        continue
                    st.session_state.questions.append((verb, tense, pronoun))
        random.shuffle(st.session_state.questions)
        st.session_state.started = True
        st.session_state.current = 0
        st.session_state.score = 0
        st.session_state.input_text = ""
        st.session_state.show_conjugation = False

# Remove accents
def remove_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ).lower()

# Submit answer
def submit_answer():
    idx = st.session_state.current
    verb, tense, pronoun = st.session_state.questions[idx]
    user_input = st.session_state.input_text.strip()

    # Get correct answer
    if verb in verbs_data["irregulars"]:
        correct_answer = verbs_data["irregulars"][verb][tense][pronoun]
    else:
        stem = verb[:-2]
        ending = "-" + verb[-2:]
        correct_answer = stem + verbs_data["regulars"][ending][tense][pronoun]

    # Compare ignoring accents
    if remove_accents(user_input) == remove_accents(correct_answer):
        st.session_state.feedback = f"✅ Correct! ({correct_answer})"
        st.session_state.score += 1
    else:
        st.session_state.feedback = f"❌ Wrong! Correct answer: {correct_answer}"

    # Move to next question
    st.session_state.current += 1
    st.session_state.input_text = ""
    st.session_state.show_conjugation = False

# Display conjugation table
def show_conjugation_table(verb, tense):
    if verb in verbs_data["irregulars"]:
        data = verbs_data["irregulars"][verb][tense]
    else:
        stem = verb[:-2]
        ending = "-" + verb[-2:]
        data = {p: stem + verbs_data["regulars"][ending][tense][p]
                for p in verbs_data["regulars"][ending][tense].keys()}

    # Filter out vosotros if not selected
    if not st.session_state.include_vosotros:
        data = {p: form for p, form in data.items() if p != "vosotros"}

    df = pd.DataFrame(list(data.items()), columns=["Pronoun", "Form"])
    st.table(df)

# Main quiz UI
if st.session_state.started:
    if st.session_state.current < len(st.session_state.questions):
        verb, tense, pronoun = st.session_state.questions[st.session_state.current]

        # Feedback from last answer
        if "feedback" in st.session_state:
            st.info(st.session_state.feedback)
            del st.session_state.feedback

        # Question text with clickable verb
        st.write(f"{pronoun} form of ", end="")
        if st.button(verb, key=f"show_{verb}_{tense}"):
            st.session_state.show_conjugation = not st.session_state.show_conjugation
        st.write(f" in {tense}:")

        # Input field (remains active)
        st.text_input(
            "Your answer:",
            key="input_text",
            on_change=submit_answer,
            placeholder="Type your answer and press Enter"
        )

        # Show conjugation table *below* input
        if st.session_state.show_conjugation:
            show_conjugation_table(verb, tense)

    else:
        st.success(f"Quiz completed! Score: {st.session_state.score}/{len(st.session_state.questions)}")
        st.session_state.started = False
