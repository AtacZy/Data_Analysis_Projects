@echo off
Z:
cd "Z:\files_prod\Data_Analysis_Projects\Automating_the_script_for_generating_data_and_sending_it_to_the_database"
.\venv\Scripts\python.exe db_loader.py > nul 2>&1
echo %date% %time% - Загрузка данных в БД выполнена >> scheduler.log