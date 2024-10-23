import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip
from google.cloud import speech
import os
from dotenv import load_dotenv
from openai import OpenAI
from google.cloud import texttospeech
import tempfile
from google.oauth2 import service_account
from pydub import AudioSegment
import json
import requests

load_dotenv()


# This function transcribes the audio (Basically turns the audio into text)
def transcribe_audio(audio_file):
    
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    if not credentials_path:
        raise ValueError("Google Cloud credentials file path is not set in .env")

    credentials = service_account.Credentials.from_service_account_file(credentials_path)

    client = speech.SpeechClient(credentials=credentials)
    
    
    with open(audio_file, "rb") as audio:
        content = audio.read()

    audio_data = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(language_code="en-US", enable_automatic_punctuation=True)

    operation = client.long_running_recognize(config=config, audio=audio_data)

    response = operation.result(timeout=600)  

    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + " "

    print("The transcript is : " + transcript)
    return transcript

# This is the Processing function that calls the other crucial functions
def process_video(video_file):
   
    audio_file = extract_audio(video_file)
    transcript = transcribe_audio(audio_file)
    corrected_text = correct_transcription(transcript)
    if not corrected_text or corrected_text.strip() == "":
        raise ValueError("Corrected text is empty. Cannot synthesize audio.")
    new_audio_file = synthesize_audio(corrected_text)
    output_video_path = replace_audio_in_video(video_file, new_audio_file)
    return output_video_path


def replace_audio_in_video(video_file, new_audio_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(video_file.read())
        temp_video_path = temp_video.name

    video = VideoFileClip(temp_video_path)
    new_audio = AudioFileClip(new_audio_file)
    
    video_with_new_audio = video.set_audio(new_audio)
    output_path = "final_video.mp4"
    video_with_new_audio.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
    return output_path


def synthesize_audio(text):
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    if not credentials_path:
        raise ValueError("Google Cloud credentials file path is not set in .env")

    credentials = service_account.Credentials.from_service_account_file(credentials_path)

    client = texttospeech.TextToSpeechClient(credentials=credentials)
    
    input_text = texttospeech.SynthesisInput(text=text)
    
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", name="en-US-Standard-J")
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    
    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    
    audio_path = "synthesized_audio.mp3"
    with open(audio_path, "wb") as out:
        out.write(response.audio_content)
    
    return audio_path


def correct_transcription(transcript):
        
    azure_openai_key = os.environ.get("AZURE_OPENAI_KEY")
    azure_openai_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")

    if azure_openai_key and azure_openai_endpoint:
        try:
            headers = {
                "Content-Type": "application/json", 
                "api-key": azure_openai_key  
            }
            
            data = {
                "messages": [{
                    "role": "user", 
                    "content": f"Correct the following text for grammar and remove filler words like 'umm' and 'hmm': {transcript}" 
                    }],  
                "max_tokens": 100  
            }
            
            response = requests.post(azure_openai_endpoint, headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()  
                corrected_text = result["choices"][0]["message"]["content"].strip()

                print(corrected_text)

                return corrected_text
            else:
                print(f"Failed to connect or retrieve response: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Failed to connect or retrieve response: {str(e)}")
    else:
        print("Please enter all the required details.")



def extract_audio(video_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(video_file.read())
        temp_video_path = temp_video.name

    clip = VideoFileClip(temp_video_path)
    audio_path = "temp_audio.wav"
    
    clip.audio.write_audiofile(audio_path)

    audio = AudioSegment.from_wav(audio_path)
    audio = audio.set_channels(1)  
    mono_audio_path = "mono_audio.wav"
    audio.export(mono_audio_path, format="wav")

    return mono_audio_path

def upload_video():
    video_file = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])
    return video_file


def main():
    st.title("AI Video Audio Replacement")
    
    video_file = upload_video()

    if video_file:
        st.write("Processing Video...")
        
        output_video_path = process_video(video_file)
        
        if output_video_path:
            st.video(output_video_path)
            st.download_button(label="Download Video", data=open(output_video_path, 'rb'), file_name="processed_video.mp4")

if __name__ == '__main__':
    main()
