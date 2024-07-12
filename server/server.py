import os
import re
from gtts import gTTS
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import google.generativeai as genai
import json
from datetime import datetime
import os
import json
from datetime import datetime
from typing import List, Dict
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
API_KEY = os.getenv("GOOGLE_AI_API_KEY")

# Configure the generative AI model
genai.configure(api_key=API_KEY)

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 18192,
}

EMBEDDING_MODEL = None
INDEX = None
TRANSCRIPT_CHUNKS: List[Dict] = []
DATA_DIR = "memorize_ai_data"
CHUNKS_FILE = os.path.join(DATA_DIR, "transcript_chunks.json")
INDEX_FILE = os.path.join(DATA_DIR, "faiss_index.bin")

def clean_markdown(text):
    # Remove asterisks, hashes, and other markdown syntax
    text = re.sub(r'[*#\-_]', '', text)
    # Remove extra newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def chunk_transcript(transcript: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
    """
    Split the transcript into overlapping chunks.
    
    :param transcript: The full transcript text
    :param chunk_size: The target size of each chunk in words
    :param overlap: The number of overlapping words between chunks
    :return: A list of transcript chunks
    """
    words = transcript.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks


def initialize_rag_system():
    global EMBEDDING_MODEL, INDEX, TRANSCRIPT_CHUNKS
    EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Load existing data if available
    if os.path.exists(CHUNKS_FILE):
        with open(CHUNKS_FILE, 'r') as f:
            TRANSCRIPT_CHUNKS = json.load(f)
    
    if os.path.exists(INDEX_FILE):
        INDEX = faiss.read_index(INDEX_FILE)
    else:
        INDEX = faiss.IndexFlatL2(384)  # 384 is the dimension of the chosen model's embeddings

def save_rag_data():
    with open(CHUNKS_FILE, 'w') as f:
        json.dump(TRANSCRIPT_CHUNKS, f)
    faiss.write_index(INDEX, INDEX_FILE)

def add_transcript_to_index(video_id: str, transcript: str, goals: List[str]):
    chunks = chunk_transcript(transcript)
    for i, chunk in enumerate(chunks):
        embedding = EMBEDDING_MODEL.encode([chunk])[0]
        INDEX.add(np.array([embedding]))
        TRANSCRIPT_CHUNKS.append({
            'video_id': video_id,
            'chunk_id': i,
            'text': chunk,
            'goals': goals
        })
    save_rag_data()  # Save after adding new data
def retrieve_relevant_chunks(query: str, n: int = 5) -> List[str]:
    query_embedding = EMBEDDING_MODEL.encode([query])[0]
    _, indices = INDEX.search(np.array([query_embedding]), n)
    return [TRANSCRIPT_CHUNKS[i]['text'] for i in indices[0]]

def get_user_goals():
    goals = []
    print("Enter your goals (press Enter on an empty line to finish):")
    while True:
        goal = input()
        if goal == "":
            break
        goals.append(goal)
    return goals

def get_video_id(link):
    # Extract video ID from various YouTube URL formats
    patterns = [
        r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?(?:embed\/)?(?:v\/)?(?:shorts\/)?(?:live\/)?([^?&\n]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, link)
        if match:
            return match.group(1)
    return None

def save_transcript(video_id, transcript, goals):
    # Create a directory to store transcripts if it doesn't exist
    if not os.path.exists('transcripts'):
        os.makedirs('transcripts')
    
    # Save transcript with metadata
    filename = f"transcripts/{video_id}.json"
    data = {
        "video_id": video_id,
        "transcript": transcript,
        "goals": goals,
        "date_added": datetime.now().isoformat()
    }
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_all_transcripts():
    all_transcripts = []
    if os.path.exists('transcripts'):
        for filename in os.listdir('transcripts'):
            if filename.endswith('.json'):
                with open(os.path.join('transcripts', filename), 'r') as f:
                    all_transcripts.append(json.load(f))
    return all_transcripts


def chat_with_knowledge(goals):
    if not TRANSCRIPT_CHUNKS:
        print("No video knowledge available. Please watch some videos first.")
        return

    chatbotModel = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction="""You are an AI assistant with knowledge based on provided video transcripts. 
        Your personality is focused on finding ways and workarounds to achieve the user's goals. 
        Always consider how the accumulated knowledge impacts the user's goals, character, behavior, attitude, and ideas. 
        Provide insights and help the user make logical decisions based on this knowledge."""
    )

    chat_session = chatbotModel.start_chat()

    print("Chat session started. Type 'exit' to end the conversation.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        
        relevant_chunks = retrieve_relevant_chunks(user_input)
        context = f"User Goals: {', '.join(goals)}\n\nRelevant Information:\n" + "\n".join(relevant_chunks)
        
        response = chat_session.send_message(f"Context: {context}\n\nUser Query: {user_input}")
        print(f"AI: {clean_markdown(response.text)}")

def generate_and_play_summary(video_id, goals):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    formatter = TextFormatter()
    text_formatted = formatter.format_transcript(transcript)

    goals_str = "\n".join(f"- {goal}" for goal in goals)
    prompt = f"Given the following goals:\n{goals_str}\n\nPlease summarize the following content, focusing on aspects relevant to these goals:\n\n{text_formatted}"

    summaryModel = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction="You're a YouTube summarizer assistant. Your job is to create high-quality summaries that represent the main ideas, quotes, and key points from the user's text input, focusing on aspects relevant to their stated goals."
    )

    chat_session = summaryModel.start_chat()
    response = chat_session.send_message(prompt)
    summary = clean_markdown(response.text)

    print("Summary:")
    print(summary)

    # Convert summary to speech and play
    tts = gTTS(text=summary, lang='en', slow=False)
    tts.save("summary.mp3")
    # os.system("start summary.mp3")
    
    add_transcript_to_index(video_id, text_formatted, goals)
    return summary

