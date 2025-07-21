import psycopg2
from config import DATABASE_URL
from typing import Optional
from psycopg2 import sql, OperationalError

#this function returns the status from database
def get_status(title:str , table:str) -> Optional[str]:
    try : 
        # Connect to PostgreSQL
        conn = psycopg2.connect(DATABASE_URL)             
        # Create a cursor
        cur = conn.cursor()

        query = "SELECT status FROM %s WHERE title = %s LIMIT 1;"

        cur.execute(query, (table,title))

        # Fetch one result
        result = cur.fetchone()
        
        # Close connections
        cur.close()
        conn.close()

        return result[0] if result else None
    except OperationalError as e:
        print("Database connection error:", e)
        return None
    except Exception as e:
        print("Error:", e)
        return None


