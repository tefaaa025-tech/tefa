import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self, db_path='db/dar_alhayat.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                family_phone TEXT,
                admission_date TEXT NOT NULL,
                department TEXT NOT NULL,
                daily_cost REAL NOT NULL,
                receives_cigarettes INTEGER DEFAULT 0,
                cigarettes_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'نشط',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                discharged_at TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date TEXT NOT NULL,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                expense_date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                position TEXT,
                phone TEXT,
                hire_date TEXT NOT NULL,
                base_salary REAL NOT NULL,
                status TEXT DEFAULT 'نشط',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS employee_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                transaction_date TEXT NOT NULL,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                full_name TEXT,
                role TEXT DEFAULT 'user',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setting_key TEXT UNIQUE NOT NULL,
                setting_value TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            SELECT COUNT(*) FROM users WHERE username = 'admin'
        ''')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('''
                INSERT INTO users (username, password, full_name, role)
                VALUES ('admin', 'admin123', 'مدير النظام', 'admin')
            ''')
        
        self.cursor.execute('''
            SELECT COUNT(*) FROM settings WHERE setting_key = 'cigarette_pack_price'
        ''')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('''
                INSERT INTO settings (setting_key, setting_value)
                VALUES ('cigarette_pack_price', '40')
            ''')
        
        self.cursor.execute('''
            SELECT COUNT(*) FROM settings WHERE setting_key = 'cigarette_box_cost'
        ''')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('''
                INSERT INTO settings (setting_key, setting_value)
                VALUES ('cigarette_box_cost', '40')
            ''')
        
        self.cursor.execute('''
            SELECT COUNT(*) FROM settings WHERE setting_key = 'cigarettes_per_box'
        ''')
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute('''
                INSERT INTO settings (setting_key, setting_value)
                VALUES ('cigarettes_per_box', '20')
            ''')
        
        self.conn.commit()
    
    def execute(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()
        return self.cursor
    
    def fetchall(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def fetchone(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()
    
    def close(self):
        if self.conn:
            self.conn.close()
