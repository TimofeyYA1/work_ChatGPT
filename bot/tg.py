import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = "7026161854:AAFTuDlQ7ialeLyfSmrYejwcYCA52-BqhP4"
ADMIN_ID = 847867090  # Telegram ID администратора
BASE_URL = "http://localhost:8080/ai/razvorot"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# === Состояния ===
class Form(StatesGroup):
    GetName = State()
    ChooseTrial = State()
    Step1_Name = State()
    Step1_Quality = State()
    Step1_Action = State()
    Step1_Reaction = State()
    Step2_Quality = State()
    Step2_Action = State()
    Step3_Acceptance = State()
    Step3_Thank = State()
    AfterTrial = State()

# === Кнопки ===
choose_trial_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔁 Пройти «Разворот»")],
        [KeyboardButton(text="✨ Вариант 2")]
    ],
    resize_keyboard=True
)

after_completion_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💸 Хочу купить ещё ключи")],
        [KeyboardButton(text="❌ Нет, спасибо")]
    ],
    resize_keyboard=True
)

# === Помощник для запросов ===
async def check_field(endpoint: str, payload: dict) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}{endpoint}", json=payload) as response:
            result = await response.json()
            return result.get("result", "")

# === Команда /start ===
@dp.message(F.text == "/start")
async def welcome(message: Message, state: FSMContext):
    await message.answer("👋 Добро пожаловать в сервис психологических практик!")
    await message.answer("Как вас зовут?")
    await state.clear()
    await state.set_state(Form.GetName)

@dp.message(Form.GetName)
async def get_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(client_name=name)
    await state.set_state(Form.ChooseTrial)
    await message.answer(
        f"{name}, рады видеть вас!\nВыберите одно из бесплатных пробных упражнений:",
        reply_markup=choose_trial_keyboard
    )

@dp.message(Form.ChooseTrial)
async def choose_trial(message: Message, state: FSMContext):
    if "разворот" in message.text.lower():
    # Первое сообщение (описание техники)
        intro = (
            "«Разворот» – это простая и быстрая практика, которая помогает:\n\n"
            "— Снижать негатив (обиды, раздражение, гнев)\n"
            "— Избегать эмоциональных «ям»\n"
            "— Перейти от обвинения к самоисследованию\n"
            "— Договариваться или отпускать отношения\n\n"
            "Основной принцип: то, что нас задевает в других — отражает нас самих."
        )
        await message.answer(intro, parse_mode="Markdown")
        await asyncio.sleep(3)
        intro = (
            """Возьмите ситуацию с конкретным человеком (или собой, которая вызвала негативную реакцию
Осознайте свою негативную эмоцию на эту ситуацию: раздражение, гнев, обида, печаль и т.п.
Опишите ситуацию, используя формулу: Человек (его имя) был (его негативное качество) и делал (действие). И это меня (злит, обижает, раздражает и т.п.)"""
        )
        await message.answer(intro, parse_mode="Markdown")
        await asyncio.sleep(3)
        question = "🔹 *Как зовут человека, о котором пойдёт речь?*"
        await message.answer(question, parse_mode="Markdown")

        # Установить состояние
        await state.set_state(Form.Step1_Name)
    elif "вариант 2" in message.text.lower():
        await message.answer("✨ Вариант 2 пока в разработке. Спасибо за интерес!", reply_markup=after_completion_keyboard)
        await state.set_state(Form.AfterTrial)
    else:
        await message.answer("❓ Пожалуйста, выберите действие кнопкой.")

# === Шаг 1 ===
@dp.message(Form.Step1_Name)
async def step1_name(message: Message, state: FSMContext):
    name = message.text.strip()
    payload = {"id": str(message.from_user.id), "who": name}
    result = await check_field("/1/who", payload)
    if "Да" in result:
        await state.update_data(who=name)
        await state.set_state(Form.Step1_Quality)
        await message.answer("🔹 *Какое негативное качество вы замечаете в нём?*", parse_mode="Markdown")
    else:
        await message.answer(f"⛔ {result}\n🔁 Попробуйте снова:")

