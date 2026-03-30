import pandas as pd
from typing import Dict
from fetch_data import IFetchData


class PlusKensaGoukaku:
    '''
    品質管理、メタル品質管理で、検査合格品で倉庫移動されていない
    製品データ(self._nonSumis)を使って、
    inspect_shipping_products(出荷処理されていない翌日出荷予定の製品。
    出荷数、現在庫、出荷後の在庫データを持つ) の出荷後の在庫データに合格品を
    プラスしていく。この段階で、出荷後の在庫がマイナスの製品があると、
    倉庫移動できないと判断する。
    '''

    def __init__(self, 
                 fetch_HK_notSumi: IFetchData, 
                 fetch_MHK_notSumi: IFetchData)-> None:
    

        # 合格していて済でないまたは、特採のデータを取得する　
        HK_nonSumi:pd.DataFrame = fetch_HK_notSumi.fetch_data()
        MHK_nonSumi:pd.DataFrame = fetch_MHK_notSumi.fetch_data()

        def create_nonSumis(dic, df):
            for i in range(len(df)):
                hinban = df.loc[i, 'Hinban']
                cans = df.loc[i, 'Cans']
                if hinban in dic:
                    dic[hinban] += cans
                else:
                    dic[hinban] = cans


        # _nonSumis = {'S6-SV3800-U': 23, 'S7-A-M': 31......}
        self._nonSumis: Dict = {} # 合格していて済でないデータ
        # self._nonSumisにHK_nonSumiデータとMHK_nonSumiデータを詰める
        create_nonSumis(self._nonSumis, HK_nonSumi)
        create_nonSumis(self._nonSumis, MHK_nonSumi)

        #TEST
        #self._nonSumis['S1-FPA3K2D5HNV-U'] = 55
        #self._nonSumis['S4-BS421BB-4-U'] = 9


    def plus_goukaku(self, inspect_shipping_products:Dict)-> Dict:
        '''
        inspect_shipping_productsを受け取って、その引当後の数に
        合格品で済になっていない品番の数を加算する
        '''
        shipping_products_plus_goukaku: Dict = {}
        if not inspect_shipping_products:
            return  shipping_products_plus_goukaku
        
        for key, inner_dic in inspect_shipping_products.items():
            if key in self._nonSumis:
                inner_dic['引当後'] = inner_dic['引当後'] + self._nonSumis[key]
        
        return  shipping_products_plus_goukaku
