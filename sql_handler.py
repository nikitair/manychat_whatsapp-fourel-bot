import sqlite3
from logging_config import logger


def sql_create_database():
    # Step 1: Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('whatsapp_bot.db')

    # Step 2: Create a cursor object using the cursor() method
    cursor = conn.cursor()

    # Step 3: Create the brokers table
    cursor.execute('''CREATE TABLE IF NOT EXISTS brokers (
                        id INTEGER PRIMARY KEY,
                        email TEXT NOT NULL,
                        phone_number TEXT,
                        name TEXT,
                        page_id TEXT,
                        database_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')

    # Step 4: Create the quote_requests table
    cursor.execute('''CREATE TABLE IF NOT EXISTS quote_requests (
                        id INTEGER PRIMARY KEY,
                        quote_body TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        broker_id INTEGER,
                        FOREIGN KEY (broker_id) REFERENCES brokers (id)
                    )''')

    # Step 5: Commit changes and close the connection
    conn.commit()
    conn.close()
    logger.info("TABLES CREATED")
    return True



def sql_insert_broker(email, phone_number, name, page_id, database_id):
    logger.info(f"SQL INSERT BROKER - {email} | {phone_number} | {name} | p_id:{page_id} | d_id:{database_id}")
    try:
        conn = sqlite3.connect('whatsapp_bot.db')
        cursor = conn.cursor()
        logger.debug("SQL CONNECTED TO DB")
        
        cursor.execute('''INSERT INTO brokers (email, phone_number, name, page_id, database_id)
                          VALUES (?, ?, ?, ?, ?)''', (email, phone_number, name, page_id, database_id))
        
        conn.commit()
        broker_id = cursor.lastrowid
        logger.info(f"SQL BROKER - {email} - INSERTED TO DB - {broker_id}")
        
    except sqlite3.Error as e:
        logger.exception(f"!!! SQL ERROR - {e}")
        
    finally:
        if conn:
            conn.close()
        logger.debug("SQL CLOSED DB CONNECTION")
        
        

def sql_insert_quote(quote_body, broker_id):
    logger.info(f"SQL INSERT QUOTE REQUEST - {quote_body} | {broker_id}")
    try:
        conn = sqlite3.connect('whatsapp_bot.db')
        cursor = conn.cursor()
        logger.debug("SQL CONNECTED TO DB")
        
        cursor.execute('''INSERT INTO quote_requests (quote_body, broker_id)
                          VALUES (?, ?)''', (quote_body, broker_id))
        
        conn.commit()
        quote_id = cursor.lastrowid
        logger.info(f"SQL QUOTE INSERTED TO DB - {quote_id}")
        
    except sqlite3.Error as e:
        logger.exception(f"!!! SQL ERROR - {e}")
        
    finally:
        if conn:
            conn.close()
        logger.debug("SQL CLOSED DB CONNECTION")
        
        
        
def get_broker_id(database_id: str):
    logger.info(f"SQL GET BROKER ID - {database_id}")
    try:
        conn = sqlite3.connect('whatsapp_bot.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT id, email FROM brokers WHERE database_id = ?''', (database_id,))
        
        broker_data = cursor.fetchone()
        logger.debug(f"SQL BROKER DATA - {broker_data}")
        
        if broker_data:
            return broker_data[0]
        else:
            logger.warning(f"! SQL NO BROKER FOUND - {database_id}")
            return None
        
    except sqlite3.Error as e:
        logger.exception(f"!!! SQL ERROR RETRIEVING BROKER: {e}")
        return None
        
    finally:
        if conn:
            conn.close()
    
    
if __name__ == "__main__":
    sql_create_database()
    # sql_insert_broker('example@email.com', '123456789', 'John Doe', 'abc123', 1)
    # sql_insert_quote('Example', 2)