@echo off
set thisdir=.
set PYTHONPATH=%thisdir%;%thisdir%\src
python "%THISDIR%\src\runner\FilesRunner.py" "%thisdir%\testcases" 
@echo ��������򿪲��Ա���
pause
