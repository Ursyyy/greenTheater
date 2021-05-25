# Aiogram bot

## Установка python
Для корректной работы работы бота необходимо установить python3.7 и несколько модулей с помощью pip 

Установим python версии 3.7 и pip

```bash
sudo apt update
sudo apt install python3.7
sudo apt install python3-setuptools
sudo apt install python3-pip
apt install mysql-server
```

Далее установим необходимые библиотеки

```bash
pip3 install aiogram gspread oauth2client mysql-connector aiocron xlsxwriter
```

## Запуск

Переходим к настройке systemd. Для этого переходим в его директорию:
```bash
cd /etc/systemd/system
```
И создаём файл bot.service:
```bash
sudo nano bot.service
```
Вписываем в открывшиеся окно следующее:
```bash
[Unit]
Description=Telegram bot 'Bot name'
After=syslog.target
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/название пользователя/название папки в которой лежит бот
ExecStart=/usr/bin/python3 /home/название пользователя/название папки в которой лежит бот/main.py

RestartSec=10
Restart=always

[Install]
WantedBy=multi-user.target
```
Закрываем и соханяем файл. После этого вводим команды:
```bash
sudo systemctl daemon-reload
sudo systemctl enable bot
sudo systemctl start bot
sudo systemctl status bot
```
Теперь бот работает самостоятельно.
