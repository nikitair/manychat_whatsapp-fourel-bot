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
       

def sql_get_brokers() -> list:
    logger.info(f"SQL GET BROKERS")
    query = """
        SELECT
            email
        FROM
            whatsapp_brokers
    """
    brokers = []
    raw_response = postgres.execute_with_connection(
        func=postgres.select_executor,
        query=query
    )
    logger.debug(f"SQL RAW RESPONSE - ({raw_response})")
    if raw_response:
        brokers = [item[0] for item in raw_response]
    return brokers


def sql_create_broker(email: str, phone_number: str = None, broker_name: str = None) -> bool:
    logger.info(f"SQL CREATE BROKER - ({email} | {phone_number} | {broker_name})")
    query = """
        INSERT INTO whatsapp_brokers
        (
            email,
            phone_number,
            broker_name
        ) 
        VALUES
        (
            %s,
            %s,
            %s
        );
    """
    postgres_response = postgres.execute_with_connection(
        func=postgres.insert_executor,
        query=query,
        params=(email, phone_number, broker_name)
    )
    logger.info(f"SQL POSTGRES INSERT RESPONSE - ({postgres_response})")
    return postgres_response


def sql_get_broker_id(email: str) -> int | None:
    logger.info(f"SQL GET broker_id - ({email})")
    query = f"""
        SELECT
            id
        FROM
            whatsapp_brokers
        WHERE
            email = '{email}'
        ORDER BY id DESC
        LIMIT 1;
    """
    raw_response = postgres.execute_with_connection(
        func = postgres.select_executor,
        query=query
    )
    logger.debug(f"SQL RAW RESPONSE - ({raw_response})")
    if raw_response:
        return raw_response[0][0]


def sql_create_quote(email: str, quote_body: str):
    logger.info(f"SQL CREATE QUOTE - ({email} | {quote_body})")
    
    # get broker_id
    broker_id = sql_get_broker_id(email)
    logger.info(f"broker_id - ({broker_id})")
    if not broker_id:
        logger.warning(f"! NO BROKERS FOUND; CREATING NEW")
        create_broker = sql_create_broker(email)
        if create_broker:
            logger.info(f"SQL NEW BROKER CREATED")
            broker_id = sql_get_broker_id(email)
    
    if broker_id:
        query = """
            INSERT INTO whatsapp_quotes
            (
                quote_body,
                broker_id
            )
            VALUES
            (
                %s,
                %s
            );
        """
        logger.info(f"SQL INSERTING QUOTE - ({quote_body})")
        postgres_response = postgres.execute_with_connection(
            func=postgres.insert_executor,
            query=query,
            params=(quote_body, broker_id)
        )
        logger.info(f"SQL POSTGRES INSERT RESPONSE - ({postgres_response})")
        return postgres_response

