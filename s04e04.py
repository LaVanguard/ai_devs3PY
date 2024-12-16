import os

from dotenv import load_dotenv

from messenger import verify_task

load_dotenv()

answer = os.environ.get("aidevs.s04e04.url")
verify_task("webhook", answer)
