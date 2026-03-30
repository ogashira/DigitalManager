from typing import List, TYPE_CHECKING
import pprint
from txt_cybozu_for_soukoidou import TxtCybozuForSoukoidou
from mymodules.instance_factory import InstanceFactory

# 実行時にはインポートせず、型チェックの為だけに書く　
if TYPE_CHECKING:
    from mymodules.eigyoubi import Eigyoubi
    from mymodules.recorder import Recorder
    from mymodules.inventory_survey import InventorySurvey
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
    成績書作成
    輸出塗料連絡表(CreateExportCoaクラス)で昨日出荷製品を調べて、
    testreport/輸出フォルダに 成績書があるか調べる。無ければ作る
    '''
    #TODO後で消す
    zenjitu = '2026/04/01'

    create_export_coa: CreateExportCoa = \
                InstanceFactory.get_create_export_coa(zenjitu, honjitu, 
                                                      six_months_ago)
    # 輸出成績書を作成する
    create_export_coa.create_coa()
    # 既存で初物でない成績書、送信済成績書がわかるdfをlogに書いておく
    create_export_coa.to_log_YTR()

    '''
    Cybozuクラスを呼び出して、品質管理、メタル品質管理の未検査品情報および
    翌日出荷品の情報をサイボウズにアップする。
    未検査品情報はUninspectedProductSurveyクラス。
    翌日出荷品の情報はInventorySurveyクラス
    '''
    txtCybozuForSoukoidou: TxtCybozuForSoukoidou = \
                    InstanceFactory.get_txtCybozuForSoukoidou(yokujitu)
    txtCybozuForSoukoidou.create_txt_for_cybozuSoukoidou()

    # sqlServer.close()を呼び出して、server, cnxnを閉じる
    InstanceFactory.delete_cnxn()

    msg = 'プログラムは無事終了しました。'
    recorder.out_log(msg)
    recorder.out_file(msg)
