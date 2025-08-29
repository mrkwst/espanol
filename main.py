import streamlit as st
import random
import json
import unicodedata

# Load JSON
with open("verbs.json", "r", encoding="utf-8") as f:
    verbs_data = json.load(f)

# Initialize session state
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.questions = []

# Sidebar for quiz settings
with st.sidebar:
    selected_verbs = st.multiselect(
        "Select verbs:",
        list(verbs_data["irregulars"].keys()) + ["hablar", "comer", "vivir"]
    )
    selected_tenses = st.multiselect(
        "Select tenses:",
        ["present", "preterite", "imperfect"]
    )
    show_vosotros = st.checkbox("Include vosotros?", value=True)
    if st.button("Start Quiz"):
        st.session_state.questions = []
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

# Function to remove accents
def remove_accents(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ).lower()

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
        st.success("Correct!")
        st.session_state.score += 1
    else:
        st.error(f"Wrong! Correct answer: {correct_answer}")

    st.session_state.current += 1
    st.session_state.input_text = ""

# Quiz display
if st.session_state.started:
    if st.session_state.current < len(st.session_state.questions):
        verb, tense, pronoun = st.session_state.questions[st.session_state.current]
        st.text_input(
            f"{pronoun} form of {verb} in {tense}:",
            key="input_text",
            on_change=submit_answer
        )
    else:
        st.success(f"Quiz completed! Score: {st.session_state.score}/{len(st.session_state.questions)}")
        st.session_state.started = False
