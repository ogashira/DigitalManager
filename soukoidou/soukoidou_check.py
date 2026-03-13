from typing import Dict
import pandas as pd
from recorder import Recorder
from ab_test_check import ABTestCheck
from inventory_survey import InventorySurvey


class SoukoidouCheck:
    '''
    倉庫移動をかけることができるかをチェックする。
    InventorySurveyクラスから、shipping_products_plus_goukakuをもらって
    引当後のマイナス在庫がないかをチェックする。
    shipping_products_plus_goukakuはInventorySurveyで作った
    inspect_shipping_productsにPlusKensaGoukakuクラスで合格品をプラスしたもの。
    また、ABTestCheckにABチェック問題ないかをしらべてもらう。
    マイナス在庫が無く、ABチェック合格なら倉庫移動できる
    '''

    def __init__(self, inventorySurvey: InventorySurvey,
                                 abTestCheck: ABTestCheck,
                                 recorder: Recorder)-> None:
        self._inventorySurvey: InventorySurvey = inventorySurvey
        self._abTestCheck: ABTestCheck = abTestCheck
        self._recorder: Recorder = recorder
    

    def minus_inventorys(self, shipping_products_plus_goukaku:Dict) -> Dict:
        '''
        引当後マイナス在庫のDictを返す
        '''
        minus_inventorys: Dict = {}
        if not shipping_products_plus_goukaku:
            return minus_inventorys

        for key, inner_dic in shipping_products_plus_goukaku.items():
            if inner_dic['引当後'] < 0:
                minus_inventorys[key] = inner_dic
        return minus_inventorys

        
    def check_is_soukoidou_ok(self)-> bool:
        is_soukoidou_ok: bool = False
        # 合格品の数をプラスしたinspect_shipping_productsをもらう
        shipping_products_plus_goukaku: Dict = \
                               self._inventorySurvey.plus_kensa_goukaku()
        # 引当後にマイナスになる在庫のdicをもらう
        minus_inventorys: Dict = self.minus_inventorys(
                                            shipping_products_plus_goukaku)
        
        if minus_inventorys:
            txt = f'以下のとおりマイナス在庫があるため倉庫移動できません' \
            f'{self._inventorySurvey.make_txt_for_Dict_Dict(minus_inventorys)}'
            self._recorder.out_log(txt, '\n')
            self._recorder.out_file(txt)
            return is_soukoidou_ok

        # ABチェックokなら小糸b試験管理シートに記入してis_soukoidou_okをTrueに
        if self._abTestCheck.check_is_abTest_ok():
            self._abTestCheck.input_to_BsikenKanriSheet()
            is_soukoidou_ok = True

        return is_soukoidou_ok
        

