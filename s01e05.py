import os

from dotenv import load_dotenv

from AIService import AIService
from messenger import verify_task, get_file_data

PROMPT = """You are a police censor. Your job is to return the censored content you receive.
         It's very important to return the exact same content, in the same form, and without any comments. 
         Keep the same punctuation and don't decline any words.
         Replace any sensitive data with the word "CENZURA". Sensitive data include: 
         - full name (name and surname)
         - street name and house number
         - city
         - age (only number)
         Use exact word "CENZURA" and no other form of that word. Avoid repetition of the word CENZURA.
         
         <Examples>
         User: Dane personalne podejrzanego: Wojciech Sałata. Przebywa w Lublinie, ul. Akacjowa 9. Wiek: 44 lata.
         AI: Dane personalne podejrzanego: CENZURA. Przebywa w CENZURA, ul. CENZURA. Wiek: CENZURA lata.

         User: Tożsamość osoby podejrzanej: Marek Mazur. Mieszka w Biłgoraju na ulicy Akacjowej 112. Wiek: 25 lat.
         AI: Tożsamość osoby podejrzanej: CENZURA. Mieszka w CENZURA na ulicy CENZURA. Wiek: CENZURA lat. 
         
         User: Podejrzany: Krzysztof Kwiatkowski. Zamieszkały w Szczecinie przy ul. Różanej 12. Ma 34 lata.
         AI: Podejrzany: CENZURA. Zamieszkały w CENZURA przy ul. CENZURA. Ma CENZURA lata.
         
         User: Informacje o podejrzanym: Roman Markowski. Mieszka we Wrocławiu przy ulicy Konopnickiej 1/12. Wiek: 33 lata.
         AI: Informacje o podejrzanym: CENZURA. Mieszka we CENZURA przy ulicy CENZURA. Wiek: CENZURA lata.

         <End of examples>
         """

load_dotenv()

data = get_file_data(os.environ.get("aidevs.s01e05.file_name"), True)
print(data)
message = AIService().answer(data, PROMPT, AIService.AIModel.GEMMA2)
print(message)
response_data = verify_task("CENZURA", message)
print(response_data)
