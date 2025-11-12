import streamlit as st
import os
import google.generativeai as genai
from langchain_groq import ChatGroq
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable, FetchedTranscript
from dotenv import load_dotenv
load_dotenv()

api_key = st.secrets("GROQ_API_KEY")

# genai.configure(api_key="AIzaSyCDIoZUVq0HDL5ili4KMvT1Qe8epm00y2g")
llm = ChatGroq(model="openai/gpt-oss-20b", api_key=api_key)

prompt = """ You are Youtube video summarizer. You will be taking the transcript text
and summarize the entire video and providing the important summary in points
within 250 words. The transcript text will be appended here:
"""

def get_video_id(youtube_video_url):
    """Safely extracts the video ID from different YouTube URL formats."""
    if "v=" in youtube_video_url:
        return youtube_video_url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in youtube_video_url:
        return youtube_video_url.split("youtu.be/")[1].split("?")[0]
    else:
        return None

def extract_transcript_details(youtube_video_url):
    try:
        video_id = get_video_id(youtube_video_url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        # Fetch transcript list
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)

        # Collect available languages
        available_langs = [t.language_code for t in transcript_list]
        st.info(f"Available transcript languages: {', '.join(available_langs)}")

        if not available_langs:
            st.error("No transcripts available for this video in any language.")
            return None

        # Pick the first transcript available (auto choice)
        first_transcript = transcript_list.find_transcript([available_langs[0]])
        print(first_transcript)
        fetched = first_transcript.fetch()


        print(fetched)
        # Build final transcript text
        transcript = " ".join([item.text for item in fetched])

        return transcript

    except NoTranscriptFound:
        st.error("No transcript found for this video.")
        return None

    except TranscriptsDisabled:
        st.error("Transcripts are disabled for this video by the creator.")
        return None

    except VideoUnavailable:
        st.error("The video is unavailable, private, or the ID is incorrect.")
        return None

    except ValueError as e:
        st.error(f"Error: {e}")
        return None

    except Exception as e:
        st.error(f"Unexpected error while fetching transcript: {e}")
        return None

    
def generate_gemini_content(transcript_text,prompt):
#     model = genai.GenerativeModel("models/gemini-2.5-pro")
    messages = [
            ("system", prompt),
            ("human", transcript_text),
        ]
    # response = model.generate_content(prompt+transcript_text)
    response = llm.invoke(messages)
    return response.text

st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube link:")

if youtube_link:
    try:
        if "v=" in youtube_link:
            video_id = youtube_link.split("v=")[1].split("&")[0]
        elif "youtu.be/" in youtube_link:
            video_id = youtube_link.split("youtu.be/")[1].split("?")[0]
        else:
            video_id = None
            st.error("Please enter a valid YouTube video URL.")

        if video_id:
            st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", width="stretch")

    except IndexError:
        st.error("Please ensure the YouTube URL is correctly formatted.")
    except Exception as e:
        pass

if st.button("Get Detailed Notes"):
    if not youtube_link:
        st.error("Please enter a YouTube link first.")
    else:
        with st.spinner("Fetching transcript..."):
            transcript_text = extract_transcript_details(youtube_link)

        if transcript_text:
            with st.spinner("Generating summary..."):
                summary = generate_gemini_content(transcript_text, prompt)

            st.markdown('## Detailed Notes:')
            st.write(summary)
        else:
            st.warning("Transcript could not be retrieved for this video.")


# import streamlit as st
# import os
# from dotenv import load_dotenv
# from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
# from langchain_groq import ChatGroq


# import requests


# load_dotenv()

# http_proxy = os.getenv("HTTP_PROXY")
# https_proxy = os.getenv("HTTPS_PROXY")

# print("HTTP_PROXY:", http_proxy)

# if http_proxy or https_proxy:
#     st.success("Proxy configured via standard HTTP_PROXY/HTTPS_PROXY environment variables.")
    
# else:
#     st.warning("No standard proxy variables (HTTP_PROXY/HTTPS_PROXY) found. Add them to secrets if needed.")

# llm = ChatGroq(model="openai/gpt-oss-20b",
#                api_key="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")

# prompt = """You are a YouTube video summarizer. You will take the transcript text
# and summarize the entire video, providing the important summary in points
# within 250 words. The transcript text will be appended here:
# """


# def get_video_id(youtube_video_url):
#     """Safely extracts the video ID from different YouTube URL formats."""
#     if "v=" in youtube_video_url:
#         return youtube_video_url.split("v=")[1].split("&")[0]
#     elif "youtu.be/" in youtube_video_url:
#         return youtube_video_url.split("youtu.be/")[1].split("?")[0]
#     else:
#         return None


# def extract_transcript_details(youtube_video_url):
#     """Fetch transcript using YouTubeTranscriptApi."""
#     try:
#         video_id = get_video_id(youtube_video_url)
#         if not video_id:
#             raise ValueError("Invalid YouTube URL")

        
#         ytt_api = YouTubeTranscriptApi()
#         transcript_list = ytt_api.list(video_id)

        
#         available_langs = [t.language_code for t in transcript_list]
#         st.info(f"Available transcript languages: {', '.join(available_langs)}")

#         if not available_langs:
#             st.error("No transcripts available for this video in any language.")
#             return None
       
#         first_transcript = transcript_list.find_transcript([available_langs[0]])
#         fetched = first_transcript.fetch()
#         transcript = " ".join([item["text"] for item in fetched])

#         return transcript

#     except NoTranscriptFound:
#         st.error("No transcript found for this video.")
#     except TranscriptsDisabled:
#         st.error("Transcripts are disabled by the creator.")
#     except VideoUnavailable:
#         st.error("The video is unavailable or private.")
#     except ValueError as e:
#         st.error(f"Error: {e}")
#     except Exception as e:
#         st.error(f"Unexpected error while fetching transcript: {e}")

#     return None


# def generate_summary(transcript_text, prompt):
#     """Generate summary using Groq LLM."""
#     messages = [
#         ("system", prompt),
#         ("human", transcript_text),
#     ]
#     response = llm.invoke(messages)
#     return response.text


# st.title("🎥 YouTube Transcript to Detailed Notes Converter")
# youtube_link = st.text_input("Enter YouTube video link:")

# if youtube_link:
#     video_id = get_video_id(youtube_link)
#     if video_id:
#         st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
#     else:
#         st.error("Please enter a valid YouTube video URL.")

# if st.button("Get Detailed Notes"):
#     if not youtube_link:
#         st.error("Please enter a YouTube link first.")
#     else:
#         with st.spinner("Fetching transcript..."):
#             transcript_text = extract_transcript_details(youtube_link)

#         if transcript_text:
#             with st.spinner("Generating summary..."):
#                 summary = generate_summary(transcript_text, prompt)

#             st.markdown("## 📝 Detailed Notes:")
#             st.write(summary)
#         else:

#             st.warning("Transcript could not be retrieved for this video.")

