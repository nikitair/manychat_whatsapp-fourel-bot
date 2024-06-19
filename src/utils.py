import httpx
import time
import io
from config.logging_config import logger
from config.database import postgres

    
def download_audio(audio_url) -> str | None:
    logger.info(f"DOWNLOAD AUDIO - {audio_url}")
    if audio_url:
        response = httpx.get(audio_url)
        status_code = response.status_code
        logger.info(f"STATUS CODE - {status_code}")
        
        if status_code == 200:
            audio_data = response.content
            file_name = f"{int(time.time())}_audio.ogg"
            
            with open(file_name, "wb") as file:
                file.write(audio_data)
            return file_name
            


def sql_save_quote(email: str, 
                   phone_number: str, 
                   broker_name: str,
                   quote_body: str,
                   page_id: str,
                   database_id: str
                   ) -> bool:
    logger.info(f"SQL INSERT QUOTE - ({email} | {quote_body} | p:{page_id} | d:{database_id})")
    
    if page_id and database_id:
    
        query = """
            INSERT INTO whatsapp_quotes
            (
                email, 
                phone_number, 
                broker_name,
                quote_body,
                page_id,
                database_id
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            );
        """
        params = ([email, phone_number, quote_body, page_id, database_id])
    else:
        query = """
            INSERT INTO whatsapp_quotes
            (
                email, 
                phone_number, 
                broker_name,
                quote_body
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            );
        """
        params = ([email, phone_number, quote_body])
    logger.info(f"QUERY => {query}")
    insert_result = postgres.execute_with_connection(
        func=postgres.insert_executor,
        query=query,
        params=params
    )
    return insert_result
