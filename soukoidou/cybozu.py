import time
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


def put_cybozu(mytxt):

    # driver = webdriver.Chrome(executable_path=r"C:/MyPythonScripts/soukoidou/chromedriver.exe")#driverpath
    #自動でPCのChromeと同じバージョンのdriverをインストールする処理
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    driver.get('https://toyo-jupiter.cybozu.com/login?redirect=https%3A%2F%2Ftoyo%2Djupiter%2Ecybozu%2Ecom%2Fo%2Fag%2Ecgi%3F')
    time.sleep(10)



    id = driver.find_element(By.NAME, 'username')
    id.send_keys('oga')#username
    password = driver.find_element(By.NAME, 'password')
    password.send_keys('aqaq')#password
    time.sleep(1)

# ログインボタンをクリック
    login_button = driver.find_element(By.CLASS_NAME, "login-button")
    login_button.click()
    time.sleep(10)




#element=driver.find_element_by_link_text("個人フォルダ")

#element.click()



#ページをスクロールせずともクリック出来た！
    #element = driver.find_element_by_xpath("//*[text()=\"品質検査管理について\"]")
    element = driver.find_element(By.XPATH, "//*[text()=\"soukoidou_test\"]")
    driver.execute_script("arguments[0].click();", element)


#添付ﾌｧｲﾙのpathを入れる
    file=()




    if file==():
        koment=(mytxt)
        driver.find_element(By.NAME, "Data").send_keys(koment)
        time.sleep(1) 
        elem=driver.find_element(By.ID, "followAddButton")
        time.sleep(1) 
        elem.click()
        
    else:
        file_choice = driver.find_element(By.NAME, "files[]")
        file_choice.send_keys(file)
        #now_upload = driver.find_element_by_class_name("fileformInput")
        #now_upload.click()
        koment=("hello world")
        driver.find_element(By.NAME, "Data").send_keys(koment)
        time.sleep(1) 
        elem=driver.find_element(By.ID, "followAddButton")
        time.sleep(1) 
        elem.click()

    driver.quit()
    
