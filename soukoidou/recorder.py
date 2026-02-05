import os
from datetime import datetime
import pandas as pd


class Recorder(object):


    def __init__ (self, myfolder: str):
        self.myfolder: str = myfolder

        
    def out_log (self, txt, rtn=''):
        print('{}{}'.format(txt, rtn))

        
    def out_file (self, txt, rtn=''):
        filePath = fr'//192.168.1.247/共有/技術課ﾌｫﾙﾀﾞ/200. effit_data' \
                   fr'/ﾏｽﾀ/DigitalManager/{self.myfolder}/log.txt'

        with open(filePath, 'a') as f:
            print('{}{}'.format(txt, rtn), file = f)


    def out_csv (self, df, filePath):
        df.to_csv(filePath, encoding='cp932')



