from dotenv import load_dotenv

from AIService import AIService

PROMPT = """Your task is to navigate a 4x6 grid to reach the 'destination'. Follow these instructions carefully:
<tr><td></td><td class='wall'></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td class='wall'></td><td></td><td></td></tr><tr><td></td><td class='wall'></td><td></td><td class='wall'></td><td></td><td></td></tr><tr><td class='robot'></td><td class='wall'></td><td></td><td></td><td></td><td class='destination'></td></tr>

The key positions in the grid (row, col):

•Start: (3,0)
•Destination: (3,5)
•Walls:
•(0,1), (1,3), (2,1), (2,3), (3,1)

For (3,0) position:
•UP empty (2,0)
•DOWN out of bounds (4,0)
•LEFT out of bounds (3,-1)
•RIGHT wall (3,1)

_thinking:
Path Planning Instructions:

1.Evaluate all potential moves from (3,0) one step at a time based on whether they lead to an empty cell, a wall, or the destination or beyond the dimensions.
2.Follow the Depth-first search algorithm to calculate a safe path, taking into consideration constraints such as walls and dimensions.
3.Output Result:
<RESULT>
{
  "steps": "DOWN, UP, RIGHT, LEFT"
}
</RESULT>"""

load_dotenv()

ROBOT = "<td class='robot'></td>"
EMPTY = "<td></td>"
WALL = "<td class='wall'></td>"
DEST = "<td class='destination'></td>"
ROW = "</tr><tr>"

map = "<table<tbody><tr>.|....@...|..@.|.|..@^....#</tr></tbody></table>"

map = map.replace("^", ROBOT).replace(".", EMPTY).replace("|", WALL).replace("#", DEST).replace("@", ROW)
answer = AIService().answer(map, PROMPT, AIService.AIModel.GPT4oMINI, None, 0)
print(answer)
