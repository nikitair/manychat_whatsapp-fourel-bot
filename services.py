import httpx
from logging_config import logger
import schemas

NOTION_API_HEADERS = {
    "Authorization": "Bearer secret_hcJF8bCOLP1ZcOR54a8kmWJ0dFMssHjEOWhSnvA0mN2",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

BROKERS_DATABASE_ID = "b8a10681aded43339ec1dc13dd44ff03"


def get_brokers_emails():
    logger.info(f"RETRIEVE EMAILS IN DB - {BROKERS_DATABASE_ID}")
    URL = f"https://api.notion.com/v1/databases/{BROKERS_DATABASE_ID}/query"

    result = {
        "emails": []
    }
    has_more = True
    next_cursor = None

    while has_more:
        payload = {}
        if next_cursor:
            payload['start_cursor'] = next_cursor

        response = httpx.post(URL, headers=NOTION_API_HEADERS, json=payload)
        status_code = response.status_code
        logger.info(f"NOTION API STATUS CODE - {status_code}")

        if status_code == 200:
            data = response.json()
            results = data.get('results', [])
            logger.debug(f"RAW DB DATA - {results}")

            for page in results:
                email_property = page['properties'].get('Email')
                if email_property and email_property['type'] == 'title':
                    email_title = email_property.get('title', [])
                    for title_item in email_title:
                        if title_item['type'] == 'text':
                            result["emails"].append(
                                title_item['text']['content'])

            has_more = data.get('has_more', False)
            next_cursor = data.get('next_cursor')
        else:
            logger.error(f"!!! Failed to retrieve data: {response.text}")
            has_more = False

    return result


def create_whatsapp_bot_database(page_id):
    logger.info(f"CREATE WHATSAPP BOT DATABASE ON PAGE - {page_id}")
    URL = "https://api.notion.com/v1/databases"

    data = {
        "parent": {"page_id": page_id},
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "WhatsApp Bot"
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

    response = httpx.post(URL, headers=NOTION_API_HEADERS, json=data)
    status_code = response.status_code
    logger.info(f"NOTION API STATUS CODE - {status_code}")

    if status_code == 200:
        new_database = response.json()
        logger.debug(f"RAW NEW DATABASE DATA - {new_database}")
        logger.info(f"WhatsApp Bot database created successfully. Database ID: {
                    new_database['id']}")
        return new_database
    else:
        logger.error(f"Failed to create WhatsApp Bot database: {
                     response.text}")
        return None


def register_broker(request: schemas.RegisterBroker):
    logger.info(f"REGISTER BROKER IN DB - {BROKERS_DATABASE_ID}")
    URL = "https://api.notion.com/v1/pages"

    email = request.email
    phone_number = request.phone_number
    name = request.name

    logger.info(f"BROKER DATA - {email} | {phone_number} | {name}")

    data = {
        "parent": {"database_id": BROKERS_DATABASE_ID},
        "properties": {
            "Email": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": email
                        }
                    }
                ]
            },
            "Phone Number": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": phone_number
                        }
                    }
                ]
            },
            "Name": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": name
                        }
                    }
                ]
            }
        }
    }

    response = httpx.post(URL, headers=NOTION_API_HEADERS, json=data)
    status_code = response.status_code
    logger.info(f"NOTION API STATUS CODE - {status_code}")

    if status_code == 200:
        new_page = response.json()
        logger.debug(f"RAW NEW PAGE DATA - {new_page}")
        page_id = new_page["id"]
        logger.info(f"Record inserted successfully. Page ID: {page_id}")

        # Now create a new database on the created page
        database_response = create_whatsapp_bot_database(page_id)
        if database_response:
            return {
                "page_id": page_id,
                "database_id": database_response["id"]
            }
    else:
        logger.error(f"Failed to insert record: {response.text}")


def insert_quote_request(request):
    result = {
        "success": True,
        "error": None
    }

    database_id = request.database_id
    quote_body = request.quote_body

    logger.info(f"INSERT QUOTE REQUEST TO DB - {database_id}")
    logger.info(f"INSERT DATA - {quote_body}")

    URL = "https://api.notion.com/v1/pages"
    PAYLOAD = {
        "parent": {
            "database_id": database_id
        },
        "properties": {
            "Quote Body": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": quote_body
                        }
                    }
                ]
            }
        }
    }

    response = httpx.post(URL, headers=NOTION_API_HEADERS, json=PAYLOAD)
    status_code = response.status_code
    logger.info(f"NOTION API STATUS CODE - {status_code}")

    if status_code == 200:
        logger.debug(f"RAW NOTION API RESPONSE - {response.json()}")
    else:
        logger.error(f"!!! NOTION API ERROR - {response.text}")
        result["success"] = False
        result["error"] = response.text

    return result


def get_broker_page(email):
    logger.info(f"GET BROKER PAGE - {email}")

    URL = f"https://api.notion.com/v1/databases/{BROKERS_DATABASE_ID}/query"

    PAYLOAD = {
        "filter": {
            "property": "Email",
            "title": {
                "equals": email
            }
        }
    }

    response = httpx.post(URL, headers=NOTION_API_HEADERS, json=PAYLOAD)
    status_code = response.status_code

    logger.info(f"STATUS CODE - {status_code}")

    if status_code == 200:
        data = response.json()
        logger.debug(f"RAW NOTION API RESPONSE - {data}")

        if len(data.get('results', [])) > 0:
            page_id = data['results'][0]['id']
            return page_id
        else:
            return None
    else:
        logger.error(f"!!! NOTION API ERROR - {response.text}")
        return None



def get_broker_database(email):
    logger.info(f"GET BROKER DATABASE - {email}")
    
    result = {
        "page_id": None,
        "database_id": None
    }
    
    page_id = get_broker_page(email)
    logger.info(f"BROKER PAGE ID - {page_id}")
    
    if page_id:
        URL = f"https://api.notion.com/v1/pages/{page_id}"
        response = httpx.get(URL, headers=NOTION_API_HEADERS)

        if response.status_code == 200:
            data = response.json()
            logger.debug(f"RAW PAGE DATA - {data}")

            database_id = data.get('parent', {}).get('database_id')
            if database_id:
                result['page_id'] = page_id
                result['database_id'] = database_id
                return result
            else:
                logger.error(f"! Database ID not found for page ID: {page_id}")
        else:
            logger.error(f"!!! Failed to fetch page data. Status code: {response.status_code}, Response: {response.text}")
    return result


if __name__ == "__main__":
    print(get_broker_database("test@testt.com"))