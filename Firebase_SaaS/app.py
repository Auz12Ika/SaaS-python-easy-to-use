from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from firebase_service import FirebaseSaaS
from models import SaaSconfig
from crypto import CryptoManager
from datetime import datetime
from typing import Tuple

app = Flask(__name__)
app.secret_key = '190800'

# Configuration
DATABASE_URL = "https://percobaan-api-2818f-default-rtdb.firebaseio.com"
SECRET_KEY = "BNzuGEnl2S63BP0adsNW8iTKJC299Ucpn8DgnkbzG6vOsdpT6JKRYRKOuCwiNSS33rdB2pbQ03YtquX1zSoTehs"

# Initialize services
firebase_service = FirebaseSaaS(DATABASE_URL, SECRET_KEY)
crypto_manager = CryptoManager(SECRET_KEY)

class AuthManager:
    def __init__(self, firebase_service: FirebaseSaaS, crypto_manager: CryptoManager):
        self.firebase_service = firebase_service
        self.crypto = crypto_manager

    def register(self, name: str, email: str, company: str, password: str) -> Tuple[bool, str]:
        """REGISTER - SIMPLE & WORKING"""
        try:
            email = email.lower().strip()
            print(f"🔄 REGISTER: Processing {email}")
            
            # Check if email exists
            existing_user = self.firebase_service.get_user_by_email(email)
            if existing_user:
                return False, "Email sudah terdaftar"
            
            # Simple password validation
            if len(password) < 6:
                return False, "Password minimal 6 karakter"

            # Hash password
            hashed_password = self.crypto.hash_password(password)
            
            # Create user data - SIMPLE VERSION
            user_data = {
                'name': name,
                'email': email, 
                'company': company,
                'password_hash': hashed_password,
                'plan': 'free',
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'is_active': True
            }

            # Save to Firebase
            user_id = self.firebase_service.create_user(user_data)
            
            if user_id:
                print(f"✅ REGISTER SUCCESS: {email} -> {user_id}")
                return True, user_id
            else:
                return False, "Gagal membuat user"
                
        except Exception as e:
            print(f"❌ REGISTER ERROR: {e}")
            return False, f"Error: {str(e)}"

    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """LOGIN - SIMPLE & WORKING"""
        try:
            email = email.lower().strip()
            print(f"🔄 LOGIN: Attempting {email}")
            
            # Find user
            user = self.firebase_service.get_user_by_email(email)
            if not user:
                return False, "User tidak ditemukan"
            
            print(f"🔍 LOGIN DEBUG: User found - {user.name}, Hash: {user.password_hash[:20] if user.password_hash else 'None'}")
            
            # Check password hash
            if not user.password_hash:
                return False, "Akun tidak memiliki password"
            
            # Verify password
            if self.crypto.verify_hash(password, user.password_hash):
                print(f"✅ LOGIN SUCCESS: {email}")
                return True, user.id
            else:
                return False, "Password salah"
                
        except Exception as e:
            print(f"❌ LOGIN ERROR: {e}")
            return False, f"Error: {str(e)}"

# Initialize auth manager
auth_manager = AuthManager(firebase_service, crypto_manager)

# ==================== ROUTES ====================

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('home.html', plans=SaaSconfig.PLANS)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """REGISTER - SIMPLE & WORKING"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip().lower()
            company = request.form.get('company', '').strip()
            password = request.form.get('password', '')
            
            # Basic validation
            if not name or not email or not password:
                return render_template('register.html', error="Nama, email, dan password wajib diisi")
            
            # Register user
            success, result = auth_manager.register(name, email, company, password)
            
            if success:
                session['user_id'] = result
                print(f"🎯 SESSION SET: {result}")
                return redirect(url_for('dashboard'))
            else:
                return render_template('register.html', error=result)
                
        except Exception as e:
            return render_template('register.html', error=f"System error: {str(e)}")
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """LOGIN - FIXED VERSION"""
    if request.method == 'POST':
        try:
            # Ambil data dari form
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            
            print(f"🔍 LOGIN ATTEMPT: {email}")
            
            # Validasi input
            if not email or not password:
                return render_template('login.html', error="Email dan password wajib diisi")
            
            # Cari user di Firebase
            user = firebase_service.get_user_by_email(email)
            if not user:
                print(f"❌ USER NOT FOUND: {email}")
                return render_template('login.html', error="Email tidak ditemukan")
            
            print(f"✅ USER OBJECT:")
            print(f"   - ID: {user.id}")
            print(f"   - Name: {user.name}")
            print(f"   - Password Hash: {user.password_hash}")
            
            # Cek apakah user punya password hash
            if not user.password_hash:
                print(f"❌ NO PASSWORD HASH IN USER OBJECT")
                return render_template('login.html', error="Akun tidak memiliki password")
            
            # Verifikasi password - DEBUG DETAIL
            print(f"🔐 PASSWORD VERIFICATION DETAIL:")
            print(f"   - Input Password: {password}")
            print(f"   - Stored Hash: {user.password_hash}")
            
            is_password_correct = crypto_manager.verify_hash(password, user.password_hash)
            print(f"   - Verification Result: {is_password_correct}")
            
            if is_password_correct:
                # Login berhasil
                session['user_id'] = user.id
                
                # Update last login
                firebase_service.update_user(user.id, {
                    'last_login': datetime.now().isoformat()
                })
                
                print(f"🎉 LOGIN SUCCESS: {user.email}")
                return redirect(url_for('dashboard'))
            else:
                print(f"❌ PASSWORD VERIFICATION FAILED")
                return render_template('login.html', error="Password salah")
                
        except Exception as e:
            print(f"🔥 LOGIN ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return render_template('login.html', error="System error: " + str(e))
    
    # GET request - tampilkan form login
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """DASHBOARD - SIMPLE & WORKING"""
    if 'user_id' not in session:
        print("❌ DASHBOARD: No session")
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    print(f"🔄 DASHBOARD: Loading user {user_id}")
    
    user = firebase_service.get_user(user_id)
    
    if not user:
        print("❌ DASHBOARD: User not found")
        session.pop('user_id', None)
        return redirect(url_for('login'))

    print(f"✅ DASHBOARD: User loaded - {user.name}")
    return render_template('dashboard.html', user=user, plans=SaaSconfig.PLANS)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    print("🚀 STARTING FIXED VERSION...")
    print("📍 Target: REGISTER & LOGIN WORKING")
    app.run(debug=True, port=5000)