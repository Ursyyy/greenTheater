import datetime

DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]
MONTH = ["", "Января", "Февряля", "Марта", "Апреля", "Мая", "Июня", "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"]
HOURS = ['10:00-11:00 (count мест свободно)', '11:00-12:00 (count)', '12:00-13:00 (count)', '13:00-14:00 (count)', '14:00-15:00 (count)', '15:00-16:00 (count)', '16:00-17:00 (count)', '17:00-18:00 (count)']
  
START_HOUR = [10, 11, 12, 13, 14, 15, 16, 17]
END_HOUR = [11, 12, 13, 14, 15, 16, 17, 18]

def getDays(maxRange:int=10) -> list:
	now = datetime.datetime.now()
	day = datetime.datetime.strptime(str(now).split()[0], '%Y-%m-%d')
	daysList = []
	if datetime.datetime.strptime('17:00:00', '%H:%M:%S').time() > now.time() and day.weekday() < 5:
		daysList.append({
			'dayName': f"{str(day.day)} {MONTH[day.month]} ({DAYS[day.weekday()]})",
			'dayStamp': str(now).split()[0]
		})
		maxRange -= 1

	for i in range(1, maxRange):
		date = now + datetime.timedelta(days=i)
		day = datetime.datetime.strptime(str(date).split()[0], '%Y-%m-%d')
		if day.weekday() >= 5: continue
		daysList.append({
			'dayName': f"{str(day.day)} {MONTH[day.month]} ({DAYS[day.weekday()]})",
			'dayStamp': str(date).split()[0]
		})
	return daysList[:5]
  
def getDay(day): 
	day = datetime.datetime.strptime(day, '%Y-%m-%d')
	return f"{str(day.day)} {MONTH[day.month]} ({DAYS[day.weekday()]})"

def getCurDay():
	now = datetime.datetime.now()
	return str(now).split('.')[0]

def getStartHours(date):
	now = datetime.datetime.now()
	if datetime.datetime.strptime(str(date).split()[0], '%Y-%m-%d') == now.time():
		print(datetime.datetime.strptime(str(date).split()[0], '%Y-%m-%d'))
		return [hour for hour in START_HOUR if datetime.datetime.strptime(f'{hour}:00:00', '%H:%M:%S').time() > now.time() ]
	return START_HOUR

def getEndHours(startHour:int):
	return [hour for hour in END_HOUR if hour > int(startHour)]



def getDaysForNotify():
	now = datetime.datetime.now()
	today = str(datetime.datetime.strptime(str(now + datetime.timedelta(days=1)).split()[0], '%Y-%m-%d')).split()[0]
	return [f"{today} 09:00:00", f"{today} 19:00:00"]

def getDayForHourNotify():
	now = str(datetime.datetime.now())
	hour = int(now.split()[1][:2])
	today = str(datetime.datetime.strptime(now.split()[0], '%Y-%m-%d')).split()[0]
	return [f'{today} {hour + 1}:00:00', f'{today} {hour + 2}:00:00']


# print(getDays())