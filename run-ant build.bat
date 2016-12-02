@echo off
@echo start to automation test
call ant  -f antxml\build-py.xml -Dtestcase.filename=simple1.xlsx
pause 

