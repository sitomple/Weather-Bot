import sqlite3
import telebot
import asyncio
import python_weather

bot = telebot.TeleBot('5895121502:AAGadLvTk_KqEr60KBpxapyAp-lSLn7t5x0')



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


def changeCity(message):
	data_base = sqlite3.connect('WeatherBot.db')  # подключение бд
	cursorObj = data_base.cursor()
	cursorObj.execute(f"UPDATE City SET CityUser = '{message.text}' where IdUser = '{message.chat.id}'")
	data_base.commit()


def saveCity(registery, message):
	data_base = sqlite3.connect('WeatherBot.db')  # подключение бд
	cursorObj = data_base.cursor()
	cursorObj.execute("INSERT INTO City(IdUser, CityUser) VALUES(?, ?)", registery)
	data_base.commit()




def returnCity(message):
	data_base = sqlite3.connect('WeatherBot.db')  # подключение бд
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


async def giveWeather(message, city):
	async with python_weather.Client(format=python_weather.IMPERIAL) as client:

	    # fetch a weather forecast from a city
		weather = await client.get(f"{city}")


	    # returns the current day's forecast temperature (int)
		bot.send_message(message.chat.id, f"{weather.current.temperature}")
	  
	    # get the weather forecast for a few days
		for forecast in weather.forecasts:
			bot.send_message(message.chat.id, f"{forecast.date} {forecast.astronomy}")
	  
	      # hourly forecasts
			for hourly in forecast.hourly:
				bot.send_message(message.chat.id, f"{hourly!r}")



@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hello! Please send me your city: \nExample: Los Angeles")




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



