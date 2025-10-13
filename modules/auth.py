import bcrypt
from datetime import datetime

class AuthManager:
    def __init__(self, db):
        self.db = db
    
    def hash_password(self, password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password, hashed):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except:
            return password == hashed
    
    def authenticate(self, username, password):
        query = 'SELECT id, username, password, full_name, role FROM users WHERE username = ?'
        user = self.db.fetchone(query, (username,))
        
        if user and self.verify_password(password, user[2]):
            return {
                'id': user[0],
                'username': user[1],
                'full_name': user[3],
                'role': user[4]
            }
        return None
    
    def create_user(self, username, password, full_name='', role='user'):
        hashed_password = self.hash_password(password)
        query = '''
            INSERT INTO users (username, password, full_name, role)
            VALUES (?, ?, ?, ?)
        '''
        try:
            self.db.execute(query, (username, hashed_password, full_name, role))
            return True
        except:
            return False
    
    def update_password(self, username, new_password):
        hashed_password = self.hash_password(new_password)
        query = 'UPDATE users SET password = ? WHERE username = ?'
        try:
            self.db.execute(query, (hashed_password, username))
            return True
        except:
            return False
    
    def initialize_default_users(self):
        admin_exists = self.db.fetchone("SELECT COUNT(*) FROM users WHERE username = 'admin'")
        if admin_exists and admin_exists[0] == 0:
            self.create_user('admin', '1231', 'مدير النظام', 'admin')
        else:
            self.update_password('admin', '1231')
        
        user_exists = self.db.fetchone("SELECT COUNT(*) FROM users WHERE username = 'user'")
        if user_exists and user_exists[0] == 0:
            self.create_user('user', '1', 'محاسب', 'accountant')
