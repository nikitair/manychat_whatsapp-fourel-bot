import httpx
import time
import io
from pydub import AudioSegment
from logging_config import logger

    
def download_audio(audio_url) -> str | None:
    logger.info(f"DOWNLOAD AUDIO - {audio_url}")
    response = httpx.get(audio_url)
    status_code = response.status_code
    logger.info(f"STATUS CODE - {status_code}")
    
    if status_code == 200:
        audio_data = response.content
        file_name = f"{str(int(time.time))}_audio.ogg"
        
        with open(file_name, "wb") as file:
            file.write(audio_data)
        return file_name
            
    
