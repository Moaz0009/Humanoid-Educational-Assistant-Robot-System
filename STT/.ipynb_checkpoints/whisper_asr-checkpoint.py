import os
os.environ["LD_PRELOAD"] = "/usr/lib/aarch64-linux-gnu/libomp.so.5"


import whisper
from pathlib import Path
import sounddevice as sd
import numpy as np



_model = whisper.load_model("turbo")  

DURATION = 4 # seconds
SAMPLE_RATE = 16000
def record_audio(duration=DURATION, sample_rate=SAMPLE_RATE):
    print("Recording..")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.float32)
    sd.wait()  
    print("\nTranscribing..")
    return audio.flatten()  
    
def transcribe_audio(duration=DURATION,sample_rate=SAMPLE_RATE,language='ar'):
    """
    Transcribes speech from an audio file using OpenAI's Whisper.

    Args:
        duration (int): audio content duration to be recorded.
        sample_rate (int): samplying rate used while recording.
        language (str, optional): Language code (e.g., 'en', 'ar'). If None, Whisper will auto-detect.

    Returns:
        str: The transcribed text.
    """
    audio_data = record_audio(duration,sample_rate)
    
    result = _model.transcribe(audio_data,language=language)
    print(result['text'])
    return result['text']
