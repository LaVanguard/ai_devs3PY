import base64

from dotenv import load_dotenv

from AIService import AIService

IMAGES1 = ["s02e02-1.jpg", "s02e02-2.jpg", "s02e02-3.jpg", "s02e02-4.jpg"]
IMAGE2 = "s02e02-5.jpg"
PROMPT1 = """You are a helpful cartography assistant that can answers what Polish city is shown on the map fragment. 

_thinking

Try to match street names and their intersections to a city in Poland. 
Analyse carefully entire map and consider the layout of the streets, their names and the overall shape of the city before presenting the result.
Take into account all texts on the map, including names of the sops or other businesses. Take into consideration unique elements of the city presented on the map fragment.
There are landmarks called "spichlerze" and "twierdza" in the city that may be depict by the map.
"""
PROMPT2 = """You are a helpful cartography assistant that can answer what Polish cities are shown on the 4 map fragments in the image.

_thinking

Try to match street names and their intersections layout to a city in Poland. 
Consider the layout of the streets, shapes of the buildings  and the overall shape of the city before presenting the result.
Pay attention to the landmarks on the map - try matching bus stops, shops relative to each other and unique 
names that may lead to determining the exact location. Take into account all the texts on te fragments.
Note that some of the street names may be incorrectly written.
Take into consideration 3 facts:
1. There are 4 map fragments on the image, each reflects different part of some city.
2. There are only 2 different cities presented on the map fragments. 3 fragments show parts of the same city.
3. The city presented on the 3 fragments has specific landmarks: the granaries and the fortress.

Once you match 3 fragments of the same city reconsider you choice taking into account all 3 fragments together.

<examples>
Fragment 1: Lush Massage
<end of exmamples>
"""
QUESTION1 = "What is the city name represented by the map fragment in the image?"
QUESTION2 = "What are the city names represented by the map fragments in the image?"
MODEL = AIService.AIModel.GPT4o

load_dotenv()

for image_path in IMAGES1:
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        message = AIService().describeImage(image_base64, QUESTION1, PROMPT1, MODEL, 1024, 0)
        print(message)
print("--------------------")
with open(IMAGE2, "rb") as image_file:
    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    message = AIService().describeImage(image_base64, QUESTION2, PROMPT2, MODEL, 1024, 0)
    print(message)
