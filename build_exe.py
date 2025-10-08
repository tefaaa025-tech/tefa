#!/usr/bin/env python3
import os
import subprocess

print('📦 بناء ملف تنفيذي EXE...')
print()

pyinstaller_command = [
    'pyinstaller',
    '--name=DarAlhayat',
    '--windowed',
    '--onefile',
    '--add-data=db:db',
    '--add-data=ui:ui',
    '--add-data=modules:modules',
    '--icon=assets/icon.ico' if os.path.exists('assets/icon.ico') else '',
    'main.py'
]

pyinstaller_command = [cmd for cmd in pyinstaller_command if cmd]

print('⚙️ تثبيت PyInstaller...')
subprocess.run(['pip', 'install', 'pyinstaller'], check=True)
print()

print('🔨 بناء البرنامج...')
subprocess.run(pyinstaller_command, check=True)
print()

print('✅ تم البناء بنجاح!')
print('📁 الملف التنفيذي موجود في: dist/DarAlhayat.exe')
