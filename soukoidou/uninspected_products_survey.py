import pandas as pd
from fetch_data import IFetchData

class UninspectedProductsSurvey:
    def __init__(self, hk:IFetchData, mhk:IFetchData)-> None:

        self.df_hk: pd.DataFrame = hk.fetch_data()
        self.df_mhk: pd.DataFrame = mhk.fetch_data()


    def txt_for_cybozu(self)-> str:
        hs = []
        for row in self.df_hk.itertuples(index=False):
            line = f'{str(row.Hinban).ljust(20)}{str(row.LOT).rjust(14)}' \
                   f'{str(row.Cans).rjust(6)}' \
                   f'{str(row.User).rjust(8)}\n'
            hs.append(line)

        hs_str = ''.join(hs)

        mhs = []
        for row in self.df_mhk.itertuples(index=False):
            line = f'{str(row.Hinban).ljust(20)}{str(row.LOT).rjust(14)}' \
                   f'{str(row.Cans).rjust(6)}\n' 
            mhs.append(line)

        mhs_str = ''.join(mhs)

        mytxt = f'検査未完了の製品\n\n' \
                f'(品質管理)\n' \
                f'{hs_str}' \
                f'------------------------------------------------\n' \
                f'(メタル品質管理)\n' \
                f'{mhs_str}\n' 

        return mytxt
