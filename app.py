from flask import Flask, request, jsonify, render_template
import time

app = Flask(__name__)

# Dữ liệu cảm biến và tư thế (biến toàn cục để lưu trữ dữ liệu mới nhất)
latest_posture = {
    "deviceKey": "AI_LAPTOP_01",
    "status": "GOOD",
    "neckDist": 120,
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
}

latest_sensors = {
    "deviceKey": "ESP32_ROOM_A",
    "temperature": 25.5,
    "humidity": 60,
    "airQuality": 150,
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
}

@app.route('/')
def index():
    return render_template('index.html', posture=latest_posture, sensors=latest_sensors)

@app.route('/api/v1/posture', methods=['POST'])
def update_posture():
    global latest_posture
    data = request.get_json()
    latest_posture = {
        "deviceKey": data.get('deviceKey'),
        "status": data.get('status'),
        "neckDist": data.get('neckDist'),
        "timestamp": data.get('timestamp')
    }
    return jsonify({"message": "Posture data updated successfully"}), 200

@app.route('/api/v1/sensors', methods=['POST'])
def update_sensors():
    global latest_sensors
    data = request.get_json()
    latest_sensors = {
        "deviceKey": data.get('deviceKey'),
        "temperature": data.get('temperature'),
        "humidity": data.get('humidity'),
        "airQuality": data.get('airQuality'),
        "timestamp": data.get('timestamp')
    }
    return jsonify({"message": "Sensor data updated successfully"}), 200

@app.route('/api/v1/data', methods=['GET'])
def get_data():
    # Trả về dữ liệu tổng hợp
    return jsonify({
        "posture": latest_posture,
        "sensors": latest_sensors
    })

if __name__ == '__main__':
    app.run(debug=True)
