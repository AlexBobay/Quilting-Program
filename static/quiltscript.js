$(document).ready(function() {
    $.get('http://127.0.0.1:5000/colors', function(data) {
        var colorSelect = document.getElementById('color');
        data.sort();
        for (var i = 0; i < data.length; i++) {
            var option = document.createElement('option');
            option.value = data[i];
            option.text = data[i];
            colorSelect.appendChild(option);
        }
    });
});

let editMode = false;  // Track whether we're in "add" mode or "edit" mode
var quilts = [];
var lastIndex = -1;

async function addQuilt() {
    var name = document.getElementById('name').value;
    var nameError = document.getElementById('nameError');
    if (!name) {
        nameError.textContent = "Name cannot be blank.";
    } else {
        nameError.textContent = "";
    }

    var color = document.getElementById('color').value;
    var colorError = document.getElementById('colorError');
    if (!color) {
        colorError.textContent = "Color cannot be blank.";
    } else {
        colorError.textContent = "";
    }

    var width = Number(document.getElementById('width').value);
    var widthError = document.getElementById('widthError');
    if (!Number.isInteger(width) || width < 1) {
        widthError.textContent = "Width must be an integer greater than 0.";
    } else {
        widthError.textContent = "";
    }

    var height = Number(document.getElementById('height').value);
    var heightError = document.getElementById('heightError');
    if (!Number.isInteger(height) || height < 1) {
        heightError.textContent = "Height must be an integer greater than 0.";
    } else {
        heightError.textContent = "";
    }

    var comments = document.getElementById('comments').value;

    //If all inputs are valid, create the quilt box
    var quiltForm = document.getElementById('quiltForm');
    if (name && color && Number.isInteger(width) && width > 0 && Number.isInteger(height) && height > 0) {
        var quiltBox = document.getElementById('quiltBox');
        createQuiltBox(quiltBox, name, color, width, height, comments, quiltForm);
    }

    document.getElementById('clearQuiltsButton').style.display = 'block';
                
    try {
        var response = await fetch('http://127.0.0.1:5000/add_quilt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                color: color,
                width: width,
                height: height,
                comments: comments
            })
        });

        if (!response.ok) {
             throw new Error(`HTTP error! status: ${response.status}`);
        }

        var data = await response.json();
        console.log(data);

        if (data.message === 'Quilt added successfully') {
            alert('Quilt added successfully!');
        } else {
            alert('There was an error adding the quilt.');
        }
    } 
    
    catch (error) {
        console.error('An error occurred:', error);  // Log any errors that might be happening
    }
}

function createQuiltBox(quiltBox, name, color, width, height, comments){
        quiltBox.style.display = 'block';  // Show the quiltBox
        var newQuilt = document.createElement('div');
        newQuilt.className = 'quilt';
        newQuilt.innerHTML = `
            <h2>${name}</h2>
            <p>Color: ${color}</p>
            <p>Width: ${width}</p>
            <p>Height: ${height}</p>
            ${comments ? `<p>Comments: ${comments}</p>` : ''}
            <button class="edit">Edit</button>
        `;

        // Add the new quilt to the quiltbox
        quiltBox.appendChild(newQuilt);
        quilts.push(newQuilt);

        addEditButton(newQuilt, quiltBox, name, color, width, height, comments);

        document.getElementById('createQuiltButton').style.display = 'block';
        document.getElementById('saveQuiltButton').style.display = 'block';
        quiltForm.reset();
}

function addEditButton(newQuilt, quiltBox, name, color, width, height, comments) {
    newQuilt.querySelector('.edit').addEventListener('click', function() {
        document.getElementById('name').value = name;
        document.getElementById('color').value = color;
        document.getElementById('width').value = width;
        document.getElementById('height').value = height;
        document.getElementById('comments').value = comments;
        quiltBox.removeChild(newQuilt);
        let quiltId = newQuilt.id;

        if (quiltBox.children.length === 0) {
            quiltBox.style.display = 'none';
            document.getElementById('createQuiltButton').style.display = "none";
        }
        enterEditMode(quiltId)
    });
}

function enterEditMode(quiltId) {
    lastIndex = quilts.findIndex(quilt => quilt.id === quiltId);
    if (lastIndex === -1) {
        console.error('Quilt not found');
        return;
    }

    editMode = true;
    document.getElementById('submitQuiltButton').style.display = "block";
    document.getElementById('addQuiltButton').style.display = "none"; // Hide the "Add Quilt" button
}

function exitEditMode() {
    editMode = false;
    document.getElementById('submitQuiltButton').style.display = "none";
    document.getElementById('addQuiltButton').style.display = "block"; // Show the "Add Quilt" button

    // Show the "Create Quilt" button when you exit the edit mode
    document.getElementById('createQuiltButton').style.display = "inline";
}

