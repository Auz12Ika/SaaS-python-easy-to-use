from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import bcrypt

@dataclass
class User :
    """Model data user"""
    def __init__(self, id: str = None, **kwargs):
        self.id = id
        self.name = kwargs.get('name', '')
        self.email = kwargs.get('email', '')
        self.company = kwargs.get('company', '')
        self.plan = kwargs.get('plan', 'free')
        self.created_at = kwargs.get('created_at', '')
        self.last_login = kwargs.get('last_login', '')
        self.is_active = kwargs.get('is_active', True)
        self.password_hash = kwargs.get('password_hash', '')

    def set_password(self, password):
        """Set password hash dari plain password"""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        """Verifikasi password terhadap hash"""
        if not self.password_hash:
            return False
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                self.password_hash.encode('utf-8')
            )
        except:
            return False

    def has_password(self):
        """Cek apakah user sudah memiliki password"""
        return bool(self.password_hash)

@dataclass
class Subscription:
        user_id: str
        plan: str
        status: str = "active"
        created_at: datetime = datetime.now()
        expires_at: Optional[datetime] = None

class SaaSconfig:
    PLANS = {
        "free": {"price": 0, "features": ["10 users", "1GB storage"]},
        "premium": {"price": 29, "features": ["100 users", "10GB storage", "Priority support"]},
        "enterprise": {"price": 99, "features": ["Unlimited users", "100GB storage", "24/7 support"]}
    }

