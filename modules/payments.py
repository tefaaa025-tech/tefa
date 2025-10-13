from datetime import datetime

class PaymentManager:
    def __init__(self, db):
        self.db = db
    
    def add_payment(self, patient_id, amount, payment_date, notes=''):
        query = '''
            INSERT INTO payments (patient_id, amount, payment_date, notes)
            VALUES (?, ?, ?, ?)
        '''
        self.db.execute(query, (patient_id, amount, payment_date, notes))
        return True
    
    def get_patient_payments(self, patient_id):
        query = '''
            SELECT * FROM payments 
            WHERE patient_id = ? 
            ORDER BY payment_date DESC
        '''
        return self.db.fetchall(query, (patient_id,))
    
    def get_all_payments(self):
        query = '''
            SELECT p.*, pt.name 
            FROM payments p
            JOIN patients pt ON p.patient_id = pt.id
            ORDER BY p.payment_date DESC
        '''
        return self.db.fetchall(query)
    
    def get_total_revenue(self):
        query = 'SELECT SUM(amount) FROM payments'
        result = self.db.fetchone(query)
        return result[0] if result[0] else 0
    
    def get_monthly_revenue(self, year, month):
        query = '''
            SELECT SUM(amount) 
            FROM payments 
            WHERE strftime('%Y', payment_date) = ? 
            AND strftime('%m', payment_date) = ?
        '''
        result = self.db.fetchone(query, (str(year), f'{month:02d}'))
        return result[0] if result[0] else 0
    
    def get_payment(self, payment_id):
        query = 'SELECT * FROM payments WHERE id = ?'
        return self.db.fetchone(query, (payment_id,))
    
    def update_payment(self, payment_id, patient_id, amount, payment_date, notes=''):
        query = '''
            UPDATE payments 
            SET patient_id = ?, amount = ?, payment_date = ?, notes = ?
            WHERE id = ?
        '''
        self.db.execute(query, (patient_id, amount, payment_date, notes, payment_id))
        return True
    
    def delete_payment(self, payment_id):
        query = 'DELETE FROM payments WHERE id = ?'
        self.db.execute(query, (payment_id,))
        return True
