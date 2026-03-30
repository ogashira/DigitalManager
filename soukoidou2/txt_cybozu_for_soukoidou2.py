from typing import List
from mymodules.recorder import Recorder
from mymodules.cybozu import ICybozu

class TxtCybozuForSoukoidou2:

    def __init__(self, 
                 is_soukoidou_ok: bool,
                 failed_soukoidous: List[List[str]],
                 cybozuForSoukoidou2: ICybozu,
                 recorder: Recorder) -> None:

        self._is_soukoidou_ok = is_soukoidou_ok
        self._failed_soukoidous = failed_soukoidous
        self._cybozuForSoukoidou2 = cybozuForSoukoidou2
        self._recorder = recorder


    def create_txt_for_cybozuSoukoidou2(self) -> None:

        def log_cybozu_result(result)-> None:
            
            if result:
                txt = f'サイボウズにアップしました。'
            else:
                txt = 'サイボウズアップに失敗しました。'
            self._recorder.out_log(txt, '\n')
            self._recorder.out_file(txt, '\n')


        if not self._is_soukoidou_ok:
            txt = '今回の倉庫移動製品はありません   by DM'
            self._recorder.out_log(txt, '\n')
            self._recorder.out_file(txt, '\n')
            return 

        if self._failed_soukoidous:
            txt1: str = '今回の倉庫移動製品です   by DM \n' \
                       '以下の製品が倉庫移動に失敗しています。\n'
            txt2 = self._recorder.out_txt_from_list_list(self._failed_soukoidous)
            txt = txt1 + txt2 + '\n'
            result = self._cybozuForSoukoidou2.put_cybozu(txt)

            log1 = '倉庫移動行いましたが、以下の製品が倉庫移動失敗です'  
            log = log1 + txt2 
            self._recorder.out_log(log, '\n')
            self._recorder.out_file(log, '\n')

            log_cybozu_result(result)
            return

        if not self._failed_soukoidous:
            txt: str = '今回の倉庫移動製品です   by DM \n' 
            result  = self._cybozuForSoukoidou2.put_cybozu(txt)

            log = '倉庫移動行いました'
            self._recorder.out_log(log, '\n')
            self._recorder.out_file(log, '\n')

            log_cybozu_result(result)
            return
