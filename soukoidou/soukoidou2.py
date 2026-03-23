from typing import List, TYPE_CHECKING
import pprint
from instance_factory import InstanceFactory
from cybozu import ICybozu
import sys

# 実行時にはインポートせず、型チェックの為だけに書く　
if TYPE_CHECKING:
    from eigyoubi import Eigyoubi
    from recorder import Recorder
    from soukoidou_check import SoukoidouCheck
    from create_koito_coa import CreateKoitoCoa
    from ab_test_check import ABTestCheck
    from effitA import EffitA


def soukoidou2()->None:

    # sqlServerTss, Effitのインスタンス生成し、cnxnを作る
    # これらは、instance_factoryクラスで保持 最後にdelete_cnxn()を実行して
    # sql_server.close()を行う
    InstanceFactory.get_sql_server_tss()
    InstanceFactory.get_sql_server_effit()

    eigyoubi:Eigyoubi = InstanceFactory.get_eigyoubi() # eigyoubiのインスタンスを生成

    zenjitu: str = eigyoubi.get_before_today()             # 2026/09/29(稼働日)
    honjitu: str = eigyoubi.get_honjitu()                  # 2026/09/30(稼働日)
    yokujitu: str = eigyoubi.get_after_today()             # 2026/10/01(稼働日)
    six_months_ago: str = eigyoubi.get_six_months_ago()    # 2026/03/31
    YmdHMS: str = eigyoubi.get_Ymd_HMS()                   # 2026/09/30 08:31:28 

    #TODO 後で消す
    #yokujitu = '2026/02/19'

    # Recorderのインスタンス生成
    recorder: Recorder = InstanceFactory.get_recorder('soukoidou2') # soukoidouはフォルダ名
    stt_msg = f'\n{YmdHMS}\nデジタル部長スタート\n'
    recorder.out_log(stt_msg, '\n')
    recorder.out_file(stt_msg, '\n')
    
    '''
    翌営業日出荷予定製品の在庫があるかどうか調べる。
    営業部で既に出荷処理を行っていれば、出荷予定製品として出てこないようにした。
    InventorySurveyクラスでinspect_shipping_products =
              { 'S6-SV3800-U':{'出荷缶数':20, '現在庫':100, '引当後':80}, ....}
    を求めて、更にSoukoidouCheckクラスで済でない合格品の数を引当後にプラスして
    引当後の在庫がマイナスにならないかをチェック。また、AB試験もチェックして
    両方okならis_soukoidou_okならTrueとする
    '''
    soukoidouCheck:SoukoidouCheck = InstanceFactory.get_soukoidou_check(yokujitu)
    # check_is_soukoidou_okの中でcreate_koito_coaも呼ばれる
    is_soukoidou_ok:bool = soukoidouCheck.check_is_soukoidou_ok()

    # 倉庫移動を行う
    if is_soukoidou_ok:
        effitA:EffitA = InstanceFactory.get_effitA(honjitu)
        effitA.soukoidou()
        # 倉庫移動が問題なく行われたかをチェックする 
        failed_soukoidous: List[List[str]] = effitA.check_before_after()

    # サイボウズにアップする
    cybozuForSoukoidou2: ICybozu = \
            InstanceFactory.get_cybozuForSoukoidou2(is_soukoidou_ok)
    cybozuForSoukoidou2.put_cybozu()

    # sqlServer.close()を呼び出して、server, cnxnを閉じる
    InstanceFactory.delete_cnxn()

    txt = 'プログラムは全て終了です'
    recorder.out_log(txt, '\n')
    recorder.out_file(txt, '\n')
