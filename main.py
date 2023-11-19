#Отсутствуют комментарии к алгоритмам и к методам.
#Работу с базой данных вынести в отдельный файл.
import sqlite3
import telebot
import asyncio
import python_weather
import re

#Токен от бота должен находится в конфигурационном файле.
bot = telebot.TeleBot('5895121502:AAGadLvTk_KqEr60KBpxapyAp-lSLn7t5x0')

#Доставать не все записи из бд а с каким-либо ограничением
def data_base_check_user(registery, message):
	data_base = sqlite3.connect('WeatherBot.db')  # подключение бд
	cursorObj = data_base.cursor()
	sqlite_select_query = """SELECT * from City"""
	cursorObj.execute(sqlite_select_query)
	records = cursorObj.fetchall()
	i = 0
	for row in records:
		i+=1
		if(row[0] == message.chat.id):
			changeCity(message)
			return
	saveCity(registery, message)

#Запрос не является безопасным.
def changeCity(message):
	data_base = sqlite3.connect('WeatherBot.db')
	cursorObj = data_base.cursor()
	cursorObj.execute(f"UPDATE City SET CityUser = '{message.text}' where IdUser = '{message.chat.id}'")
	data_base.commit()

#Запрос не является безопасным.
def saveCity(registery, message):
	data_base = sqlite3.connect('WeatherBot.db')
	cursorObj = data_base.cursor()
	cursorObj.execute("INSERT INTO City(IdUser, CityUser) VALUES(?, ?)", registery)
	data_base.commit()

#Доставать не все записи из бд а с каким-либо ограничением
def returnCity(message):
	data_base = sqlite3.connect('WeatherBot.db')  
	cursorObj = data_base.cursor()
	sqlite_select_query = """SELECT * from City"""
	cursorObj.execute(sqlite_select_query)
	records = cursorObj.fetchall()
	i = 0
	for row in records:
		i+=1
		if(row[0] == message.chat.id):
			asyncio.run(giveWeather(message, row[1]))
			return
		

#Добавить несколько языков.
async def giveWeather(message, city):
	async with python_weather.Client(format=python_weather.IMPERIAL) as client:
		weather = await client.get(f"{city}")

		bot.send_message(message.chat.id, f"{weather.current.temperature}")
	  
		for forecast in weather.forecasts:
			bot.send_message(message.chat.id, f"Дата: {forecast.date}\n"
					f"Фаза луны: {forecast.astronomy.moon_phase.name}\n"
					f"Рассвет: {forecast.astronomy.sun_rise}\n"
					f"Закат: {forecast.astronomy.sun_set}\n")
	  
			day_weather = ""
			for hourly in forecast.hourly:
				day_weather += f"{hourly!r}"
			
			matches = re.findall("<HourlyForecast time=datetime.time\((.*?)\) temperature=(.*?) description='(.*?)' type=(.*?)>", day_weather)

			answer = ""
			for match in matches:
				answer += f"time: {match[0]}, temperature: {match[1]}, description: {match[2]}, type: {match[3]} \n"
			
			bot.send_message(message.chat.id, f"{answer}")


#Желатльно добавить несколько языков.
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Доброго времени суток! Напиши мне город, в котором хочешь узнать погоду: \nПример: Los Angeles")



#Маленький функционал. Неверное название у метода.
@bot.message_handler(func=lambda message: True)
def echo_message(message):
	if (message.text != 'Погода'):
		bot.send_message(message.chat.id, "Город сохранён")
		registery = (f'{message.chat.id}', f'{message.text}')
		data_base_check_user(registery, message)


	elif (message.text == 'Погода'):
		returnCity(message)


if __name__ == '__main__':
	bot.infinity_polling()