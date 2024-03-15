import asyncio, os
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import FSInputFile
from aiogram.filters.command import Command
from aiogram.methods import DeleteWebhook
import t2s, s2t, gpt
from random import choice

if os.path.isfile('tg_api.txt'):
    with open('tg_api.txt', 'r') as tg_api:
        token = tg_api.readline()
else:
    raise Exception("Don't forget to provide you TG bot token in 'tg_api.txt'")

topics = ['animals', 'cars']
topic = choice(topics)

bot = Bot(token)                    # Объект бота с токеном
dp = Dispatcher()                   # Диспетчер для бота
model_t2s, speaker = t2s.t2s_init() # запускаем модель Silero
model_s2t, Fs = s2t.s2t_init()      # запускаем модель Vosk
client_gpt, history = gpt.gpt_init(topic) # проверяем готовность GPT


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello! I am here to help you improve your conversation skills. Have a nice talk with a LLM!")
    await message.answer(f'Today you will speak about {topic}.')

    tmp = history[-1]['content']
    filename = t2s.t2s(tmp, model_t2s, speaker)
    file = FSInputFile(filename)
    
    await bot.send_voice(message.from_user.id, file)
    os.remove(filename)
    
# Хэндлер на получение текста
@dp.message(F.content_type==types.ContentType.TEXT)
async def cmd_text(message: types.Message):
    new_question = {"role": "user", "content": message.text}
    history.append(new_question)
    
    response = gpt.gpt_answer(client_gpt, history, message.text)
    new_answer = {"role": "assistant", "content": response}
    history.append(new_answer)

    await message.answer(response)
    
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
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)
    
# Запуск бота
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass

# EOF
