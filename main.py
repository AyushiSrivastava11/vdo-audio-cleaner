# import streamlit as st
# from moviepy.editor import VideoFileClip
# from google.cloud import speech
# import os
# import openai
# from google.cloud import texttospeech

# def process_video(video_file):
#     # Extract audio
#     return "/home/ayu/Downloads/Replace your UMMs & AHHs with this....mp4"
    
#     audio_file = extract_audio(video_file)
    
#     # Transcribe
#     transcript = transcribe_audio(audio_file)
    
#     # Correct transcription
#     corrected_text = correct_transcription(transcript)
    
#     # Synthesize new audio
#     new_audio_file = synthesize_audio(corrected_text)
    
#     # Replace old audio with new audio in the video
#     output_video_path = replace_audio_in_video(video_file, new_audio_file)
    
#     return output_video_path


# def replace_audio_in_video(video_file, new_audio_file):
#     video = VideoFileClip(video_file)
#     new_audio = AudioFileClip(new_audio_file)
    
#     video_with_new_audio = video.set_audio(new_audio)
#     output_path = "final_video.mp4"
#     video_with_new_audio.write_videofile(output_path, codec="libx264", audio_codec="aac")
    
#     return output_path


# def synthesize_audio(text):
#     client = texttospeech.TextToSpeechClient()
#     input_text = texttospeech.SynthesisInput(text=text)
    
#     voice = texttospeech.VoiceSelectionParams(language_code="en-US", name="en-US-Standard-J")
#     audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
    
#     response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    
#     audio_path = "synthesized_audio.mp3"
#     with open(audio_path, "wb") as out:
#         out.write(response.audio_content)
    
#     return audio_path


# def correct_transcription(transcript):
#     openai.api_key = os.getenv("AZURE_OPENAI_KEY")

#     response = openai.Completion.create(
#         engine="gpt-4o",
#         prompt=f"Correct the following text for grammar and remove filler words like 'umm' and 'hmm': {transcript}",
#         max_tokens=500
#     )
    
#     corrected_text = response.choices[0].text.strip()
#     return corrected_text


# def transcribe_audio(audio_file):
#     client = speech.SpeechClient()
    
#     with open(audio_file, "rb") as audio:
#         content = audio.read()

#     audio_data = speech.RecognitionAudio(content=content)
#     config = speech.RecognitionConfig(language_code="en-US")

#     response = client.recognize(config=config, audio=audio_data)

#     transcript = ""
#     for result in response.results:
#         transcript += result.alternatives[0].transcript + " "
    
#     return transcript


# def extract_audio(video_file):
#     clip = VideoFileClip(video_file)
#     audio_path = "temp_audio.wav"
#     clip.audio.write_audiofile(audio_path)
#     return audio_path


# def upload_video():
#     video_file = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])
#     return video_file


# def main():
#     st.title("AI Video Audio Replacement")
    
#     # Step 1: Upload a video file
#     video_file = upload_video()

#     if video_file:
#         st.write("Processing Video...")
        
#         # Step 2: Process the video (transcribe, correct, synthesize, replace audio)
#         output_video_path = process_video(video_file)
        
#         # Step 3: Play or download the result
#         if output_video_path:
#             st.video(output_video_path)
#             st.download_button(label="Download Video", data=open(output_video_path, 'rb'), file_name="processed_video.mp4")

# if __name__ == '__main__':
#     main()



import streamlit as st
from moviepy.editor import VideoFileClip, AudioFileClip
from google.cloud import speech
import os
import openai
from google.cloud import texttospeech
import tempfile

def process_video(video_file):
    # Extract audio
    audio_file = extract_audio(video_file)
    
    # Transcribe
    transcript = transcribe_audio(audio_file)
    print(transcript)
    return "/home/ayu/Downloads/Replace your UMMs & AHHs with this....mp4"

    
    # Correct transcription
    corrected_text = correct_transcription(transcript)
    
    # Synthesize new audio
    new_audio_file = synthesize_audio(corrected_text)
    
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
    openai.api_key = os.getenv("AZURE_OPENAI_KEY")

    response = openai.Completion.create(
        engine="gpt-4o",
        prompt=f"Correct the following text for grammar and remove filler words like 'umm' and 'hmm': {transcript}",
        max_tokens=500
    )
    
    corrected_text = response.choices[0].text.strip()
    return corrected_text


def transcribe_audio(audio_file):
    client = speech.SpeechClient()
    
    with open(audio_file, "rb") as audio:
        content = audio.read()

    audio_data = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(language_code="en-US")

    response = client.recognize(config=config, audio=audio_data)

    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript + " "
    
    return transcript


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
    
    return audio_path


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
