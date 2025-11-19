# app_fixed.py - SINGLE FILE DENGAN SEMUA TEMPLATE
import requests
import json
from flask import Flask, render_template_string, request, redirect, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'firebase-saas-secret-key'

DATABASE_URL = "https://percobaan-api-2818f-default-rtdb.firebaseio.com"
SECRET_KEY = "BNzuGEnl2S63BP0adsNW8iTKJC299Ucpn8DgnkbzG6vOsdpT6JKRYRKOuCwiNSS33rdB2pbQ03YtquX1zSoTehs"

# ==================== TEMPLATE STRINGS ====================
HOME_HTML = '''
<!DOCTYPE html><html><head><title>Firebase SaaS</title><style>
body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
.container { background: #f9f9f9; padding: 30px; border-radius: 10px; }
.btn { background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px; }
.status { background: white; padding: 15px; border-radius: 5px; margin: 15px 0; }
</style></head>
<body><div class="container">
    <h1>🚀 Firebase SaaS Platform</h1>
    <p>Platform SaaS sederhana berbasis Firebase</p>
    <div class="status">
        <h3>🔥 Status Sistem:</h3>
        <p>Firebase: <strong style="color: green;">✅ Terhubung</strong></p>
        <p>Server: <strong style="color: green;">✅ Berjalan</strong></p>
        <p>Waktu: <strong>{{ timestamp }}</strong></p>
    </div>
    <div style="margin: 30px 0;">
        <a href="/login" class="btn">🔐 Login</a>
        <a href="/register" class="btn" style="background: #28a745;">📝 Register</a>
    </div>
</div></body></html>
'''

LOGIN_HTML = '''
<!DOCTYPE html><html><head><title>Login</title><style>
body { font-family: Arial; max-width: 400px; margin: 50px auto; padding: 20px; }
.form-group { margin: 15px 0; } label { display: block; margin-bottom: 5px; }
input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
.error { color: red; margin: 10px 0; }
</style></head>
<body><h2>🔐 Login</h2>
{% if error %}<div class="error">{{ error }}</div>{% endif %}
<form method="POST">
    <div class="form-group"><label>Email:</label><input type="email" name="email" required></div>
    <div class="form-group"><label>Password:</label><input type="password" name="password" required></div>
    <button type="submit">Login</button>
</form>
<p style="margin-top: 20px;"><a href="/register">Belum punya akun? Daftar disini</a></p>
</body></html>
'''

REGISTER_HTML = '''
<!DOCTYPE html><html><head><title>Register</title><style>
body { font-family: Arial; max-width: 400px; margin: 50px auto; padding: 20px; }
.form-group { margin: 15px 0; } label { display: block; margin-bottom: 5px; }
input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
button { background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
.error { color: red; margin: 10px 0; }
</style></head>
<body><h2>📝 Register</h2>
{% if error %}<div class="error">{{ error }}</div>{% endif %}
<form method="POST">
    <div class="form-group"><label>Nama Lengkap:</label><input type="text" name="name" required></div>
    <div class="form-group"><label>Email:</label><input type="email" name="email" required></div>
    <div class="form-group"><label>Password:</label><input type="password" name="password" required></div>
    <button type="submit">Daftar</button>
</form>
<p style="margin-top: 20px;"><a href="/login">Sudah punya akun? Login disini</a></p>
</body></html>
'''

DASHBOARD_HTML = '''
<!DOCTYPE html><html><head><title>Dashboard</title><style>
body { font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px; }
.header { background: #007bff; color: white; padding: 20px; border-radius: 5px; }
.user-info { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
.btn { background: #28a745; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; }
</style></head>
<body>
<div class="header"><h1>📊 Dashboard</h1><p>Selamat datang di Firebase SaaS Platform</p></div>
<div class="user-info"><h3>Informasi Akun</h3>
    <p><strong>Nama:</strong> {{ user.name }}</p>
    <p><strong>Email:</strong> {{ user.email }}</p>
    <p><strong>Plan:</strong> {{ user.plan }}</p>
    <p><strong>Bergabung:</strong> {{ user.created_at }}</p>
</div>
<div style="margin: 20px 0;"><h3>🚀 Fitur SaaS</h3>
    <ul><li>User Management</li><li>Subscription Plans</li><li>Firebase Integration</li><li>Real-time Database</li></ul>
</div>
<a href="/logout" class="btn">Logout</a>
</body></html>
'''

# ==================== ROUTES ====================
@app.route('/')
def home():
    return render_template_string(HOME_HTML, timestamp=datetime.now().strftime("%H:%M:%S"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Simple login logic
        session['user_id'] = 'demo_user'
        return redirect('/dashboard')
    return render_template_string(LOGIN_HTML)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        session['user_id'] = 'new_user'
        return redirect('/dashboard')
    return render_template_string(REGISTER_HTML)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_data = {
        'name': 'Demo User',
        'email': 'demo@example.com', 
        'plan': 'free',
        'created_at': datetime.now().strftime("%Y-%m-%d")
    }
    return render_template_string(DASHBOARD_HTML, user=user_data)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')

if __name__ == '__main__':
    print("🚀 Server running on http://localhost:5000")
    print("✅ Firebase SaaS Ready!")
    app.run(debug=True, port=5000)