from config.logging_config import logger
import schemas
import ai
import utils
import os


def get_registered_brokers():
    logger.info(f"GET REGISTERED BROKERS")
    brokers = utils.sql_get_broker_emails()
    logger.info(f"REGISTERED BROKERS - ({brokers})")
    return {"emails": brokers}


def register_broker(request: schemas.RegisterBroker):
    result = {"success": False}
    email = request.email
    phone_number = request.phone_number
    broker_name = request.name
    logger.info(f"REGISTER BROKER - ({email} | {phone_number} | {broker_name})")
    
    created_broker = utils.sql_create_broker(
        email=email,
        phone_number=phone_number,
        broker_name=broker_name
    )
    if created_broker:
        logger.info(f"SUCCESSFULLY REGISTERED BROKER - ({email})")
        result["success"] = True
    return result


def save_quote(request: schemas.InsertQuoteRequest):
    result = {"success": False}
    email = request.email
    quote_body = request.quote_body
    logger.info(f"SAVE QUOTE - ({email} | {quote_body})")
    
    saved_quote = utils.sql_create_quote(
        email=email,
        quote_body=quote_body
    )
    if saved_quote:
        logger.info(f"SUCCESSFULLY SAVED QUOTE - ({email} | {quote_body})")
        result["success"] = True
    
    return result
    

def convert_voice_to_text(request: schemas.VoiceToText):
    audio_url = request.audio_url
    logger.info(f"CONVERT VOICE TO TEXT - {audio_url}")
    result = {
        "text": audio_url
    }
    
    # download audio
    audio_file_path = utils.download_audio(audio_url)
    logger.info(f"DOWNLOADED AUDIO FILE PATH - {audio_file_path}")
    if audio_file_path:
        # transcript with open ai api
        transcription = ai.ai_transcript_audio_to_text(audio_file_path)
        logger.info(f"OPEN AI TRANSCRIPTION - {transcription}")
        
        if transcription:
            result["text"] = transcription
            
        # delete old audio file
        try:
            os.remove(audio_file_path)
            logger.info(f"FILE DELETED - {audio_file_path}")
        except Exception as ex:
            logger.exception(f"!!! FAILED DELETING AUDIO FILE - {ex}")
            
    return result


def sync_brokers():
    logger.info(f"SYNCHRONIZE BROKERS WITH NOTION")
    result = {
        "sync_brokers": []
        }
    
    # get brokers to sync
    brokers_to_sync = utils.sql_get_brokers_for_notion_sync()
    logger.info(f"{len(brokers_to_sync)} BROKERS FOUND FOR SYNC")
    logger.info(f"BROKERS TO SYNC - ({brokers_to_sync})")
    if not brokers_to_sync:
        logger.warning("NO BROKERS TO SYNC")
        return result
    
    # iterate through brokers
    for i, broker in enumerate(brokers_to_sync, start=1):
        email = broker["email"]
        phone_number = broker["phone_number"]
        broker_name = broker["broker_name"]
        logger.info(f"BROKER #{i}: ({email} | {phone_number} | {broker_name})")
        
        # register in notion
        registered = utils.notion_register_broker(
            email=email,
            phone_number=phone_number,
            broker_name=broker_name
        )
        logger.info(f"NOTION REGISTRATION RESULT - ({registered})")
        if registered["success"]:
            
            # update DB
            page_id = registered["page_id"]
            database_id = registered["database_id"]
            
            updated = utils.sql_update_broker_notion_status(
                email=email,
                page_id=page_id,
                database_id=database_id
            )
            if updated:
                logger.info(f"BROKER - ({email}) SUCCESSFULLY SYNCHRONIZED")
                result["sync_brokers"].append(broker)
    return result


def sync_quotes():
    logger.info(f"SYNCHRONIZE QUOTES WITH NOTION")
    result = {
        "sync_quotes": []
        }
    
    # get quotes to sync
    quotes_to_sync = utils.sql_get_quotes_for_notion_sync()
    logger.info(f"{len(quotes_to_sync)} QOUTES FOUND FOR SYNC")
    logger.info(f"QUOTES TO SYNC - ({quotes_to_sync})")
    if not quotes_to_sync:
        logger.warning("NO QUOTES TO SYNC")
        return result
    
    # iterate through brokers
    for i, quote in enumerate(quotes_to_sync, start=1):
        quote_body = quote["quote_body"]
        quote_id = quote["quote_id"]
        database_id = quote["database_id"]
        email = quote["email"]
        
        logger.info(f"QUOTE #{i}: ({email} | {quote_body} | d_id: {database_id})")
        
        # insert to notion
        inserted = utils.notion_insert_quote(
            quote_body=quote_body,
            database_id=database_id,
            email=email
        )
        logger.info(f"NOTION INSERTION RESULT - ({inserted})")
        if inserted:
            
            #update DB
            updated = utils.sql_update_quote_notion_status(
                quote_id=quote_id,
                email=email,
                quote_body=quote_body
            )
            if updated:
                logger.info(f"QUOTE - ({email} | id: {quote_id} | {quote_body}) SUCCESSFULLY SYNCHRONIZED")
                result["sync_quotes"].append(quote)
    return result
        
        


