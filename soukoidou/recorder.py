import os
import platform
from datetime import datetime
import pandas as pd
import datetime
from typing import List


class Recorder(object):


    def __init__ (self, mydir: str):
        base_dir:str = fr'//192.168.1.247/共有/技術課ﾌｫﾙﾀﾞ' \
                       fr'/01.DigitalManager/{mydir}'
        if platform.system() == 'Linux':
            base_dir = fr'/mnt/public/技術課ﾌｫﾙﾀﾞ' \
                       fr'/01.DigitalManager/{mydir}'
        date = datetime.datetime.today().strftime("%Y%m%d")
        date_dir = os.path.join(base_dir, date)
        self.log_file_path = os.path.join(date_dir, "log.txt")

        # date_dirが存在しない場合は作成する
        if not os.path.exists(date_dir):
            os.makedirs(date_dir)

        
    def out_log (self, txt, rtn=''):
        print('{}{}'.format(txt, rtn))

    def out_log_df(self, df, title:str):
        print(title)
        print(df)

        
    def out_file (self, txt, rtn=''):

        with open(self.log_file_path, 'a') as f:
            print('{}{}'.format(txt, rtn), file = f)


    def out_file_from_list(self, list:List[str], title:str)-> None:
        '''
        一次元リストからファイルに出力する
        １要素、１行ずつ表示する
        '''
        # (リスト)の中身を全て文字列に変換する
        list_str = [str(item) for item in list]
        txt = '\n'.join(list_str)

        with open(self.log_file_path, 'a') as f:
            print(f'\n{title}\n{txt}\n', file = f)
        

    def out_file_from_list_list(self, lists:List[List], title:str)-> None:
        '''
        二次元リストをファイルに出力する。
        innerリストはカンマ区切りで、１行ずつ表示する
        '''
        row_txts:List = [] 
        for list in lists:
            # (リスト)の中身を全て文字列に変換する
            list_str = [str(item) for item in list]
            row_txt = ','.join(list_str)
            row_txts.append(row_txt)
                
        txt = '\n'.join(row_txts)
        with open(self.log_file_path, 'a') as f:
            print(f'\n{title}\n{txt}', file = f)


    def out_file_from_df(self, df:pd.DataFrame, title:str)-> None:
        '''
        DataFrameからファイルに出力する
        １行ずつ表示する
        DataFrameを二次元リストにしてout_file_from_list_listに渡す
        '''
        lists:List[list] = df.values.tolist() # dfを二次元リストにする
        self.out_file_from_list_list(lists, title)


    def out_csv (self, df, filePath):
        df.to_csv(filePath, encoding='cp932')




