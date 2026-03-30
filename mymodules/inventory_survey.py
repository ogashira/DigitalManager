from typing import List, Dict
import pandas as pd
from fetch_data import IFetchData
from plus_kensa_goukaku import PlusKensaGoukaku


class InventorySurvey:

    def __init__(self, 
                 instances_for_inventorySurvey: Dict[str, IFetchData],
                 plusKensaGoukaku: PlusKensaGoukaku
                 )-> None:
        
        self.plusKensaGoukaku: PlusKensaGoukaku = plusKensaGoukaku
        # 出荷予定データ
        fy: IFetchData = instances_for_inventorySurvey['fetchYotei']
        self.yotei: pd.DataFrame = fy.fetch_data()

        # 出荷処理済データ
        fus: IFetchData = instances_for_inventorySurvey['fetchUriageSumi']
        self.uriage_sumi: pd.DataFrame = fus.fetch_data()

        # 在庫データをDictにする {'S6-SV3800-U': 15, ......}
        fi: IFetchData = instances_for_inventorySurvey['fetchInventory']
        inventory: pd.DataFrame = fi.fetch_data()
        self.inventory_qty: Dict = {}
        for i in range(len(inventory)):
            if not inventory.loc[i, 'Hinban'] in self.inventory_qty:
                self.inventory_qty[inventory.loc[i, 'Hinban']] = \
                                                       inventory.loc[i, 'Qty']
                continue

            self.inventory_qty[inventory.loc[i, 'Hinban']] += \
                                                   inventory.loc[i, 'Qty']

        # 品番マスタ
        fh: IFetchData = instances_for_inventorySurvey['fetchHinban']
        self.hinban: pd.DataFrame = fh.fetch_data()
        
        # 検査日数表から検査をする品番を得る
        fip: IFetchData = instances_for_inventorySurvey['fetchInspectProducts']
        df_inspect_products = fip.fetch_data()
        self.inspect_products: List = list(set(df_inspect_products['ITEM_ID']))

        # 今日中に倉庫移動が必要な製品(検査する出荷製品)
        # self._inspect_shipping_products= 
        #         { 'S6-SV3800-U':{'出荷缶数':20, '現在庫':100, '引当後':80}, ....}
        self._inspect_shipping_products = self.calc_inspect_shipping_products()

        print('inspect_shipping_products>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print(self._inspect_shipping_products)


    def plus_kensa_goukaku(self)-> Dict:
        return self.plusKensaGoukaku.plus_goukaku(
                                              self._inspect_shipping_products)
    
    def calc_inspect_shipping_products(self)-> Dict:
        # 出荷処理していない翌日出荷製品を求める。
        if self.yotei.empty:
            dict_yotei:Dict = {}
            return dict_yotei
        merged_df = self.yotei.merge(self.uriage_sumi, 
                                     on=list(self.yotei.columns),
                                     how='left',
                                     indicator=True)
        df_filtered = merged_df[merged_df['_merge'] == 'left_only']. \
                                                    drop(columns=['_merge'])

        '''
        # TODO 後で消す 出荷処理済みを削除しないテストケース
        df_filtered = self.yotei
        '''



        # indexを振りなおす（大事)
        df_filtered = df_filtered.reset_index(drop=True)
        if df_filtered.empty:
            dict_filtered = {}
            return dict_filtered

        # 管理している品番と缶数に変更する。

            # real_hinban_dicとharikae_dicを作る
        real_hinbans: Dict = {} #{'S6-UV221-1-U': 'S6-UV221-U'.......}
        harikaes: Dict = {}     #{'S6-UV221-U: 'S6-SV3800-U'.........}
        tjus: Dict = {}         #{'S6-UV221-U': 15000,...............} 
        for i in range(len(self.hinban)):
            if self.hinban.loc[i, 'RealHinban'] != ' ':
                real_hinbans[self.hinban.loc[i, 'Hinban']] = \
                        self.hinban.loc[i, 'RealHinban'] 

            if self.hinban.loc[i, 'Harikae'] != ' ':
                harikaes[self.hinban.loc[i, 'Hinban']] = \
                        self.hinban.loc[i, 'Harikae'] 

            if self.hinban.loc[i, 'Tju'] > 0:
                tjus[self.hinban.loc[i, 'Hinban']] = \
                        self.hinban.loc[i, 'Tju'] 
            
            # dfのHinbanをRealHinbanに置き換える
        for i in range(len(df_filtered)):
            if df_filtered.loc[i, 'Hinban'] in real_hinbans:
                df_filtered.loc[i, 'Hinban'] = \
                               real_hinbans[df_filtered.loc[i, 'Hinban']]

            # dfのHinbanをharikaeに置き換える
        for i in range(len(df_filtered)):
            if df_filtered.loc[i, 'Hinban'] in harikaes:
                df_filtered.loc[i, 'Hinban'] = \
                               harikaes[df_filtered.loc[i, 'Hinban']]

        # 単位がKGだったらCNに変換する
        for i in range(len(df_filtered)):
            try:
                if df_filtered.loc[i, 'TaniCD'] == 'KG':
                    df_filtered.loc[i, 'Qty'] = \
                            df_filtered.loc[i, 'Qty'] / \
                            (tjus[df_filtered.loc[i, 'Hinban']]/1000)

                    df_filtered.loc[i, 'TaniCD'] = 'CN'
            except:
                df_filtered.loc[i, 'TaniCD'] = 'CN'

        # 検査が必要な出荷品番だけをDicに詰める
        tmp : Dict = {}
        for i in range(len(df_filtered)):
            hinban:str = df_filtered.loc[i, 'Hinban']
            Qty:int = df_filtered.loc[i, 'Qty']
            if df_filtered.loc[i, 'Hinban'] in self.inspect_products:
                tmp[hinban] = Qty

        # 出荷缶数,現在庫,引当後のdictを作る
        # {'S6-UV542-U':{'出荷缶数':20, '現在庫':35, '引当後':15}, ....}
        
        result: Dict = {}
        for key, val in tmp.items():
            #inventory_qty(現在庫)が0の製品はkeyが存在しないので、
            #inventory_qty[key]でエラーになってしまう。
            qty = 0
            if  key in self.inventory_qty:
                qty = self.inventory_qty[key]
            inner: Dict = {}
            result[key] = inner
            result[key]['出荷缶数'] = val
            result[key]['現在庫'] = qty
            result[key]['引当後'] = qty - val

        return result
    

    def txt_for_cybozu(self) -> str:
        mytxt = ''
        if not self._inspect_shipping_products:
            mytxt = '翌営業日の出荷製品は処理済みです\n'
            return mytxt

        mytxt = f'翌営業日出荷予定の製品と在庫数\n' \
                f'出荷処理済の製品は表示されません\n' \
                f'(出荷後にマイナスの製品は本日中に倉庫移動してください！)\n\n' \
                f'{self.make_txt_for_Dict_Dict(self._inspect_shipping_products)}'

        return mytxt


    def make_txt_for_Dict_Dict(self, dict_dict:Dict)-> str: 
        yoteizaiko = []
        for mykey,innerdic in dict_dict.items():
            line = f'{mykey.ljust(20)}{str(innerdic["出荷缶数"]).rjust(8)}' \
                   f'{str(innerdic["現在庫"]).rjust(8)}' \
                   f'{str(innerdic["引当後"]).rjust(8)}\n'
            yoteizaiko.append(line)

        yoteizaiko_str = ''.join(yoteizaiko)

        mytxt = f'{"品番".ljust(20)}{"出荷".rjust(4)}{"現在庫".rjust(6)}'  \
                f'{"出荷後".rjust(6)}\n{yoteizaiko_str}\n' 

        return mytxt