# LEGACY
# def get_brokers_emails():
#     logger.info(f"RETRIEVE EMAILS IN DB - {BROKERS_DATABASE_ID}")
#     URL = f"https://api.notion.com/v1/databases/{BROKERS_DATABASE_ID}/query"

#     result = {
#         "emails": []
#     }
#     has_more = True
#     next_cursor = None

#     while has_more:
#         payload = {}
#         if next_cursor:
#             payload['start_cursor'] = next_cursor

#         response = httpx.post(URL, headers=NOTION_API_HEADERS, json=payload)
#         status_code = response.status_code
#         logger.info(f"NOTION API STATUS CODE - {status_code}")

#         if status_code == 200:
#             data = response.json()
#             results = data.get('results', [])
#             logger.debug(f"RAW DB DATA - {results}")

#             for page in results:
#                 email_property = page['properties'].get('Email')
#                 if email_property and email_property['type'] == 'title':
#                     email_title = email_property.get('title', [])
#                     for title_item in email_title:
#                         if title_item['type'] == 'text':
#                             result["emails"].append(
#                                 title_item['text']['content'])

#             has_more = data.get('has_more', False)
#             next_cursor = data.get('next_cursor')
#         else:
#             logger.error(f"!!! Failed to retrieve data: {response.text}")
#             has_more = False

#     logger.info(f"FOUND EMAILS - {result['emails']}")
#     return result


# def create_whatsapp_bot_database(page_id, email: str = None):
#     logger.info(f"CREATE WhatsApp DATABASE FOR - {email} ON PAGE - {page_id}")
#     URL = "https://api.notion.com/v1/databases"

#     data = {
#         "parent": {"page_id": page_id},
#         "title": [
#             {
#                 "type": "text",
#                 "text": {
#                     "content": "WhatsApp Bot"
#                 }
#             }
#         ],
#         "properties": {
#             "Quote Body": {
#                 "title": {}
#             },
#             "Created at": {
#                 "created_time": {}
#             }
#         }
#     }

#     response = httpx.post(URL, headers=NOTION_API_HEADERS, json=data)
#     status_code = response.status_code
#     logger.info(f"NOTION API STATUS CODE - {status_code}")

#     if status_code == 200:
#         new_database = response.json()
#         logger.debug(f"RAW NEW DATABASE DATA - {new_database}")
#         logger.info(f"WhatsApp DATABASE CREATED FOR - {email}. Database ID: {new_database['id']}")
#         return new_database
#     else:
#         logger.error(f"!!! FAILED CREATING WhatsApp BOT DATABASE FOR - {email}: {response.text}")
#         return None


# def register_broker(request: schemas.RegisterBroker):
#     logger.info(f"REGISTER BROKER IN DB - {BROKERS_DATABASE_ID}")
#     URL = "https://api.notion.com/v1/pages"

#     email = request.email
#     phone_number = request.phone_number
#     name = request.name

#     logger.info(f"BROKER DATA - {email} | {phone_number} | {name}")

#     data = {
#         "parent": {"database_id": BROKERS_DATABASE_ID},
#         "properties": {
#             "Email": {
#                 "title": [
#                     {
#                         "type": "text",
#                         "text": {
#                             "content": email
#                         }
#                     }
#                 ]
#             },
#             "Phone Number": {
#                 "rich_text": [
#                     {
#                         "type": "text",
#                         "text": {
#                             "content": phone_number
#                         }
#                     }
#                 ]
#             },
#             "Name": {
#                 "rich_text": [
#                     {
#                         "type": "text",
#                         "text": {
#                             "content": name
#                         }
#                     }
#                 ]
#             }
#         }
#     }

#     response = httpx.post(URL, headers=NOTION_API_HEADERS, json=data)
#     status_code = response.status_code
#     logger.info(f"NOTION API STATUS CODE - {status_code}")

#     if status_code == 200:
#         new_page = response.json()
#         logger.debug(f"RAW NEW PAGE DATA - {new_page}")
#         time.sleep(2)
#         page_id = new_page["id"]
#         logger.info(f"CREATED PAGE FOR BROKER - {email}; Page ID: {page_id}")

#         # Now create a new database on the created page
#         database_response = create_whatsapp_bot_database(page_id)
#         if database_response:
#             logger.info(f"BROKER - {email} - SUCCESSFULLY REGISTERED")
            
