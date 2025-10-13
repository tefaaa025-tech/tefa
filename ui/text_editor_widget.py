# --- NEW FEATURE: Text Editor ---
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTextEdit, QFileDialog, QMessageBox, QToolBar,
                             QFontComboBox, QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCharFormat, QTextCursor, QPageSize, QPageLayout
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

class TextEditorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        # Font selection
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.change_font)
        toolbar_layout.addWidget(self.font_combo)
        
        # Font size
        self.font_size = QSpinBox()
        self.font_size.setValue(12)
        self.font_size.setMinimum(6)
        self.font_size.setMaximum(72)
        self.font_size.valueChanged.connect(self.change_font_size)
        toolbar_layout.addWidget(self.font_size)
        
        # Bold button
        bold_btn = QPushButton('B')
        bold_btn.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        bold_btn.setCheckable(True)
        bold_btn.clicked.connect(self.toggle_bold)
        bold_btn.setFixedWidth(40)
        toolbar_layout.addWidget(bold_btn)
        
        # Italic button
        italic_btn = QPushButton('I')
        italic_btn.setFont(QFont('Arial', 12, QFont.Weight.Normal))
        italic_btn.font().setItalic(True)
        italic_btn.setCheckable(True)
        italic_btn.clicked.connect(self.toggle_italic)
        italic_btn.setFixedWidth(40)
        toolbar_layout.addWidget(italic_btn)
        
        # Underline button
        underline_btn = QPushButton('U')
        underline_btn.setFont(QFont('Arial', 12, QFont.Weight.Normal))
        underline_btn.font().setUnderline(True)
        underline_btn.setCheckable(True)
        underline_btn.clicked.connect(self.toggle_underline)
        underline_btn.setFixedWidth(40)
        toolbar_layout.addWidget(underline_btn)
        
        toolbar_layout.addSpacing(20)
        
        # Alignment buttons
        align_left_btn = QPushButton('⬅')
        align_left_btn.clicked.connect(self.align_left)
        align_left_btn.setFixedWidth(40)
        toolbar_layout.addWidget(align_left_btn)
        
        align_center_btn = QPushButton('↔')
        align_center_btn.clicked.connect(self.align_center)
        align_center_btn.setFixedWidth(40)
        toolbar_layout.addWidget(align_center_btn)
        
        align_right_btn = QPushButton('➡')
        align_right_btn.clicked.connect(self.align_right)
        align_right_btn.setFixedWidth(40)
        toolbar_layout.addWidget(align_right_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # Text editor
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont('Arial', 12))
        layout.addWidget(self.text_edit)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        
        new_btn = QPushButton('📄 جديد')
        new_btn.clicked.connect(self.new_document)
        btn_layout.addWidget(new_btn)
        
        open_btn = QPushButton('📂 فتح')
        open_btn.clicked.connect(self.open_file)
        btn_layout.addWidget(open_btn)
        
        save_txt_btn = QPushButton('💾 حفظ TXT')
        save_txt_btn.clicked.connect(self.save_as_txt)
        btn_layout.addWidget(save_txt_btn)
        
        save_docx_btn = QPushButton('💾 حفظ DOCX')
        save_docx_btn.clicked.connect(self.save_as_docx)
        btn_layout.addWidget(save_docx_btn)
        
        print_btn = QPushButton('🖨️ طباعة')
        print_btn.clicked.connect(self.print_document)
        btn_layout.addWidget(print_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def change_font(self, font):
        self.text_edit.setCurrentFont(font)
    
    def change_font_size(self, size):
        self.text_edit.setFontPointSize(size)
    
    def toggle_bold(self):
        fmt = QTextCharFormat()
        if self.text_edit.fontWeight() == QFont.Weight.Bold:
            fmt.setFontWeight(QFont.Weight.Normal)
        else:
            fmt.setFontWeight(QFont.Weight.Bold)
        self.text_edit.mergeCurrentCharFormat(fmt)
    
    def toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.text_edit.fontItalic())
        self.text_edit.mergeCurrentCharFormat(fmt)
    
    def toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.text_edit.fontUnderline())
        self.text_edit.mergeCurrentCharFormat(fmt)
    
    def align_left(self):
        self.text_edit.setAlignment(Qt.AlignmentFlag.AlignLeft)
    
    def align_center(self):
        self.text_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def align_right(self):
        self.text_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
    
    def new_document(self):
        if self.text_edit.document().isModified():
            reply = QMessageBox.question(
                self,
                'حفظ التغييرات؟',
                'هل تريد حفظ التغييرات قبل إنشاء مستند جديد؟',
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.save_as_txt()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        self.text_edit.clear()
        self.current_file = None
    
    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'فتح ملف',
            '',
            'Text Files (*.txt);;Word Documents (*.docx);;All Files (*)'
        )
        
        if file_path:
            try:
                if file_path.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.text_edit.setPlainText(f.read())
                elif file_path.endswith('.docx'):
                    doc = Document(file_path)
                    full_text = []
                    for para in doc.paragraphs:
                        full_text.append(para.text)
                    self.text_edit.setPlainText('\n'.join(full_text))
                
                self.current_file = file_path
                QMessageBox.information(self, 'نجح', 'تم فتح الملف بنجاح')
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'حدث خطأ أثناء فتح الملف:\n{str(e)}')
    
    def save_as_txt(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'حفظ كملف نصي',
            self.current_file if self.current_file and self.current_file.endswith('.txt') else 'document.txt',
            'Text Files (*.txt)'
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                
                self.current_file = file_path
                self.text_edit.document().setModified(False)
                QMessageBox.information(self, 'نجح', 'تم حفظ الملف بنجاح')
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'حدث خطأ أثناء الحفظ:\n{str(e)}')
    
    def save_as_docx(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            'حفظ كمستند Word',
            self.current_file if self.current_file and self.current_file.endswith('.docx') else 'document.docx',
            'Word Documents (*.docx)'
        )
        
        if file_path:
            try:
                doc = Document()
                
                # Set RTL direction for Arabic text
                section = doc.sections[0]
                
                # Get text from editor
                text = self.text_edit.toPlainText()
                paragraphs = text.split('\n')
                
                for para_text in paragraphs:
                    if para_text.strip():
                        para = doc.add_paragraph(para_text)
                        # Set RTL for Arabic text
                        para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                    else:
                        doc.add_paragraph()
                
                doc.save(file_path)
                self.current_file = file_path
                self.text_edit.document().setModified(False)
                QMessageBox.information(self, 'نجح', 'تم حفظ الملف بنجاح')
            except Exception as e:
                QMessageBox.critical(self, 'خطأ', f'حدث خطأ أثناء الحفظ:\n{str(e)}')
    
    def print_document(self):
        try:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            dialog = QPrintDialog(printer, self)
            
            if dialog.exec() == QPrintDialog.DialogCode.Accepted:
                self.text_edit.document().print(printer)
                QMessageBox.information(self, 'نجح', 'تم الطباعة بنجاح')
        except Exception as e:
            QMessageBox.critical(self, 'خطأ', f'حدث خطأ أثناء الطباعة:\n{str(e)}')
