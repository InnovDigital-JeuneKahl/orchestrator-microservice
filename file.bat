@echo off
REM Create directories
mkdir app\config
mkdir app\api
mkdir app\core
mkdir app\models
mkdir app\services
mkdir config
mkdir tests

REM Create empty Python files with initial comments
echo.> app\__init__.py
echo.> app\main.py
echo.> app\config\__init__.py
echo.> app\config\settings.py
echo.> app\api\__init__.py
echo.> app\api\routes.py
echo.> app\core\__init__.py
echo.> app\core\file_router.py
echo.> app\core\metadata_extractor.py
echo.> app\core\transcription.py
echo.> app\models\__init__.py
echo.> app\models\schemas.py
echo.> app\services\__init__.py
echo.> app\services\rag_service.py
echo.> app\services\qa_service.py
echo.> tests\__init__.py
echo.> tests\test_api.py

REM Create root files
echo.> config\service_mapping.json
echo.> requirements.txt
echo.> Dockerfile
echo.> README.md

echo Project structure created successfully.
pause
