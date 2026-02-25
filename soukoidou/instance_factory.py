from dataclasses import dataclass
from re import I
from typing import Dict
import platform
import sys
from eigyoubi import Eigyoubi
from inventory_survey import InventorySurvey
from uninspected_products_survey import UninspectedProductsSurvey
from recorder import Recorder
from create_export_coa import CreateExportCoa
from soukoidou_check import SoukoidouCheck
from create_koito_coa import CreateKoitoCoa
from fetch_data import * 

'''
サーバーにあるsql_server.pyをモジュールとして使う
importするためにsys.path.appendでpathを認識させて
importと生成を行う
'''
shared_folder_path:str = r'./'
if platform.system() == 'Linux':
    shared_folder_path = \
            r'/mnt/public/技術課ﾌｫﾙﾀﾞ/200. effit_data/ﾏｽﾀ/sql_python_module'
elif platform.system() == 'Windows':
    shared_folder_path = \
   r'//192.168.1.247/共有/技術課ﾌｫﾙﾀﾞ/200. effit_data/ﾏｽﾀ/sql_python_module'
else:
    pass

sys.path.append(shared_folder_path)
from sql_server_tss_addmin import SqlServer as SqlServerTss # tssサーバー
from sql_server import SqlServer as SqlServerEffit  # effitAサーバー
from I_tss_coa import ITssCoa
from tss_coa_from_hs import TssCoaFromHs 
from tss_coa_from_mhs import TssCoaFromMhs 
from list_contents_of_zip_files import ListContentsOfZipFiles

class InstanceFactory:

    _instances: Dict = {}


    @classmethod
    def get_listContentsOfZipFiles(cls)->ListContentsOfZipFiles:
        return ListContentsOfZipFiles()


    @classmethod
    def get_sql_server_tss(cls)->SqlServerTss:
        return SqlServerTss()


    @classmethod
    def get_sql_server_effit(cls)-> SqlServerEffit:
        return SqlServerEffit()


    @classmethod
    def get_eigyoubi(cls, cnxn_tss)-> Eigyoubi:
        fetchHolidays: IFetchData = FetchHolidays(cnxn_tss)
        return Eigyoubi(fetchHolidays)


    @classmethod
    def get_recorder(cls, mydir:str)-> Recorder:
        ins_name:str = 'recorder'
        if not ins_name in cls._instances:
            cls._instances[ins_name] = Recorder(mydir)
        return cls._instances[ins_name]


    @classmethod
    def get_inventory_survey(cls, cnxn_tss, cnxn_effit, 
                                                    yokujitu)-> InventorySurvey:
        
        fetchYotei: IFetchData = FetchYotei(cnxn_effit, yokujitu)
        fetchUriageSumi: IFetchData = FetchUriageSumi(cnxn_effit, yokujitu)
        fetchInventory: IFetchData = FetchInventory(cnxn_effit)
        fetchHinban: IFetchData = FetchHinban(cnxn_effit)
        fetchInspectProducts: IFetchData = FetchInspectProducts(cnxn_tss)

        instances_for_inventorySurvey: Dict[str, IFetchData] = {
                                'fetchYotei': fetchYotei,
                                'fetchUriageSumi': fetchUriageSumi,
                                'fetchInventory': fetchInventory,
                                'fetchHinban': fetchHinban,
                                'fetchInspectProducts': fetchInspectProducts}

        return InventorySurvey(instances_for_inventorySurvey)


    @classmethod
    def get_uninspected_products_survey(cls, cnxn_tss)-> UninspectedProductsSurvey:
        fetchHk: IFetchData = FetchHk(cnxn_tss)
        fetchMhk: IFetchData = FetchMhk(cnxn_tss)
        return UninspectedProductsSurvey(fetchHk, fetchMhk)


    @classmethod
    def get_create_export_coa(cls, zenjitu, cnxn_tss, 
                                               six_months_ago)-> CreateExportCoa:

        @dataclass
        class ArgsForCreateExportCoa: 
            zenjitu: str
            fetch_HS_lot: IFetchData = FetchHkLot(cnxn_tss, six_months_ago) 
            fetch_MHS_lot: IFetchData = FetchMhkLot(cnxn_tss, six_months_ago)
            recorder: Recorder = cls._instances['recorder']
            tss_coa_from_hs: ITssCoa = TssCoaFromHs()
            tss_coa_from_mhs: ITssCoa = TssCoaFromMhs()
            listContentsOfZipFiles: ListContentsOfZipFiles = ListContentsOfZipFiles()
        
        args: ArgsForCreateExportCoa = ArgsForCreateExportCoa(zenjitu)

        return CreateExportCoa(args) 


    @classmethod
    def get_soukoidou_check(cls, cnxn_tss)-> SoukoidouCheck:
        return SoukoidouCheck(cnxn_tss)


    @classmethod
    def get_create_koito_coa(cls, cnxn_tss)-> CreateKoitoCoa:
        return CreateKoitoCoa(cnxn_tss)
