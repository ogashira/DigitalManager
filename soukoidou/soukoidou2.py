from typing import Dict, TYPE_CHECKING
import pprint
from instance_factory import InstanceFactory
from cybozu import *

# 実行時にはインポートせず、型チェックの為だけに書く　
if TYPE_CHECKING:
    from sql_server_tss import SqlServer as SqlServerTss # tssサーバー
    from sql_server import SqlServer as SqlServerEffit  # effitAサーバー
    from eigyoubi import Eigyoubi
    from recorder import Recorder
    from inventory_survey import InventorySurvey
    from soukoidou_check import SoukoidouCheck
    from create_koito_coa import CreateKoitoCoa

def soukoidou2()->None:
    sql_server_tss: SqlServerTss = InstanceFactory.get_sql_server_tss()
    sql_server_effit: SqlServerEffit = InstanceFactory.get_sql_server_effit()
    cnxn_tss = sql_server_tss.get_cnxn()
    cnxn_effit = sql_server_effit.get_cnxn() 

    eigyoubi:Eigyoubi = InstanceFactory.get_eigyoubi(cnxn_tss) # eigyoubiのインスタンスを生成

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
    '''
    inventory_survey:InventorySurvey = \
            InstanceFactory.get_inventory_survey( cnxn_tss, cnxn_effit, yokujitu)
    # inspect_shipping_products= 
    #         { 'S6-SV3800-U':{'出荷缶数':20, '現在庫':100, '引当後':80}, ....}
    # ラベル張替え品もkg売り品も品質管理で管理している品番名に変換されている。
    inspect_shipping_products = inventory_survey.get_inspect_shipping_products()

    soukoidouCheck:SoukoidouCheck = InstanceFactory.get_soukoidou_check(cnxn_tss)
    # inspect_shipping_produxtsをsoukoidou_checkに渡して引当後の数に
    # 合格品の数をプラスして書き換えてもらう
    soukoidouCheck.soukoidou_check(inspect_shipping_products)

    # 引当後マイナス在庫のdicをもらう
    ''' minus_inventorysが空だったら倉庫移動をかけても良い'''
    minus_inventorys: Dict = \
            soukoidouCheck.minus_inventorys(inspect_shipping_products)
 
    # 小糸成績書を発行する 
    createKoitoCoa: CreateKoitoCoa = \
            InstanceFactory.get_create_koito_coa(cnxn_tss)



    pprint.pprint(inspect_shipping_products)
    print('minus_inventorys')
    pprint.pprint(minus_inventorys)

    sql_server_tss.close()
    sql_server_effit.close()
