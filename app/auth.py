from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from .models import db, User, WorkSession
from .store import current_stats, reset_stats

auth_bp = Blueprint('auth', __name__)

# --- 1. ĐĂNG NHẬP ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username, password=password).first()
        
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            # Lưu tên thật vào session để hiển thị (nếu không có thì lấy username)
            session['fullname'] = user.fullname if user.fullname else user.username
            
            reset_stats()
            return redirect(url_for('main.index'))
        else:
            flash('Sai tài khoản hoặc mật khẩu!')
            
    return render_template('login.html')

# --- 2. ĐĂNG KÝ (Cập nhật mới) ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Lấy thông tin cá nhân từ form
        fullname = request.form.get('fullname')
        phone = request.form.get('phone')
        dob_str = request.form.get('dob') # Dạng chuỗi 'YYYY-MM-DD'
        
        # Xử lý ngày sinh
        dob_obj = None
        if dob_str:
            try:
                dob_obj = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                pass 
        
        if User.query.filter_by(username=username).first():
            flash('Tài khoản đã tồn tại!')
        else:
            # Lưu user mới với đầy đủ thông tin
            new_user = User(
                username=username, 
                password=password,
                fullname=fullname,
                phone=phone,
                dob=dob_obj
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash('Đăng ký thành công! Hãy đăng nhập.')
            return redirect(url_for('auth.login'))
            
    return render_template('register.html')

# --- 3. ĐĂNG XUẤT ---
@auth_bp.route('/logout')
def logout():
    if 'user_id' in session and current_stats["start_time"]:
        end_time = datetime.now()
        duration = (end_time - current_stats["start_time"]).total_seconds() / 60.0
        
        avg_t = 0
        avg_h = 0
        if current_stats["count_samples"] > 0:
            avg_t = current_stats["temp_sum"] / current_stats["count_samples"]
            avg_h = current_stats["humid_sum"] / current_stats["count_samples"]
            
        new_session = WorkSession(
            user_id=session['user_id'],
            start_time=current_stats["start_time"],
            end_time=end_time,
            duration_minutes=round(duration, 2),
            warning_count=current_stats["warning_count"],
            avg_temp=round(avg_t, 2),
            avg_humidity=round(avg_h, 2)
        )
        db.session.add(new_session)
        db.session.commit()

    # Xóa sạch session
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('fullname', None)
    
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    # Bắt buộc phải đăng nhập mới được vào
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Lấy thông tin user hiện tại từ DB
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        # Nhận dữ liệu từ form
        fullname = request.form.get('fullname')
        phone = request.form.get('phone')
        dob_str = request.form.get('dob')
        
        # Xử lý ngày sinh
        dob_obj = None
        if dob_str:
            try:
                dob_obj = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        # Cập nhật vào đối tượng user
        user.fullname = fullname
        user.phone = phone
        user.dob = dob_obj
        
        # Lưu xuống DB
        db.session.commit()
        
        # Cập nhật lại session fullname để Dashboard hiển thị tên mới ngay
        session['fullname'] = user.fullname if user.fullname else user.username
        
        flash('Cập nhật thông tin thành công!')
        
        # Reload lại trang để thấy thay đổi
        return redirect(url_for('auth.profile'))
        
    return render_template('profile.html', user=user)