@dp.message(Form.Step1_Quality)
async def step1_quality(message: Message, state: FSMContext):
    quality = message.text.strip()
    payload = {"id": str(message.from_user.id), "quality": quality}
    result = await check_field("/1/quality", payload)
    if "Да" in result:
        await state.update_data(quality=quality)
        await state.set_state(Form.Step1_Action)
        await message.answer("🔹 *Какие действия делает этот человек, что вам не нравятся?*", parse_mode="Markdown")
    else:
        await message.answer(f"⛔ {result}\n🔁 Попробуйте снова:")

@dp.message(Form.Step1_Action)
async def step1_action(message: Message, state: FSMContext):
    action = message.text.strip()
    payload = {"id": str(message.from_user.id), "what_was_he_doing": action}
    result = await check_field("/1/action", payload)
    if "Да" in result:
        await state.update_data(what_was_he_doing=action)
        await state.set_state(Form.Step1_Reaction)
        await message.answer("🔹 *Какая у вас была эмоциональная реакция на это?*", parse_mode="Markdown")
    else:
        await message.answer(f"⛔ {result}\n🔁 Попробуйте снова:")

@dp.message(Form.Step1_Reaction)
async def step1_reaction(message: Message, state: FSMContext):
    reaction = message.text.strip()
    payload = {"id": str(message.from_user.id), "reaction": reaction}
    result = await check_field("/1/reaction", payload)
    if "Да" in result:
        await state.update_data(reaction=reaction)
        data = await state.get_data()
        await message.answer(
            f"✅ *Шаг 1 завершён! {data['who']}, {data['quality']} и {data['what_was_he_doing']}, {data['reaction']}*\n\n",
            parse_mode="Markdown"
        )
        await state.set_state(Form.Step2_Quality)
        await message.answer("""Признайте свое неэффективное качество, которое отразил вам человек. 
Вы можете быть таким же (прямое зеркало) или противоположным (обратное зеркало). 
Определите своё новое качество и действие. 
Формула: Я всегда (качество) и (действие). Меня это радует.

🔹 *Какое позитивное качество вы хотите развивать в себе?*""", parse_mode="Markdown")
    else:
        await message.answer(f"⛔ {result}\n🔁 Попробуйте снова:")

# === Шаг 2 ===
@dp.message(Form.Step2_Quality)
async def step2_quality(message: Message, state: FSMContext):
    quality = message.text.strip()
    payload = {"id": str(message.from_user.id), "scenery": quality}
    result = await check_field("/2/scenery", payload)
    if "Да" in result:
        await state.update_data(new_quality=quality)
        await state.set_state(Form.Step2_Action)
        await message.answer("🔹 *Какое действие теперь будет вашим новым паттерном?*", parse_mode="Markdown")
    else:
        await message.answer(f"⛔ {result}\n🔁 Повторите попытку:")

@dp.message(Form.Step2_Action)
async def step2_action(message: Message, state: FSMContext):
    action = message.text.strip()
    payload = {"id": str(message.from_user.id), "positive_reaction": action}
    result = await check_field("/2/reaction", payload)
    if "Да" in result:
        await state.update_data(new_action=action)
        user_data = await state.get_data()
        await message.answer(
            f"""✅ *Шаг 2 завершён!*\n\n Ваш новый паттерн:\n— *{user_data['new_quality']}*, *{user_data['new_action']}*\n
Я всегда *{user_data['new_quality']}* и *{user_data['new_action']}*. И меня это радует.""",
            parse_mode="Markdown"
        )
        await asyncio.sleep(3)
        await message.answer(f"""Примите свободу другого человека быть таким, какой он есть, и поступать так, как он считают нужным.\nИскренне поблагодарите челевека за то, что благодаря этой ситуации вы увидели, над чем вам можно поработать:\nДорогой(Имя)! Я принимаю твою свободу выбора быть (качество) и делать (действие). Я благодарю тебя за возможность мне улучшить себя и стать (качество)\nНапишите благодарность человеку за урок,а потом прочтите это вслух.""",parse_mode="Markdown")

        await asyncio.sleep(3)
        await state.set_state(Form.Step3_Acceptance)
        await message.answer("🔹 *Что вы принимаете в этой ситуации?*",parse_mode="Markdown")

    else:
        await message.answer(f"⛔ {result}\n🔁 Повторите попытку:")

