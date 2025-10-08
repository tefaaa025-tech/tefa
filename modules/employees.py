from datetime import datetime

class EmployeeManager:
    def __init__(self, db):
        self.db = db
    
    def add_employee(self, name, position, phone, hire_date, base_salary):
        query = '''
            INSERT INTO employees (name, position, phone, hire_date, base_salary, status)
            VALUES (?, ?, ?, ?, ?, 'نشط')
        '''
        self.db.execute(query, (name, position, phone, hire_date, base_salary))
        return True
    
    def get_all_employees(self, status=None):
        if status:
            query = 'SELECT * FROM employees WHERE status = ? ORDER BY id DESC'
            return self.db.fetchall(query, (status,))
        else:
            query = 'SELECT * FROM employees ORDER BY id DESC'
            return self.db.fetchall(query)
    
    def get_employee(self, employee_id):
        query = 'SELECT * FROM employees WHERE id = ?'
        return self.db.fetchone(query, (employee_id,))
    
    def update_employee(self, employee_id, name, position, phone, base_salary):
        query = '''
            UPDATE employees 
            SET name = ?, position = ?, phone = ?, base_salary = ?
            WHERE id = ?
        '''
        self.db.execute(query, (name, position, phone, base_salary, employee_id))
        return True
    
    def add_transaction(self, employee_id, transaction_type, amount, transaction_date, notes=''):
        query = '''
            INSERT INTO employee_transactions (employee_id, transaction_type, amount, transaction_date, notes)
            VALUES (?, ?, ?, ?, ?)
        '''
        self.db.execute(query, (employee_id, transaction_type, amount, transaction_date, notes))
        return True
    
    def get_employee_transactions(self, employee_id):
        query = '''
            SELECT * FROM employee_transactions 
            WHERE employee_id = ? 
            ORDER BY transaction_date DESC
        '''
        return self.db.fetchall(query, (employee_id,))
    
    def get_active_count(self):
        query = 'SELECT COUNT(*) FROM employees WHERE status = "نشط"'
        result = self.db.fetchone(query)
        return result[0] if result else 0
    
    def calculate_employee_balance(self, employee_id):
        query = '''
            SELECT transaction_type, SUM(amount) 
            FROM employee_transactions 
            WHERE employee_id = ? 
            GROUP BY transaction_type
        '''
        transactions = self.db.fetchall(query, (employee_id,))
        
        salary_paid = 0
        deductions = 0
        advances = 0
        bonuses = 0
        
        for trans in transactions:
            trans_type = trans[0]
            amount = trans[1] if trans[1] else 0
            
            if trans_type == 'راتب':
                salary_paid += amount
            elif trans_type == 'خصم':
                deductions += amount
            elif trans_type == 'سلفة':
                advances += amount
            elif trans_type == 'مكافأة':
                bonuses += amount
        
        return {
            'salary_paid': salary_paid,
            'deductions': deductions,
            'advances': advances,
            'bonuses': bonuses,
            'total': salary_paid + bonuses - deductions - advances
        }
    
    def get_all_transactions(self):
        query = '''
            SELECT et.*, e.name 
            FROM employee_transactions et
            JOIN employees e ON et.employee_id = e.id
            ORDER BY et.transaction_date DESC
        '''
        return self.db.fetchall(query)