def generate_notes(video_id, goals):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    formatter = TextFormatter()
    text_formatted = formatter.format_transcript(transcript)

    goals_str = "\n".join(f"- {goal}" for goal in goals)
    prompt = f"Given the following goals:\n{goals_str}\n\nPlease create in-depth notes in a question-and-answer format based on the following content, focusing on aspects relevant to these goals:\n\n{text_formatted}"

    noteModel = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction="You're a note-taking master. Your job is to create high-quality notes in question and answer format from the user's text input, focusing on aspects relevant to their stated goals."
    )

    chat_session = noteModel.start_chat()
    response = chat_session.send_message(prompt)
    return clean_markdown(response.text)

def run_quiz(video_id, goals):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    formatter = TextFormatter()
    text_formatted = formatter.format_transcript(transcript)

    goals_str = "\n".join(f"- {goal}" for goal in goals)
    initial_prompt = f"""Given the following goals:
{goals_str}

And based on the following transcript of a YouTube video:

{text_formatted}

Your task is to create a quiz that tests the viewer's understanding of the key points from this video, especially as they relate to the given goals. 

Please follow these guidelines:
1. Generate questions that are directly based on the content of the video.
2. Focus on the main ideas, important details, and concepts that align with the user's goals.
3. Avoid asking about trivial details or information not present in the video.
4. Ensure questions are clear, concise, and unambiguous.
5. You will generate one question at a time, and wait for the user's response before providing feedback and moving to the next question.

Do you understand these instructions? If so, please respond with 'Ready to begin the quiz.'"""

    quizModel = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction="You are a quiz master specializing in creating educational quizzes based on video content. Your questions should be relevant, engaging, and directly tied to the material presented in the video."
    )

    chat_session = quizModel.start_chat()
    response = chat_session.send_message(initial_prompt)
    
    if "Ready to begin the quiz" not in response.text:
        print("Error: AI model did not confirm understanding. Please try again.")
        return

    for i in range(7):
        # Generate a single question
        question_response = chat_session.send_message("Generate the next question based on the video content. Provide only the question, without any additional text or question number.")
        question = clean_markdown(question_response.text)
        print(f"\nQuestion {i+1}: {question}")
        
        # Get user's answer
        user_answer = input("Your answer: ")
        
        # Get feedback on the answer
        feedback_response = chat_session.send_message(f"The question was: {question}\nUser's answer: {user_answer}\nProvide feedback and the correct answer, referencing specific content from the video to support your explanation.")
        print(f"Feedback: {clean_markdown(feedback_response.text)}\n")

        # Option to discuss further
        while True:
            discuss = input("Ready for the next question? Enter 1 to continue, or 2 to discuss further: ")
            if discuss == '1':
                break
            elif discuss == '2':
                follow_up = input("What would you like to discuss or ask about this question/answer? ")
                discussion_response = chat_session.send_message(f"User wants to discuss further: {follow_up}\nPlease provide more context or clarification based on the video content.")
                print(f"Discussion: {clean_markdown(discussion_response.text)}\n")
            else:
                print("Invalid input. Please enter 1 or 2.")

def main():
    initialize_rag_system()
    goals = get_user_goals()
    
    while True:
        print("\nChoose an option:")
        print("1. Watch a video")
        print("2. Create quiz")
        print("3. Create in-depth notes")
        print("4. Chat with knowledge")
        print("5. Exit")
        
        choice = input("Enter your choice: ")

        if choice == "1":
            youtube_link = input("Enter YouTube video link: ")
            video_id = get_video_id(youtube_link)
            if not video_id:
                print("Invalid YouTube link. Please try again.")
                continue
            generate_and_play_summary(video_id, goals)
        elif choice == "2":
            if not os.path.exists('transcripts') or not os.listdir('transcripts'):
                print("No videos watched yet. Please watch a video first.")
                continue
            run_quiz(load_all_transcripts()[-1]['video_id'], goals)
        elif choice == "3":
            if not os.path.exists('transcripts') or not os.listdir('transcripts'):
                print("No videos watched yet. Please watch a video first.")
                continue
            notes = generate_notes(load_all_transcripts()[-1]['video_id'], goals)
            print("\nIn-depth Notes:")
            print(notes)
        elif choice == "4":
            chat_with_knowledge(goals)
        elif choice == "5":
            save_rag_data()
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()