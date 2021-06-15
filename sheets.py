import gspread

from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient.discovery import build
from config import PATH_TO_JSON_FILE, TABLE_ID, TABLE_COUNTS

scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(PATH_TO_JSON_FILE, scope)
client = gspread.authorize(creds)



def WriteDataToSheets(sheetTitle: str, insertData: list):
	sheet = client.open_by_key(TABLE_ID)
	try:
		worksheet = sheet.worksheet(sheetTitle)
		worksheet.delete_columns(1, 5)	
		worksheet.clear()
	except Exception as e:
		print(e)
		# return
		worksheet = sheet.add_worksheet(sheetTitle, rows="50", cols="26")
	Title = ["Дата", "Время", "Кол-во забронированных столов", "Кол-во свободных столов"]
	worksheet.insert_row(Title, 1)	
	# worksheet.insert_note('A5', "Что-то там")
	for index, data in enumerate(insertData, 2):
		worksheet.insert_row(data[:-1], index)
		worksheet.insert_note(f'C{index}', data[-1])
		worksheet.add_rows(1)
	worksheet.set_basic_filter(f'A1:C{len(insertData) + 1}')

def WriteUsers(users: list):
	sheet = client.open_by_key(TABLE_ID)
	try:
		worksheet = sheet.worksheet('Пользователи')
		worksheet.clear()	
	except:
		worksheet = sheet.add_worksheet('Пользователи', rows="50", cols="26")
	Title = ["ФИО", "Название команды", "Номер телефона", "Ник в телеграме"]
	worksheet.insert_row(Title, 1)	
	for index, data in enumerate(users, 2):
		worksheet.insert_row(data, index)
		worksheet.add_rows(1)
	worksheet.set_basic_filter(f'A1:D{len(users) + 1}')
