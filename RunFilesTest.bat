@echo off
set thisdir=.
set PYTHONPATH=%thisdir%;%thisdir%\src
python "%THISDIR%\src\runner\FilesRunner.py" "%thisdir%\QE\testcases" 
@echo ��������򿪲��Ա���
pause
