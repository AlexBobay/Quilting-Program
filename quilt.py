import numpy as np
import math
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS, cross_origin
import logging
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import os
import time
import json

logging.basicConfig(filename='flask.log', level=logging.DEBUG)
app = Flask(__name__)
app.secret_key = 'Whistlepigs'  
CORS(app)

# Create a quilt class
class quiltInfo:
    next_id = 1  # Class variable to keep track of the next ID to assign

    def __str__(self):
        return f'QuiltInfo(id={self.id}, name={self.name}, color={self.color}, width={self.width}, height={self.height}, comments={self.comments})'
    
    def __init__(self, name, color, width, height, comments="", id=None):
        if id is None:
            self.id = quiltInfo.next_id  # Assign the next ID to this quilt
            quiltInfo.next_id += 1  # Increment the next ID
        else:
            self.id = id
        self.name = name
        self.color = color
        self.width = width*10
        self.height = height*10
        self.area = self.width*self.height
        self.comments = comments if comments is not None else ""

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['name'],
            data['color'],
            data['width'],
            data['height'],
            data.get('comments', ""),
            id=data.get('id')
        )
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'color': self.color,
            'width': self.width / 10,
            'height': self.height / 10,
            'area': self.area,
            'comments': self.comments,
        }
    
    def __eq__(self, other):
        if isinstance(other, quiltInfo):
            return self.__dict__ == other.__dict__
        return False

quiltList = []

colorList = (("navy", (0, 0, 0.5, 1)),
("black", (0, 0, 0, 1)),
("gray", (0.5, 0.5, 0.5, 1)),
("goldenrod", (0.85, 0.65, 0.13, 1)),
("blue", (0, 0, 1, 1)),
("red", (1, 0, 0, 1)),
("white", (1, 1, 1, 1)),
("green", (0, 0.5, 0, 1)),
("brown", (0.65, 0.16, 0.16, 1)),
("burgundy", (0.5, 0, 0.13, 1)),
("lightblue", (0.68, 0.85, 0.9, 1)),
("neongreen", (0.3, 1, 0, 1)),
("skyblue", (0.53, 0.81, 0.92, 1)),
("orange", (1, 0.5, 0, 1)),
("yellow", (1, 1, 0, 1)),
("indigo", (0.29, 0, 0.51, 1)),
("violet", (0.93, 0.51, 0.93, 1)))

colorList = [(name, tuple(int(c * 255) if i < 3 else c for i, c in enumerate(color))) for name, color in colorList]
@app.route('/')
def home():
    global quiltList, img_str
    quiltList.clear()
    img_str = None
    if 'quiltList' not in session:
        session['quiltList'] = []
    else:
        session['quiltList'].clear()
    print('Quilts cleared:', session['quiltList']) 
    return render_template('quiltsite.html')

#these have to be on top or else the code will not work
@app.route('/get_units', methods=['POST'])
def get_units():
    data = request.get_json()
    print('Received data:', data)  # Add this line
    if data and 'units' in data:
        units = data.get('units')
        if units is not None:
            session['units'] = units  # Store units in session
            print("Units: ", units)
            return jsonify({'units': units})
        else:
            print("Units key is present but the value is None")
            return jsonify({'error': 'Units key is present but the value is None'}), 400
    else:
        print("No data provided or units not included in data")
        return jsonify({'error': 'No data provided or units not included in data'}), 400
        
#for the color picker
@app.route('/colors', methods=['GET'])
@cross_origin(origins=['http://127.0.0.1:5000'])
def get_colors():
    color_list = [color[0] for color in colorList]  # Extract the color names from the tuples
    return jsonify(color_list)

#for adding quilts
@app.route('/add_quilt', methods=['POST'])
@cross_origin(origins=['http://127.0.0.1:5000'])
def add_quilt():
    data = request.get_json()
    print(data)  # Add this line to print the data received from the client
    name = data.get('name')
    color = data.get('color')
    width = data.get('width')
    
    height = data.get('height')
    comments = data.get('comments', '')

    if name is None or not name:
        return jsonify({"message": "Name is required"}), 400
    if color is None or not color:
        return jsonify({"message": "Color is required"}), 400
    if width is None or not width:
        return jsonify({"message": "Width is required"}), 400
    if height is None or not height:
        return jsonify({"message": "Height is required"}), 400
    try:
        addQuilt(name, color, width, height, comments)
    except Exception as e:
        print(f"Error when adding quilt: {e}")
        return jsonify({"message": f"Error when adding quilt: {e}"}), 500
    
    return jsonify({"message": "Quilt added successfully"}), 200

