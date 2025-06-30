from dotenv import load_dotenv
import os

load_dotenv()

RECRUITER_TOKEN = os.getenv("RECRUITER_TOKEN")
CANDIDATE_TOKEN = os.getenv("CANDIDATE_TOKEN")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
EXPIRY_MINUTES = os.getenv("TOKEN_EXPIRY")

DB_USERNAME = os.getenv("DATABASE_USERNAME")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
DB_NAME = os.getenv("DATABASE_NAME")
DATABASE_HOST = os.getenv("DATABASE_HOST")
