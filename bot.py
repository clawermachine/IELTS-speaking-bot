import asyncio, os
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import FSInputFile, BotCommand
from aiogram.filters.command import Command
from aiogram.methods import DeleteWebhook
import t2s, s2t, gpt
from emoji import emojize
from random import choice

with open('tg_api.txt', 'r') as tg_api:
    token = tg_api.readline()

assert token != 'None', "Don't forget to provide you TG bot token in 'tg_api.txt'"

topics = ['animals', 'cars', 'science', 'people']
topic = choice(topics)

bot = Bot(token)                    # Объект бота с токеном
dp = Dispatcher()                   # Диспетчер для бота
    
#model_t2s, speaker = t2s.t2s_init() # запускаем модель Silero
#model_s2t, Fs = s2t.s2t_init()      # запускаем модель Vosk
#client_gpt, history = gpt.gpt_init(topic) # проверяем готовность GPT

    
# Создаем меню
async def set_main_menu(bot: Bot):
    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/chat',
                   description=emojize(':robot:') + ' Have a voice chat with AI'),
        BotCommand(command='/record',
                   description=emojize(':microphone:') + ' Record your speech on a topic'),
        BotCommand(command='/listen',
                   description=emojize(':headphone:') + ' Listen your records on a topic')]

    await bot.set_my_commands(main_menu_commands)

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer('Hello! I am here to help you improve your conversation skills.\nYou can have a live voice conversation with a LLM or record and listen your single speeches.\nAll based on IELTS topics.')

# Хэндлер на команду /record
@dp.message(Command("record"))
async def cmd_chat(message: types.Message):
    await message.answer('Choose your topic, part and question:')

# Хэндлер на команду /listen
@dp.message(Command("listen"))
async def cmd_chat(message: types.Message):
    await message.answer('Choose recording from your history:')
    
# Хэндлер на команду /chat
@dp.message(Command("chat"))
async def cmd_chat(message: types.Message):
    await message.answer('Have a nice talk with a LLM!')
    await message.answer('Please answer with not very long voices!')
    await message.answer(f'Today you will speak about {topic}.')

    tmp = history[-1]['content']
    filename = t2s.t2s(tmp, model_t2s, speaker)
    file = FSInputFile(filename)
    
    await bot.send_voice(message.from_user.id, file)
    os.remove(filename)
    
# Хэндлер на получение текста
@dp.message(F.content_type==types.ContentType.TEXT)
async def cmd_text(message: types.Message):
    '''
new_question = {"role": "user", "content": message.text}
    history.append(new_question)
    
    response = gpt.gpt_answer(client_gpt, history, message.text)
    new_answer = {"role": "assistant", "content": response}
    history.append(new_answer)

    await message.answer(response)
    '''
    await message.answer('Не читери! гусик следит за тобой.')
    
# Хэндлер на получение голосового
@dp.message(F.content_type==types.ContentType.VOICE)
async def cmd_text(message: types.Message):   
    file_id = message.voice.file_id # Get file id
    file = await bot.get_file(file_id) # Get file path
    
    await bot.download_file(file.file_path, 'voice.ogg')

    recognized, length = s2t.s2t('voice.ogg', model_s2t, Fs)
    wpm = int(len(recognized.split()) * 60 / length)
    await message.answer(str('Your WPM rate: ' + str(wpm)))
    
    new_question = {"role": "user", "content": recognized}
    history.append(new_question)
    
    answer = gpt.gpt_answer(client_gpt, history, recognized)
    new_answer = {"role": "assistant", "content": answer}
    history.append(new_answer)

    filename = t2s.t2s(answer, model_t2s, speaker)
    file = FSInputFile(filename)
    
    await bot.send_voice(message.from_user.id, file)
    os.remove(filename)


async def main():
    await set_main_menu(bot)
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)
    
# Запуск бота
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass

# EOF
