from re import I
import pandas as pd
import platform
import datetime
from typing import List, cast
import os
import sys
import pdfplumber
import pprint
import zenhan
from fetch_data import IFetchData, FetchHkLot, FetchMhkLot
from recorder import Recorder


class CreateKoitoCoa:
    '''
    TSS品質管理で試験種=A or B,かつ((移動=Null or 済でない)かつ判定=合格)
    のものは小糸成績書を作成する。
    メタル品質管理からは小糸成績書を発行しない（syukkaロボットが作る) '''

    def __init__(self, fetchKoitoCoa: IFetchData)-> None:

        self.check_path = r'\\192.168.1.247\共有\営業課ﾌｫﾙﾀﾞ\testreport\櫻田'
        if platform.system() == 'Linux':
            self.check_path = r'/mnt/public/営業課ﾌｫﾙﾀﾞ/testreport/櫻田' 
        self.output_path = r'\\192.168.1.247\共有\営業課ﾌｫﾙﾀﾞ\testreport\ABﾁｪｯｸ'
        
        # koitoCoaが必要な品質管理のデータフレーム
        HS_need_koito_coa: pd.DataFrame = fetchKoitoCoa.fetch_data()

        # 櫻田フォルダ、ABチェックフォルダに小糸成績書が存在するか？
        # TODO　続きはABチェック後

         
        
        # 納入日のリストを作る
        nounyubis: List[str] = list(set(self.YTR['納品日']))

        first_path:str = r'//192.168.1.247/共有/営業課ﾌｫﾙﾀﾞ/testreport/zip_files'
        if platform.system() == 'Linux':
            first_path:str = r'/mnt/public/営業課ﾌｫﾙﾀﾞ/testreport/zip_files'

        # zip_files/送信済のファイル名リストを取得する
        listContentsOfZipFiles = ListContentsOfZipFiles() # インスタンス
        self.sentCoas: List[str] = [] # zip_files/送信済のpdfファイル名リスト
        for nounyuu_dire in nounyubis:
            nounyuu_dire = f'{nounyuu_dire[:4]}{nounyuu_dire[5:7]}{nounyuu_dire[8:]}'
            path = f'{first_path}/{nounyuu_dire}/送信済'
            # zip_files/送信済のファイル名リストを取得する
            self.sentCoas += \
                       listContentsOfZipFiles.list_contents_of_zip_files(path)


        # is_Exists_coa 列（既にcoaがあるか？）を作る
        if not self.YTR.empty:
            self.YTR['is_exists_coa'] = \
                    self.YTR.apply(self.judge_is_exists_coa, axis=1)
            self.YTR['already_sent_coa_exists'] = \
                    self.YTR.apply(self.already_sent_coa_exists, axis=1)



    def judge_is_exists_coa(self, row)-> bool:

        is_exists_coa:bool = False

        ikisaki: str = zenhan.z2h(row['行き先']).replace('/', '-')
        order_no: str = zenhan.z2h(row['オーダーナンバー'])
        lot: str = zenhan.z2h(row['ロット番号'])

        for filename in os.listdir(self.coa_path):
            '''
            ここを実行するとものすごく遅くなる
            # ファイルの絶対パスを生成
            #file_path = os.path.join(self.coa_path, filename)

            # ファイルであり、かつpdfファイルであるかを確認
            #if os.path.isfile(file_path) and filename.lower().endswith(".pdf"):
                # ファイル名から拡張子を除いた部分を取得
                #base_filename = os.path.splitext(filename)[0]
            '''
            # ファイルの絶対パス
            file_path = os.path.join(self.coa_path, filename)
            filename = zenhan.z2h(filename)
            if (ikisaki in filename 
                and order_no in filename
                and lot in filename
                and not self.check_is_hatumono(file_path)):
                is_exists_coa = True

        return is_exists_coa

