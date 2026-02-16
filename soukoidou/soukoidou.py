from typing import List
import platform
import sys
import pprint
from eigyoubi import Eigyoubi
from inventory_survey import InventorySurvey
from uninspected_products_survey import UninspectedProductsSurvey
from recorder import Recorder
from cybozu import *
from create_export_coa import CreateExportCoa

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


def soukoidou()->None:

    msg:str = '''事前に、TSSシステム「品質管理」「メタル品質管理」のデータを
effitAから取り込んでおいてください'''

    print(msg)

    sql_server_tss = SqlServerTss()
    sql_server_effit = SqlServerEffit()
    cnxn_tss = sql_server_tss.get_cnxn()
    cnxn_effit = sql_server_effit.get_cnxn() 


    eigyoubi = Eigyoubi(cnxn_tss) # eigyoubiのインスタンスを生成

    zenjitu: str = eigyoubi.get_before_today()       # 2026/09/29(稼働日)
    honjitu: str = eigyoubi.get_honjitu()             # 2026/09/30(稼働日)
    yokujitu: str = eigyoubi.get_after_today()        # 2026/10/01(稼働日)
    six_months_ago: str = eigyoubi.get_six_months_ago()    # 2026/03/31


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

    # コンソール表示とtxt出力
    recorder = Recorder('soukoidou') # soukoidouはフォルダ名
    recorder.out_log(mytxt)
    recorder.out_file(mytxt)

    '''
    成績書作成
    輸出塗料連絡表(CreateExportCoaクラス)で昨日出荷製品を調べて、
    testreport/輸出フォルダに 成績書があるか調べる。無ければ作る
    '''
    #TODO後で消す
    zenjitu = '2025/12/23'
    create_export_coa = CreateExportCoa(zenjitu, six_months_ago, 
                                                        cnxn_tss, recorder)
    nonCreate_coa: List[List[str]] = create_export_coa.create_coa()


    # 既存で初物でない成績書、送信済成績書がわかるdfをlogに書いておく
    create_export_coa.to_log_YTR()


    print()
    print('(成績書作成で失敗したcoa)')
    pprint.pprint(nonCreate_coa)
    recorder.out_file_from_list_list(nonCreate_coa, '(成績書作成で失敗したcoa)')


    # メッセージをサイボウズにアップする
    # put_cybozu(mytxt)

    sql_server_tss.close()
    sql_server_effit.close()


