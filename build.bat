@echo off

pyinstaller --onefile --clean --upx-dir=upx/ --exclude-module=tkinter --exclude-module=test --exclude-module=pydoc --name="Reword" main.py

rmdir /s /q build
copy words.txt dist/
rename dist Reword