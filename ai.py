import openai
from logging_config import logger

API_KEY = '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'


def ai_transcript_audio_to_text(audio_file_path: str) -> str | None:
    logger.info(f"AI TRANSCRIPT AUDIO TO TEXT - {audio_file_path}")
    client = openai.OpenAI(
        api_key=API_KEY
    )
    try:
        audio_file= open(audio_file_path, "rb")
    except Exception as ex:
        logger.exception(f"!!! FAILED OPENING FILE - {ex}")
    else:
        try:
            transcription = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
            return transcription.text
        except Exception as ex:
            logger.exception(f"!!! OPEN AI API ERROR - {ex}")
