﻿@echo off

set "ip="
for /f %%r in ('curl -s http://icanhazip.com') do (
  set ip=%%r 
)

echo External IP: %ip%

..\WinPython\python-2.7.6.amd64\scripts\pip install python-gnupg

if exist db\ob.db goto dbexists
..\WinPython\python-2.7.6.amd64\python node\setup_db.py db\ob.db

:dbexists
..\WinPython\python-2.7.6.amd64\python node\tornadoloop.py -p 12345 -l logs\production.log -u 1 %ip%