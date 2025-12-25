from flask import Blueprint, jsonify, request, session, render_template, redirect, url_for
from .store import latest_posture, latest_sensors, light_state, current_stats
from .models import WorkSession

# Tạo Blueprint tên là 'main'
main_bp = Blueprint('main', __name__)

# --- 1. TRANG CHỦ (DASHBOARD) ---
@main_bp.route('/')
def index():
    # Kiểm tra đăng nhập
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Lấy lịch sử làm việc của user hiện tại (5 phiên gần nhất)
    history = WorkSession.query.filter_by(user_id=session['user_id']).order_by(WorkSession.start_time.desc()).limit(5).all()
    
    # Ưu tiên hiển thị Họ tên thật, nếu chưa có thì hiển thị Username
    display_name = session.get('fullname', session['username'])
    
    return render_template('index.html', 
                           username=display_name, 
                           posture=latest_posture, 
                           sensors=latest_sensors,
                           history=history)

# --- 2. CÁC API NHẬN DỮ LIỆU TỪ PHẦN CỨNG ---

# API nhận dữ liệu AI (Tư thế)
@main_bp.route('/api/v1/posture', methods=['POST'])
def update_posture():
    data = request.get_json()
    
    # Cập nhật biến toàn cục
    latest_posture.update({
        "status": data.get('status'),
        "neckDist": data.get('neckDist'),
        "timestamp": data.get('timestamp')
    })
    
    # Logic đếm cảnh báo nếu đang trong phiên làm việc
    if 'user_id' in session and data.get('status') == "BAD":
        current_stats["warning_count"] += 1

    return jsonify({"message": "Posture updated"}), 200

# API nhận dữ liệu ESP32 (Cảm biến)
@main_bp.route('/api/v1/sensors', methods=['POST'])
def update_sensors():
    data = request.get_json()
    
    temp = data.get('temperature', 0)
    hum = data.get('humidity', 0)

    # Cập nhật biến toàn cục
    latest_sensors.update({
        "temperature": temp,
        "humidity": hum,
        "gas": data.get('gas'),
        "isAlarm": data.get('isAlarm'),
        "timestamp": data.get('timestamp')
    })
    
    # Cộng dồn dữ liệu để tính trung bình sau này
    if 'user_id' in session:
        current_stats["temp_sum"] += float(temp)
        current_stats["humid_sum"] += float(hum)
        current_stats["count_samples"] += 1

    return jsonify({"message": "Sensor data updated"}), 200

# --- 3. API GIAO TIẾP VỚI FRONTEND (WEB) ---

# Web gọi hàm này định kỳ để lấy dữ liệu mới nhất vẽ lên màn hình
@main_bp.route('/api/v1/data', methods=['GET'])
def get_data():
    return jsonify({
        "posture": latest_posture,
        "sensors": latest_sensors,
        # Gửi thêm số cảnh báo của phiên hiện tại
        "session_warnings": current_stats["warning_count"] if 'user_id' in session else 0
    })

# --- 4. API ĐIỀU KHIỂN ĐÈN ---

# Web bấm nút -> Gửi lệnh vào đây
@main_bp.route('/api/v1/light/toggle', methods=['POST'])
def toggle_light():
    data = request.get_json()
    light_state["status"] = data.get("status")
    return jsonify({"message": "Light updated", "current_status": light_state["status"]}), 200

# ESP32 hỏi trạng thái đèn -> Gọi cái này
@main_bp.route('/api/v1/light/status', methods=['GET'])
def get_light_status():
    return jsonify(light_state)