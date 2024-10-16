import os
from flask import Flask, render_template, redirect, request, send_file, url_for, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import socket


app = Flask(__name__)
app.config['SECRET_KEY'] = 'fdsjhkFByukeafgsdyrdgj'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# 資料庫模型
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 登入表單
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=80)])
    submit = SubmitField('Login')

# 註冊表單
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=80)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

# 初始化資料庫
with app.app_context():
    db.create_all()

# 首頁
@app.route('/')
def home():
    return render_template('home.html')

# 登入頁面
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

# 註冊頁面
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user is None:
            # 在註冊時使用 pbkdf2:sha256 加密
            hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Your account has been created!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists. Please choose a different one.', 'danger')
    return render_template('register.html', form=form)

# 儀表板頁面
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# 登出
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# 處理表單提交
@app.route('/submit', methods=['POST'])
def submit():
    id = request.form.get('id')
    
    if id == "buy_gbl":
        return redirect('https://youtu.be/UIp6_0kct_U')
    
    elif id == "download_mc_mod":
        return render_template('download_mod.html')
    
    elif id == "dlmcmodac":
        return render_template('home.html')
    
    elif id == "video":
        return render_template('video.html')
                
    else:
        return render_template('404.html')
    
@app.route('/download_mc_mod')
def download_mc_mod ():
    return render_template('download_mod.html')

@app.route('/buy_gbl')
def buy_gbl():
    return redirect('https://youtu.be/UIp6_0kct_U')

@app.route('/video')
def video():
    return render_template('video.html')

# 文件下載
@app.route('/download', methods=['GET', 'POST'])
def download_file():
    try:
        # 獲取當前腳本的目錄
        dir_path = os.path.dirname(os.path.realpath(__file__))
        # 使用相對路徑構建檔案路徑
        file_path = os.path.join(dir_path, 'static', 'mods.zip')
        
        # 檢查檔案是否存在
        if not os.path.exists(file_path):
            return render_template('404.html')
        
        return send_file(file_path, as_attachment=True)
    
    except Exception as e:
        return str(e)
    

# 影片資料
video_data = {
    1: {"title": "香港國安法教育", "description": "香港國安法教育-羽毛球篇", "video_file": "video1.mp4"},
    #2: {"title": "新功能預告", "description": "即將推出的新功能介紹。", "video_file": "video2.mp4"},
    #3: {"title": "使用教學", "description": "巨軟系統的使用教學。", "video_file": "video3.mp4"}
}

# 影片播放頁面
@app.route('/playvideo/<int:video_id>')
def playvideo(video_id):
    video = video_data.get(video_id, {"title": "影片未找到", "description": "抱歉，我們找不到該影片。", "video_file": ""})
    return render_template('playvideo.html', video_title=video['title'], video_description=video['description'], video_file=video['video_file'])


# 檢查Minecraft伺服器是否在線
def is_minecraft_server_online(ip, port=25565):
    try:
        with socket.create_connection((ip, port), timeout=10):
            return True
    except OSError:
        return False

# Minecraft伺服器狀態檢查路由
@app.route('/check_server_status')
@login_required
def check_server_status():
    ip = "192.168.0.230"
    if is_minecraft_server_online(ip):
        return jsonify(status='online')
    else:
        return jsonify(status='offline')

# 統一404錯誤處理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
