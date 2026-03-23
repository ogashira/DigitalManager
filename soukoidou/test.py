import subprocess
import time
import platform

txt = r'\\192.168.1.245\effit_A\Menu\EMN300I.exe' \
    + ' ' + r'toyo_2019,生産C10,1,admin,東洋工業塗料'
if platform.system()=='Linux':
    txt = r'/mnt/effitA/Menu/EMN300I.exe toyo_2019,生産C10,1,admin,東洋工業塗料'
subprocess.Popen(txt)
time.sleep(20)
