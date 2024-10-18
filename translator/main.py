import os
from dotenv import load_dotenv
import assemblyai as aai
from translate import Translator
from elevenlabs import stream
from elevenlabs.client import ElevenLabs

load_dotenv()

# getting API keys
AAI_API_KEY = os.getenv("ASSEMBLY_AI_API_KEY")
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")

#voices
ELEVEN_LAB_VOICES = {
    "charlotte": "XB0fDUnXU5powFXDhCwa"
}

class Voice_To_Voice_Session:
    def __init__(self):
        aai.settings.api_key = AAI_API_KEY
        
        self.client = ElevenLabs(
        api_key= ELEVEN_LABS_API_KEY,
    )
        
        self.transcriber = None
        
        self.translation_text = ''

    # Step one: get english transcript
    def start_transcription(self):
        print(f"Realtime transcription started", end='\r\n')
        
        self.transcriber = aai.RealtimeTranscriber(
            sample_rate=16_000,
            encoding=aai.AudioEncoding.pcm_s16le,
            on_data=self.on_data,
            on_error=self.on_error,
            on_open=self.on_open,
            on_close=self.on_close,
            )
        
        # self.transcriber.configure_end_utterance_silence_threshold(1000)
        self.transcriber.connect()
        
        microphone_stream = aai.extras.MicrophoneStream(sample_rate=16_000)
        self.transcriber.stream(microphone_stream) #streaming audio into transcriber
        
    def translate_text(self, text: str) -> str:    
        translator = Translator(from_lang="en", to_lang='de')
        translation = translator.translate(text)
        return translation
    
    def generate_ai_voice(self, partial_transcribed_text):
        self.stop_transcription()
        # translate text
        
        # translated_text = self.translate_text(partial_transcribed_text)
        translated_text = partial_transcribed_text # workaround
        # print(translated_text)
        
        text_buffer = ''
        full_text = ''
        for chunk in translated_text:
            # print({"chunk": chunk})
            text_buffer += chunk
            
        if(text_buffer.endswith('.')):
            audio_stream = self.client.generate(text=full_text, model='eleven_turbo_v2_5', stream=True)
            # print(text_buffer, end='\n', flush=True)
            stream(audio_stream)
            full_text += text_buffer
            text_buffer = ''
            
        if text_buffer:
            audio_stream = self.client.generate(text=text_buffer, model='eleven_turbo_v2_5', stream=True)
            # print(text_buffer, end='\n', flush=True)
            stream(audio_stream)
            full_text += text_buffer
            
        self.start_transcription()
        
    def stop_transcription(self):
            self.transcriber.close()
            self.transcriber = None
    
    def on_open(self, session_opened: aai.RealtimeSessionOpened):
        #print("Session ID:", session_opened.session_id)
        return

    def on_data(self, transcript: aai.RealtimeTranscript):
        if not transcript.text:
            return

        if isinstance(transcript, aai.RealtimeFinalTranscript):
            self.generate_ai_voice(transcript.text)
            print(transcript.text)
        else:
            print(transcript.text, end="\r")
            # self.generate_ai_voice(transcript.text)
            # print(' ')

    def on_error(self, error: aai.RealtimeError):
        #print("An error occurred:", error)
        return

    def on_close(self):
        #print("Closing Session")
        return

voice_to_voice_instance = Voice_To_Voice_Session()
voice_to_voice_instance.start_transcription()