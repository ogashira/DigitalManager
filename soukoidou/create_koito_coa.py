import pandas as pd
import platform
from typing import List
import os
import sys
import zenhan
from recorder import Recorder
import coa_check


'''
サーバーにあるsql_server.pyをモジュールとして使う
importするためにsys.path.appendでpathを認識させて
importと生成を行う
'''
shared_folder_path:str = r'./'
if platform.system() == 'Linux':
    shared_folder_path = \
            r'/mnt/public/技術課ﾌｫﾙﾀﾞ/200. effit_data/ﾏｽﾀ/sql_python_module'
elif platform.system() == 'Windows':
    shared_folder_path = \
   r'//192.168.1.247/共有/技術課ﾌｫﾙﾀﾞ/200. effit_data/ﾏｽﾀ/sql_python_module'
else:
    pass

sys.path.append(shared_folder_path)
from I_tss_coa import ITssCoa


class CreateKoitoCoa:
    '''
    TSS品質管理で試験種=A or B,かつ((移動=Null or 済でない)かつ判定=合格)
    のものは小糸成績書を作成する。
    メタル品質管理からは小糸成績書を発行しない（syukkaロボットが作る) 
    櫻田フォルダにnon初物の小糸成績書がなかったら作る
    '''

    def __init__(self, tssCoaFromHs: ITssCoa, recorder: Recorder)-> None:

        self._tssCoaFromHs: ITssCoa = tssCoaFromHs
        self._recorder: Recorder = recorder

        self.check_path = r'\\192.168.1.247\共有\営業課ﾌｫﾙﾀﾞ\testreport\櫻田'
        if platform.system() == 'Linux':
            self.check_path = r'/mnt/public/営業課ﾌｫﾙﾀﾞ/testreport/櫻田' 
        self.output_path = r'\\192.168.1.247\共有\営業課ﾌｫﾙﾀﾞ\testreport\櫻田'
        

    def _is_exists_koito_coa(self, lot)-> bool:
        return coa_check.is_koitoExists_noHatumono(lot, self.check_path)


    def _is_hatumono_koito(self, lot)-> bool:
        return coa_check.is_hatumono_koito(lot, self.check_path)


    def create_koito_coa(self, passed_koitos_thistime)-> None:
        HS_nonCreate_coa = []
        for _, row in passed_koitos_thistime.iterrows():
            lot = row['LOT']
            hinban = row['Hinban']
            if self._is_exists_koito_coa(lot):
                txt = f'{hinban} {lot} の小糸成績書はすでに櫻田フォルダにあります。初物ではありません。'
                self._recorder.out_log(txt, '\n')
                self._recorder.out_file(txt, '\n')
                continue


            is_success_or_failed: str = self._tssCoaFromHs.create_coa(lot, 
                                                     self.output_path, '小糸')
            if is_success_or_failed != 'success':
                line: List[str] = [row['Hinban'], lot, '小糸向け']
                line.append(is_success_or_failed)
                HS_nonCreate_coa.append(line)

            if self._is_hatumono_koito(lot):
                add_txt = '↑　NG 初物です\n'
            else:
                add_txt = '↑　OK 初物ではありません\n'

            txt = f'{hinban} {lot} の小糸成績書を作成します \n' \
                  f'{add_txt}'
            self._recorder.out_log(txt, '\n')
            self._recorder.out_file(txt, '\n')


        

