import streamlit as st
from utils import get_video_id, process_video, get_processed_videos, generate_summary, initialize_session_state
from localization import initialize_language_selection, get_translation, set_rtl_style

# Initialize session state
initialize_session_state()

st.set_page_config(page_title=f"{get_translation('app_title')} - {get_translation('summary_title')}", layout="wide")

# Initialize language selection
initialize_language_selection()

# Set RTL style if Arabic is selected
set_rtl_style()


st.title(get_translation("summary_title"))

# Section for processing new videos
st.header(get_translation("process_new_video"))
video_url = st.text_input(get_translation("enter_youtube_url"))
if st.button(get_translation("process_video")):
    video_id = get_video_id(video_url)
    if video_id:
        with st.spinner(get_translation("processing_video")):
            summary, transcript, title = process_video(video_id, st.session_state.goals)
            st.session_state.last_processed_video = video_id
            
            st.subheader(f"{get_translation('video_title')}: {title}")
            st.subheader(get_translation("summary"))
            st.write(summary)
    else:
        st.error(get_translation("invalid_url"))

# Section for selecting and viewing summaries of processed videos
st.header(get_translation("view_processed_summaries"))
processed_videos = get_processed_videos()
if processed_videos:
    video_options = {title: video_id for video_id, title in processed_videos}
    selected_title = st.selectbox(get_translation("choose_processed_video"), list(video_options.keys()))
    selected_video_id = video_options[selected_title]
    
    if st.button(get_translation("view_summary")):
        with st.spinner(get_translation("retrieving_summary")):
            summary, _ = generate_summary(selected_video_id, st.session_state.goals)
            
            st.subheader(f"{get_translation('summary_for')}: {selected_title}")
            st.write(summary)
else:
    st.write(get_translation("no_videos_processed"))

# Display list of all processed videos
st.subheader(get_translation("all_processed_videos"))
if processed_videos:
    for video_id, title in processed_videos:
        st.write(f"- {title} (ID: {video_id})")
else:
    st.write(get_translation("no_videos_processed"))