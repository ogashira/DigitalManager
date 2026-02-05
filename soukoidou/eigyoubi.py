import sys 
from datetime import date, timedelta
from fetch_data import *
from typing import List

class Eigyoubi:
    '''
    前日、翌日の稼働日を調査する
    '''

    def __init__(self, cnxn):

        fetch_data:IFetchData = FetchHolidays(cnxn)
        df_holidays:pd.DataFrame = fetch_data.fetch_data() 

        if df_holidays.empty:
            print('休日データ取得できないため中止します')
            sys.exit()

        self.holidays:List = list(df_holidays['KJ_DT']) 


    def get_before_today(self)-> str:
        today = date.today()
        before_today = today
        while True:
            before_today = before_today - timedelta(days=1)
            before_str:str = before_today.strftime("%Y/%m/%d")
            if not before_str in self.holidays:
                return before_str
        

    def get_after_today(self)-> str:
        today = date.today()
        after_today = today
        while True:
            after_today = after_today + timedelta(days=1)
            after_str = after_today.strftime("%Y/%m/%d")
            if not after_str in self.holidays:
                return after_str


    def get_honjitu(self)-> str:
        return date.today().strftime("%Y/%m/%d")


