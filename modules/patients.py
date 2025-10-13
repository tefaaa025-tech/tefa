from datetime import datetime

class PatientManager:
    def __init__(self, db):
        self.db = db
    
    def add_patient(self, name, family_phone, admission_date, department, 
                   daily_cost, receives_cigarettes, cigarettes_count):
        query = '''
            INSERT INTO patients (name, family_phone, admission_date, department, 
                                daily_cost, receives_cigarettes, cigarettes_count, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'نشط')
        '''
        self.db.execute(query, (name, family_phone, admission_date, department,
                               daily_cost, receives_cigarettes, cigarettes_count))
        return True
    
    def get_all_patients(self, status=None):
        if status:
            query = 'SELECT * FROM patients WHERE status = ? ORDER BY id DESC'
            return self.db.fetchall(query, (status,))
        else:
            query = 'SELECT * FROM patients ORDER BY id DESC'
            return self.db.fetchall(query)
    
    def get_patient(self, patient_id):
        query = 'SELECT * FROM patients WHERE id = ?'
        return self.db.fetchone(query, (patient_id,))
    
    def update_patient(self, patient_id, name, family_phone, department, 
                      daily_cost, receives_cigarettes, cigarettes_count):
        query = '''
            UPDATE patients 
            SET name = ?, family_phone = ?, department = ?,
                daily_cost = ?, receives_cigarettes = ?, cigarettes_count = ?
            WHERE id = ?
        '''
        self.db.execute(query, (name, family_phone, department, daily_cost,
                               receives_cigarettes, cigarettes_count, patient_id))
        return True
    
    def discharge_patient(self, patient_id):
        query = '''
            UPDATE patients 
            SET status = 'متخرج', discharged_at = ?
            WHERE id = ?
        '''
        self.db.execute(query, (datetime.now().strftime('%Y-%m-%d'), patient_id))
        return True
    
    def get_patient_balance(self, patient_id):
        patient = self.get_patient(patient_id)
        if not patient:
            return 0
        
        admission_date = datetime.strptime(patient[3], '%Y-%m-%d')
        if patient[8] == 'متخرج' and patient[10]:
            discharge_date = datetime.strptime(patient[10], '%Y-%m-%d')
        else:
            discharge_date = datetime.now()
        
        days = (discharge_date - admission_date).days + 1
        total_cost = days * float(patient[5])
        
        payments_query = 'SELECT SUM(amount) FROM payments WHERE patient_id = ?'
        payments = self.db.fetchone(payments_query, (patient_id,))
        total_paid = float(payments[0]) if payments[0] else 0
        
        return total_cost - total_paid
    
    def get_active_count(self):
        query = 'SELECT COUNT(*) FROM patients WHERE status = "نشط"'
        result = self.db.fetchone(query)
        return result[0] if result else 0
    
    def get_graduated_count(self):
        query = 'SELECT COUNT(*) FROM patients WHERE status = "متخرج"'
        result = self.db.fetchone(query)
        return result[0] if result else 0
    
    def get_total_cigarettes(self):
        query = 'SELECT SUM(cigarettes_count) FROM patients WHERE status = "نشط" AND receives_cigarettes = 1'
        result = self.db.fetchone(query)
        return int(result[0]) if result[0] else 0
    
    def get_patient_detailed_statement(self, patient_id):
        patient = self.get_patient(patient_id)
        if not patient:
            return None
        
        admission_date = datetime.strptime(patient[3], '%Y-%m-%d')
        if patient[8] == 'متخرج' and patient[10]:
            discharge_date = datetime.strptime(patient[10], '%Y-%m-%d')
        else:
            discharge_date = datetime.now()
        
        days = (discharge_date - admission_date).days + 1
        accommodation_cost = days * float(patient[5])
        
        payments_query = '''
            SELECT payment_date, amount, notes 
            FROM payments 
            WHERE patient_id = ? 
            ORDER BY payment_date DESC
        '''
        payments = self.db.fetchall(payments_query, (patient_id,))
        total_paid = sum(p[1] for p in payments)
        
        cigarettes_cost = 0
        if patient[6]:
            box_cost_query = "SELECT setting_value FROM settings WHERE setting_key = 'cigarette_box_cost'"
            box_cost_result = self.db.fetchone(box_cost_query)
            cigarette_box_cost = float(box_cost_result[0]) if box_cost_result else 40
            
            per_box_query = "SELECT setting_value FROM settings WHERE setting_key = 'cigarettes_per_box'"
            per_box_result = self.db.fetchone(per_box_query)
            cigarettes_per_box = float(per_box_result[0]) if per_box_result else 20
            
            cigarettes_per_day = patient[7]
            cigarettes_cost = cigarettes_per_day * days * (cigarette_box_cost / cigarettes_per_box)
        
        total_expenses = accommodation_cost + cigarettes_cost
        balance = total_expenses - total_paid
        
        return {
            'patient': patient,
            'admission_date': admission_date,
            'discharge_date': discharge_date if patient[8] == 'متخرج' else None,
            'days': days,
            'accommodation_cost': accommodation_cost,
            'cigarettes_cost': cigarettes_cost,
            'total_expenses': total_expenses,
            'payments': payments,
            'total_paid': total_paid,
            'balance': balance
        }
