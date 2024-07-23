import streamlit as st
from utils import get_current_language
from localization import initialize_language_selection, get_translation, set_rtl_style

st.set_page_config(page_title=get_translation("app_title"), layout="wide")

# Initialize language selection
initialize_language_selection()

# Set RTL style if Arabic is selected
set_rtl_style()



st.title(get_translation("app_title"))
st.write(get_translation("welcome"))

# Initialize goals in session state if not present
if 'goals' not in st.session_state:
    st.session_state.goals = []

# Sidebar for goals management and navigation
with st.sidebar:
    st.title(get_translation("learning_goals"))
    for i, goal in enumerate(st.session_state.goals):
        col1, col2 = st.columns([3, 1])
        col1.write(f"{i+1}. {goal}")
        if col2.button(get_translation("delete"), key=f"delete_{i}"):
            st.session_state.goals.pop(i)
            st.rerun()
    
    new_goal = st.text_input(get_translation("add_new_goal"))
    if st.button(get_translation("add_goal")):
        st.session_state.goals.append(new_goal)
        st.rerun()

# Main page content
st.header(get_translation("getting_started"))
st.write(get_translation("getting_started_instructions"))

# Display current goals
st.header(get_translation("current_goals"))
if st.session_state.goals:
    for i, goal in enumerate(st.session_state.goals, 1):
        st.write(f"{i}. {goal}")
else:
    st.write(get_translation("no_goals"))

# Reminders and tips
st.header(get_translation("tips"))
st.info(get_translation("tips_content"))