from mymodules.inventory_survey import InventorySurvey
from uninspected_products_survey import UninspectedProductsSurvey
from mymodules.recorder import Recorder
from mymodules.cybozu import ICybozu


class TxtCybozuForSoukoidou:

    def __init__(self, inventorySurvey: InventorySurvey, 
                 uninspectedProductsSurvey: UninspectedProductsSurvey, 
                 cybozuForSoukoidou: ICybozu,
                 recorder: Recorder)-> None:

        self._inventorySurvey = inventorySurvey
        self._uninspectedProductsSurvey = uninspectedProductsSurvey
        self._cybozuForSoukoidou = cybozuForSoukoidou
        self._recorder = recorder


    def create_txt_for_cybozuSoukoidou(self)->None:
        inspect_shipping_products = \
                self._inventorySurvey.calc_inspect_shipping_products()
        
        addTxt = self._inventorySurvey.make_txt_for_Dict_Dict(
                                            inspect_shipping_products)
        txt = f'\n(inspect_shipping_productsの表示)\n' \
                + addTxt
        self._recorder.out_log(txt, '\n')
        self._recorder.out_file(txt, '\n')



        txt_hs_mhs = self._uninspectedProductsSurvey.txt_for_cybozu()
        txt_zaiko = self._inventorySurvey.txt_for_cybozu()
        mytxt = f'{txt_hs_mhs}\n\n' \
                f'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n\n' \
                f'{txt_zaiko}'

        # コンソール表示とtxt出力
        self._recorder.out_log(mytxt)
        self._recorder.out_file(mytxt)

        # サイボウズにアップする
        self._put_cybozu(mytxt)

    def _put_cybozu(self, mytxt:str)-> None:
        is_cybozu_up: bool = self._cybozuForSoukoidou.put_cybozu(mytxt)
        if is_cybozu_up:
            txt = 'サイボウズに未検査品と在庫状況をアップしました。'
        else:
            txt = 'サイボウズへのアップ失敗です。'

        self._recorder.out_log(txt, '\n')
        self._recorder.out_file(txt, '\n')
