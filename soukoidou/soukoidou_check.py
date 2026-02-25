import pandas as pd
from typing import Dict, List
from fetch_data import FetchMhkNotSumi, FetchHkNotSumi, IFetchData


class SoukoidouCheck:

    def __init__(self, cnxn_tss)-> None:
        # 合格していて済でないデータを取得する　
        fetch_HK:IFetchData = FetchHkNotSumi(cnxn_tss)
        fetch_MHK:IFetchData = FetchMhkNotSumi(cnxn_tss)
        HK_nonSumi:pd.DataFrame = fetch_HK.fetch_data()
        MHK_nonSumi:pd.DataFrame = fetch_MHK.fetch_data()

        def create_nonSumis(dic, df):
            for i in range(len(df)):
                hinban = df.loc[i, 'Hinban']
                cans = df.loc[i, 'Cans']
                if hinban in dic:
                    dic[hinban] += cans
                else:
                    dic[hinban] = cans


        # nonSumis = {'S6-SV3800-U': 23, 'S7-A-M': 31......}
        self.nonSumis: Dict = {} # 合格していて済でないデータ
        # self.nonSumisにHK_nonSumiデータとMHK_nonSumiデータを詰める
        create_nonSumis(self.nonSumis, HK_nonSumi)
        create_nonSumis(self.nonSumis, MHK_nonSumi)

        #TEST
        #self.nonSumis['S1-FPA3K2D5HNV-U'] = 55
        #self.nonSumis['S4-BS421BB-4-U'] = 9


    def soukoidou_check(self, inspect_shipping_products:Dict)-> None:
        '''
        inspect_shipping_productsを受け取って、その引当後の数に
        合格品で済になっていない品番の数を加算する
        '''
        if not inspect_shipping_products:
            return 
        
        for key, inner_dic in inspect_shipping_products.items():
            if key in self.nonSumis:
                inner_dic['引当後'] = inner_dic['引当後'] + self.nonSumis[key]
        

    def minus_inventorys(self, inspect_shipping_products:Dict) -> Dict:
        '''
        引当後マイナス在庫のDictを返す
        '''
        minus_inventorys: Dict = {}
        if not inspect_shipping_products:
            return minus_inventorys

        for key, inner_dic in inspect_shipping_products.items():
            if inner_dic['引当後'] < 0:
                minus_inventorys[key] = inner_dic
        return minus_inventorys

        
