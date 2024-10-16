import os
from dotenv import load_dotenv
import assemblyai as aai
from translate import Translator
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import uuid
import subprocess

def play_audio(file_path):
    # or stream audio back to client 
    subprocess.run(['ffplay', '-nodisp', '-autoexit', file_path])

load_dotenv()
# getting API keys
AAI_API_KEY = os.getenv("ASSEMBLY_AI_API_KEY")
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")

# Eleven labs voices
ELEVEN_LAB_VOICES = {
    "charlotte": "XB0fDUnXU5powFXDhCwa"
}

# creating aai transcriber
aai.settings.api_key = AAI_API_KEY

config = aai.TranscriptionConfig(speaker_labels=True)

# temporary auth token 30min(1800 sec) duration
token = aai.RealtimeTranscriber.create_temporary_token(
    expires_in=1800
)

def text_to_speech(text: str) -> str:

    # ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    client = ElevenLabs(
        api_key= ELEVEN_LABS_API_KEY,
    )
    
    response = client.text_to_speech.convert(
        voice_id="XB0fDUnXU5powFXDhCwa", #clone your voice on elevenlabs dashboard and copy the id
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2", # use the turbo model for low latency, for other languages use the `eleven_multilingual_v2`
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.8,
            style=0.5,
            use_speaker_boost=True,
        ),
    )

    save_file_path = f"{uuid.uuid4()}.mp3"

    # Writing the audio to a file
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

    print(f"{save_file_path}: A new audio file was saved successfully!")

    # Return the path of the saved audio file
    return save_file_path

def translate_text(text: str) -> str:
    # languages = ["de"]
    # list_translations = []

    # for lan in languages:
    translator = Translator(from_lang="en", to_lang='de')
    translation = translator.translate(text)
    # list_translations.append(translation)

    return translation


def on_open(session_opened: aai.RealtimeSessionOpened):
    print("Session opened with ID:", session_opened.session_id)


def on_error(error: aai.RealtimeError):
    print("Error:", error)


def on_close():
    print("Session closed")
    
def on_data(transcript: aai.RealtimeTranscript):
    if not transcript.text:
        return

    if isinstance(transcript, aai.RealtimeFinalTranscript):
        # Add new line after final transcript.
        translation=translate_text(transcript.text)
        translated_audio_path=text_to_speech(translation)
        play_audio(translated_audio_path)
        print(translation, end="\r\n")
    else:
        translation_partial=translate_text(transcript.text)
        print(translation_partial, end="\r")
        

# live transcription setup
transcriber = aai.RealtimeTranscriber(
    sample_rate=16_000,
    encoding=aai.AudioEncoding.pcm_s16le,
    token=token,
    end_utterance_silence_threshold=500,
    on_data=on_data,
    on_error=on_error,
    on_open=on_open,
    on_close=on_close,
)
# extra config to consider in optimization disable_partial_transcripts=True

transcriber.connect()

microphone_stream = aai.extras.MicrophoneStream(sample_rate=16_000)

transcriber.stream(microphone_stream)

# transcriber.close()