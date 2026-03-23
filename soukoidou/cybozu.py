import time
import configparser
from abc import ABC, abstractmethod
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from uninspected_products_survey import UninspectedProductsSurvey
from inventory_survey import InventorySurvey
from recorder import Recorder

class ICybozu(ABC):

    def __init__(self)-> None:
        config = configparser.ConfigParser()
        config.read('cybozu.ini')
        self._login_name = config['cybozu']['id']
        self._login_pass = config['cybozu']['password']

        #自動でPCのChromeと同じバージョンのdriverをインストールする処理
        service = Service(ChromeDriverManager().install())
        self._driver = webdriver.Chrome(service=service)

        self._driver.get('https://toyo-jupiter.cybozu.com/login?redirect=' 
                'https%3A%2F%2Ftoyo%2Djupiter%2Ecybozu%2Ecom%2Fo%2Fag%2Ecgi%3F')
        time.sleep(10)


        id = self._driver.find_element(By.NAME, 'username')
        id.send_keys(self._login_name)#username
        password = self._driver.find_element(By.NAME, 'password')
        password.send_keys(self._login_pass)#password
        time.sleep(1)

    # ログインボタンをクリック
        login_button = self._driver.find_element(By.CLASS_NAME, "login-button")
        login_button.click()
        time.sleep(10)

    @abstractmethod
    def put_cybozu(self)-> None:
        pass


class CybozuForSoukoidou(ICybozu):

    def __init__(self, txt)-> None:
        super().__init__()
        self._txt = txt

    def put_cybozu(self)-> None:
        
        try:
            #element = self._driver.find_element_by_xpath("//*[text()=\"品質検査管理について\"]")
            element = self._driver.find_element(By.XPATH, "//*[text()=\"soukoidou_test\"]")
            self._driver.execute_script("arguments[0].click();", element)
            koment=(self._txt)
            self._driver.find_element(By.NAME, "Data").send_keys(koment)
            time.sleep(1) 
            elem=self._driver.find_element(By.ID, "followAddButton")
            time.sleep(1) 
            elem.click()

            msg = 'サイボウズに未検査品と在庫状況をアップしました。'
            print(msg)
        except Exception as e:
            msg = 'サイボウズへのアップ失敗です。'
            print(msg)
            print(e)
        finally:
            self._driver.quit()
        

class CybozuForSoukoidou2(ICybozu):

    def __init__(self, is_soukoidou_ok: bool, recorder: Recorder)-> None:

        super().__init__()
        self._is_soukoidou_ok = is_soukoidou_ok
        self._recorder = recorder

    def put_cybozu(self)-> None:

        mytxt = '今回の倉庫移動製品です    by DM'
        what_up = 'syukko_data.csv'
        if not self._is_soukoidou_ok:
            mytxt = '今回の倉庫移動製品はありません   by DM'
            what_up = 'コメント'
        
        file=(r'\\192.168.1.247\共有\技術課ﾌｫﾙﾀﾞ\200. effit_data\syukko_data.csv')

        try:
            #element = self._driver.find_element_by_xpath("//*[text()=\"品質検査管理について\"]")
            element = self._driver.find_element(By.XPATH, "//*[text()=\"soukoidou_test\"]")
            self._driver.execute_script("arguments[0].click();", element)

            if self._is_soukoidou_ok: # 倉庫移動したならファイルを添付する
                file_choice = self._driver.find_element(By.NAME, "files[]")
                file_choice.send_keys(file)

            koment=(mytxt)
            self._driver.find_element(By.NAME, "Data").send_keys(koment)
            time.sleep(1) 
            elem=self._driver.find_element(By.ID, "followAddButton")
            time.sleep(1) 
            elem.click()
            msg = f'サイボウズに{what_up}をアップしました。'
            self._recorder.out_log(msg, '\n')
            self._recorder.out_file(msg, '\n')
        except Exception as e:
            msg = f'サイボウズへの{what_up}アップ失敗です。'
            self._recorder.out_log(msg)
            self._recorder.out_log(f'{e}', '\n')
            self._recorder.out_file(msg)
            self._recorder.out_file(f'{e}', '\n')
        finally:
            self._driver.quit()