async function submitQuilt(index) {
    let id;
    try {
        const response = await fetch(`/get-quilt-id/${index}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (response.ok) {
            const data = await response.json();
            id = data.id;
            console.log(id);
        } else {
            console.error(`HTTP error! status: ${response.status}`);
        }
    } catch (error) {
        console.error('Error:', error);
    }

    // Get new values from the form
    var quiltForm = document.getElementById('quiltForm');
    var quiltName = document.getElementById('name').value;
    var newValues = {
        color: document.getElementById('color').value,
        width: document.getElementById('width').value,
        height: document.getElementById('height').value,
        comments: document.getElementById('comments').value,
    };
    newValues.name = quiltName;

    // Send a PUT request to the server with the new data
    try {
        const response = await fetch(`/update-quilt/${id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newValues)
        });
        if (response.ok) {
            const updatedData = await response.json();
            console.log(updatedData);
            console.log('Quilt updated successfully');
            exitEditMode();
        } else {
            console.error(`HTTP error! status: ${response.status}`);
        }
    } catch (error) {
        console.error('Error:', error);
    }

    widthElement = parseInt(document.getElementById('width').value);
    heightElement = parseInt(document.getElementById('height').value);
    colorElement = document.getElementById('color').value;
    commentsElement = document.getElementById('comments').value;

    if (quiltName && colorElement && Number.isInteger(widthElement) && widthElement > 0 && 
    Number.isInteger(heightElement) && heightElement > 0) {
        var quiltBox = document.getElementById('quiltBox');
        createQuiltBox(quiltBox, quiltName, colorElement, 
        widthElement, heightElement, commentsElement, quiltForm);
        quiltBox.appendChild(newQuilt);
        quilts.push(newQuilt);
    }
}

document.getElementById('saveQuiltButton').addEventListener('click', async function() {
    try {
        // Fetch the quilt data from the server
        const response = await fetch('/getQuiltData');
        if (response.headers.get('Content-Type').includes('application/json')) {
            let quilts = await response.json();
            quilts = quilts.map(quilt => {
                return {
                    ...quilt,
                    width: parseInt(quilt.width, 10),
                    height: parseInt(quilt.height, 10),
                    area: parseInt(quilt.width, 10) * parseInt(quilt.height, 10)
                };
            });
    
            // Convert the quilt data to a JSON string
            const json = JSON.stringify(quilts, null, 2);
    
            // Create a new Blob object with the JSON string
            const blob = new Blob([json], {type: 'application/json'});
    
            // Create a URL for the Blob object
            const url = URL.createObjectURL(blob);
    
            // Create a new link element
            const link = document.createElement('a');
    
            // Set the href of the link to the URL of the Blob object
            link.href = url;
    
            // Set the download attribute of the link to the desired file name
            link.download = 'quilts.json';
    
            // Append the link to the body
            document.body.appendChild(link);
    
            // Programmatically click the link
            link.click();
    
            // Remove the link from the body
            document.body.removeChild(link);
            const data = await clearResponse.json();
            console.log(data);
        } else {
            console.error('Expected JSON but received', await response.text());
        }

        
    } catch (error) {
        console.error('Error:', error);
    }
});

document.getElementById('loadQuiltButton').addEventListener('click', function() {
    var fileInput = document.getElementById('jsonFileInput');
    var file = fileInput.files[0];
    if (file) {
        var reader = new FileReader();
        reader.onload = function(e) {
            try {
                var data = JSON.parse(e.target.result);
                addQuilt = data;

                // Send a POST request to the server with the loaded data
                fetch('/load_quilts', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(data => {
                    console.log(data);
                    var quiltBox = document.getElementById('quiltBox');
                    for (var i = 0; i < addQuilt.length; i++) {
                        var quilt = addQuilt[i];
                        if (quilt.hasOwnProperty('name') && quilt.hasOwnProperty('color') && quilt.hasOwnProperty('width') && quilt.hasOwnProperty('height') && quilt.hasOwnProperty('comments')) {
                            createQuiltBox(quiltBox, quilt.name, quilt.color, quilt.width, quilt.height, quilt.comments);
                            document.getElementById('clearQuiltsButton').style.display = 'block';
                        } else {
                            console.error('Quilt does not have all required properties:', quilt);
                        }
                    }
                })
                .catch(error => console.error('Error:', error));

            } catch (error) {
                console.error('Error parsing JSON:', error);
            }
        };
        reader.onerror = function() {
            console.error('Error reading file:', reader.error);
        };
        reader.readAsText(file);
    } else {
        console.error('No file selected');
    }
});

function clearQuilts() {
    // Get the quiltBox element
    var quiltBox = document.getElementById('quiltBox');

    // Remove all quilts from the quiltBox
    while (quiltBox.firstChild) {
        quiltBox.removeChild(quiltBox.firstChild);
    }

    // Hide the "Clear Quilts" button
    document.getElementById('clearQuiltsButton').style.display = 'none';
}