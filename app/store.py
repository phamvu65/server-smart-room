from datetime import datetime

# Biến lưu trữ RAM
latest_posture = {"deviceKey": "AI_LAPTOP", "status": "WAITING", "neckDist": 0, "timestamp": "..."}
latest_sensors = {"deviceKey": "ESP32", "temperature": 0, "humidity": 0, "gas": 0, "isAlarm": False, "timestamp": "..."}
light_state = {"status": "OFF"}

current_stats = {
    "temp_sum": 0, "humid_sum": 0, "count_samples": 0,
    "warning_count": 0, "start_time": None
}

def reset_stats():
    current_stats["temp_sum"] = 0
    current_stats["humid_sum"] = 0
    current_stats["count_samples"] = 0
    current_stats["warning_count"] = 0
    current_stats["start_time"] = datetime.now()