#             # insert to sql database
#             # sql.sql_insert_broker(
#             #     email=email,
#             #     phone_number=phone_number,
#             #     name=name,
#             #     page_id=page_id,
#             #     database_id=database_response["id"]
#             # )
            
#             return {
#                 "page_id": page_id,
#                 "database_id": database_response["id"]
#             }
#     else:
#         logger.error(f"Failed to insert record: {response.text}")


# def insert_quote_request(request: schemas.InsertQuoteRequest):
#     result = {
#         "success": True,
#         "error": None
#     }

#     database_id = request.database_id
#     quote_body = request.quote_body
#     email = request.email

#     phone_number = request.phone_number
#     broker_name = request.broker_name
#     quote_body = request.quote_body
#     database_id = request.database_id
#     page_id = request.page_id

#     logger.info(f"INSERT QUOTE REQUEST FOR - {email} TO DB - {database_id}")
#     logger.info(f"INSERT DATA - {quote_body}")
    
#     # 1. save to Postgres
#     sql_save_result = utils.sql_save_quote(
#         email=email,
#         phone_number=phone_number,
#         broker_name=broker_name,
#         quote_body=quote_body,
#         database_id=database_id,
#         page_id=page_id
#     )
#     if sql_save_result:
#         logger.info(f"SQL SUCCESSFULLY SAVED QUOTE FOR - {email}")

#     # 2. save to Notion
#     URL = "https://api.notion.com/v1/pages"
#     PAYLOAD = {
#         "parent": {
#             "database_id": database_id
#         },
#         "properties": {
#             "Quote Body": {
#                 "title": [
#                     {
#                         "type": "text",
#                         "text": {
#                             "content": quote_body
#                         }
#                     }
#                 ]
#             }
#         }
#     }

#     response = httpx.post(URL, headers=NOTION_API_HEADERS, json=PAYLOAD)
#     status_code = response.status_code
#     logger.info(f"NOTION API STATUS CODE - {status_code}")

#     if status_code == 200:
#         logger.debug(f"RAW NOTION API RESPONSE - {response.json()}")
#         logger.info(f"NOTION SUCCESSFULLY SAVED QUOTE FOR - {email}")
        
#     else:
#         logger.error(f"!!! FAILED INSERTING QUOTE FOR - {email}: {response.text}")
#         result["success"] = False
#         result["error"] = response.text

#     return result


# def get_broker_page(email):
#     logger.info(f"GET BROKER PAGE - {email}")

#     URL = f"https://api.notion.com/v1/databases/{BROKERS_DATABASE_ID}/query"

#     PAYLOAD = {
#         "filter": {
#             "property": "Email",
#             "title": {
#                 "equals": email
#             }
#         }
#     }

#     response = httpx.post(URL, headers=NOTION_API_HEADERS, json=PAYLOAD)
#     status_code = response.status_code

#     logger.info(f"STATUS CODE - {status_code}")

#     if status_code == 200:
#         logger.info(f"PAGE FOUND FOR - {email}")
#         data = response.json()
#         logger.debug(f"RAW NOTION API RESPONSE - {data}")

#         if len(data.get('results', [])) > 0:
#             page_id = data['results'][0]['id']
#             return page_id
#         else:
#             return None
#     else:
#         logger.error(f"!!! FAILED FINDING PAGE FOR - {email}: {response.text}")
#         return None



# def get_broker_database(email):
#     logger.info(f"GET BROKER DATABASE - {email}")
    
#     result = {
#         "page_id": None,
#         "database_id": None
#     }
    
#     page_id = get_broker_page(email)
#     logger.info(f"BROKER PAGE ID - {page_id}")
    
#     if page_id:
#         result['page_id'] = page_id
        
#         URL = f"https://api.notion.com/v1/blocks/{page_id}/children"
#         response = httpx.get(URL, headers=NOTION_API_HEADERS)

#         if response.status_code == 200:
#             data = response.json().get("results", [])
#             logger.debug(f"RAW PAGE DATA - {data}")
            
#             if data:
#                 for item in data:
#                     if item.get('child_database') and item['child_database']['title'] == 'WhatsApp Bot':
#                         database_id = item['id']
#                         break
#                 if database_id:
#                     result['database_id'] = database_id
#                 else:
#                     logger.error(f"!!! Database NOT found for - {email}; page ID: {page_id}")
#         else:
#             logger.error(f"!!! Database NOT found for - {email}; page ID: {page_id}")
#             logger.error(f"!!! NOTION API ERROR. Status code: {response.status_code}, Response: {response.text}")
#     return result





if __name__ == "__main__":
    # print(get_broker_database("string"))
    ...