def addQuilt(name, color, width, height, comments=None):
    if not width or not height:
        raise ValueError("Width and height cannot be None or empty")
    # Create a new quilt object
    new_quilt = quiltInfo(name, color, width, height, comments)
    if comments is not None:
        new_quilt.comments = comments
    quiltList.append(new_quilt)
    return new_quilt

#for editing quilts
@app.route('/get-quilt-id/<int:index>', methods=['GET'])
@cross_origin(origins=['http://127.0.0.1:5000'])
def get_quilt_id(index):
    # Assuming quiltList is a list of quiltInfo objects
    if index >= 0 and index < len(quiltList):
        return jsonify({'id': quiltList[index].id})
    else:
        return jsonify({'error': 'No quilts found'}), 404

@app.route('/update-quilt/<int:id>', methods=['PUT'])
def update_quilt(id):
    # Get the new values from the request
    new_values = request.get_json()

    # Find the quilt with the given ID and update its properties
    for quilt in quiltList:
        if quilt.id == id:
            if 'name' in new_values:
                quilt.name = new_values['name']
            if 'color' in new_values:
                quilt.color = new_values['color']
            if 'width' in new_values:
                quilt.width = new_values['width']
            if 'height' in new_values:
                quilt.height = new_values['height']
            if 'comments' in new_values:
                quilt.comments = new_values['comments']
            for each in quiltList:
                print(each)
            return jsonify(quilt.__dict__), 200 
    # If no quilt with the given ID was found, return an error
    return jsonify({'error': 'Quilt not found'}), 404

