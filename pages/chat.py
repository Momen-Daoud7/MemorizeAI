import streamlit as st
from utils import get_processed_videos, chat_with_video, initialize_session_state
from localization import initialize_language_selection, get_translation, set_rtl_style

# Initialize session state
initialize_session_state()

st.set_page_config(page_title=f"{get_translation('app_title')} - {get_translation('chat_title')}", layout="wide")

# Initialize language selection
initialize_language_selection()

# Set RTL style if Arabic is selected
set_rtl_style()

st.title(get_translation("chat_title"))

# Initialize chat history in session state if not present
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

processed_videos = get_processed_videos()
if processed_videos:
    video_options = {title: video_id for video_id, title in processed_videos}
    selected_title = st.selectbox(get_translation("select_video_chat"), list(video_options.keys()))
    selected_video = video_options[selected_title]
    
    st.subheader(f"{get_translation('chatting_about')} {selected_title}")
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input(get_translation("ask_about_video")):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in chat_with_video(prompt, selected_video, st.session_state.goals):
                full_response += response
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
        
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})

    if st.button(get_translation("clear_chat")):
        st.session_state.chat_history = []
        st.rerun()
else:
    st.warning(get_translation("no_videos_processed"))