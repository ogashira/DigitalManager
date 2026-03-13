from typing import List, TYPE_CHECKING
import pprint
from cybozu import *
from instance_factory import InstanceFactory

# 実行時にはインポートせず、型チェックの為だけに書く　
if TYPE_CHECKING:
    from eigyoubi import Eigyoubi
    from recorder import Recorder
    from inventory_survey import InventorySurvey
    from uninspected_products_survey import UninspectedProductsSurvey
    from create_export_coa import CreateExportCoa


def soukoidou()->None:

    # sqlServerTss, Effitのインスタンス生成し、cnxnを作る
    # これらは、instance_factoryクラスで保持 最後にdelete_cnxn()を実行して
    # sql_server.close()を行う
    InstanceFactory.get_sql_server_tss()
    InstanceFactory.get_sql_server_effit()

    eigyoubi: Eigyoubi = InstanceFactory.get_eigyoubi() # eigyoubiのインスタンスを生成

    zenjitu: str = eigyoubi.get_before_today()             # 2026/09/29(稼働日)
    honjitu: str = eigyoubi.get_honjitu()                  # 2026/09/30(稼働日)
    yokujitu: str = eigyoubi.get_after_today()             # 2026/10/01(稼働日)
    six_months_ago: str = eigyoubi.get_six_months_ago()    # 2026/03/31
    YmdHMS: str = eigyoubi.get_Ymd_HMS()                    # 2026/09/30 08:31:28 

    # Recorderのインスタンス生成
    recorder:Recorder = InstanceFactory.get_recorder('soukoidou') # soukoidouはフォルダ名
    stt_msg = f'\n{YmdHMS}\nデジタル部長スタート\n'
    recorder.out_log(stt_msg, '\n')
    recorder.out_file(stt_msg, '\n')

    msg:str = '事前に、TSSシステム「品質管理」「メタル品質管理」のデータを\n' \
              'effitAから取り込んでおいてください\n'
    print(msg)

    '''
    翌営業日出荷予定製品の在庫があるかどうか調べる。
    営業部で既に出荷処理を行っていれば、出荷予定製品として出てこないようにした。
    '''
    inventory_survey:InventorySurvey = InstanceFactory.get_inventory_survey(
                                                                       yokujitu)

    # サイボウズメッセージ用のテキスト
    mytxt_zaiko = inventory_survey.txt_for_cybozu()

    '''
    品質管理、メタル品質管理から検査未完了のデータを持ってくる
    '''
    uninspected_products_survey: UninspectedProductsSurvey = \
                           InstanceFactory.get_uninspected_products_survey()
    # サイボウズメッセージ用のテキスト
    mytxt_hs_mhs = uninspected_products_survey.txt_for_cybozu()

    mytxt = f'{mytxt_hs_mhs}\n\n' \
            f'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n' \
            f'{mytxt_zaiko}'

    # コンソール表示とtxt出力
    recorder.out_log(mytxt)
    recorder.out_file(mytxt)

    '''
    成績書作成
    輸出塗料連絡表(CreateExportCoaクラス)で昨日出荷製品を調べて、
    testreport/輸出フォルダに 成績書があるか調べる。無ければ作る
    '''
    #TODO後で消す
    zenjitu = '2025/12/23'

    create_export_coa: CreateExportCoa = \
                InstanceFactory.get_create_export_coa(zenjitu, 
                                                      six_months_ago)

    nonCreate_coa: List[List[str]] = create_export_coa.create_coa()


    # 既存で初物でない成績書、送信済成績書がわかるdfをlogに書いておく
    create_export_coa.to_log_YTR()


    print()
    print('(成績書作成で失敗したcoa)')
    pprint.pprint(nonCreate_coa)
    recorder.out_file_from_list_list(nonCreate_coa, '(成績書作成で失敗したcoa)')

    # メッセージをサイボウズにアップする
    try:
        put_cybozu(mytxt)
        msg = 'サイボウズに未検査品と在庫状況をアップしました。'
        recorder.out_log(msg, '\n')
        recorder.out_file(msg, '\n')
    except Exception as e:
        msg = 'サイボウズへのアップ失敗です。'
        recorder.out_log(msg)
        recorder.out_log(f'{e}', '\n')
        recorder.out_file(msg)
        recorder.out_file(f'{e}', '\n')
        

    # sqlServer.close()を呼び出して、server, cnxnを閉じる
    InstanceFactory.delete_cnxn()

    msg = 'プログラムは無事終了しました。'
    recorder.out_log(msg)
    recorder.out_file(msg)
