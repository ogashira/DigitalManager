import pandas as pd
from typing import Dict, List
from fetch_data import IFetchData
from recorder import Recorder


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
                 fetch_MHK_notSumi: IFetchData,
                 recorder: Recorder)-> None:
    
        self._recorder = recorder
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

        # 合格で済ではない品番とlotを表示する
        self._show_nonSumi(HK_nonSumi, MHK_nonSumi)


    def _show_nonSumi(self, HK_nonSumi, MHK_nonSumi)-> None:
        def make_list(df)-> List:
            toList: List[List[str]] = []
            if df.empty:
                return toList
            for _, row in df.iterrows():
                line:List[str] = [row['Hinban'], row['LOT']]
                toList.append(line)
            
            return toList

        list_HK = make_list(HK_nonSumi)
        list_MHK = make_list(MHK_nonSumi)

        list_HK_MHK = list_HK + list_MHK
        out_txt = self._recorder.out_txt_from_list_list(list_HK_MHK)

        txt = '(倉庫移動する製品)\n'
        out_txt = txt + out_txt
        self._recorder.out_log(out_txt, '\n')
        self._recorder.out_file(out_txt, '\n')


    def ask_is_exists_nonSumis(self)->bool:
        is_exists_nonSumis:bool = False
        if self._nonSumis:
            is_exists_nonSumis = True
        return is_exists_nonSumis


    def plus_goukaku(self, inspect_shipping_products:Dict)-> Dict:
        '''
        inspect_shipping_productsを受け取って、その引当後の数に
        合格品で済になっていない品番の数を加算する
        '''
        if not inspect_shipping_products:
            return  inspect_shipping_products
        
        for key, inner_dic in inspect_shipping_products.items():
            if key in self._nonSumis:
                inner_dic['引当後'] = inner_dic['引当後'] + self._nonSumis[key]
        
        return  inspect_shipping_products
