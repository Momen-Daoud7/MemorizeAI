import os
import json
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptAvailable
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
COLLECTIONS_FILE = 'collections.json'
GEMINI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
GMAIL_USER = "impoweredlab@gmail.com"
GMAIL_PASSWORD = "yicc hbck atdu dlkm"
RECIPIENT_EMAILS = ["momenfbi123@gmail.com","ahmed@impoweredlab.com"]
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 18192,
}

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction="You're a YouTube summarizer assistant. Your job is to create high-quality summaries that represent the main ideas, quotes,analogies and key points from the user's text input, focusing on aspects relevant to their stated goals."
    )
def get_authenticated_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('youtube', 'v3', credentials=creds)

def get_recent_videos(youtube, channel_id, published_after):
    videos = []
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        type="video",
        order="date",
        publishedAfter=published_after.isoformat() + "Z",
        maxResults=50
    )
    while request:
        response = request.execute()
        for item in response['items']:
            videos.append({
                'title': item['snippet']['title'],
                'video_id': item['id']['videoId'],
                'published_at': datetime.strptime(item['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ"),
                'channel_title': item['snippet']['channelTitle']
            })
        request = youtube.search().list_next(request, response)
    return videos

def get_channel_info(youtube, channel_id):
    request = youtube.channels().list(
        part="snippet",
        id=channel_id
    )
    response = request.execute()
    return response['items'][0]['snippet']['title']

def get_video_transcript(video_id, max_retries=3, delay=2):
    for attempt in range(max_retries):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return ' '.join([entry['text'] for entry in transcript])
        except TranscriptsDisabled:
            return "Transcripts are disabled for this video."
        except NoTranscriptAvailable:
            if attempt < max_retries - 1:  # if it's not the last attempt
                print(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # exponential backoff
            else:
                return "No transcript is available for this video after multiple attempts."
        except Exception as e:
            if attempt < max_retries - 1:  # if it's not the last attempt
                print(f"Attempt {attempt + 1} failed due to error: {str(e)}. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # exponential backoff
            else:
                return f"An error occurred while fetching the transcript: {str(e)}"
    
    return "Failed to fetch transcript after multiple attempts."

def summarize_transcript(transcript, title):
    prompt = f"Please summarize the following content, focusing on aspects relevant to these goals:\n\n{transcript}"
    response = model.generate_content(prompt)
    return response.text

def load_collections():
    if os.path.exists(COLLECTIONS_FILE):
        with open(COLLECTIONS_FILE, 'r') as f:
            return json.load(f)
    return {
        "AI News": [
            "UCbY9xX3_jW5c2fjlZVBI4cg",  # MKBHD
            "UChpleBmo18P08aKCIgti38g",  # Linus Tech Tips
            "UCawZsQWqfGSbCI5yjkdVkTA",
            "UCUTF61UNExRdjmoK5mXwWfQ",
            "UC5l7RouTQ60oUjLjt1Nh-UQ"
        ],
        # "Podcasts": [
        #     "UCGX7nGXpz-CmO_Arg-cgJ7A",  # Joe Scott
        #     "UCSHZKyawb77ixDdsGog4iWA",  # SciShow
        # ]
    }

def send_email(subject, body, recipients):
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = ', '.join(recipients)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USER, recipients, msg.as_string())
        server.close()
        print(f"Email sent successfully to {', '.join(recipients)}!")
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")

def format_email_body(all_summaries):
    body = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            h2 { color: #2980b9; }
            h3 { color: #16a085; }
            .video-summary { background-color: #f8f9fa; border-left: 4px solid #3498db; padding: 15px; margin-bottom: 20px; border-radius: 4px; }
            a { color: #3498db; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
    """
    for collection, summaries in all_summaries.items():
        body += f"<h1>{collection}</h1>"
        for summary in summaries:
            body += "<div class='video-summary'>"
            body += f"<h2>{summary['channel']}</h2>"
            body += f"<h3>{summary['title']}</h3>"
            body += f"<p><strong>Published:</strong> {summary['published_at']}</p>"
            body += f"<p><strong>Link:</strong> <a href='https://www.youtube.com/watch?v={summary['video_id']}'>Watch Video</a></p>"
            
            # Remove asterisks and split into paragraphs
            cleaned_summary = summary['summary'].replace('*', '')
            paragraphs = cleaned_summary.split('\n')
            for paragraph in paragraphs:
                if paragraph.strip():
                    body += f"<p>{paragraph}</p>"
            
            body += "</div>"
    body += "</body></html>"
    return body

def main():
    youtube = get_authenticated_service()
    collections = load_collections()

    published_after = datetime.utcnow() - timedelta(days=1)  # Get videos from the last 24 hours

    all_summaries = {}

    for collection_name, channel_ids in collections.items():
        print(f"\nTracking collection: {collection_name}")
        collection_summaries = []
        
        for channel_id in channel_ids:
            channel_title = get_channel_info(youtube, channel_id)
            recent_videos = get_recent_videos(youtube, channel_id, published_after)

            print(f"\nChannel: {channel_title}")
            print(f"Found {len(recent_videos)} recent videos:")
            
            for video in recent_videos:
                print(f"Processing: {video['title']}")
                transcript = get_video_transcript(video['video_id'])
                summary = summarize_transcript(transcript, video['title'])
                
                collection_summaries.append({
                    'channel': channel_title,
                    'title': video['title'],
                    'video_id': video['video_id'],
                    'published_at': video['published_at'],
                    'summary': summary
                })

        all_summaries[collection_name] = collection_summaries

    # Format and send email
    email_body = format_email_body(all_summaries)
    send_email("Your Daily YouTube Channel Summary", email_body, RECIPIENT_EMAILS)

    # Save summaries to a JSON file (optional, you can remove if not needed)
    with open('video_summaries.json', 'w') as f:
        json.dump(all_summaries, f, indent=2, default=str)

if __name__ == '__main__':
    main()