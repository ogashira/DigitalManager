import pandas as pd
import platform
import datetime
from typing import List, cast
import sys
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
from list_contents_of_zip_files import ListContentsOfZipFiles


class CreateExportCoa:
    '''
    輸出塗料連絡表で、発送日が前営業日で、「成績書記載名称」が "-" 
    でない製品を作成する。
    - /testreport/輸出/ に既に存在する成績書は作成しない。
    - /testreport/輸出/に存在していても、「初物 要チェック」がある場合は作成する。
    - /testreport/zip_files/<納入日フォルダ>/送信済/*.zipに成績書がある場合は
    作成しない
    '''

    def __init__(self, args)-> None:

        zenjitu = args.zenjitu
        # recorderのインスタンスをもらっておく
        self.recorder:Recorder = args.recorder

        self.HS: ITssCoa = args.tss_coa_from_hs
        self.MHS: ITssCoa = args.tss_coa_from_mhs


        path = r'\\192.168.1.247\Guest\輸出塗料連絡表.xlsx'
        self.coa_path = r'\\192.168.1.247\共有\営業課ﾌｫﾙﾀﾞ\testreport\輸出'
        self.YSSH_path = r'\\192.168.1.247\共有\技術課ﾌｫﾙﾀﾞ\200. effit_data' \
                         r'\ﾏｽﾀ\coaﾒｰﾙ送信関連\輸出成績作成表.xlsx'
        if platform.system() == 'Linux':
            path = r'/mnt/guest/輸出塗料連絡表.xlsx'
            self.coa_path = r'/mnt/public/営業課ﾌｫﾙﾀﾞ/testreport/輸出' 
            self.YSSH_path = r'/mnt/public/技術課ﾌｫﾙﾀﾞ/200. effit_data' \
                             r'/ﾏｽﾀ/coaﾒｰﾙ送信関連/輸出成績作成表.xlsx'
        self.output_path = r'\\192.168.1.247\共有\営業課ﾌｫﾙﾀﾞ\testreport\輸出'
        
        df = pd.read_excel(path, sheet_name='輸出塗料連絡表', skiprows=1)
        # 発送日と納入日を'%Y/%m/%d'にする
        df['発送日'] = df['発送日'].map(lambda x : x.strftime('%Y/%m/%d') 
                                         if type(x) == datetime.datetime else x)
        df['納品日'] = df['納品日'].map(lambda x : x.strftime('%Y/%m/%d') 
                                         if type(x) == datetime.datetime else x)

        # 成績表記載名称が"-"は成績書不要
        self.YTR = df[(df['発送日'] == zenjitu) & \
                          (df['成績表記載名称'] != '-')].reset_index(drop=True)
        
        # 納入日のリストを作る
        nounyubis: List[str] = list(set(self.YTR['納品日']))

        first_path:str = r'//192.168.1.247/共有/営業課ﾌｫﾙﾀﾞ/testreport/zip_files'
        if platform.system() == 'Linux':
            first_path:str = r'/mnt/public/営業課ﾌｫﾙﾀﾞ/testreport/zip_files'

        # zip_files/送信済のファイル名リストを取得する
        self.sentCoas: List[str] = [] # zip_files/送信済のpdfファイル名リスト
        for nounyuu_dire in nounyubis:
            nounyuu_dire = f'{nounyuu_dire[:4]}{nounyuu_dire[5:7]}{nounyuu_dire[8:]}'
            path = f'{first_path}/{nounyuu_dire}/送信済'
            # zip_files/送信済のファイル名リストを取得する
            self.sentCoas += \
                       args.listContentsOfZipFiles.list_contents_of_zip_files(path)


        # is_Exists_coa 列（既にcoaがあるか？）を作る
        # 追加引数はタプルとして渡すので(self.coa_path, ) コンマが必要
        # ['is_exists_coa']は初物は除外する。['already_sent_coa_exists']は
        # 初物チェックはしない
        if not self.YTR.empty:
            self.YTR['is_exists_coa'] = self.YTR.apply(
                    coa_check.is_existsCoa_noHatumono_seriesArgs, 
                    axis=1, args=(self.coa_path,)
                    )
            self.YTR['already_sent_coa_exists'] = self.YTR.apply(
                    coa_check.is_existsCoa_seriesArgs, 
                    axis=1, args=(self.sentCoas,))

        # HSとMHSからlotのリストを得る。輸出塗料連絡表のLotがどちらのデータベースに
        # あるかを判定して、成績書を作成する
        df_HS = args.fetch_HS_lot.fetch_data()
        self.HS_lots: List[str] = list(df_HS['LOT'])

        df_MHS = args.fetch_MHS_lot.fetch_data()
        self.MHS_lots: List[str] = list(df_MHS['LOT'])


    def create_coa(self)-> List[List[str]]:

        if self.YTR.empty:
            return []

        # 全部ありなら、何もしない
        if (self.YTR['is_exists_coa'] == True).all():
            return []

        nonCreate_coa = [] 
        HS_nonCreate_coa = []
        MHS_nonCreate_coa = []

        # 輸出生成期作成表を取得する
        YSSH = pd.read_excel(self.YSSH_path,  skiprows=3)
        mksk_dic = dict(zip(YSSH['輸出塗料連絡表表記'], 
                                                     YSSH['userform1combobox']))

        # 輸出塗料連絡表で成績書が存在しない、かつ送信済でない行でループする
        YTR_false = self.YTR[(self.YTR['is_exists_coa'] == False) & 
            (self.YTR['already_sent_coa_exists']== False)].reset_index(drop=True) 
        if YTR_false.empty:
            txt = '新たに作成する成績書はありません'
            self.recorder.out_log(txt)
            self.recorder.out_file(txt)
            return []

        for i in range(len(YTR_false)):  
            mksk:str = mksk_dic[YTR_false.loc[i, '行き先']]
            ikisaki:str = YTR_false.loc[i, '行き先']
            lot:str =  YTR_false.loc[i, 'ロット番号']
            name:str = YTR_false.loc[i, '品名']
            order_no = YTR_false.loc[i, 'オーダーナンバー']

            txt = (f'{ikisaki},{lot},{name},{order_no}の成績書作成中')
            self.recorder.out_log(txt, '\n')
                  
            # 品室管理にある場合
            if lot in self.HS_lots:
                is_success_or_failed_HS: str = self.HS.create_coa(lot, 
                                                         self.output_path, mksk)
                if is_success_or_failed_HS != 'success':
                    line: List[str] = [mksk, lot, name, order_no ]
                    line.append(is_success_or_failed_HS)
                    HS_nonCreate_coa.append(line)
            elif lot in self.MHS_lots: # メタル品質管理にある場合
                is_success_or_failed_MHS: str = self.MHS.create_coa(lot, 
                                                      self.output_path)
                if is_success_or_failed_MHS != 'success':
                    line: List[str] = [mksk, lot, name, order_no ]
                    line.append(is_success_or_failed_MHS)
                    MHS_nonCreate_coa.append(line)
            else:
                line: List[str] = [mksk, lot, name, order_no, 'データベースにLotなし' ]
                nonCreate_coa.append(line)

            # 初物チェックして初物だったらnonCreate_coaにappendする
            if coa_check.is_hatumono(ikisaki, lot, order_no, self.coa_path):
                nonCreate_coa.append([mksk, lot, name, order_no, '初物NG'])
                print('↑ 初物です')
            #self.warning_hatumono(coa_folder)

        return nonCreate_coa



    def to_log_YTR(self)-> None:
        # DataFrameでcastしないとpyrightがSeriesになるかもしれないと警告だす。
        df:pd.DataFrame = cast(pd.DataFrame,self.YTR[['行き先', 
                                                      'オーダーナンバー', 
                                                      '品名', 
                                                      'is_exists_coa', 
                                                      'already_sent_coa_exists']])
        self.recorder.out_file_from_df(df, 
                             '(既存で初物でない成績書:-2列、送信済成績書:-1列)')
        
