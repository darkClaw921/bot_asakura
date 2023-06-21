import os
import telebot
from dotenv import load_dotenv
from pprint import pprint
from chat import GPT
import workYDB
import json
#from workBitrix import *
from helper import *
from workRedis import *
from createKeyboard import *
from loguru import logger
import sys

logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")
logger.add("file_1.log", rotation="50 MB")

load_dotenv()

gpt = GPT()
GPT.set_key(os.getenv('KEY_AI'))
bot = telebot.TeleBot(os.getenv('TELEBOT_TOKEN'))
# инициализация бота и диспетчера
#dp = Dispatcher(bot)
sql = workYDB.Ydb()
#expert_promt = gpt.load_prompt('https://docs.google.com/document/d/181Q-jJpSpV0PGnGnx45zQTHlHSQxXvkpuqlKmVlHDvU/edit?usp=sharing')
#answer = gpt.answer(expert_promt, 
#           'Я хочу, чтобы после завершения обучения мне подобрали работу')
#print(answer)
#testModel = 'https://docs.google.com/document/d/1PIdVe-fmX8DtAIJOx2g65b8SGrVs30C7OGeeMFLNppk/edit?usp=sharing'


model_index = 'https://docs.google.com/document/d/1lx3cMGzSQGubG071oocgO6e1bHmu4TaXFeLRNeHu-Ow/edit?usp=sharing'
model_ind = gpt.load_search_indexes(model_index)


@bot.message_handler(commands=['addmodel'])
def add_new_model(message):
    sql.set_payload(message.chat.id, 'addmodel')
    bot.send_message(message.chat.id, 
        "Пришлите ссылку model google document и через пробел название модели (model1). Не используйте уже существующие названия модели\n Внимани! конец ссылки должен вылядить так /edit?usp=sharing",)

@bot.message_handler(commands=['addpromt'])
def add_new_model(message):
    sql.set_payload(message.chat.id, 'addpromt')
    bot.send_message(message.chat.id, 
        "Пришлите ссылку promt google document и через пробел название промта (promt1). Не используйте уже существующие названия модели\n Внимани! конец ссылки должен вылядить так /edit?usp=sharing",)
    

@bot.message_handler(commands=['help', 'start'])
def say_welcome(message):

    pprint(message.text)
    row = {'id': 'Uint64', 'MODEL_DIALOG': 'String', 'TEXT': 'String'}
    sql.create_table(str(abs(message.chat.id)), row)
    row = {'id': abs(message.chat.id), 'payload': '',}
    sql.replace_query('user', row)
    bot.send_message(abs(message.chat.id),'/allcontext очистка моделей, промта и истории\n/addmodel добавление новой модели\n/model1 - модель 1 Просто обычный чат /context сбросит контекст по текущей модели\nДоюавление моделей кроме model1 пока нельзя\n/restart перезапись главного документа', 
                     parse_mode='markdown')
#expert_promt = gpt.load_prompt('https://docs.google.com/document/d/181Q-jJpSpV0PGnGnx45zQTHlHSQxXvkpuqlKmVlHDvU/')
@bot.message_handler(commands=['allcontext'])
def send_button(message):
    #payload = sql.get_payload(message.chat.id)
    

    #answer = gpt.answer(validation_promt, context, temp = 0.1)
    #sql.delete_query(message.chat.id, f'MODEL_DIALOG = "{payload}"')
    sql.set_payload(message.chat.id, ' ')
    row = {'id': message.chat.id, 'model':'', 'promt':''}
    sql.replace_query('user', row)
    #bot.send_message(message.chat.id, answer)
    clear_history(message.chat.id)
    bot.send_message(message.chat.id, 
        "Весь контекст сброшен",)

@bot.message_handler(commands=['context'])
def send_button(message):
    #payload = sql.get_payload(message.chat.id)
    #answer = gpt.answer(validation_promt, context, temp = 0.1)
    #sql.delete_query(message.chat.id, f'MODEL_DIALOG = "{payload}"')
    #sql.set_payload(message.chat.id, ' ')
    #row = {'id': message.chat.id, 'model':'', 'promt':''}
    #sql.replace_query('user', row)
    #bot.send_message(message.chat.id, answer)
    clear_history(message.chat.id)
    bot.send_message(message.chat.id, 
        "Текущий контекст сброшен",)

@bot.message_handler(commands=['model'])
def select_model(message):
    #payload = sql.get_payload(message.chat.id)
    models= sql.get_models()
    #print(models)
    keyboard = create_keyboard_is_row(models)
    sql.set_payload(message.chat.id, 'model')
    bot.send_message(message.chat.id,'Выберите модель',reply_markup=keyboard)

