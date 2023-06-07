@echo off

if not exist requirements.txt (
    echo Файл requirements.txt не найден.
    exit /b
)

pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Установка зависимостей не удалась.
) else (
    echo Установка зависимостей завершена успешно.
)

exit /b
