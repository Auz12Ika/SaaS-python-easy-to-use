from datetime import datetime
from typing import Tuple
from firebase_service import FirebaseSaaS
import bcrypt

class AuthManager:
    def __init__(self, firebase_service: FirebaseSaaS):
        self.firebase_service = firebase_service

    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """Validasi kekuatan password"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
            
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
            
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
            
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"
            
        return True, "Password is strong"

    def register(self, name: str, email: str, company: str, password: str) -> Tuple[bool, str]:
        """Register user"""
        email = email.lower().strip()
        existing_user = self.firebase_service.get_user_by_email(email)
        if existing_user:
            return False, "Email already registered."

        # Validasi password
        is_valid, message = self.validate_password_strength(password)
        if not is_valid:
            return False, message

        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
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

        user_id = self.firebase_service.create_user(user_data)
        if user_id:
            self.firebase_service.log_activity(user_id, "User registered.")
            return True, user_id
        else:
            return False, "Registration failed."

    def login(self, email: str, password: str) -> Tuple[bool, str]:
        """Login user - FIXED VERSION"""
        email = email.lower().strip()
        
        # Cari user di Firebase
        user = self.firebase_service.get_user_by_email(email)
        if not user:
            print("DEBUG LOGIN: User not found")
            return False, "User not found"
        
        # Debug: print data user yang ditemukan
        print(f"DEBUG LOGIN: User object: {user}")
        print(f"DEBUG LOGIN: User ID: {user.id}, Email: {user.email}")
        
        # Cek apakah user memiliki password_hash
        if not user.password_hash:
            print("DEBUG LOGIN: No password hash found")
            return False, "No password set for this account"
        
        # Verifikasi password
        try:
            if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                print("DEBUG LOGIN: Password correct")
                # Update last login
                self.firebase_service.update_user(user.id, {
                    'last_login': datetime.now().isoformat()
                })
                return True, user.id
            else:
                print("DEBUG LOGIN: Wrong password")
                return False, "Wrong password"
        except Exception as e:
            print(f"DEBUG LOGIN: Password verification error: {e}")
            return False, f"Password verification failed: {str(e)}"