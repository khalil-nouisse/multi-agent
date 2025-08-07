# Global config: API keys, env vars, etc.
from dotenv import load_dotenv
load_dotenv()  # Assure-toi que c'est au tout début
import os
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2')
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT")

#email SMTP
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


# CRM API configuration
CRM_API_BASE_URL = os.getenv('CRM_API_URL')
CRM_API_KEY = os.getenv('CRM_API_KEY')


#CHROMA DB and tech LOG files
CHROMA_DB_URL = os.getenv('CHROMA_DB_URL')
LOG_AGGREGATION_API_URL = os.getenv('LOG_AGGREGATION_API_URL')


#human support email 
HUMAN_SUPPORT_EMAIL = os.getenv('HUMAN_SUPPORT_EMAIL')
ENGINEERING_TEAM_EMAIL = os.getenv('ENGINEERING_TEAM_EMAIL')
