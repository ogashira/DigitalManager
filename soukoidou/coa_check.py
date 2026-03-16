'''
is_existsCoa_noHatumono 
    引数: 行き先, lot, order_no, path(フォルダ)
    戻り値: bool
    作ったcoaをpathの中から探して、初物かどうかチェックする

is_existsCoa_noHatumono_seriesArgs
    引数: pd.Series, path(フォルダ)
    戻り値: bool
    フォルダの中にオーダーＮｏ,lot,行き先,が含まれるファイル名を持つ
    *初物でない*ファイルが あるかを調べる。

is_existsCoa_seriesArgs
    引数: pd.Series, coas:List[str](ファイル名のリスト)
    戻り値: bool
    フォルダの中にオーダーＮｏ,lot,行き先,が含まれるファイル名を持つ
    ファイルが あるかを調べる。 初物は無視する。 

is_existsKoitoCoa_seriesArgs
    引数: pd.Series, path(フォルダ)
    戻り値: bool
    TODO: 続きはABチェック後
'''
from typing import Optional, List
import pandas as pd
import os
import pdfplumber
import zenhan


def is_hatumono(ikisaki: str, lot: str, 
                            order_no: str, path: str)-> bool:
    '''
    作ったcoaをpathの中から探して、初物かどうかチェックする
    '''

    is_hatumono:bool = False

    ikisaki = zenhan.z2h(str(ikisaki)).replace('/', '-')
    order_no = zenhan.z2h(str(order_no))
    lot = zenhan.z2h(str(lot))

    for filename in os.listdir(path):
        # ファイルの絶対パス
        file_path = os.path.join(path, filename)
        filename = zenhan.z2h(filename)
        if (ikisaki in filename 
            and order_no in filename
            and lot in filename
            and check_is_hatumono(file_path)):
            is_hatumono = True

    return is_hatumono


def is_hatumono_koito(lot: str, path: str)-> bool:
    '''
    作ったcoaをpathの中から探して、初物かどうかチェックする
    '''

    is_hatumono:bool = False

    lot = zenhan.z2h(str(lot))

    for filename in os.listdir(path):
        # ファイルの絶対パス
        file_path = os.path.join(path, filename)
        filenames:List = zenhan.z2h(filename).split('_')
        if len(filenames) == 4:
            if ( filenames[1] ==lot
                and (filenames[3] == '小糸.pdf' or filenames[3] == '小糸.PDF')
                and check_is_hatumono(file_path)):
                is_hatumono = True

    return is_hatumono


def is_koitoExists_noHatumono(lot: str, path: str)-> bool:
    '''
    coaを櫻田フォルダ中から探して、初物かどうかチェックし、
    初物でないcoaがあったらTrueを返す
    '''
    is_koitoExists_noHatumono:bool = False

    lot = zenhan.z2h(str(lot))
    

    for filename in os.listdir(path):
        # ファイルの絶対パス
        file_path = os.path.join(path, filename)
        filenames:List = zenhan.z2h(filename).split('_')
        if len(filenames) == 4:
            if (filenames[1] == lot 
                and (filenames[3] == '小糸.pdf' or filenames[3] == '小糸.PDF')
                and not check_is_hatumono(file_path)):
                is_koitoExists_noHatumono = True

    return is_koitoExists_noHatumono


def is_existsCoa_noHatumono_seriesArgs(row: Optional[pd.Series],
                                    path)-> bool:
    is_existsCoa_noHatumono:bool = False

    if row is None:
        return is_existsCoa_noHatumono

    ikisaki: str = zenhan.z2h(row['行き先']).replace('/', '-')
    order_no: str = zenhan.z2h(row['オーダーナンバー'])
    lot: str = zenhan.z2h(row['ロット番号'])

    for filename in os.listdir(path):
        # ファイルの絶対パス
        file_path = os.path.join(path, filename)
        filename = zenhan.z2h(filename)
        if (ikisaki in filename 
            and order_no in filename
            and lot in filename
            and not check_is_hatumono(file_path)):
            is_existsCoa_noHatumono= True

    return is_existsCoa_noHatumono


def is_existsCoa_seriesArgs(row: Optional[pd.Series], sentCoas:List[str])-> bool:
    '''
    ファイル名のリストの中に、行き先、order_no,
    lotが含まれるファイル名があるか？あったらTrueを返す。
    '''
    is_existsCoa:bool = False

    if row is None:
        return is_existsCoa

    ikisaki: str = zenhan.z2h(row['行き先']).replace('/', '-')
    order_no: str = zenhan.z2h(row['オーダーナンバー'])
    lot: str = zenhan.z2h(row['ロット番号'])

    for filename in sentCoas: # ファイル名のリスト
        filename = zenhan.z2h(filename)
        if (ikisaki in filename 
            and order_no in filename
            and lot in filename):
            is_existsCoa = True

    return is_existsCoa


def check_is_hatumono(pdf_path)-> bool:
    
    is_hatumono = False
    target_text = "初物 要チェック"

    with pdfplumber.open(pdf_path) as pdf:

        # 1ページずつループ
        for i, page in enumerate(pdf.pages):
            # ページからテキストを抽出
            text = page.extract_text()
            
            # テキストが存在し、かつターゲット文字列が含まれているか
            if text and target_text in text:
                is_hatumono = True
    
    return is_hatumono 
