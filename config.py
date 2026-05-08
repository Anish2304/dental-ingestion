import os
from dotenv import load_dotenv

load_dotenv()

# OpenDental API
OPENDENTAL_API_KEY  = os.getenv("OPENDENTAL_API_KEY", "")
OPENDENTAL_BASE_URL = os.getenv("OPENDENTAL_BASE_URL", "https://api.opendental.com/api/v1")

# Playwright — URL of the patient-entry HTML frontend
FRONTEND_URL = os.getenv("FRONTEND_URL", "")

# Database
DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(__file__), "docudent.db"))

LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")