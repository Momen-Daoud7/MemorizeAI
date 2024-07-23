import streamlit as st
import os
import re
import json
from typing import List, Generator, Tuple, Dict
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables and set up AI model
load_dotenv()
API_KEY = os.getenv("GOOGLE_AI_API_KEY")
genai.configure(api_key=API_KEY)
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 18192,
}

def initialize_session_state():
    if 'processed_videos' not in st.session_state:
        st.session_state.processed_videos = {}
    if 'transcripts' not in st.session_state:
        st.session_state.transcripts = {}
    if 'goals' not in st.session_state:
        st.session_state.goals = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []



def get_current_language() -> str:
    return st.session_state.get("language", "en")

def get_video_id(link: str) -> str:
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?(?:embed\/)?(?:v\/)?(?:shorts\/)?(?:live\/)?([^?&\n]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id: str) -> str:
    if video_id not in st.session_state.transcripts:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            formatter = TextFormatter()
            formatted_transcript = formatter.format_transcript(transcript)
            st.session_state.transcripts[video_id] = formatted_transcript
        except Exception as e:
            st.error(f"Error fetching transcript: {str(e)}")
            return ""
    
    return st.session_state.transcripts[video_id]
def get_video_id(link: str) -> str:
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?(?:embed\/)?(?:v\/)?(?:shorts\/)?(?:live\/)?([^?&\n]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id: str) -> str:
    if video_id not in st.session_state.transcripts:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatter = TextFormatter()
        formatted_transcript = formatter.format_transcript(transcript)
        st.session_state.transcripts[video_id] = formatted_transcript
    
    return st.session_state.transcripts[video_id]

def generate_summary(video_id: str, goals: List[str]) -> Tuple[str, str]:
    transcript = get_transcript(video_id)
    
    goals_str = "\n".join(f"- {goal}" for goal in goals)
    language = get_current_language()
    lang_instruction = "in English" if language == "en" else "in Arabic"
    prompt = f"""Given the following goals:
{goals_str}

Please summarize the following content {lang_instruction}, focusing on aspects relevant to these goals:

{transcript}

Ensure the summary is comprehensive yet concise, highlighting key points related to the given goals."""

    summaryModel = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction="You're a YouTube summarizer assistant. Your job is to create high-quality summaries that represent the main ideas, quotes,stories and key points from the user's text input, focusing on aspects relevant to their stated goals."
    )
    response = summaryModel.generate_content(prompt)
    summary = response.text

    return summary, transcript

def chat_with_video(query: str, video_id: str, goals: List[str]) -> Generator[str, None, None]:
    transcript = get_transcript(video_id)
    goals_str = ", ".join(goals)
    context = f"User Goals: {goals_str}\n\nRelevant Information:\n{transcript}\n\n"
    
    language = get_current_language()
    lang_instruction = "Respond in English" if language == "en" else "Respond in Arabic"
    
    chatModel = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction=f"""You are an AI assistant with knowledge based on provided video transcripts. 
        Your personality is focused on finding ways and workarounds to achieve the user's goals. 
        Always consider how the accumulated knowledge impacts the user's goals, character, behavior, attitude, and ideas. 
        Provide insights and help the user make logical decisions based on this knowledge.
        {lang_instruction}."""
    )
    response = chatModel.generate_content(f"{context}\n\nUser Query: {query}", stream=True)
    
    for chunk in response:
        yield chunk.text

def generate_quiz(video_id: str, goals: List[str]) -> List[dict]:
    transcript = get_transcript(video_id)
    
    goals_str = "\n".join(f"- {goal}" for goal in goals)
    language = get_current_language()
    lang_instruction = "in English" if language == "en" else "in Arabic"
    prompt = f"""Given the following goals:
{goals_str}

And based on the following transcript of a YouTube video:

{transcript}

Generate 5 quiz questions {lang_instruction} based on the video content, focusing on aspects relevant to the given goals. 
For each question, provide:
1. The question
2. Four multiple-choice options (A, B, C, D)
3. The correct answer
4. A brief explanation of why it's correct

Format the output as a JSON string."""

    quizModel = genai.GenerativeModel(model_name="gemini-1.5-pro")
    response = quizModel.generate_content(prompt)
    return json.loads(response.text)

def generate_notes(video_id: str, goals: List[str]) -> str:
    transcript = get_transcript(video_id)

    goals_str = "\n".join(f"- {goal}" for goal in goals)
    language = get_current_language()
    lang_instruction = "in English" if language == "en" else "in Arabic"
    prompt = f"""Given the following goals:
{goals_str}

And based on the following transcript of a YouTube video:

{transcript}

Create a comprehensive set of question and answer notes {lang_instruction} based on the given text focusing on aspects relevant to these goals. Break down the information into individual, detailed points, focusing on each specific fact, concept, or idea mentioned. Format your response as a series of questions followed by their corresponding answers. Ensure that each Q&A pair covers a single, discrete piece of information from the text. Don't summarize or generalize; instead, aim to capture every detail in the form of a specific question and a precise answer. This approach should allow for an in-depth study of the material, covering all aspects of the content without omitting any details.
 
Format the output as markdown."""

        
    noteModel = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction="You're a note-taking master. Your job is to create high-quality notes in question and answer format from the user's text input, focusing on aspects relevant to their stated goals."
    )
    response = noteModel.generate_content(prompt)
    return response.text

def generate_title(video_id: str) -> str:
    transcript = get_transcript(video_id)
    language = get_current_language()
    lang_instruction = "in English" if language == "en" else "in Arabic"
    prompt = f"Based on the following transcript, generate a concise and informative title {lang_instruction} for the video (max 10 words):\n\n{transcript[:1000]}..."
    
    titleModel = genai.GenerativeModel(model_name="gemini-1.5-pro")
    response = titleModel.generate_content(prompt)
    return response.text.strip()

def process_video(video_id: str, goals: List[str]) -> Tuple[str, str, str]:
    summary, transcript = generate_summary(video_id, goals)
    title = generate_title(video_id)
    
    st.session_state.processed_videos[video_id] = title
    
    return summary, transcript, title

def get_processed_videos() -> List[Tuple[str, str]]:
    return list(st.session_state.processed_videos.items())
# Initialize session state variables
if 'processed_videos' not in st.session_state:
    st.session_state.processed_videos = {}

if 'transcripts' not in st.session_state:
    st.session_state.transcripts = {}