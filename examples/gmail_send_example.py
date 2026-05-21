import os
import sys

from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from agrobot_rules.gmail_client import send_gmail_message

load_dotenv(".env")


if __name__ == "__main__":
    result = send_gmail_message(
        to=os.environ["GMAIL_ADVISOR_TO"],
        subject="AgroBot - prueba de salida por Gmail",
        body="AgroBot ya puede enviar salidas operativas por Gmail.",
        sender=os.getenv("GMAIL_SENDER"),
    )
    print(result)
