from flask import Flask, request, jsonify

from AIService import AIService

PROMPT = """
## Prompt: Map Description for Drone Navigation

**Context**: The map is a **4x4 grid** (4 columns and 4 rows). Each square on the map contains a specific object or is empty. 
The drone **always starts from the starting point** in the **top-left corner** of the map (Row 1, Column 1). 
At any moment, you must describe **what is directly under the drone**, based on its current position on the map.

**Map Grid (numbering starts at 1)**:

1. **Row 1**:
   - **Column 1 (Start)**: Starting point (location pin symbol).
   - **Column 2**: Empty square with grass.
   - **Column 3**: Single tree.
   - **Column 4**: House.

2. **Row 2**:
   - **Column 1**: Empty square with grass.
   - **Column 2**: Windmill.
   - **Column 3**: Empty square with grass.
   - **Column 4**: Empty square with grass.

3. **Row 3**:
   - **Column 1**: Empty square with grass.
   - **Column 2**: Empty square with grass.
   - **Column 3**: Rocks.
   - **Column 4**: Two trees.

4. **Row 4**:
   - **Column 1**: Mountains.
   - **Column 2**: Mountains.
   - **Column 3**: Car.
   - **Column 4**: Cave.

**Instructions**:
1. Always start the analysis from the starting point at **Row 1, Column 1**.
2. As the drone moves, describe what is located at its current position.
3. Each square can be identified using coordinates: **(row, column)**.
4. The objects on the map are:
   - **Starting Point**: Location pin symbol.
   - **Empty Square**: Grass only.
   - **Tree** or **Trees**.
   - **House**.
   - **Windmill**.
   - **Rocks**.
   - **Mountains**.
   - **Car**.
   - **Cave**.

**Example of Movement Descriptions**:
- Start: "The drone is at the starting point (1,1) – location pin symbol."
- Move to (1,3): "The drone is now over a tree."
"""

app = Flask(__name__)

service = AIService()


@app.route('/', methods=['GET'])
def home():
    return "Ready to fly drone!"


@app.route('/', methods=['POST'])
def fly_drone():
    data = request.get_json()
    print(data)
    description = service.answer(data.get("instruction"), PROMPT)
    print(description)
    response = jsonify({"description": description})
    return response


if __name__ == '__main__':
    app.run()
