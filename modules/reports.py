from datetime import datetime, timedelta
import os
import webbrowser
import tempfile

class ReportGenerator:
    def __init__(self, db):
        self.db = db
    
    def _get_html_template(self, title, content):
        return f'''<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        @media print {{
            body {{
                margin: 0;
                padding: 20px;
            }}
            .no-print {{
                display: none;
            }}
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            direction: rtl;
            text-align: right;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            margin: 0;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .header {{
            text-align: center;
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            color: #667eea;
            margin: 0;
            font-size: 32px;
            font-weight: bold;
        }}
        
        .header h2 {{
            color: #764ba2;
            margin: 10px 0 0 0;
            font-size: 24px;
        }}
        
        .header .date {{
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .stat-card.revenue {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }}
        
        .stat-card.expenses {{
            background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
        }}
        
        .stat-card.profit {{
            background: linear-gradient(135deg, #2193b0 0%, #6dd5ed 100%);
        }}
        
        .stat-card h3 {{
            margin: 0 0 10px 0;
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .stat-card .value {{
            font-size: 28px;
            font-weight: bold;
            margin: 0;
        }}
        
        .details-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .details-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: right;
            font-weight: bold;
        }}
        
        .details-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
        }}
        
        .details-table tr:hover {{
            background-color: #f5f5f5;
        }}
        
        .summary {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 30px 0;
        }}
        
        .summary h3 {{
            color: #667eea;
            margin-top: 0;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #eee;
            color: #666;
            font-size: 14px;
        }}
        
        .print-button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            margin: 20px auto;
            display: block;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }}
        
        .print-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0,0,0,0.3);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 دار الحياة للطب النفسي وعلاج الإدمان</h1>
            <h2>{title}</h2>
            <div class="date">تاريخ الطباعة: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
        </div>
        
        {content}
        
        <div class="footer">
            <p><strong>دار الحياة للطب النفسي وعلاج الإدمان</strong></p>
            <p>نظام المحاسبة الإلكتروني</p>
        </div>
        
        <button class="print-button no-print" onclick="window.print()">🖨️ طباعة التقرير</button>
    </div>
</body>
</html>'''
    
    def generate_monthly_report(self, year, month, output_path):
        from modules.payments import PaymentManager
        from modules.expenses import ExpenseManager
        from modules.patients import PatientManager
        
        payment_mgr = PaymentManager(self.db)
        expense_mgr = ExpenseManager(self.db)
        patient_mgr = PatientManager(self.db)
        
        revenue = payment_mgr.get_monthly_revenue(year, month)
        expenses = expense_mgr.get_monthly_expenses(year, month)
        profit = revenue - expenses
        
        active = patient_mgr.get_active_count()
        graduated = patient_mgr.get_graduated_count()
        
        payments_query = '''
            SELECT p.payment_date, pt.name, p.amount, p.notes 
            FROM payments p
            JOIN patients pt ON p.patient_id = pt.id
            WHERE strftime('%Y', p.payment_date) = ? AND strftime('%m', p.payment_date) = ?
            ORDER BY p.payment_date DESC
        '''
        payments = self.db.fetchall(payments_query, (str(year), f'{month:02d}'))
        
        expenses_query = '''
            SELECT expense_date, category, amount, description
            FROM expenses
            WHERE strftime('%Y', expense_date) = ? AND strftime('%m', expense_date) = ?
            ORDER BY expense_date DESC
        '''
        expenses_list = self.db.fetchall(expenses_query, (str(year), f'{month:02d}'))
        
        payments_table = ''
        if payments:
            payments_table = '''
            <h3>💰 المدفوعات</h3>
            <table class="details-table">
                <tr>
                    <th>التاريخ</th>
                    <th>اسم المريض</th>
                    <th>المبلغ</th>
                    <th>ملاحظات</th>
                </tr>
            '''
            for payment in payments:
                notes = payment[3] if payment[3] else '-'
                payments_table += f'''
                <tr>
                    <td>{payment[0]}</td>
                    <td>{payment[1]}</td>
                    <td>{payment[2]:.2f} جنيه</td>
                    <td>{notes}</td>
                </tr>
                '''
            payments_table += '</table>'
        
        expenses_table = ''
        if expenses_list:
            expenses_table = '''
            <h3>💸 المصروفات</h3>
            <table class="details-table">
                <tr>
                    <th>التاريخ</th>
                    <th>البند</th>
                    <th>المبلغ</th>
                    <th>الوصف</th>
                </tr>
            '''
            for expense in expenses_list:
                desc = expense[3] if expense[3] else '-'
                expenses_table += f'''
                <tr>
                    <td>{expense[0]}</td>
                    <td>{expense[1]}</td>
                    <td>{expense[2]:.2f} جنيه</td>
                    <td>{desc}</td>
                </tr>
                '''
            expenses_table += '</table>'
        
        content = f'''
        <div class="stats-grid">
            <div class="stat-card revenue">
                <h3>إجمالي الإيرادات</h3>
                <div class="value">{revenue:.2f} جنيه</div>
            </div>
            <div class="stat-card expenses">
                <h3>إجمالي المصروفات</h3>
                <div class="value">{expenses:.2f} جنيه</div>
            </div>
            <div class="stat-card profit">
                <h3>صافي الربح</h3>
                <div class="value">{profit:.2f} جنيه</div>
            </div>
        </div>
        
        <div class="summary">
            <h3>📊 ملخص الشهر</h3>
            <p><strong>المرضى النشطون:</strong> {active} مريض</p>
            <p><strong>الخريجون:</strong> {graduated} مريض</p>
            <p><strong>عدد المدفوعات:</strong> {len(payments) if payments else 0}</p>
            <p><strong>عدد المصروفات:</strong> {len(expenses_list) if expenses_list else 0}</p>
        </div>
        
        {payments_table}
        {expenses_table}
        '''
        
        html = self._get_html_template(f'تقرير شهري - {year}/{month:02d}', content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        webbrowser.open('file://' + os.path.abspath(output_path))
        return True
    
    def generate_daily_report(self, date, output_path):
        revenue_query = 'SELECT SUM(amount) FROM payments WHERE payment_date = ?'
        revenue_result = self.db.fetchone(revenue_query, (date,))
        revenue = float(revenue_result[0]) if revenue_result and revenue_result[0] is not None else 0.0
        
        expense_query = 'SELECT SUM(amount) FROM expenses WHERE expense_date = ?'
        expenses_result = self.db.fetchone(expense_query, (date,))
        expenses = float(expenses_result[0]) if expenses_result and expenses_result[0] is not None else 0.0
        
        profit = revenue - expenses
        
        payments_query = '''
            SELECT p.payment_date, pt.name, p.amount, p.notes 
            FROM payments p
            JOIN patients pt ON p.patient_id = pt.id
            WHERE p.payment_date = ?
            ORDER BY p.id DESC
        '''
        payments = self.db.fetchall(payments_query, (date,))
        
        expenses_query = '''
            SELECT expense_date, category, amount, description
            FROM expenses
            WHERE expense_date = ?
            ORDER BY id DESC
        '''
        expenses_list = self.db.fetchall(expenses_query, (date,))
        
        payments_table = ''
        if payments:
            payments_table = '''
            <h3>💰 المدفوعات</h3>
            <table class="details-table">
                <tr>
                    <th>الوقت</th>
                    <th>اسم المريض</th>
                    <th>المبلغ</th>
                    <th>ملاحظات</th>
                </tr>
            '''
            for payment in payments:
                notes = payment[3] if payment[3] else '-'
                payments_table += f'''
                <tr>
                    <td>{payment[0]}</td>
                    <td>{payment[1]}</td>
                    <td>{payment[2]:.2f} جنيه</td>
                    <td>{notes}</td>
                </tr>
                '''
            payments_table += '</table>'
        
        expenses_table = ''
        if expenses_list:
            expenses_table = '''
            <h3>💸 المصروفات</h3>
            <table class="details-table">
                <tr>
                    <th>الوقت</th>
                    <th>البند</th>
                    <th>المبلغ</th>
                    <th>الوصف</th>
                </tr>
            '''
            for expense in expenses_list:
                desc = expense[3] if expense[3] else '-'
                expenses_table += f'''
                <tr>
                    <td>{expense[0]}</td>
                    <td>{expense[1]}</td>
                    <td>{expense[2]:.2f} جنيه</td>
                    <td>{desc}</td>
                </tr>
                '''
            expenses_table += '</table>'
        
        content = f'''
        <div class="stats-grid">
            <div class="stat-card revenue">
                <h3>إجمالي الإيرادات</h3>
                <div class="value">{revenue:.2f} جنيه</div>
            </div>
            <div class="stat-card expenses">
                <h3>إجمالي المصروفات</h3>
                <div class="value">{expenses:.2f} جنيه</div>
            </div>
            <div class="stat-card profit">
                <h3>صافي الربح</h3>
                <div class="value">{profit:.2f} جنيه</div>
            </div>
        </div>
        
        <div class="summary">
            <h3>📊 ملخص اليوم</h3>
            <p><strong>عدد المدفوعات:</strong> {len(payments) if payments else 0}</p>
            <p><strong>عدد المصروفات:</strong> {len(expenses_list) if expenses_list else 0}</p>
        </div>
        
        {payments_table}
        {expenses_table}
        '''
        
        html = self._get_html_template(f'تقرير يومي - {date}', content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        webbrowser.open('file://' + os.path.abspath(output_path))
        return True
    
    def generate_weekly_report(self, start_date, end_date, output_path):
        revenue_query = 'SELECT SUM(amount) FROM payments WHERE payment_date BETWEEN ? AND ?'
        revenue_result = self.db.fetchone(revenue_query, (start_date, end_date))
        revenue = float(revenue_result[0]) if revenue_result and revenue_result[0] is not None else 0.0
        
        expense_query = 'SELECT SUM(amount) FROM expenses WHERE expense_date BETWEEN ? AND ?'
        expenses_result = self.db.fetchone(expense_query, (start_date, end_date))
        expenses = float(expenses_result[0]) if expenses_result and expenses_result[0] is not None else 0.0
        
        profit = revenue - expenses
        
        payments_query = '''
            SELECT p.payment_date, pt.name, p.amount, p.notes 
            FROM payments p
            JOIN patients pt ON p.patient_id = pt.id
            WHERE p.payment_date BETWEEN ? AND ?
            ORDER BY p.payment_date DESC
        '''
        payments = self.db.fetchall(payments_query, (start_date, end_date))
        
        expenses_query = '''
            SELECT expense_date, category, amount, description
            FROM expenses
            WHERE expense_date BETWEEN ? AND ?
            ORDER BY expense_date DESC
        '''
        expenses_list = self.db.fetchall(expenses_query, (start_date, end_date))
        
        payments_table = ''
        if payments:
            payments_table = '''
            <h3>💰 المدفوعات</h3>
            <table class="details-table">
                <tr>
                    <th>التاريخ</th>
                    <th>اسم المريض</th>
                    <th>المبلغ</th>
                    <th>ملاحظات</th>
                </tr>
            '''
            for payment in payments:
                notes = payment[3] if payment[3] else '-'
                payments_table += f'''
                <tr>
                    <td>{payment[0]}</td>
                    <td>{payment[1]}</td>
                    <td>{payment[2]:.2f} جنيه</td>
                    <td>{notes}</td>
                </tr>
                '''
            payments_table += '</table>'
        
        expenses_table = ''
        if expenses_list:
            expenses_table = '''
            <h3>💸 المصروفات</h3>
            <table class="details-table">
                <tr>
                    <th>التاريخ</th>
                    <th>البند</th>
                    <th>المبلغ</th>
                    <th>الوصف</th>
                </tr>
            '''
            for expense in expenses_list:
                desc = expense[3] if expense[3] else '-'
                expenses_table += f'''
                <tr>
                    <td>{expense[0]}</td>
                    <td>{expense[1]}</td>
                    <td>{expense[2]:.2f} جنيه</td>
                    <td>{desc}</td>
                </tr>
                '''
            expenses_table += '</table>'
        
        content = f'''
        <div class="stats-grid">
            <div class="stat-card revenue">
                <h3>إجمالي الإيرادات</h3>
                <div class="value">{revenue:.2f} جنيه</div>
            </div>
            <div class="stat-card expenses">
                <h3>إجمالي المصروفات</h3>
                <div class="value">{expenses:.2f} جنيه</div>
            </div>
            <div class="stat-card profit">
                <h3>صافي الربح</h3>
                <div class="value">{profit:.2f} جنيه</div>
            </div>
        </div>
        
        <div class="summary">
            <h3>📊 ملخص الفترة</h3>
            <p><strong>من تاريخ:</strong> {start_date}</p>
            <p><strong>إلى تاريخ:</strong> {end_date}</p>
            <p><strong>عدد المدفوعات:</strong> {len(payments) if payments else 0}</p>
            <p><strong>عدد المصروفات:</strong> {len(expenses_list) if expenses_list else 0}</p>
        </div>
        
        {payments_table}
        {expenses_table}
        '''
        
        html = self._get_html_template(f'تقرير أسبوعي - من {start_date} إلى {end_date}', content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        webbrowser.open('file://' + os.path.abspath(output_path))
        return True
    
    def generate_yearly_report(self, year, output_path):
        from modules.payments import PaymentManager
        from modules.expenses import ExpenseManager
        from modules.patients import PatientManager
        
        payment_mgr = PaymentManager(self.db)
        expense_mgr = ExpenseManager(self.db)
        patient_mgr = PatientManager(self.db)
        
        revenue_query = "SELECT SUM(amount) FROM payments WHERE strftime('%Y', payment_date) = ?"
        revenue_result = self.db.fetchone(revenue_query, (str(year),))
        revenue = float(revenue_result[0]) if revenue_result and revenue_result[0] is not None else 0.0
        
        expense_query = "SELECT SUM(amount) FROM expenses WHERE strftime('%Y', expense_date) = ?"
        expenses_result = self.db.fetchone(expense_query, (str(year),))
        expenses = float(expenses_result[0]) if expenses_result and expenses_result[0] is not None else 0.0
        
        profit = revenue - expenses
        
        active = patient_mgr.get_active_count()
        graduated = patient_mgr.get_graduated_count()
        
        monthly_stats = []
        for month in range(1, 13):
            month_revenue = payment_mgr.get_monthly_revenue(year, month)
            month_expenses = expense_mgr.get_monthly_expenses(year, month)
            month_profit = month_revenue - month_expenses
            monthly_stats.append((month, month_revenue, month_expenses, month_profit))
        
        month_names = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
                      'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
        
        monthly_table = '''
        <h3>📅 الإحصائيات الشهرية</h3>
        <table class="details-table">
            <tr>
                <th>الشهر</th>
                <th>الإيرادات</th>
                <th>المصروفات</th>
                <th>الربح</th>
            </tr>
        '''
        
        for month, m_revenue, m_expenses, m_profit in monthly_stats:
            monthly_table += f'''
            <tr>
                <td>{month_names[month-1]}</td>
                <td>{m_revenue:.2f} جنيه</td>
                <td>{m_expenses:.2f} جنيه</td>
                <td>{m_profit:.2f} جنيه</td>
            </tr>
            '''
        monthly_table += '</table>'
        
        content = f'''
        <div class="stats-grid">
            <div class="stat-card revenue">
                <h3>إجمالي الإيرادات</h3>
                <div class="value">{revenue:.2f} جنيه</div>
            </div>
            <div class="stat-card expenses">
                <h3>إجمالي المصروفات</h3>
                <div class="value">{expenses:.2f} جنيه</div>
            </div>
            <div class="stat-card profit">
                <h3>صافي الربح</h3>
                <div class="value">{profit:.2f} جنيه</div>
            </div>
        </div>
        
        <div class="summary">
            <h3>📊 ملخص السنة</h3>
            <p><strong>المرضى النشطون:</strong> {active} مريض</p>
            <p><strong>الخريجون:</strong> {graduated} مريض</p>
        </div>
        
        {monthly_table}
        '''
        
        html = self._get_html_template(f'تقرير سنوي - {year}', content)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        webbrowser.open('file://' + os.path.abspath(output_path))
        return True
