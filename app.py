from flask import Flask, request, jsonify, render_template
import time

app = Flask(__name__)

# --- 1. DỮ LIỆU MẶC ĐỊNH (Lưu trữ trạng thái hiện tại) ---
latest_posture = {
    "deviceKey": "AI_LAPTOP_01",
    "status": "GOOD",
    "neckDist": 0,
    "timestamp": "Waiting..."
}

latest_sensors = {
    "deviceKey": "ESP32_ROOM_A",
    "temperature": 0,
    "humidity": 0,
    "airQuality": 100,
    "gas": 0,             # <--- Mới thêm: Chỉ số Gas
    "isAlarm": False,     # <--- Mới thêm: Trạng thái Còi
    "timestamp": "Waiting..."
}

# Trạng thái đèn (Mặc định là Tắt)
light_state = {"status": "OFF"}

# --- 2. CÁC ĐƯỜNG DẪN WEB (ROUTER) ---

@app.route('/')
def index():
    return render_template('index.html', posture=latest_posture, sensors=latest_sensors)

# API nhận dữ liệu AI (Tư thế)
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
    return jsonify({"message": "Posture updated"}), 200

# API nhận dữ liệu ESP32 (Cảm biến) -> QUAN TRỌNG: Đã thêm Gas
@app.route('/api/v1/sensors', methods=['POST'])
def update_sensors():
    global latest_sensors
    data = request.get_json()
    
    # Cập nhật đầy đủ các trường dữ liệu từ ESP32
    latest_sensors = {
        "deviceKey": data.get('deviceKey'),
        "temperature": data.get('temperature'),
        "humidity": data.get('humidity'),
        "airQuality": data.get('airQuality'),
        "gas": data.get('gas'),           # <--- Server đã nhận Gas
        "isAlarm": data.get('isAlarm'),   # <--- Server đã nhận Báo động
        "timestamp": data.get('timestamp')
    }
    # In ra Terminal để bạn kiểm tra xem có nhận được không
    print(f"Update Sensor: Temp={latest_sensors['temperature']}, Gas={latest_sensors['gas']}")
    
    return jsonify({"message": "Sensor data updated"}), 200

# API trả dữ liệu cho Web (Frontend gọi cái này để vẽ lại giao diện)
@app.route('/api/v1/data', methods=['GET'])
def get_data():
    return jsonify({
        "posture": latest_posture,
        "sensors": latest_sensors
    })

# --- 3. CÁC API ĐIỀU KHIỂN ĐÈN ---

# Web bấm nút -> Gửi lệnh vào đây
@app.route('/api/v1/light/toggle', methods=['POST'])
def toggle_light():
    global light_state
    data = request.get_json()
    light_state["status"] = data.get("status")
    print(f"Lệnh điều khiển đèn: {light_state['status']}")
    return jsonify({"message": "Light updated", "current_status": light_state["status"]}), 200

# ESP32 hỏi trạng thái đèn -> Gọi cái này
@app.route('/api/v1/light/status', methods=['GET'])
def get_light_status():
    return jsonify(light_state)

if __name__ == '__main__':
    # Chạy ở 0.0.0.0 để ESP32 có thể truy cập
    app.run(host='0.0.0.0', port=5000, debug=True)