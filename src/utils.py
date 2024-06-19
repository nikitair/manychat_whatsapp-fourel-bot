import httpx
import time
from config.logging_config import logger
from config.database import postgres


NOTION_API_HEADERS = {
    "Authorization": "Bearer secret_hcJF8bCOLP1ZcOR54a8kmWJ0dFMssHjEOWhSnvA0mN2",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

BROKERS_DATABASE_ID = "b8a10681aded43339ec1dc13dd44ff03"

    
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
       

def sql_get_broker_emails() -> list:
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


def notion_create_broker_page(email: str, phone_number: str, broker_name: str) -> str | None:
    logger.info(f"NOTION CREATE BROKER PAGE - ({email} | {phone_number} | {broker_name})")
    payload = {
        "parent": {"database_id": BROKERS_DATABASE_ID},
        "properties": {
            "Email": {
                "title": [
                    {
                        "text": {
                            "content": email
                        }
                    }
                ]
            },
            "Phone Number": {
                "rich_text": [
                    {
                        "text": {
                            "content": phone_number
                        }
                    }
                ]
            },
            "Name": {
                "rich_text": [
                    {
                        "text": {
                            "content": broker_name
                        }
                    }
                ]
            }
        }
    }
    
    response = httpx.post(
        url="https://api.notion.com/v1/pages",
        headers=NOTION_API_HEADERS,
        json=payload
    )
    
    status_code = response.status_code
    logger.info(f"NOTION API STATUS CODE - ({status_code})")
    if status_code == 200:
        logger.info(f"NOTION SUCCESSFULLY CREATED BROKER PAGE - ({email})")
        return response.json()["id"]
    else:
        logger.error(f"!!! FAILED CREATING NOTION BROKER PAGE - ({email})")
        
        
def notion_create_quotes_database(email: str, page_id: str) -> str | None:
    logger.info(f"NOTION CREATE QUOTES DATABASE - ({email}; p_id: {page_id})")
    payload = {
        "parent": {"page_id": page_id},
        "is_inline": True,
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "Quotes"
                }
            }
        ],
        "properties": {
            "Quote Body": {
                "title": {}
            },
            "Created at": {
                "created_time": {}
            }
        }
    }
    response = httpx.post(
        url="https://api.notion.com/v1/databases",
        headers=NOTION_API_HEADERS,
        json=payload
    )
    status_code = response.status_code
    logger.info(f"NOTION API STATUS CODE - ({status_code})")
    if status_code == 200:
        logger.info(f"NOTION SUCCESSFULLY CREATED QUOTES DATABASE - ({email}; p_id: {page_id})")
        return response.json()["id"]
    else:
        logger.error(f"!!! FAILED CREATING NOTION QUOTES DATABASE - {email}; p_id: {page_id})")
        
        

def notion_register_broker(email: str, phone_number: str, broker_name: str) -> dict:
    result = {
        "success": False,
        "page_id": None,
        "database_id": None
    }
    logger.info(f"NOTION REGISTER BROKER - ({email} | {phone_number} | {broker_name})")
    
    # create page
    page_id = notion_create_broker_page(
        email=email,
        phone_number=phone_number,
        broker_name=broker_name
    )
    logger.info(f"PAGE ID FOR ({email}) - ({page_id})")
    if page_id:
        result["page_id"] = page_id
        
        database_id = notion_create_quotes_database(
            email=email,
            page_id=page_id
        )
        logger.info(f"DATABASE ID FOR ({email}) - ({database_id})")
        if database_id:
            result["database_id"] = database_id
            result["success"] = True
    
    return result
        
        
def sql_update_broker_notion_status(email: str, page_id: str, database_id: str) -> bool:
    logger.info(f"SQL UPDATE BROKER NOTION STATUS - ({email} | p: {page_id} | d: {database_id})")
    query = f"""
        UPDATE whatsapp_brokers
        SET
            in_notion = TRUE,
            page_id = '{page_id}',
            database_id = '{database_id}'
        WHERE
            email = '{email}'
    """
    postgres_response = postgres.execute_with_connection(
        func=postgres.update_executor,
        query=query
    )
    logger.info(f"SQL POSTGRES UPDATE RESPONSE - ({postgres_response})")
    return postgres_response
    

def sql_get_brokers_for_notion_sync() -> list:
    logger.info(f"SQL GET BROKERS FOR NOTION SYNCHRONIZATION")
    query = """
        SELECT
            email,
            phone_number,
            broker_name
        FROM
            whatsapp_brokers
        WHERE
            in_notion = FALSE
    """
    brokers = []
    raw_response = postgres.execute_with_connection(
        func=postgres.select_executor,
        query=query
    )
    logger.debug(f"SQL RAW RESPONSE - ({raw_response})")
    if raw_response:
        for item in raw_response:
            brokers.append(
                {
                    "email": item[0],
                    "phone_number": item[1],
                    "broker_name": item[2]
                }
            )
    return brokers


def sql_get_quotes_for_notion_sync() -> list:
    logger.info(f"SQL GET QUOTES FOR NOTION SYNCHRONIZATION")
    query = """
        SELECT
            quotes.quote_body,
            quotes.id,
            brokers.database_id,
            brokers.email
        FROM
            whatsapp_quotes quotes
        LEFT JOIN whatsapp_brokers brokers
            ON quotes.broker_id = brokers.id
        WHERE
            quotes.in_notion = FALSE
    """
    brokers = []
    raw_response = postgres.execute_with_connection(
        func=postgres.select_executor,
        query=query
    )
    logger.debug(f"SQL RAW RESPONSE - ({raw_response})")
    if raw_response:
        for item in raw_response:
            brokers.append(
                {
                    "quote_body": item[0],
                    "quote_id": item[1],
                    "database_id": item[2],
                    "email": item[3]
                }
            )
    return brokers


def notion_insert_quote(quote_body: str, database_id: str, email: str) -> bool:
    logger.info(f"NOTION INSERT QUOTE - ({email} | {quote_body}; d_id: {database_id})")
    payload = {
        'parent': { 'database_id': database_id },
        'properties': {
            'Quote Body': {
                'title': [
                    {
                        'text': { 'content': quote_body }
                    }
                ]
            }
        }
    }
    response = httpx.post(
        url="https://api.notion.com/v1/pages",
        headers=NOTION_API_HEADERS,
        json=payload
    )
    status_code = response.status_code
    logger.info(f"NOTION API STATUS CODE - ({status_code})")
    if status_code == 200:
        logger.info(f"NOTION SUCCESSFULLY INSERTED QUOTES DATABASE - ({email} | {quote_body}; d_id: {database_id})")
        return True
    else:
        logger.error(f"!!! FAILED INSERTING QUOTE - ({email} | {quote_body}; d_id: {database_id}) - {response.text}")
        
        
        
def sql_update_quote_notion_status(quote_id: int, email: str, quote_body: str) -> bool:
    logger.info(f"SQL UPDATE QUOTE NOTION STATUS - ({email} | id: {quote_id} | {quote_body})")
    query = f"""
        UPDATE whatsapp_quotes
        SET
            in_notion = TRUE
        WHERE
            id = '{quote_id}'
    """
    postgres_response = postgres.execute_with_connection(
        func=postgres.update_executor,
        query=query
    )
    logger.info(f"SQL POSTGRES UPDATE RESPONSE - ({postgres_response})")
    return postgres_response
