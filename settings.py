from dotenv import load_dotenv
import os

load_dotenv()  # .env dosyasını yükle

NETGSM_USERCODE = os.getenv("NETGSM_USERCODE")
NETGSM_PASSWORD = os.getenv("NETGSM_PASSWORD")
NETGSM_HEADER = os.getenv("NETGSM_HEADER")
