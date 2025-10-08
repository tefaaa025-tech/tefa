import pandas as pd
from openpyxl import load_workbook
from datetime import datetime

class ImportExport:
    def __init__(self, db, patient_mgr):
        self.db = db
        self.patient_mgr = patient_mgr
    
    def import_patients_from_excel(self, file_path):
        try:
            df = pd.read_excel(file_path)
            
            required_cols = ['الاسم', 'هاتف الأهل', 'تاريخ الدخول', 'القسم', 'التكلفة اليومية']
            
            for index, row in df.iterrows():
                name = str(row.get('الاسم', ''))
                family_phone = str(row.get('هاتف الأهل', ''))
                admission_date = str(row.get('تاريخ الدخول', datetime.now().strftime('%Y-%m-%d')))
                department = str(row.get('القسم', 'ديتوكس'))
                daily_cost = float(row.get('التكلفة اليومية', 0))
                receives_cigarettes = 1 if row.get('يستلم سجائر', 'لا') == 'نعم' else 0
                cigarettes_count = int(row.get('عدد السجائر', 0))
                
                self.patient_mgr.add_patient(
                    name, family_phone, admission_date, department,
                    daily_cost, receives_cigarettes, cigarettes_count
                )
            
            return True, len(df)
        except Exception as e:
            return False, str(e)
    
    def export_patients_to_excel(self, file_path):
        try:
            patients = self.patient_mgr.get_all_patients()
            
            data = []
            for p in patients:
                data.append({
                    'الرقم': p[0],
                    'الاسم': p[1],
                    'هاتف الأهل': p[2],
                    'تاريخ الدخول': p[3],
                    'القسم': p[4],
                    'التكلفة اليومية': p[5],
                    'يستلم سجائر': 'نعم' if p[6] else 'لا',
                    'عدد السجائر': p[7],
                    'الحالة': p[8]
                })
            
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False, engine='openpyxl')
            
            return True
        except Exception as e:
            return False
