import streamlit as st
from utils import get_processed_videos, generate_notes, initialize_session_state
from localization import initialize_language_selection, get_translation, set_rtl_style

st.set_page_config(page_title=f"{get_translation('app_title')} - {get_translation('notes_title')}", layout="wide")

# Initialize session state
initialize_session_state()

# Initialize language selection
initialize_language_selection()

# Set RTL style if Arabic is selected
set_rtl_style()



st.title(get_translation("notes_title"))

processed_videos = get_processed_videos()
if processed_videos:
    video_options = {title: video_id for video_id, title in processed_videos}
    selected_title = st.selectbox(get_translation("select_video_notes"), list(video_options.keys()))
    selected_video = video_options[selected_title]
    
    if st.button(get_translation("generate_notes")):
        with st.spinner(get_translation("generating_notes")):
            notes = generate_notes(selected_video, st.session_state.goals)
            st.subheader(f"{get_translation('notes_for')} {selected_title}")
            st.markdown(notes)
            st.download_button(
                get_translation("download_notes"), 
                notes, 
                f"{selected_title}_notes.md"
            )
else:
    st.warning(get_translation("no_videos_processed"))