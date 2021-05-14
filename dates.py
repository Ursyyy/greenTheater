import datetime

DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
MONTH = ["", "Января", "Февряля", "Марта", "Апреля", "Мая", "Июня", "Июля", "Августа", "Сентября", "Октября", "Ноября", "Декабря"]
HOURS = ['10:00-11:00 (count мест свободно)', '11:00-12:00 (count)', '12:00-13:00 (count)', '13:00-14:00 (count)', '14:00-15:00 (count)', '15:00-16:00 (count)', '16:00-17:00 (count)', '17:00-18:00 (count)']
  
def getDays() -> list:
    now = datetime.datetime.now()
    day = datetime.datetime.strptime(str(now).split()[0], '%Y-%m-%d')
    daysList = [{
        'dayName': f"{str(day.day)} {MONTH[day.month]} ({DAYS[day.weekday()]})",
        'dayStamp': str(now).split()[0]
    }]
    for i in range(1, 7):
        date = now + datetime.timedelta(days=i)
        day = datetime.datetime.strptime(str(date).split()[0], '%Y-%m-%d')
        daysList.append({
            'dayName': f"{str(day.day)} {MONTH[day.month]} ({DAYS[day.weekday()]})",
            'dayStamp': str(date).split()[0]
        })
    return daysList
  
def getDay(day): 
    day = datetime.datetime.strptime(day, '%Y-%m-%d')
    return f"{str(day.day)} {MONTH[day.month]} ({DAYS[day.weekday()]})"
