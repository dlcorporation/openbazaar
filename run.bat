@echo off


set "ip="
for /f %%r in ('curl -s http://icanhazip.com') do (
  set ip=%%r 
)

echo External IP: %ip%

WinPython-64bit-2.7.6.4\python-2.7.6.amd64\python.exe Code\node\tornadoloop.py -p 12345 -s tcp://seed.openbazaar.org:12345 -l Code\logs\production.log -u 1 %ip%