@echo off
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Compiling... Please wait...
pyinstaller --onefile --windowed --hidden-import=tkinterdnd2 --name="TagAutocomplete" tag_autocomplete_app.py

echo.
if exist "dist\TagAutocomplete.exe" (
    echo SUCCESS! File created: dist\TagAutocomplete.exe
) else (
    echo ERROR! Compilation failed
)

pause
