from datetime import datetime

class ExpenseManager:
    def __init__(self, db):
        self.db = db
    
    def add_expense(self, category, amount, expense_date, description=''):
        query = '''
            INSERT INTO expenses (category, amount, expense_date, description)
            VALUES (?, ?, ?, ?)
        '''
        self.db.execute(query, (category, amount, expense_date, description))
        return True
    
    def get_all_expenses(self):
        query = 'SELECT * FROM expenses ORDER BY expense_date DESC'
        return self.db.fetchall(query)
    
    def get_total_expenses(self):
        query = 'SELECT SUM(amount) FROM expenses'
        result = self.db.fetchone(query)
        return result[0] if result[0] else 0
    
    def get_monthly_expenses(self, year, month):
        query = '''
            SELECT SUM(amount) 
            FROM expenses 
            WHERE strftime('%Y', expense_date) = ? 
            AND strftime('%m', expense_date) = ?
        '''
        result = self.db.fetchone(query, (str(year), f'{month:02d}'))
        return result[0] if result[0] else 0
    
    def get_expenses_by_category(self):
        query = '''
            SELECT category, SUM(amount) as total
            FROM expenses
            GROUP BY category
            ORDER BY total DESC
        '''
        return self.db.fetchall(query)
    
    def get_expense(self, expense_id):
        query = 'SELECT * FROM expenses WHERE id = ?'
        return self.db.fetchone(query, (expense_id,))
    
    def update_expense(self, expense_id, category, amount, expense_date, description=''):
        query = '''
            UPDATE expenses 
            SET category = ?, amount = ?, expense_date = ?, description = ?
            WHERE id = ?
        '''
        self.db.execute(query, (category, amount, expense_date, description, expense_id))
        return True
    
    def delete_expense(self, expense_id):
        query = 'DELETE FROM expenses WHERE id = ?'
        self.db.execute(query, (expense_id,))
        return True