@bot.message_handler(commands=['promt'])
def select_promt(message):
    #payload = sql.get_payload(message.chat.id)
    promts = sql.get_promts()
    #print(promts)
    keyboard = create_keyboard_is_row(promts)
    sql.set_payload(message.chat.id, 'promt')
    bot.send_message(message.chat.id,'Выберите промт',reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def any_message(message):
    #print('это сообщение', message)
    #text = message.text.lower()
    pprint(message)
    print(f'{message.chat.type=}')
    print(message.chat.type)
    print(f'message.from_user')
    print(f'{message=}')
    #if message.chat.type in ["group", "supergroup"] and message.from_bot:
    #    print("Сообщение было отправлено боту в группе или супергруппе")
    #bot.forward_message(chat_id''=, from_chat_id='-******', message_id='*****')
    text = message.text
    userID= abs(message.chat.id)
    #payload = sql.get_payload(userID)
    payload = '' 
    print(f'{payload=}')
    modelUrl = None
    promtUrl = None
    promt = None
    model_index = None

    #modelIndexUser = sql.get_model_for_user(userID)
    #promtUser = sql.get_promt_for_user(userID)
    #modelIndexUrl = sql.get_model_url(modelIndexUser)
    modelIndexUrl = None

    #promtUrl = sql.get_promt_url(promtUser)
    promtUrl = 'https://docs.google.com/document/d/1_6dAkz3dEBK6x30Tg33dS3wg9hOnc7I_7NK3a6HHqDs/edit?usp=sharing' 
    modelIndexUrl = 'https://docs.google.com/document/d/1chaz9Z4t6xc4cw_0LY8bhMlRMiisRW7w5Mk7GFX94yQ/edit?usp=sharing'
    #print(f'{promtUser=}')
    print(f'{promtUrl=}')

    if payload == 'addmodel':
        text = text.split(' ')
        rows = {'model': text[1], 'url': text[0] }
        sql.replace_query('model',rows)
        return 0
    
    if payload == 'addpromt':
        text = text.split(' ')
        rows = {'promt': text[1], 'url': text[0] }
        sql.replace_query('promt',rows)
        return 0
    
    if payload == 'promt':
        #promtUrl = sql.get_promt_url(text)
        sql.set_payload(message.chat.id, '')
        row = {'promt':text}
        sql.update_query('user', row, f'id={userID}')
        #sql.replace_query('user', row)
        return 0

    if payload == 'model':     
        #modelUrl = sql.get_model_url(text)
        sql.set_payload(message.chat.id, '')
        row = {'model':text}
        sql.update_query('user', row, f'id={userID}')
        #model_index=gpt.load_search_indexes(modelUrl)
        #sql.set_payload(message.chat.id, '')
        return 0
        
   
    add_message_to_history(userID, 'user', text)
    history = get_history(str(userID))
    
    logger.info(f'{promtUrl=}')
    logger.info(f'{modelIndexUrl=}')
    #print(f'{history}')
    try:
        if promtUrl is not None and modelIndexUrl is not None:
            promt = gpt.load_prompt(promtUrl)
            modelIndex = gpt.load_search_indexes(modelIndexUrl)
            answer = gpt.answer_index(promt, text, history, modelIndex)
        elif promtUrl is not None:
            print('это promt')
            promt = gpt.load_prompt(promtUrl)
            answer = gpt.answer(promt, history=history)
        elif modelIndexUrl is not None:
            modelIndex = gpt.load_prompt(modelIndexUrl)
            #modelIndex = gpt.load_search_indexes(modelIndexUrl)
            answer = gpt.answer(modelIndex, history=history)
        #bot.send_message(userID, answer)
        #return 0
    except Exception as e:
        bot.send_message(userID, e)
        bot.send_message(userID, 'начинаю sammury: ответ может занять больше времени, но не более 3х минут')
        history = get_history(str(userID))
        summaryHistory = gpt.get_summary(history)
        logger.info(f'summary истории {summaryHistory}')
        #print(f'summary: {summaryHistory}')
        logger.info(f'история до summary {history}')
        #print('история до очистки \n', history)
        #print('история summary \n', summaryHistory)
        #clear_history(userID)
        history = [summaryHistory]
        history.extend([{'role':'user', 'content': text}])
        add_old_history(userID,history)
        history = get_history(str(userID))
        logger.info(f'история после summary {history}')

        if promtUrl is not None and modelIndexUrl is not None:
            promt = gpt.load_prompt(promtUrl)
            modelIndex = gpt.load_search_indexes(modelIndexUrl)
            answer = gpt.answer_index(promt, text, history, modelIndex)
        elif promtUrl is not None:
            promt = gpt.load_prompt(promtUrl)
            answer = gpt.answer(promt, history=history)
            #answer = gpt.answer_index(promt,text, model_ind, history=history)
        elif modelIndexUrl is not None:
            modelIndex = gpt.load_prompt(modelIndexUrl)
            #modelIndex = gpt.load_search_indexes(modelIndexUrl)
            answer = gpt.answer(modelIndex, history=history)
        #bot.send_message(userID, e)
        
        #   return 0
    #bot.send_message(userID, answer)
    #answer = gpt.answer_index(promt,text, history,model_ind)
    #try:
    add_message_to_history(userID, 'assistant', answer)
    bot.send_message(message.chat.id, answer)
    #b = gpt.get_summary(history)
    #print(f'{b=}')
    #except Exception as e:
    #    bot.send_message('?')

bot.infinity_polling()
