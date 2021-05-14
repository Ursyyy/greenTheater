import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import *


local = {
    'hello': "Вам потребуется для начала ввести свои данные. Отправте мне свое имя: ",
    'input_lastName': 'Введите вашу фамилию',
    'input_phone': 'Отправте номер телефона',
    'input_command': 'Отправьте название вашей команды',
    'confirm_user_data': """Ваши данные:
    Имя: firstName
    Фамилия: lastName
    Номер телефона: phone
    Команда: command""",
    'success_reg': 'Регистрация успешна',
    'smth_wrong': 'Что-то пошло не так, свяжитесь с админимтратором, чтоб узнать подробности'
} 

def UpdateLang(sheetName:str=TEXT_VARIABLES) -> dict:  
	scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
	creds = ServiceAccountCredentials.from_json_keyfile_name(PATH_TO_JSON_FILE, scope)
	client = gspread.authorize(creds)
	global local
	sheet = client.open_by_key(sheetName).get_worksheet(0)	
	langs = sheet.get_all_values()[0]
	data = sheet.get_all_values()[1:]
	for x in range(len(data)):
		valiable_name = data[x][0]
		append_data = {}
		for y in range(1,len(data[x])):
			append_data[langs[y]] = data[x][y]
		local[valiable_name] = append_data


# UpdateLang()