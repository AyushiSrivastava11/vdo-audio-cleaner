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

load_dotenv()

def transcribe_audio(audio_file):
    credentials = service_account.Credentials.from_service_account_file(os.environ.get("PATH_TO_GOOGLE_API"))
    client = speech.SpeechClient(credentials=credentials)
    
    
    with open(audio_file, "rb") as audio:
        content = audio.read()

    audio_data = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(language_code="en-US", enable_automatic_punctuation=True)

    # Use long-running recognize to handle larger files
    operation = client.long_running_recognize(config=config, audio=audio_data)

    # Wait for the operation to complete
    response = operation.result(timeout=600)  # Wait for up to 10 minutes

    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + " "

    print("The transcript is : " + transcript)
    return transcript


def process_video(video_file):
    # Extract audio
    audio_file = extract_audio(video_file)
    print("Audio Extracted")
    
    # Transcribe
    transcript = transcribe_audio(audio_file)

    print("Audio Transcribed")

    
    # Correct transcription
    corrected_text = correct_transcription(transcript)
    print("TEXT Transcribed")

    
    # Synthesize new audio
    new_audio_file = synthesize_audio(corrected_text)
    print("TEXT to AUDIO")

    # return "HELLO WORLD"
    # return "/home/ayu/Downloads/Replace your UMMs & AHHs with this....mp4"

    
    # Replace old audio with new audio in the video
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
    credentials = service_account.Credentials.from_service_account_file(os.environ.get("PATH_TO_GOOGLE_API"))
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)
    
    voice = texttospeech.VoiceSelectionParams(language_code="en-US", name="en-US-Standard-J")
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    
    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    
    audio_path = "synthesized_audio.mp3"
    with open(audio_path, "wb") as out:
        out.write(response.audio_content)
    
    return audio_path


def correct_transcription(transcript):
    # Create an instance of the OpenAI client
    client = OpenAI(api_key=os.environ.get("AZURE_OPENAI_KEY"))

    # Prepare the request to correct the transcription
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that corrects grammar and removes filler words."
            },
            {
                "role": "user",
                "content": f"Correct the following text for grammar and remove filler words like 'umm' and 'hmm': {transcript}"
            }
        ],
        model="gpt-4", 
    )

    # Extract the corrected text from the response
    corrected_text = chat_completion['choices'][0]['message']['content'].strip()
    return corrected_text



def extract_audio(video_file):
    # Create a temporary file to save the uploaded video
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(video_file.read())
        temp_video_path = temp_video.name

    # Load the video file from the temp path
    clip = VideoFileClip(temp_video_path)
    audio_path = "temp_audio.wav"
    
    # Extract audio and save to file
    clip.audio.write_audiofile(audio_path)

    # Convert stereo to mono using pydub
    audio = AudioSegment.from_wav(audio_path)
    audio = audio.set_channels(1)  # Convert to mono
    mono_audio_path = "mono_audio.wav"
    audio.export(mono_audio_path, format="wav")

    return mono_audio_path

def upload_video():
    video_file = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])
    return video_file


def main():
    st.title("AI Video Audio Replacement")
    
    # Step 1: Upload a video file
    video_file = upload_video()

    if video_file:
        st.write("Processing Video...")
        
        # Step 2: Process the video (transcribe, correct, synthesize, replace audio)
        output_video_path = process_video(video_file)
        
        # Step 3: Play or download the result
        if output_video_path:
            st.video(output_video_path)
            st.download_button(label="Download Video", data=open(output_video_path, 'rb'), file_name="processed_video.mp4")

if __name__ == '__main__':
    main()
