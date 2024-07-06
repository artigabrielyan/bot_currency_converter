import telebot
from currency_converter import CurrencyConverter
from telebot import types
import math


token = '7213524823:AAFG7o6l1bPjUAO8H1UPbAUPh5LvFM1h9Wk'
bot = telebot.TeleBot(token)
currency = CurrencyConverter()
amount = 0

@bot.message_handler(commands=['start'])
def start(message):
    '''Функция - start'''
    bot.send_message(message.chat.id, f'Здравствуйте!'
                                      f'\nВведите сумму для конвертации.')
    bot.register_next_step_handler(message, summa_num)

def summa_num(message):
    '''Функция создающая вспомогательные кнопки для конвертации'''
    global amount
    amount = message.text.strip()
    if message.text.strip()[0] == '-' and message.text.strip()[1:].isdigit():
        bot.send_message(message.chat.id, 'Введено отрицательное число! Повторите попытку.')
        bot.register_next_step_handler(message, summa_num)
    elif message.text.strip() == '0':
        bot.send_message(message.chat.id, 'Введено значение ноль! Повторите попытку.')
        bot.register_next_step_handler(message, summa_num)
    elif not amount.isdigit():
        bot.send_message(message.chat.id, 'Введен неверный формат числа! Повторите попытку.')
        bot.register_next_step_handler(message, summa_num)
    else:
        amount = int(message.text.strip())
        markup = types.InlineKeyboardMarkup()
        bt1 = types.InlineKeyboardButton('USD/EUR', callback_data='USD/EUR')
        bt2 = types.InlineKeyboardButton('EUR/USD', callback_data='EUR/USD')
        bt3 = types.InlineKeyboardButton('RUB/USD', callback_data='RUB/USD')
        bt4 = types.InlineKeyboardButton('RUB/EUR', callback_data='RUB/EUR')
        bt5 = types.InlineKeyboardButton('Другая валютная пара', callback_data='else')
        markup.row(bt1, bt2)
        markup.row(bt3, bt4)
        markup.row(bt5)
        bot.send_message(message.chat.id, 'Выберите пару валют', reply_markup=markup)

def round_small_num(num, digits=2):
    '''Функция для корректного округления чисел меньше 1'''
    scale = int(-math.floor(math.log10(abs(num - int(num))))) + digits - 1
    if scale < digits:
        scale = digits
    return round(num, scale)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    '''Функция, выполняющая конвертацию валюты'''
    if call.data != 'else':
        values = call.data.split('/')
        result = currency.convert(amount, values[0], values[1])
        if result > 1:
            result = round(result, 1)
        else:
            result = round_small_num(result)
        bot.send_message(call.message.chat.id, f'Результат: {result}.\nВведите следующую сумму для конвертации.')
        bot.register_next_step_handler(call.message, summa_num)
    else:
        bot.send_message(call.message.chat.id, 'Введите валютную пару через слэш, как в примере выше')
        bot.register_next_step_handler(call.message, different_callback)


def different_callback(message):
    '''Функция, конвертирующая валюту из валютной пары, задаваемой пользователем'''
    try:
        values = message.text.upper().split('/')
        result = currency.convert(amount, values[0], values[1])
        if result > 1:
            result = round(result, 1)
        else:
            result = round_small_num(result)
        bot.send_message(message.chat.id, f'Результат: {result}.\nВведите следующую сумму для конвертации.')
        bot.register_next_step_handler(message, summa_num)
    except Exception:
        bot.send_message(message.chat.id, f'Ощибка ввода. Введите корректное значение.'
                                                f'\nПример: USD/EUR - Перевод долларов в евро')
        bot.register_next_step_handler(message, different_callback)


if __name__ == '__main__':
    bot.infinity_polling()