import sys
import os
from pathlib import Path
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

from recorder import Recorder

class ICybozu(ABC):

    def __init__(self)-> None:

        if getattr(sys, 'frozen', False):
            # PyInstallerでexe化された場合、EXEがあるフォルダを起点にする
            base_dir = os.path.dirname(sys.executable)
        else:
            # 開発時（通常のPython実行）
            # ~/projects/DigitalManager/mymodules/cybozu.py の 2つ上のディレクトリ
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        INI_PATH = os.path.join(base_dir, "cybozu_ini", "cybozu.ini")

        config = configparser.ConfigParser()
        config.read(INI_PATH)
        
        if 'cybozu' not in config:
            raise FileNotFoundError(f"設定ファイルが見つからないか、形式が正しくありません: {INI_PATH}")

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
    def put_cybozu(self, txt)-> bool:
        pass


class CybozuForSoukoidou(ICybozu):

    def __init__(self)-> None:
        super().__init__()


    def put_cybozu(self, txt)-> bool:
        
        try:
            element = self._driver.find_element(By.XPATH, "//*[text()=\"品質検査管理について\"]")
            #element = self._driver.find_element(By.XPATH, "//*[text()=\"soukoidou_test\"]")
            self._driver.execute_script("arguments[0].click();", element)
            koment=(txt)
            self._driver.find_element(By.NAME, "Data").send_keys(koment)
            time.sleep(1) 
            elem=self._driver.find_element(By.ID, "followAddButton")
            time.sleep(1) 
            elem.click()
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            self._driver.quit()
        

class CybozuForSoukoidou2(ICybozu):

    def __init__(self)-> None:

        super().__init__()

    def put_cybozu(self, txt)-> bool:

        file=(r'\\192.168.1.247\共有\技術課ﾌｫﾙﾀﾞ\200. effit_data\syukko_data.csv')

        try:
            element = self._driver.find_element(By.XPATH, "//*[text()=\"倉庫移動お知らせ\"]")
            #element = self._driver.find_element(By.XPATH, "//*[text()=\"soukoidou_test\"]")
            self._driver.execute_script("arguments[0].click();", element)

            file_choice = self._driver.find_element(By.NAME, "files[]")
            file_choice.send_keys(file)

            koment=(txt)
            self._driver.find_element(By.NAME, "Data").send_keys(koment)
            time.sleep(1) 
            elem=self._driver.find_element(By.ID, "followAddButton")
            time.sleep(1) 
            elem.click()
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            self._driver.quit()
