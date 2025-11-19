import requests
import json
from typing import Dict, List, Optional
from models import User, Subscription, SaaSconfig

class FirebaseSaaS:
    """core firebase SaaS service class."""

    def __init__(self, database_url: str, secret_key: str):
        self.database_url = database_url.rstrip('/')
        self.secret_key = secret_key

    def _build_url(self, path: str) -> str:
        """Build the full URL for Firebase requests."""
        clean_path = path.strip('/')
        return f"{self.database_url}/{clean_path}.json?auth={self.secret_key}"
    
    # === User management ===
    def create_user(self, user_data: Dict) -> Optional[str]:
        """Create a new user in Firebase."""
        url = self._build_url('users')

        # timestamp for created_at
        user_data['created_at'] = self._get_timestamp()
        user_data["last_login"] = self._get_timestamp()
        user_data['is_active'] = True

        try:
            response = requests.post(url, json=user_data)
            response.raise_for_status()
            if response.status_code == 200:
                result = response.json()
                user_id = result.get('name')
                self._create_subscription(user_id, user_data.get('plan', 'free'))
                return user_id
        except Exception as e:
            print(f"Error creating user: {e}")
        return None

    def get_user_by_email(self, email: str) -> User:
        """Cari user by email - FIXED untuk pastikan baca password_hash"""
        try:
            # Get semua users
            response = requests.get(f"{self.database_url}/users.json")
            if response.status_code == 200:
                users_data = response.json() or {}
            
            # Cari user dengan email yang cocok
                for user_id, user_data in users_data.items():
                    if user_data and user_data.get('email', '').lower() == email.lower():
                        print(f"✅ USER DATA DITEMUKAN:")
                        print(f"   - ID: {user_id}")
                        print(f"   - Name: {user_data.get('name')}")
                        print(f"   - Email: {user_data.get('email')}")
                        print(f"   - Password Hash: {user_data.get('password_hash', 'NOT FOUND')}")
                    
                    # PASTIKAN password_hash diambil dengan benar
                        password_hash = user_data.get('password_hash')
                    
                        return User(
                            id=user_id,
                            name=user_data.get('name', ''),
                            email=user_data.get('email', ''),
                            company=user_data.get('company', ''),
                            plan=user_data.get('plan', 'free'),
                            created_at=user_data.get('created_at', ''),
                            last_login=user_data.get('last_login', ''),
                            is_active=user_data.get('is_active', True),
                            password_hash=password_hash  # PASTIKAN INI DIAmbil
                        )
            
                return None
            else:
                print(f"❌ FIREBASE ERROR: {response.status_code}")
                return None
        except Exception as e:
            print(f"🔥 FIREBASE EXCEPTION: {e}")
            return None

    def get_user(self, user_id: str) -> Optional[User]:
        """get user by ID from Firebase."""
        url = self._build_url(f'users/{user_id}')
        try:
            response = requests.get(url)
            response.raise_for_status()
            if response.status_code == 200:
                user_data = response.json()
                return User(
                    id=user_id,
                    name=user_data.get('name', ''),
                    email=user_data.get('email', ''),
                    company=user_data.get('company', ''),
                    plan=user_data.get('plan', 'free'),
                    created_at=user_data.get('created_at', ''),
                    last_login=user_data.get('last_login'),
                    is_active=user_data.get('is_active', True)
                )
        except Exception as e:
            print(f"Error retrieving user: {e}")
        return None

    def update_user(self, user_id: str, updates: Dict) -> bool:
        """Update user information in Firebase."""
        url = self._build_url(f'users/{user_id}')
        try:
            response = requests.patch(url, json=updates)
            response.raise_for_status()
            return response.status_code == 200
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    # === Subscription management ===
    def _create_subscription(self, user_id: str, plan: str) -> bool:
        """Create a subscription for a user."""
        url = self._build_url(f'subscriptions/{user_id}')
        subscription_data = {
            "user_id": user_id,
            "plan": plan,
            "status": "active",
            "created_at": self._get_timestamp(),
            "expires_at": self._get_future_timestamp(days=30)
        }

        try:
            response = requests.put(url, json=subscription_data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error creating subscription: {e}")
            return False
    
    def get_subscription(self, user_id: str) -> Optional[Dict]:
        """Get subscription details for a user."""
        url = self._build_url(f'subscriptions/{user_id}')
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error retrieving subscription: {e}")
        return None

    def upgrade_subscription(self, user_id: str, new_plan: str) -> bool:
        """Upgrade a user's subscription plan."""
        if new_plan not in SaaSconfig.PLANS:
            print(f"Plan {new_plan} does not exist.")
            return False
        
        subscription_update = {
            "plan": new_plan,
            "upgraded_at": self._get_timestamp(),
            "status": "active",
            "expires_at": self._get_future_timestamp(days=30)
        }

        url = self._build_url(f'subscriptions/{user_id}')
        try:
            response = requests.patch(url, json=subscription_update)

            # record plan in user data as well
            if response.status_code == 200:
                self.update_user(user_id, {"plan": new_plan})
                return True
        except Exception as e:
            print(f"Error upgrading subscription: {e}")
            return False

    # === analytics ===
    def log_activity(self, user_id: str, activity: str, details: Dict = None):
        """Log user activity."""
        url = self._build_url('activities')
        activity_data = {
            "user_id": user_id,
            "activity": activity,
            "details": details or {},
            "timestamp": self._get_timestamp()
        }
        try:
            response = requests.post(url, json=activity_data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error logging activity: {e}")
            return False
    
    def get_user_stats(self) -> Dict:
        """Get basic user statistics."""
        url = self._build_url('users')
        stats = {"total_users": 0, "active_users": 0}
        try:
            response = requests.get(url)
            if response.status_code == 200:
                users = response.json()
                stats["total_users"] = len(users)
                stats["active_users"] = sum(1 for user in users.values() if user.get('is_active'))
                plans_count = {}
                for user in users.values():
                    plan = user.get('plan', 'free')
                    plans_count[plan] = plans_count.get(plan, 0) + 1
            
            return {
                "total_users": stats["total_users"],
                "active_users": stats["active_users"],
                "plans_count": plans_count
            }
        except Exception as e:
            print(f"Error retrieving user stats: {e}")
        return {}

    # === utilities ===
    def _get_timestamp(self) -> str:
        """Get the current timestamp as a string."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'

    def _get_future_timestamp(self, days: int = 30) -> str:
        """Get a future timestamp as a string."""
        from datetime import datetime, timedelta
        future_date = datetime.utcnow() + timedelta(days=days)
        return future_date.isoformat() + 'Z'