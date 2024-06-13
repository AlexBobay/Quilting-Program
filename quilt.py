import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.patches as patches
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS, cross_origin
import logging
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
    
    def __init__(self, number, name, color, width, height, comments=""):
        self.id = quiltInfo.next_id  # Assign the next ID to this quilt
        quiltInfo.next_id += 1  # Increment the next ID
        self.number = number
        self.name = name
        self.color = color
        self.width = width
        self.height = height
        self.area = width*height
        self.comments = comments
        self.comments = comments if comments is not None else ""

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

@app.route('/')
def home():
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

@app.route('/clear-upon-refresh', methods=['GET'])
def clear_upon_refresh():
    session['quiltList'] = []
    print('Quilts cleared:', session['quiltList'])  
    return jsonify(success=True)
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)

@app.route('/quiltmaker')
def quiltmaker():
    return render_template('quiltmaker.html')

"""
def find_factors(n):
    # Check if the number is a perfect square and greater than 1
    if math.sqrt(n) == int(math.sqrt(n)) and math.sqrt(n) > 1:
        return int(math.sqrt(n)), int(math.sqrt(n))

    # If not, find the two closest factors
    for i in range(int(math.sqrt(n)), 1, -1):  # start from sqrt(n) and end at 2
        if n % i == 0:
            return i, n // i
    else:
        return 1, n

def fit_squares(ax, width, height, colorList, quiltList):
    # Create a dictionary from colorList
    color_dict = dict(colorList)

    # Create a grid to keep track of occupied space
    grid = [[0]*width for _ in range(height)]

    # Sort quiltList from largest to smallest
    quiltList = sorted(quiltList, key=lambda quilt: quilt.width * quilt.height, reverse=True)

    for quilt in quiltList:
        # Try both orientations for each quilt
        for quilt_width, quilt_height in [(quilt.width, quilt.height), (quilt.height, quilt.width)]:
            color = color_dict[quilt.color]  # Get the color value from the dictionary
            # Find the first position where the quilt fits
            for i in range(height - quilt_height + 1):  # Ensure i doesn't exceed the height of the grid minus the height of the quilt
                for j in range(width - quilt_width + 1):  # Ensure j doesn't exceed the width of the grid minus the width of the quilt
                    if all(grid[i+k][j+l] == 0 for k in range(quilt_height) for l in range(quilt_width)):  # Check if all cells in the quilt's region are 0
                        # Place the quilt
                        small_square = patches.Rectangle((j, i), quilt_width, quilt_height, fill=True, color=color)
                        ax.add_patch(small_square)

                        # Add the quilt number to the center of the quilt
                        ax.text(j + quilt_width / 2, i + quilt_height / 2, str(quilt.number), ha='center', va='center')

                        # Update the grid
                        for k in range(quilt_height):
                            for l in range(quilt_width):
                                grid[i+k][j+l] = 1

                        # Break out of the j and i loops since we've placed the quilt
                        break
                else:
                    continue
                break
            else:
                continue
            break


info = open("quiltinfo.txt", "r")
# Read in the quilt information

quiltLines = []
for line in info:
   quiltLines.append(line.strip().split())
info.close()

# Create a list of quilt objects

for each in quiltLines:
    quilt = quiltInfo(each[0], each[1], each[2], int(each[3]), int(each[4]))
    if len(each) > 6:
        quilt.comments = each[5]
    quiltList.append(quilt)

# Calculate the total area of all quilts
totalArea = 0
for each in quiltList:
    totalArea += each.area
print( "Total area of all quilts: ", totalArea)

while True:
    # Find the factors of the total area
    width,height = find_factors(totalArea)
    while ((width, height) == (1, totalArea)) or (width > 60) or (width < 36) or (height < width*1.5):
        totalArea += 1
        width,height = find_factors(totalArea)
    print("Width, Height: ", width, height)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    square = patches.Rectangle((0, 0), width, height, fill=False)
    ax.add_patch(square)
    ax.set_aspect('equal')
    fit_squares(ax, width, height, colorList, quiltList)
    if(len(ax.patches) == len(quiltList)):
        break
    else:
        plt.close(fig)
        totalArea += 10
        

plt.xlim(0, width)
plt.ylim(0, height)
plt.gca().set_aspect('equal', adjustable='box')
plt.show()
plt.savefig('quilt.png')
"""