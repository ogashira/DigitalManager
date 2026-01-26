import re, csv, pickle
from tani import Tani
from zaiko import Zaiko
from sql_server import *

class Yotei:

    def __init__(self, yokujitu, henkou=False):
        self.yokujitu = yokujitu
        
        if henkou == True:
            yotei_csv = open(r'\\192.168.1.247\共有\技術課ﾌｫﾙﾀﾞ\200. effit_data\yotei.csv','r')
            reader = csv.reader(yotei_csv)
            reader = list(reader)
            yotei_csv.close()
        else:
            sql = SqlServer()
            yotei_df = sql.get_yotei(self.yokujitu)
            yotei_df = yotei_df.fillna('')
            
            col = list(yotei_df.columns)

            yotei_l = yotei_df.values.tolist()
            yotei_l.insert(0, col)
            yotei_l.insert(0, ['yotei.csv'])

            reader = yotei_l.copy() 

        
            out_file = open(r'\\192.168.1.247\共有\技術課ﾌｫﾙﾀﾞ\200. effit_data\yotei.csv', 'w',newline='')
            out_writer = csv.writer(out_file)
            for row in reader:
                out_writer.writerow(row)

            out_file.close()
        

        regex = re.compile(r'^T[012345]')
        regex2 = re.compile(r'^S1-|S2-|S3-|S4-|S5-|S6-|S7-|S8-|S9-|S10-HBLU680|S10-P2|S10-P3|S10-P4|S11-')
        
        self.yotei_rows = []
        for row in reader:
            if re.search(regex,row[0]) and re.search(regex2,row[5]):
                self.yotei_rows.append(row)
                

        tani = Tani()
        self.tani_data = tani.get_tani()

        zaiko = Zaiko()
        self.zaiko_data = zaiko.get_zaiko()



        def cng_ex(mykey):
            regex = re.compile(r'-EX-.*$')
            mo = regex.search(mykey)
            if mo:
                oldkey = mo.group()
                newkey = mykey.replace(oldkey, '-EX')
            else:
                newkey = mykey
            return newkey   
        

        def cng_harikae(mykey):
            if mykey=='S6-UV355-U':
                newkey = 'S6-SV450036-U'
            elif mykey == 'S9-GH200-TH':
                newkey = 'S9-U100-TH'
            elif mykey =='S6-UV221':
                newkey = 'S6-SV3800-U'
            elif mykey == 'S9-K560-TH':
                newkey = 'S9-U330-TH'
            else:
                newkey = mykey
            
            return newkey
            





        #yotei_rowsをDICにする
        self.yotei_dic = {}
        for cnt in range(0, len(self.yotei_rows)):
            kansuu = int(float(str(self.yotei_rows[cnt][7]).replace(',','')))
            setkey =self.yotei_rows[cnt][5]
            if setkey not in self.yotei_dic:
                self.yotei_dic[setkey] = [kansuu,self.yotei_rows[cnt][8]]
            else:
                self.yotei_dic[setkey] = [self.yotei_dic[setkey][0] + kansuu, self.yotei_rows[cnt][8]]




        # KGなら、重量を入れ目で割る、'KG→CN'にして'-1-'を'-'にする
        #{S6-SV3800-U:[7,'KG→'CN']} になる。7はCN(缶)
        self.yotei_data = {}
        for mykey,cans in self.yotei_dic.items():
            mykey = cng_harikae(mykey) #mykeyをcng_harikaeに渡してﾗﾍﾞﾙ張替製品の元品番を獲得する。
            mykey = cng_ex(mykey) #mykeyを関数cng_ex()に渡して'-EX'の後の文字を削除する。
            if cans[1] == 'KG':
                setkey = mykey.replace('-1-','-')
                ireme = self.tani_data[setkey][0] #taniﾃﾞｰﾀから入れ目を取得する
                can = 'KG→CN'
                kansuu = cans[0]/ireme
                kansuu = int(kansuu)
            else:
                setkey = mykey
                can = cans[1]
                kansuu = cans[0]
            if setkey not in self.yotei_data:
                self.yotei_data[setkey] = [kansuu, can]
            else:
                self.yotei_data[setkey] = [self.yotei_data[setkey][0]+kansuu, self.yotei_data[setkey][1]+can]
            

        #現在庫から引く
        self.yotei_zaiko = {}
        for mykey,cans in self.yotei_data.items():
            zaikosuu = self.zaiko_data.get(mykey, 0)
            yoteisuu = cans[0]
            zaiko_zan = zaikosuu - yoteisuu
            self.yotei_zaiko[mykey] = [zaiko_zan, cans[1]]

        pickle.dump(self.yotei_zaiko, open(r'C:\MyPythonScripts\soukoidou\yoteizaiko.dump' , 'wb')) 
    
        
        
    def get_yoteidata(self):
        return self.yotei_data #-1-→-　kg→cn　など
        
    def get_yoteidic(self):
        return self.yotei_dic #予定をdicにしたもの

    def get_yotei_zaiko(self):
        return self.yotei_zaiko #　現在庫から出荷予定数を引いたもの
    
    def get_zaiko_data(self):
        return self.zaiko_data  #Zaikoｸﾗｽから持ってきた現在庫ﾃﾞｰﾀ











    
