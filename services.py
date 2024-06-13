import httpx
from logging_config import logger

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
            
            for page in results:
                email_property = page['properties'].get('Email')
                if email_property and email_property['type'] == 'title':
                    email_title = email_property.get('title', [])
                    for title_item in email_title:
                        if title_item['type'] == 'text':
                            result["emails"].append(title_item['text']['content'])
            
            has_more = data.get('has_more', False)
            next_cursor = data.get('next_cursor')
        else:
            logger.error(f"!!! Failed to retrieve data: {response.text}")
            has_more = False
    
    return result


def get_broker_by_email(email: str):
    logger.info(f"RETRIEVE USER WITH EMAIL - {email} FROM DB - {BROKERS_DATABASE_ID}")
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
    logger.info(f"NOTION API STATUS CODE - {status_code}")
    
    if status_code == 200:
        raw_response_data = response.json()
        logger.debug(f"RAW NOTION API RESPONSE - {raw_response_data}")
        
        brokers = raw_response_data.get("results", [])
        if brokers:
            return brokers[0]["id"]
        
    else:
        logger.error(f"!!! NOTION API ERROR - {response.text}")
        
        
if __name__ == "__main__":
    # print(get_broker_by_email("test2@test.com"))
    print(get_brokers_emails())