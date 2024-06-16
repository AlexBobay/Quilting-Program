import numpy as np
import math
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS, cross_origin
import logging
from PIL import Image, ImageDraw

#import quilt  # Assuming quilt.py is in the same directory

logging.basicConfig(filename='flask.log', level=logging.DEBUG)
app = Flask(__name__)
app.secret_key = 'Whistlepigs'  
CORS(app)

# Create a quilt class
class quiltInfo:
    next_id = 1  # Class variable to keep track of the next ID to assign

    def __str__(self):
        return f'QuiltInfo(id={self.id}, name={self.name}, color={self.color}, width={self.width}, height={self.height}, comments={self.comments})'
    
    def __init__(self, name, color, width, height, comments=""):
        self.id = quiltInfo.next_id  # Assign the next ID to this quilt
        quiltInfo.next_id += 1  # Increment the next ID
        self.name = name
        self.color = color
        self.width = width*10
        self.height = height*10
        self.area = self.width*self.height
        self.comments = comments if comments is not None else ""

    @classmethod
    def from_dict(cls, data):
        return cls(data['name'], data['color'], data['width'], data['height'], data.get('comments', ""))

quiltList = []

colorList = (("navy", (0, 0, 0.5, 1)),
("black", (0, 0, 0, 1)),
("gray", (0.5, 0.5, 0.5, 1)),
("goldenrod", (0.85, 0.65, 0.13, 1)),
("blue", (0, 0, 1, 1)),
("red", (1, 0, 0, 1)),
("white", (0.3, 0.7, 0.4, 1)),
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

colorList = [(name, tuple(int(c * 255) for c in color)) for name, color in colorList]
@app.route('/')
def home():
    global quiltList
    quiltList.clear()
    if 'quiltList' not in session:
        session['quiltList'] = []
    else:
        session['quiltList'].clear()
    print('Quilts cleared:', session['quiltList']) 
    return render_template('quiltsite.html')

def addQuilt(name, color, width, height, comments=None):
    if not width or not height:
        raise ValueError("Width and height cannot be None or empty")
    # Create a new quilt object
    new_quilt = quiltInfo(name, color, width, height, comments)
    if comments is not None:
        new_quilt.comments = comments
    quiltList.append(new_quilt)
    return new_quilt

def find_factors(n):
    # Check if the number is a perfect square and greater than 1
    if math.sqrt(n) == int(math.sqrt(n)) and math.sqrt(n) > 1:
        root = int(math.sqrt(n))
        if root % 10 == 0:  # Check if the root is a multiple of 10
            return root, root

    # If not, find the two closest factors
    for i in range(int(math.sqrt(n)), 1, -1):  # start from sqrt(n) and end at 2
        if n % i == 0:
            other_factor = n // i
            if i % 10 == 0 and other_factor % 10 == 0:  # Check if both factors are multiples of 10
                return i, other_factor
    else:
        return 1, n  # Return None, None if no suitable factors are found

def fit_squares(width, height, colorList, quiltList, d):
    print("Fitting squares")
    
    # Create a dictionary from colorList
    color_dict = dict(colorList)

    # Create a grid to keep track of occupied space
    grid = [[0]*width for _ in range(height)]
    quiltList = [quilt for quilt in quiltList if isinstance(quilt, quiltInfo)]

    print(f"Number of quilts: {len(quiltList)}")  # Check if quiltList is empty
    
    # Sort quiltList from largest to smallest
    quiltList = sorted(quiltList, key=lambda quilt: quilt.width * quilt.height, reverse=True)
    
    quiltsAdded = 0
    for quilt in quiltList:
        print(f"Processing quilt {quilt.id}")
        quilt_width = int(quilt.width)
        quilt_height = int(quilt.height)
        # Try both orientations for each quilt
        for quilt_width, quilt_height in [(quilt.width, quilt.height), (quilt.height, quilt.width)]:
            if quilt.color in color_dict:
                color = color_dict[quilt.color]
            else:
                print(f"Error: quilt color {quilt.color} is not a valid color.")
            # Find the first position where the quilt fits
            for i in range(height - quilt_height + 1, height + 1, 10):
                for j in range(width - quilt_width + 1, width + 1, 10):
                    if all(grid[i+k][j+l] == 0 for k in range(quilt_height) for l in range(quilt_width)):  # Check if all cells in the quilt's region are 0
                        # Place the quilt
                        d.rectangle([j, i, j+quilt_width, i+quilt_height], fill=color)

                        # Add the quilt number to the center of the quilt
                        d.text((j+quilt_width//2, i+quilt_height//2), str(quilt.id), fill='black')

                        # Update the grid
                        for k in range(quilt_height):
                            for l in range(quilt_width):
                                grid[i+k][j+l] = 1
                        
                        print(f"Placed quilt {quilt.id} at position ({j}, {i})")
                        quiltsAdded += 1
                        # Break out of the j and i loops since we've placed the quilt
                        break
                else:
                    continue
                break
            else:
                continue
            break
    return quiltsAdded
        

@app.route('/colors', methods=['GET'])
@cross_origin(origins=['http://127.0.0.1:5000'])
def get_colors():
    color_list = [color[0] for color in colorList]  # Extract the color names from the tuples
    return jsonify(color_list)

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

@app.route('/get-quilt-id/<int:index>', methods=['GET'])
@cross_origin(origins=['http://127.0.0.1:5000'])
def get_quilt_id(index):
    # Assuming quiltList is a list of quiltInfo objects
    if index >= 0 and index < len(quiltList):
        return jsonify({'id': quiltList[index].id})
    else:
        return jsonify({'error': 'No quilts found'}), 404

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
    
def make_quilt(quiltList):
    try:
        totalArea = sum([int(quilt.area) for quilt in quiltList])  # Use dot notation
        print("Total area: ", totalArea)
    except ValueError:
        print("Error: one or more quilt areas are not valid numbers.")

    width,height = find_factors(totalArea)
    while ((width, height) == (1, totalArea)) or (width > 600) or (width < 360) or (height < width*1.5):
        totalArea += 100
        width,height = find_factors(totalArea)
    print("Width, Height: ", width, height)

    finalQuilt = Image.new('RGB', (width, height), 'white')
    d = ImageDraw.Draw(finalQuilt)
    quiltsAdded = fit_squares(width, height, colorList, quiltList, d)
   
    while quiltsAdded != len(quiltList):
        finalQuilt.close()
        finalQuilt = Image.new('RGB', (width, height), 'white')
        totalArea += 100
        width,height = find_factors(totalArea)
        print("Width, Height: ", width, height)
        fit_squares(width, height, colorList, quiltList, totalArea)
    
    finalQuilt.show()
        

@app.route('/quiltmaker')
def quiltmaker():
    # Render the template first
    response = render_template('quiltmaker.html', quiltList=quiltList, colorList=colorList)
    # Then call make_quilt
    make_quilt(quiltList)
    # Return the rendered template
    return response

if __name__ == '__main__':
    def run_flask_app():
        app.run(debug=True, port=5000)

run_flask_app()
#<img src="{{ url_for('static', filename='plot.png', _t=time.time()) }}" alt="Plot image">-->