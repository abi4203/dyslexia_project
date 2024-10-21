from flask import Flask, Response, render_template, jsonify, request, Blueprint
import cv2
from ultralytics import YOLO
import random
import os
import sqlite3

module1_blueprint = Blueprint('module1', __name__, template_folder='templates', static_folder='static')

# Load YOLOv8 model
model = YOLO('yolov8n.pt')

# Initialize camera
cap = cv2.VideoCapture(0)

# Create a directory to save detected images
IMAGE_DIR = os.path.join(os.path.dirname(__file__), '../static/detected_images')

os.makedirs(IMAGE_DIR, exist_ok=True)

# Database setup
def init_db():
    conn = sqlite3.connect('game.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS scores
                 (name TEXT, code TEXT, score INTEGER)''')
    conn.close()

init_db()

@module1_blueprint.route('/')
def landing_page():
    return render_template('landing.html')

@module1_blueprint.route('/game')
def game_page():
    return render_template('game.html')

def gen_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        results = model(frame)
        detections = results[0].boxes

        for box in detections:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = box.conf.item()
            cls = int(box.cls.item())
            label = f"{model.names[cls]} {conf:.2f}"
            frame = cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            frame = cv2.putText(frame, label, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@module1_blueprint.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@module1_blueprint.route('/capture', methods=['POST'])
def capture():
    success, frame = cap.read()
    detected_object_name = ""
    cropped_object_image_path = ""
    choices = []

    if success:
        results = model(frame)
        detections = results[0].boxes

        if detections:
            highest_conf_box = max(detections, key=lambda box: box.conf)
            detected_object_name = model.names[int(highest_conf_box.cls)]
            x1, y1, x2, y2 = map(int, highest_conf_box.xyxy[0].tolist())
            cropped_frame = frame[y1:y2, x1:x2]
            cropped_object_image_path = os.path.join(IMAGE_DIR, f'cropped_{detected_object_name}.jpg')
            cv2.imwrite(cropped_object_image_path, cropped_frame)
            jumbled_names = generate_jumbled_names(detected_object_name)
            choices = [detected_object_name] + jumbled_names
            random.shuffle(choices)

    return jsonify({
        "object": detected_object_name,
        "choices": choices,
        "cropped_image_path": f'static/detected_images/cropped_{detected_object_name}.jpg'.replace("\\", "/")
    })

@module1_blueprint.route('/update_score', methods=['POST'])
def update_score():
    data = request.get_json()
    name = data['name']
    code = data['code']
    score = data['score']

    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    # Check if the player already has a score
    cursor.execute("SELECT score FROM scores WHERE name=? AND code=?", (name, code))
    existing_score = cursor.fetchone()

    if existing_score:
        new_score = existing_score[0] + score
        cursor.execute("UPDATE scores SET score=? WHERE name=? AND code=?", (new_score, name, code))
    else:
        new_score = score
        cursor.execute("INSERT INTO scores (name, code, score) VALUES (?, ?, ?)", (name, code, new_score))

    conn.commit()
    total_score = new_score
    conn.close()

    return jsonify({"total_score": total_score})
    
@module1_blueprint.route('/get_score', methods=['GET'])
def get_score():
    name = request.args.get('name')
    code = request.args.get('code')

    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()

    cursor.execute("SELECT score FROM scores WHERE name=? AND code=?", (name, code))
    result = cursor.fetchone()

    conn.close()

    if result:
        total_score = result[0]
    else:
        total_score = 0

    return jsonify({"total_score": total_score})

def generate_jumbled_names(correct_name):
    # Generate two jumbled versions of the correct name
    def jumble_word(word):
        word = list(word)
        random.shuffle(word)
        return ''.join(word)
    
    jumbled_names = []
    while len(jumbled_names) < 2:
        jumbled = jumble_word(correct_name)
        if jumbled != correct_name and jumbled not in jumbled_names:
            jumbled_names.append(jumbled)

    return jumbled_names


