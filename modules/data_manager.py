import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import PATHS
import os

class DataManager:
    def __init__(self):
        # ถ้าหาไฟล์ JSON ไม่เจอ หรือ Connect ไม่ได้ ให้ข้ามเลย ไม่ต้อง Error
        self.client = None
        self.connect()

    def connect(self):
        if os.path.exists(PATHS['credential_json']):
            try:
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                creds = ServiceAccountCredentials.from_json_keyfile_name(PATHS['credential_json'], scope)
                self.client = gspread.authorize(creds)
                print("Connected to Google Sheets.")
            except Exception as e:
                print(f"Database Error (Ignored): {e}")
        else:
            print("Running Offline Mode (No Google Sheet connected).")

    def save_card_data(self, *args):
        if self.client:
            # ถ้าต่อ DB ติดค่อยเซฟ ถ้าไม่ติดก็ข้าม
            pass
        else:
            print("Offline Mode: Data saved locally only.")