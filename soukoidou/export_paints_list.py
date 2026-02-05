import pandas as pd
import platform

class ExportPaintsList:

    def __init__(self)-> None:
        path = r'\\192.168.1.247\Guest\輸出塗料連絡表.xlsx'
        if platform.system() == 'Linux':
            path = r'/mnt/guest/輸出塗料連絡表.xlsx'
        
        self.YTR = pd.read_excel(path, sheet_name='輸出塗料連絡表', skiprows=1)
        

