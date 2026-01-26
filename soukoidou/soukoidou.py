'''
import time, sys, pprint 
from yotei import Yotei
from seisekisyo import *
from excelsagyou import *
from jisseki import *
'''
from typing import List
import platform
import sys
from eigyoubi import Eigyoubi
from inventory_survey import InventorySurvey
from uninspected_products_survey import UninspectedProductsSurvey
from cybozu import *


def soukoidou()->None:

    msg:str = '''事前に、TSSシステム「品質管理」「メタル品質管理」のデータを
effitAから取り込んでおいてください'''

    print(msg)

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
    from sql_server_tss import SqlServer as SqlServerTss # tssサーバー
    from sql_server import SqlServer as SqlServerEffit  # effitAサーバー
    sql_server_tss = SqlServerTss()
    sql_server_effit = SqlServerEffit()
    cnxn_tss = sql_server_tss.get_cnxn()
    cnxn_effit = sql_server_effit.get_cnxn() 


    eigyoubi = Eigyoubi(cnxn_tss) # eigyoubiのインスタンスを生成

    zen_torikomibi: str = eigyoubi.get_before_today() # 2026/09/29
    honjitu: str = eigyoubi.get_honjitu()             # 2026/09/30
    yokujitu: str = eigyoubi.get_after_today()        # 2026/10/01

    '''
    翌営業日出荷予定製品の在庫があるかどうか調べる。
    営業部で既に出荷処理を行っていれば、出荷予定製品として出てこないようにした。
    '''
    inventory_survey:InventorySurvey = InventorySurvey(cnxn_tss, 
                                                      cnxn_effit, yokujitu)
    # サイボウズメッセージ用のテキスト
    mytxt_zaiko = inventory_survey.txt_for_cybozu()

    '''
    品質管理、メタル品質管理から検査未完了のデータを持ってくる
    '''
    uninspected_products_survey = UninspectedProductsSurvey(cnxn_tss)
    # サイボウズメッセージ用のテキスト
    mytxt_hs_mhs = uninspected_products_survey.txt_for_cybozu()

    mytxt = f'{mytxt_hs_mhs}\n\n' \
            f'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n' \
            f'{mytxt_zaiko}'

    # メッセージをサイボウズにアップする
    put_cybozu(mytxt)

    sql_server_tss.close()
    sql_server_effit.close()


    '''
    # テキストファイルに書き出す>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    f = open(r'\\192.168.1.247\共有\技術課ﾌｫﾙﾀﾞ\200. effit_data\hinkan.txt', 'w') # 書き込みモードで開く
    f.write('予定日入力\n\n')
    f.write(str(yoteibi_str)+'\n\n\n') # 引数の文字列をファイルに書き込む
    f.write('本日試験\n\n')
    f.write(str(siken_str) +'\n\n\n')
    f.write('ﾂﾀﾝｶｰﾒﾝ\n\n')
    f.write(str(tk_siken_str) +'\n\n\n')
    f.write('出荷予定の在庫\n\n')
    f.write(str(yoteizaiko_str) + '\n\n\n')

    f.write('発行を要する成績書\n\n')
    f.write(str(yt_data) + '\n\n\n')

    f.write('品管ｼｰﾄから発行した成績書\n\n')
    f.write(str(mycoa) + '\n\n\n')

    f.write('品管ｼｰﾄでｴﾗｰﾒｯｾｰｼﾞが出た成績書\n\n')
    f.write(str(miss_coa) +'\n\n\n')

    f.write('品管ｼｰﾄでは未発行の成績書\n\n')
    f.write(str(mycheck) + '\n\n\n')





    f.close() # ファイルを閉じる



    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    #テキストファイルに情報を追加

    f = open(r'\\192.168.1.247\共有\技術課ﾌｫﾙﾀﾞ\200. effit_data\hinkan.txt', 'a') # 追記モードで開く

    f.write('ﾒﾀﾙ品管ｼｰﾄで発行する成績書\n\n')
    f.write(str(pprint.pformat(mtl_coa)) + '\n\n\n')
    f.write('ﾒﾀﾙ品管ｼｰﾄで発行した成績書\n\n')
    f.write(str(pprint.pformat(mtl_coa_sumi)) + '\n\n\n')
    f.write('ﾒﾀﾙ品管ｼｰﾄで発行時ｴﾗｰが出た成績書\n\n')
    f.write(str(pprint.pformat(mtl_coa_miss)) + '\n\n\n')
    f.write('ﾒﾀﾙ品管ｼｰﾄでlotが無かったﾘｽﾄ')
    f.write(str(pprint.pformat(mtl_coa_lotnasi)))

    f.close() # ファイルを閉じる

'''