# for saving quilts
@app.route('/getQuiltData', methods=['GET'])
def get_quilt_data():
    try:
        # Assuming quiltList is a list of QuiltInfo objects
        # Convert each QuiltInfo object to a dictionary before sending
        quilt_dicts = [quilt.__dict__ for quilt in quiltList]
        print(quilt_dicts)
        # Convert area and height to integers
        for quilt_dict in quilt_dicts:
            if 'area' in quilt_dict and quilt_dict['area'] != '':
                quilt_dict['area'] = int(quilt_dict['area'])
            if 'height' in quilt_dict and quilt_dict['height'] != '':
                quilt_dict['height'] = int(quilt_dict['height'])
        return jsonify(quilt_dicts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#for loading quilts
@app.route('/load_quilts', methods=['POST'])
def load_quilts():
    data = request.get_json()
    if data:
        quiltList.clear()
        for quilt_data in data:
            quilt = quiltInfo.from_dict(quilt_data)   # Convert dictionary to Quilt instance
            quiltList.append(quilt)
        return jsonify({'status': 'success', 'message': 'Quilts loaded successfully'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400
    
#for creating the final quilt
def find_factors(n):
    # If not, find the two closest factors
    for i in range(int(math.sqrt(n)), 1, -1):  # start from sqrt(n) and end at 2
        if n % i == 0:
            other_factor = n // i
            if i % 10 == 0 and other_factor % 10 == 0:  # Check if both factors are multiples of 10
                return i, other_factor
    else:
        # Round up both factors to the nearest 10
        i = math.ceil(i / 10.0) * 10
        n = math.ceil(n / 10.0) * 10
        return i, n  # Return factors rounded up to the nearest 100 if no suitable factors are found

def adjust_dimensions(totalArea):
    width, height = find_factors(totalArea)
    units = session.get('units')  # Retrieve units from session
    #print('Units:', units)  # Add this line
    if units == 'in':
        min_width = 600
        max_width = 1200
    else:
        min_width = 1520
        max_width = 3050
    while (width, height) == (10, totalArea/10) or not (min_width < width < max_width) or not (height > width*1.5):
        totalArea += 100
        width, height = find_factors(totalArea)
    return width, height, totalArea

def fit_squares(width, height, colorList, quiltList, d):
    print("Fitting squares")
    
    # Create a dictionary from colorList
    color_dict = dict(colorList)

    # Create a grid to keep track of occupied space
    grid = [[0]*width for _ in range(height)]
    quiltList = [quilt for quilt in quiltList if isinstance(quilt, quiltInfo)]
    
    # Sort quiltList from largest to smallest
    quiltList = sorted(quiltList, key=lambda quilt: quilt.width * quilt.height, reverse=True)
    
    quiltsAdded = 0
    font = ImageFont.truetype("arial", 25)
    for quilt in quiltList:
        quiltPlaced = False
        quilt_width = int(quilt.width)
        quilt_height = int(quilt.height)
        # Try both orientations for each quilt
        for quilt_width, quilt_height in [(quilt.width, quilt.height), (quilt.height, quilt.width)]:
            if quilt.color in color_dict:
                color = color_dict[quilt.color]
            # Find the first position where the quilt fits
            for i in range(0, height - quilt_height + 1,10):
                if quiltPlaced:
                    break
                for j in range(0, width - quilt_width + 1, 10):
                    if all(grid[i+k][j+l] == 0 for k in range(quilt_height) for l in range(quilt_width)):  # Check if all cells in the quilt's region are 0
                        # Place the quilt
                        d.rectangle([j, i, j+quilt_width, i+quilt_height], fill=color, outline='black')

                        # Calculate the center of the quilt
                        center_x = j + quilt_width // 2
                        center_y = i + quilt_height // 2

                        # Add the quilt number to the center of the quilt
                        d.text((center_x, center_y), str(quilt.id), fill='black', font=font, anchor="mm", stroke_width=2, stroke_fill='white')

                        # Update the grid
                        for k in range(quilt_height):
                            for l in range(quilt_width):
                                grid[i+k][j+l] = 1
                        
                        quiltsAdded += 1
                        quiltPlaced = True
                        break
                if quiltPlaced:  # If the quilt is placed in the first orientation, break the loop and don't try the second orientation
                    break
    for i in range(height):
        for j in range(width):
            if grid[i][j] == 0:  # If the cell is unclaimed
                # Alternate the color based on the sum of the coordinates
                color = 'red' if ((i // 2) + (j // 2)) % 2 == 0 else 'white'
                d.point((j, i), fill=color)
    return quiltsAdded

def make_quilt(quiltList):
    try:
        totalArea = sum([int(quilt.area) for quilt in quiltList])  # Use dot notation
        print("Total area: ", totalArea)
    except ValueError:
        print("Error: one or more quilt areas are not valid numbers.")

    width,height = find_factors(totalArea)
    width, height, totalArea = adjust_dimensions(totalArea)
    print("Width, Height: ", width, height)

    finalQuilt = Image.new('RGB', (width, height), 'white')
    d = ImageDraw.Draw(finalQuilt)
    quiltsAdded = fit_squares(width, height, colorList, quiltList, d)
   
    while quiltsAdded != len(quiltList):
        print ("Quilts Added: ", quiltsAdded)
        quiltsAdded = 0
        finalQuilt.close()
        totalArea += 1000
        width,height = find_factors(totalArea)
        width, height, totalArea = adjust_dimensions(totalArea)
        print("Width, Height: ", width, height)
        finalQuilt = Image.new('RGB', (width, height), 'white')
        d = ImageDraw.Draw(finalQuilt)
        quiltsAdded = fit_squares(width, height, colorList, quiltList, d)
    
    finalQuilt.save("finalQuilt.png")

    # Convert the image to base64
    buffer = BytesIO()
    finalQuilt.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return img_str

@app.route('/quiltmaker')
def quiltmaker():
    
    # Load the previous quiltList
    try:
        with open('previous_quilt_list.json', 'r') as f:
            previous_quilt_list = [quiltInfo.from_dict(quilt_dict) for quilt_dict in json.load(f)]
            if previous_quilt_list:
                quiltInfo.next_id = max(quilt.id for quilt in previous_quilt_list) + 1
    except FileNotFoundError:
        previous_quilt_list = None

    # Reset the IDs of the quilts
    for i, quilt in enumerate(quiltList, start=1):
        quilt.id = i

    # Check if the image file exists and the 'make_quilt' flag is False
    if previous_quilt_list is None or [quilt.to_dict() for quilt in previous_quilt_list] != [quilt.to_dict() for quilt in quiltList]:
        # If not, or if the 'make_quilt' flag is True, generate the image string
        img_str = make_quilt(quiltList)
        # Store the image string in a file
        with open('img_str.txt', 'w') as f:
            f.write(img_str)
        # Set the 'make_quilt' flag to False

        # Save the quiltList to a file
        with open('previous_quilt_list.json', 'w') as f:
            json.dump([quilt.to_dict() for quilt in quiltList], f)

    # Read the image string from the file
    with open('img_str.txt', 'r') as f:
        img_str = f.read()
    
    # Render the template first
    response = render_template('quiltmaker.html', quiltList=quiltList, colorList=colorList, img_str=img_str)
    # Return the rendered template
    return response


# Save the quiltList to a file
with open('previous_quilt_list.json', 'w') as f:
    json.dump(quiltList, f)

if __name__ == '__main__':
    def run_flask_app():
        app.run(host='0.0.0.0', debug=True, port=8080)

run_flask_app()