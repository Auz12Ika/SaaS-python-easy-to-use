import bcrypt
from cryptography.fernet import Fernet
import base64
import os

class CryptoManager:
    def __init__(self, secret_key: str):
        # Generate key dari secret_key yang ada
        key = base64.urlsafe_b64encode(secret_key[:32].encode().ljust(32, b'\0'))
        self.cipher = Fernet(key)
    
    def hash_password(self, password: str) -> str:
        """Hash password untuk authentication (tidak bisa di-reverse)"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_hash(self, password: str, hashed_password: str) -> bool:
        """Verifikasi password terhadap hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except:
            return False
    
    def encrypt(self, data: str) -> str:
        """Enkripsi data (bisa di-decrypt)"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()