# === Шаг 3 ===
@dp.message(Form.Step3_Acceptance)
async def step3_acceptance(message: Message, state: FSMContext):
    text = message.text.strip()
    payload = {"id": str(message.from_user.id), "acceptance": text}
    result = await check_field("/3/acceptance", payload)
    if "Да" in result:
        await state.update_data(acceptance=text)
        await state.set_state(Form.Step3_Thank)
        await message.answer("🔹 *За что вы можете поблагодарить этого человека или эту ситуацию?*", parse_mode="Markdown")
    else:
        await message.answer(f"⛔ {result}\n🔁 Попробуйте снова:")

@dp.message(Form.Step3_Thank)
async def step3_thank(message: Message, state: FSMContext):
    text = message.text.strip()
    payload = {"id": str(message.from_user.id), "thank": text}
    result = await check_field("/3/thank", payload)
    if "Да" in result:
        await state.update_data(thank=text)
        data = await state.get_data()
        await message.answer(
            "🎯 *Разворот завершён!*\n\n"
    "Вы прошли глубокую практику самоисследования, которая помогает осознать свои реакции, взглянуть на ситуацию с другой стороны и обрести внутреннюю свободу.\n\n"
    "*Вот ваш личный Разворот:*\n\n"
    "📄 *Шаг 1: Осознание негативной реакции*\n"
    f"Вы указали: *{data['who']}* — *{data['quality']}*, делал — *{data['what_was_he_doing']}*, и это вызвало у вас реакцию: *{data['reaction']}*\n\n"
    "📄 *Шаг 2: Поиск нового паттерна*\n"
    f"Вы выбрали развивать в себе качество *{data['new_quality']}* и теперь будете действовать по-другому — *{data['new_action']}*\n"
    f"→ _Я всегда {data['new_quality']} и {data['new_action']}. И меня это радует._\n\n"
    "📄 *Шаг 3: Принятие и благодарность*\n"
    f"Вы приняли ситуацию: *{data['acceptance']}*\n"
    f"И поблагодарили: *{data['thank']}*\n\n"
    "🌱 Это не просто ответы — это начало внутренней трансформации.\n"
    "Благодаря честному взгляду на себя вы сделали шаг к зрелости, осознанности и гармонии в отношениях.\n\n"
    "Если вы хотите продолжить работу с собой или получить новые ключи для саморазвития — мы рядом 💙",
            reply_markup=after_completion_keyboard,
            parse_mode="Markdown"
        )
        await state.set_state(Form.AfterTrial)
    else:
        await message.answer(f"⛔ {result}\n🔁 Попробуйте ещё раз:")

# === Завершение: upsell ===
@dp.message(Form.AfterTrial)
async def handle_upsell(message: Message, state: FSMContext):
    if "купить" in message.text.lower():
        data = await state.get_data()
        client_name = data.get("client_name", "Не указано")
        await bot.send_message(ADMIN_ID, f"🛍 Клиент хочет купить ключи!\nИмя: {client_name}\nID: {message.from_user.id}")
        await message.answer("✅ Спасибо! Мы скоро свяжемся с вами.")
    else:
        await message.answer("🙏 Спасибо, что воспользовались MindKey!")
    await state.clear()

# === Запуск ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
