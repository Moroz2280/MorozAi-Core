@echo off
echo Активирую виртуальную среду...
call venv\Scripts\activate

echo Запускаю сервер FastAPI (uvicorn)...
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause