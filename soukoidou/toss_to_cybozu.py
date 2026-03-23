from inventory_survey import InventorySurvey
from uninspected_products_survey import UninspectedProductsSurvey
from recorder import Recorder


class TossToCybozu:

    def __init__(self, inventorySurvey: InventorySurvey, 
                 uninspectedProductsSurvey: UninspectedProductsSurvey, 
                 recorder: Recorder)-> None:

        self._inventorySurvey = inventorySurvey
        self._uninspectedProductsSurvey = uninspectedProductsSurvey
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


