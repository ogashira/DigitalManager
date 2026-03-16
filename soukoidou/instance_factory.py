from dataclasses import dataclass
from typing import Dict, TYPE_CHECKING, Any
import platform
import sys
from fetch_data import IFetchData

# 実行時にはインポートせず、型チェックの為だけに書く
if TYPE_CHECKING:
    from eigyoubi import Eigyoubi
    from inventory_survey import InventorySurvey
    from uninspected_products_survey import UninspectedProductsSurvey
    from create_export_coa import CreateExportCoa
    from soukoidou_check import SoukoidouCheck
    from create_koito_coa import CreateKoitoCoa
    from ab_test_check import ABTestCheck
    from plus_kensa_goukaku import PlusKensaGoukaku

class InstanceFactory:
    '''
    各モジュールのインポートは必要な時にメソッド内で行う。
    冒頭でまとめてやると実行速度が急激に遅くなったため
    '''

    _sqlServerTss: Any = None
    _sqlServerEffit: Any = None
    _cnxn_tss = None
    _cnxn_effit = None

    _instances: Dict[str, Any] = {}

    @classmethod
    def _setup_sql_path(cls) -> None:
        """SQLサーバー用モジュールのパスを通す (一度だけ実行)"""
        if 'sql_path_setup' in cls._instances:
            return
            
        shared_folder_path: str = r'./'
        if platform.system() == 'Linux':
            shared_folder_path = \
                r'/mnt/public/技術課ﾌｫﾙﾀﾞ/200. effit_data/ﾏｽﾀ/sql_python_module'
        elif platform.system() == 'Windows':
            shared_folder_path = \
                r'//192.168.1.247/共有/技術課ﾌｫﾙﾀﾞ/200. effit_data/ﾏｽﾀ/sql_python_module'
        
        if shared_folder_path not in sys.path:
            sys.path.append(shared_folder_path)
        cls._instances['sql_path_setup'] = True

    @classmethod
    def get_sql_server_tss(cls) -> None:
        if cls._sqlServerTss is None:
            cls._setup_sql_path()
            from sql_server_tss_addmin import SqlServer as SqlServerTss
            cls._sqlServerTss = SqlServerTss()
            cls._cnxn_tss = cls._sqlServerTss.get_cnxn()

    @classmethod
    def get_sql_server_effit(cls) -> None:
        if cls._sqlServerEffit is None:
            cls._setup_sql_path()
            from sql_server import SqlServer as SqlServerEffit
            cls._sqlServerEffit = SqlServerEffit()
            cls._cnxn_effit = cls._sqlServerEffit.get_cnxn()

    @classmethod
    def delete_cnxn(cls) -> None:
        if cls._sqlServerTss:
            cls._sqlServerTss.close()
        if cls._sqlServerEffit:
            cls._sqlServerEffit.close()

    @classmethod
    def get_fetchHolidays(cls) -> IFetchData:
        from fetch_data import FetchHolidays
        ins_name: str = 'fetchHolidays'
        if ins_name not in cls._instances:
            cls.get_sql_server_tss()
            cls._instances[ins_name] = FetchHolidays(cls._cnxn_tss)
        return cls._instances[ins_name]

    @classmethod
    def get_fetchYotei(cls, yokujitu) -> IFetchData:
        from fetch_data import FetchYotei
        ins_name: str = 'fetchYotei'
        if ins_name not in cls._instances:
            cls.get_sql_server_effit()
            cls._instances[ins_name] = FetchYotei(cls._cnxn_effit, yokujitu)
        return cls._instances[ins_name]

    @classmethod
    def get_fetchUriageSumi(cls, yokujitu) -> IFetchData:
        from fetch_data import FetchUriageSumi
        ins_name: str = 'fetchUriageSumi'
        if ins_name not in cls._instances:
            cls.get_sql_server_effit()
            cls._instances[ins_name] = FetchUriageSumi(cls._cnxn_effit, yokujitu)
        return cls._instances[ins_name]

    @classmethod
    def get_fetchInventory(cls) -> IFetchData:
        from fetch_data import FetchInventory
        ins_name: str = 'fetchInventory'
        if ins_name not in cls._instances:
            cls.get_sql_server_effit()
            cls._instances[ins_name] = FetchInventory(cls._cnxn_effit)
        return cls._instances[ins_name]

    @classmethod
    def get_fetchHinban(cls) -> IFetchData:
        from fetch_data import FetchHinban
        ins_name: str = 'fetchHinban'
        if ins_name not in cls._instances:
            cls.get_sql_server_effit()
            cls._instances[ins_name] = FetchHinban(cls._cnxn_effit)
        return cls._instances[ins_name]

    @classmethod
    def get_fetchInspectProducts(cls) -> IFetchData:
        from fetch_data import FetchInspectProducts
        ins_name: str = 'fetchInspectProducts'
        if ins_name not in cls._instances:
            cls.get_sql_server_tss()
            cls._instances[ins_name] = FetchInspectProducts(cls._cnxn_tss)
        return cls._instances[ins_name]

    @classmethod
    def get_fetchHk(cls) -> IFetchData:
        from fetch_data import FetchHk
        ins_name: str = 'fetchHk'
        if ins_name not in cls._instances:
            cls.get_sql_server_tss()
            cls._instances[ins_name] = FetchHk(cls._cnxn_tss)
        return cls._instances[ins_name]

    @classmethod
    def get_fetchMhk(cls) -> IFetchData:
        from fetch_data import FetchMhk
        ins_name: str = 'fetchMhk'
        if ins_name not in cls._instances:
            cls.get_sql_server_tss()
            cls._instances[ins_name] = FetchMhk(cls._cnxn_tss)
        return cls._instances[ins_name]

    @classmethod
    def get_fetch_HS_lot(cls, six_months_ago) -> IFetchData:
        from fetch_data import FetchHkLot
        ins_name: str = 'fetch_HS_lot'
        if ins_name not in cls._instances:
            cls.get_sql_server_tss()
            cls._instances[ins_name] = FetchHkLot(cls._cnxn_tss, six_months_ago)
        return cls._instances[ins_name]

    @classmethod
    def get_fetch_MHS_lot(cls, six_months_ago) -> IFetchData:
        from fetch_data import FetchMhkLot
        ins_name: str = 'fetch_MHS_lot'
        if ins_name not in cls._instances:
            cls.get_sql_server_tss()
            cls._instances[ins_name] = FetchMhkLot(cls._cnxn_tss, six_months_ago)
        return cls._instances[ins_name]

    @classmethod
    def get_fetch_HK_notSumi(cls) -> IFetchData:
        from fetch_data import FetchHkNotSumi
        ins_name: str = 'fetch_HK_notSumi'
        if ins_name not in cls._instances:
            cls.get_sql_server_tss()
            cls._instances[ins_name] = FetchHkNotSumi(cls._cnxn_tss)
        return cls._instances[ins_name]

    @classmethod
    def get_fetch_koito_kensa(cls) -> IFetchData:
        from fetch_data import FetchKoitoKensa
        ins_name: str = 'fetch_koito_kensa'
        if ins_name not in cls._instances:
            cls.get_sql_server_tss()
            cls._instances[ins_name] = FetchKoitoKensa(cls._cnxn_tss)
        return cls._instances[ins_name]

    @classmethod
    def get_fetch_MHK_notSumi(cls) -> IFetchData:
        from fetch_data import FetchMhkNotSumi
        ins_name: str = 'fetch_MHK_notSumi'
        if ins_name not in cls._instances:
            cls.get_sql_server_tss()
            cls._instances[ins_name] = FetchMhkNotSumi(cls._cnxn_tss)
        return cls._instances[ins_name]

    @classmethod
    def get_listContentsOfZipFiles(cls):
        from list_contents_of_zip_files import ListContentsOfZipFiles
        return ListContentsOfZipFiles()

    @classmethod
    def get_eigyoubi(cls) -> "Eigyoubi":
        from eigyoubi import Eigyoubi
        fetchHolidays = cls.get_fetchHolidays()
        return Eigyoubi(fetchHolidays)

    @classmethod
    def get_recorder(cls, mydir: str) -> "Recorder":
        from recorder import Recorder
        ins_name: str = 'recorder'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = Recorder(mydir)
        return cls._instances[ins_name]


    @classmethod
    def get_plus_kensa_goukaku(cls) -> "PlusKensaGoukaku":
        from plus_kensa_goukaku import PlusKensaGoukaku
        fetchHKnotSumi = cls.get_fetch_HK_notSumi()
        fetchMHKnotSumi = cls.get_fetch_MHK_notSumi()
        ins_name: str = 'plus_kensa_goukaku'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = PlusKensaGoukaku(
                                                        fetchHKnotSumi,
                                                        fetchMHKnotSumi
                                                       )
        return cls._instances[ins_name]


    @classmethod
    def get_inventory_survey(cls, yokujitu) -> "InventorySurvey":
        from inventory_survey import InventorySurvey
        ins_name: str = 'inventory_survey'
        if ins_name not in cls._instances:
            instances_for_inventorySurvey: Dict[str, IFetchData] = {
                'fetchYotei': cls.get_fetchYotei(yokujitu),
                'fetchUriageSumi': cls.get_fetchUriageSumi(yokujitu),
                'fetchInventory': cls.get_fetchInventory(),
                'fetchHinban': cls.get_fetchHinban(),
                'fetchInspectProducts': cls.get_fetchInspectProducts()
            }
            plusKensaGoukaku = cls.get_plus_kensa_goukaku()
            
            cls._instances[ins_name] = InventorySurvey(
                                    instances_for_inventorySurvey,
                                    plusKensaGoukaku
                                    )
        return cls._instances[ins_name]


    @classmethod
    def get_uninspected_products_survey(cls) -> "UninspectedProductsSurvey":
        from uninspected_products_survey import UninspectedProductsSurvey
        fetchHk = cls.get_fetchHk()
        fetchMhk = cls.get_fetchMhk()
        return UninspectedProductsSurvey(fetchHk, fetchMhk)

    @classmethod
    def get_create_export_coa(cls, zenjitu, six_months_ago) -> "CreateExportCoa":
        from create_export_coa import CreateExportCoa
        from I_tss_coa import ITssCoa
        from tss_coa_from_hs import TssCoaFromHs 
        from tss_coa_from_mhs import TssCoaFromMhs 
        from list_contents_of_zip_files import ListContentsOfZipFiles
        from recorder import Recorder

        @dataclass
        class ArgsForCreateExportCoa: 
            zenjitu: str
            fetch_HS_lot: IFetchData = cls.get_fetch_HS_lot(six_months_ago) 
            fetch_MHS_lot: IFetchData = cls.get_fetch_MHS_lot(six_months_ago)
            tss_coa_from_hs: ITssCoa = TssCoaFromHs()
            tss_coa_from_mhs: ITssCoa = TssCoaFromMhs()
            listContentsOfZipFiles: ListContentsOfZipFiles = \
                                                    ListContentsOfZipFiles()
            recorder: Recorder = cls._instances['recorder']
        
        args = ArgsForCreateExportCoa(zenjitu)
        return CreateExportCoa(args) 

    @classmethod
    def get_soukoidou_check(cls, yokujitu) -> "SoukoidouCheck":
        from soukoidou_check import SoukoidouCheck
        inventorySurvey = cls.get_inventory_survey(yokujitu)
        abTestCheck = cls.get_ab_test_check()
        recorder = cls._instances['recorder']
        
        return SoukoidouCheck(inventorySurvey, abTestCheck, recorder)

    @classmethod
    def get_create_koito_coa(cls) -> "CreateKoitoCoa":
        from create_koito_coa import CreateKoitoCoa
        from I_tss_coa import ITssCoa
        from tss_coa_from_hs import TssCoaFromHs 
        tssCoaFromHs: ITssCoa = TssCoaFromHs()
        ins_name = 'create_koito_coa'
        if ins_name not in cls._instances: 
            cls._instances[ins_name] = \
                    CreateKoitoCoa(tssCoaFromHs, cls._instances['recorder'])
        return cls._instances[ins_name]

    @classmethod
    def get_ab_test_check(cls) -> "ABTestCheck":
        from ab_test_check import ABTestCheck
        fetchKoitoKensa: IFetchData = cls.get_fetch_koito_kensa()
        createKoitoCoa = cls.get_create_koito_coa()
        ins_name = 'ab_test_check'
        if ins_name not in cls._instances:
            cls._instances[ins_name] = ABTestCheck(fetchKoitoKensa,
                                                   createKoitoCoa,
                                                   cls._instances['recorder'])

        return cls._instances[ins_name]
