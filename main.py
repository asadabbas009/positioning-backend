from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable WebSockets

# Folder containing position images
IMAGE_FOLDER = os.path.join(os.getcwd(), "positions")

# Ensure the folder exists
if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)

# Store latest force sensor value and triggered position
force_sensor_value = 0
last_position = None

# Mapping positions to image filenames
POSITION_IMAGES = {
    "HEAD_FIRST_SUPINE": "image_1.jpeg.jpg",
    "HEAD_FIRST_PRONE": "image_2.jpeg.jpg",
    "HEAD_FIRST_DECUBITUS_RIGHT": "image_3.jpeg.jpg",
    "HEAD_FIRST_DECUBITUS_LEFT": "image_4.jpeg.jpg",
    "FEET_FIRST_SUPINE": "image_5.jpeg.jpg",
    "FEET_FIRST_PRONE": "image_6.jpeg.jpg",
    "FEET_FIRST": "image_7.jpeg.jpg",
    "DECUBITUS_RIGHT": "image_8.jpeg.jpg",
    "FEET_FIRST_DECUBITUS_LEFT": "image_9.jpeg.jpg",
}

@app.route('/trigger', methods=['POST'])
def trigger_position():
    global last_position

    data = request.get_json()
    position = data.get("position")

    if position in POSITION_IMAGES:
        image_filename = POSITION_IMAGES[position]
        image_url = f"http://{request.host}/positions/{image_filename}"
        last_position = position  # Store last triggered position
        
        # Convert position name for better readability
        position_name = position.replace("_", " ")
        
        # Print position name in Flask backend
        print(f"Received Position: {position_name}")

        # Emit the new position to all connected clients
        socketio.emit("update_position", {"position": position_name, "image_url": image_url})

        return jsonify({"status": "success", "position": position_name, "image_url": image_url})

    return jsonify({"status": "error", "message": "Invalid position"}), 400

@app.route('/positions/<filename>')
def get_image(filename):
    return send_from_directory(IMAGE_FOLDER , filename)

@app.route('/force_sensor', methods=['POST', 'GET'])
def handle_force_sensor():
    global force_sensor_value

    if request.method == 'POST':
        data = request.get_json()
        force_value = data.get("force_value")

        if force_value is not None:
            force_sensor_value = force_value  # Store the latest value
            print(f"Force Sensor Value: {force_value}")  # Print in Flask backend
            return jsonify({"status": "success", "message": "Force sensor value updated."})

        return jsonify({"status": "error", "message": "No force value provided"}), 400

    elif request.method == 'GET':
        return jsonify({"force_value": force_sensor_value})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)