import subprocess
import pyautogui
from typing import List
import time
import os
import sys

from soukoidou_csv import SoukoidouCsv
from recorder import Recorder


class EffitA:

    def __init__(self, soukoidouCsv: SoukoidouCsv,
                 recorder: Recorder)-> None:

        self._soukoidouCsv = soukoidouCsv
        self._recorder = recorder
        # 倉庫移動前のbefore_soukoidouCsvを取っておく
        self._before_soukoidouCsv = self._soukoidouCsv.get_before_soukoidouCsv()

    def soukoidou(self)-> None:
        self._soukoidouCsv.create_soukoidouCsv()
        if not self._soukoidouCsv.is_soukoidou_ok():
            sys.exit(1)


        # effitA立ち上げ
        subprocess.Popen(r'\\192.168.1.245\effit_A\Menu\EMN300I.exe' \
                         + ' ' + r'toyo_2019,生産C10,1,admin,東洋工業塗料')
        time.sleep(20)

        pyautogui.typewrite('honsya')
        pyautogui.typewrite(['enter'])
        pyautogui.typewrite('tajiri')
        pyautogui.typewrite(['enter', 'enter'])

        time.sleep(5)

        myclc = pyautogui.locateOnScreen(
                r'C:\MyPythonScripts\soukoidou2\effita_png\caps_error.png'
                )

        if myclc != None:
            pyautogui.typewrite(['capslock'])
            pyautogui.typewrite(['enter'])
            pyautogui.typewrite(['tab','tab'])
            pyautogui.typewrite('honsya')
            pyautogui.typewrite(['enter'])
            pyautogui.typewrite('tajiri')
            pyautogui.typewrite(['enter', 'enter'])  

        time.sleep(20)

        # effitA取り込み処理
        pyautogui.typewrite(['down','down','down'])
        pyautogui.typewrite(['enter'])
        time.sleep(2)
        pyautogui.typewrite(['tab','tab','tab','tab','tab','tab','tab','tab',
                             'tab','tab','tab','tab','tab','tab','tab','tab',
                             'tab','tab','tab'])
        pyautogui.typewrite(['enter'])
        time.sleep(20)

        pyautogui.typewrite('000410')
        pyautogui.typewrite(['enter'])
        pyautogui.typewrite('@0001')
        pyautogui.typewrite(['enter','enter'])
        time.sleep(10)


        myclc = pyautogui.locateOnScreen(
                r'C:\MyPythonScripts\soukoidou2\soukoidou_png\data_torikomi.png'
                )
        clc_cent = pyautogui.center(myclc)
        pyautogui.click(clc_cent)
        pyautogui.typewrite(['enter'])
        pyautogui.typewrite(['enter'])
        time.sleep(20)
        pyautogui.typewrite(['enter'])
        time.sleep(5)

        myclc = pyautogui.locateOnScreen(
                r'C:\MyPythonScripts\soukoidou2\soukoidou_png\data_check.png'
                )
        clc_cent = pyautogui.center(myclc)
        pyautogui.click(clc_cent)
        time.sleep(30)
        pyautogui.typewrite(['enter'])
        time.sleep(5)


        myclc = pyautogui.locateOnScreen(
                r'C:\MyPythonScripts\soukoidou2\soukoidou_png\data_kousin.png'
                )
        clc_cent = pyautogui.center(myclc)
        pyautogui.click(clc_cent)
        pyautogui.typewrite(['enter'])
        time.sleep(30)
        pyautogui.typewrite(['enter'])
        time.sleep(5)


        myclc = pyautogui.locateOnScreen(
                r'C:\MyPythonScripts\soukoidou2\soukoidou_png\data_sakujo.png'
                )
        clc_cent = pyautogui.center(myclc)
        pyautogui.click(clc_cent)
        time.sleep(2)
        pyautogui.typewrite(['enter'])
        time.sleep(2)
        pyautogui.typewrite(['enter'])
        time.sleep(5)


        myclc = pyautogui.locateOnScreen(
                r'C:\MyPythonScripts\soukoidou2\soukoidou_png\end.png'
                )
        clc_cent = pyautogui.center(myclc)
        pyautogui.click(clc_cent)
        time.sleep(1)

        #倉庫移動画面終了
        myclc = pyautogui.locateOnScreen(
                r'C:\MyPythonScripts\soukoidou2\effita_png\syuuryou.png'
                )
        clc_cent = pyautogui.center(myclc)
        pyautogui.click(clc_cent)
        #effita終了

    def check_before_after(self)-> List[List[str]]:
        '''
        self._before_soukoidouCsvとafter_soukoidouCsvを比較する
        必ずsoukoidou()を実行したあとに行う
        '''
        after_soukoidouCsv = self._soukoidouCsv.get_after_soukoidouCsv()
        # ロットNoの重複をなくしてリストを作る
        after_list = list(set(after_soukoidouCsv['ロットＮＯ']))
        
        # lotが存在しない場合はfaild_soukoidousに詰める
        failed_soukoidous: List[List[str]] = []
        for _, row in self._before_soukoidouCsv.iterrows():
            lot = row['ロットNo.']
            hinban = row['品番']
            if lot not in after_list:
                line:List[str] = [hinban, lot]
                failed_soukoidous.append(line)

        self._out_log(failed_soukoidous)

        return failed_soukoidous
            
    
    def _out_log(self, failed_soukoidous)-> None:

        if not failed_soukoidous:
            txt = r'倉庫移動はすべて成功です'
            self._recorder.out_log(txt, '\n')
            self._recorder.out_file(txt, '\n')
            return

        txt = r'以下の品番、Lotの倉庫移動が行われていません。'
        self._recorder.out_log(txt, '\n')
        self._recorder.out_file(txt, '\n')
        return
