import platform
import subprocess
import pandas as pd

from recorder import Recorder
from soukoidou.fetch_data import IFetchData


class SoukoidouCsv:

    def __init__(self, fetchSyukko: IFetchData, recorder: Recorder)-> None:
        self._fetchSyukko = fetchSyukko
        self._recorder: Recorder = recorder
        self._program_path = r'\\192.168.1.247\共有\TSS_System\TssSystem' \
                             r'\ToyoKogyo\Bat\ToyoKogyoHsBat\ToyoKogyoHsBat.exe'
        if platform.system() == 'Linux':
            self._program_path = r'/mnt/public/TSS_System/TssSystem' \
                             r'ToyoKogyo/Bat/ToyoKogyoHsBat/ToyoKogyoHsBat.exe'
        self._returncode = 0

    def create_soukoidouCsv(self)-> None:    
        '''
        returncode
        1 : 成功
        2 : effitの処理が残っているため失敗
        3 : effitの処理をするデータが無い
        '''
        result = subprocess.run([self._program_path], 
                                               capture_output=True, text=True)
        self._returncode: int = result.returncode
        print(self._returncode)
        self._out_log()

    def _out_log(self)-> None:
        if self._returncode == 0:
            txt = '倉庫移動.csvを作れませんでした。処理を中止します。'
            self._recorder.out_log(txt, '\n')
            self._recorder.out_file(txt, '\n')
            return

        if self._returncode == 1:
            txt = '倉庫移動.csvを作りました。倉庫移動を行います。'
            self._recorder.out_log(txt, '\n')
            self._recorder.out_file(txt, '\n')
            return
        
        if self._returncode == 2:
            txt = '前回の倉庫移動.csvが残っています。処理を中止します。'
            self._recorder.out_log(txt, '\n')
            self._recorder.out_file(txt, '\n')
            return

        if self._returncode = 3:
            txt = '倉庫移動する製品はありません'
            self._recorder.out_log(txt, '\n')
            self._recorder.out_file(txt, '\n')
            return

    def is_soukoidou_ok(self)-> bool
            return self._returncode == 1

    def get_before_soukoidouCsv(self)-> pd.DataFrame:
        '''
        effit_A/倉庫移動/に作られた倉庫移動.csvファイル
        '''
        before_soukoidouCsv = pd.DataFrame()
        if self._returncode != 1:
            return before_soukoidouCsv #空のデータフレーム

        path = r'\\192.168.1.245\effit_A\倉庫移動\倉庫移動.csv'
        if platform.system()== 'Linux':
            path = r'/mnt/effitA/倉庫移動/倉庫移動.csv'
        before_soukoidouCsv = pd.read_csv(path, encoding='cp932')

        return before_soukoidouCsv


    def get_after_soukoidouCsv(self)-> pd.DataFrame:
        after_soukoidouCsv = self._fetchSyukko.fetch_data()
        path = \
        r'\\192.168.1.247\共有\技術課ﾌｫﾙﾀﾞ\200. effit_data\syukko_data.csv'
        if platform.system()== 'Linux':
            path = \
            r'/mnt/public/技術課ﾌｫﾙﾀﾞ/200. effit_data/syukko_data.csv'
        # csvファイルとして保存する
        after_soukoidouCsv.to_csv(path)

        return after_soukoidouCsv
