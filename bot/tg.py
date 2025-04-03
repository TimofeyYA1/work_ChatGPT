import asyncio
import aiohttp
import re
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = "7390929840:AAH81vk7XvWz6C-AGT5DJTEm4O0IYLL3jVM"
BASE_URL = "http://138.124.52.134:8080/ai/razvorot/"
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# === STATES ===
class Form(StatesGroup):
    Step1_Name = State()
    Step1_Quality = State()
    Step1_Action = State()
    Step1_Reaction = State()
    Retry_Step1_Name = State()
    Retry_Step1_Quality = State()
    Retry_Step1_Action = State()
    Retry_Step1_Reaction = State()
    Step2_Quality = State()
    Step2_Action = State()
    Retry_Step2_Quality = State()
    Retry_Step2_Action = State()
    Step3_Acceptance = State()
    Step3_Thank = State()
    Retry_Step3_Acceptance = State()
    Retry_Step3_Thank = State()

# === HELPERS ===
def extract_failed_fields(response: str) -> list[int]:
    return [int(num) for num in re.findall(r"<(\d+)>", response)]

async def send_data_to_server(page_number: int, data: dict) -> str:
    url = f"{BASE_URL}{page_number}"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                result = await response.json()
                return result.get("result", "")
            return await response.text()

# === START ===
@dp.message(F.text == "/start")
async def start_handler(message: Message, state: FSMContext):
    intro_1 = (
        "«Разворот» – это простая и быстрая практика, которая помогает:\n\n"
        "— Снижать негатив (обиды, раздражение, гнев)\n"
        "— Избегать эмоциональных «ям»\n"
        "— Перейти от обвинения к самоисследованию\n"
        "— Договариваться или отпускать отношения\n\n"
        "Основной принцип: то, что нас задевает в других — отражает нас самих."
    )
    await message.answer(intro_1)
    await asyncio.sleep(5)
    intro_2 = (
        "Теперь перейдём к практике:\n\n"
        """Возьмите ситуацию с кониретным человеком (или собой, которая вызвала негативную реакцию\nОсознайте свою негативную реакцию на эту ситуацию: раздражение, гнев, обида, печаль и т.л.\nОпишите ситуацию, используя формулу: Человек (его имя) был (его негативное качество) и делал (действие). И это меня (злит, обижает, раздражает и т.п.)"""
        "🔹 *Как зовут человека, о котором пойдёт речь?*"
    )
    await state.clear()
    await state.set_state(Form.Step1_Name)
    await message.answer(intro_2, parse_mode="Markdown")

# === STEP 1 ===
@dp.message(Form.Step1_Name)
async def step1_name(message: Message, state: FSMContext):
    await state.update_data(who=message.text.strip())
    await message.answer("🔹 *Какое негативное качество вы замечаете в нём?*", parse_mode="Markdown")
    await state.set_state(Form.Step1_Quality)

@dp.message(Form.Step1_Quality)
async def step1_quality(message: Message, state: FSMContext):
    await state.update_data(quality=message.text.strip())
    await message.answer("🔹 *Какие действия делает этот человек, что вам не нравятся?*", parse_mode="Markdown")
    await state.set_state(Form.Step1_Action)

@dp.message(Form.Step1_Action)
async def step1_action(message: Message, state: FSMContext):
    await state.update_data(what_was_he_doing=message.text.strip())
    await message.answer("🔹 *Какая у вас была эмоциональная реакция на это?*", parse_mode="Markdown")
    await state.set_state(Form.Step1_Reaction)
async def check_step1_all_and_send(message: Message, state: FSMContext):
    data = await state.get_data()
    required_fields = ["who", "quality", "what_was_he_doing", "reaction"]

    if all(data.get(k) for k in required_fields):
        payload = {
            "who": data["who"],
            "quality": data["quality"],
            "what_was_he_doing": data["what_was_he_doing"],
            "reaction": data["reaction"],
            "id": str(message.from_user.id)
        }
        response = await send_data_to_server(1, payload)
        failed = extract_failed_fields(response)

        if not failed:
            await message.answer(
                "✅ *Шаг 1 завершён!*\n\n"
                f"— Имя: *{payload['who']}*\n"
                f"— Качество: *{payload['quality']}*\n"
                f"— Действие: *{payload['what_was_he_doing']}*\n"
                f"— Ваша реакция: *{payload['reaction']}*",
                parse_mode="Markdown"
            )
            await state.set_state(Form.Step2_Quality)
            await message.answer("🔹 *Какое позитивное качество вы хотите развивать в себе?*", parse_mode="Markdown")
        else:
            await message.answer(f"⛔ Ошибка:\n{response.strip()}", parse_mode="Markdown")
            if 1 in failed:
                await state.set_state(Form.Retry_Step1_Name)
                await message.answer("🔁 Введите имя заново:")
            elif 2 in failed:
                await state.set_state(Form.Retry_Step1_Quality)
                await message.answer("🔁 Введите негативное качество заново:")
            elif 3 in failed:
                await state.set_state(Form.Retry_Step1_Action)
                await message.answer("🔁 Что делал этот человек?")
            elif 4 in failed:
                await state.set_state(Form.Retry_Step1_Reaction)
                await message.answer("🔁 Какая у вас была реакция?")

@dp.message(Form.Step1_Reaction)
async def step1_reaction(message: Message, state: FSMContext):
    await state.update_data(reaction=message.text.strip())
    user_data = await state.get_data()
    payload = {
        "who": user_data.get("who"),
        "quality": user_data.get("quality"),
        "what_was_he_doing": user_data.get("what_was_he_doing"),
        "reaction": user_data.get("reaction"),
        "id": str(message.from_user.id)
    }
    response = await send_data_to_server(1, payload)
    failed = extract_failed_fields(response)
    if not failed:
        await message.answer(
            "✅ *Шаг 1 завершён!*\n\n"
            f"— Имя: *{payload['who']}*\n"
            f"— Качество: *{payload['quality']}*\n"
            f"— Действие: *{payload['what_was_he_doing']}*\n"
            f"— Ваша реакция: *{payload['reaction']}*",
            parse_mode="Markdown"
        )
        await state.set_state(Form.Step2_Quality)
        await message.answer("""Признайте свое неэфективное качество, которое отразил вам человек. Вы нажете быть таким же (прамое зеркало) или проявить себя кардинально противоположно (обратное зеркало), но тоже неэфективно\nОпределите свое новое позитивное качество или действие, которое станет вашим новым «паттерном» поведения.\nЗапишите формулу: Я всегда(новое качество) и делаю (действие). И меня это радует.\n🔹 *Какое позитивное качество вы хотите развивать в себе?*""" , parse_mode="Markdown")
    else:
        await message.answer(f"⛔ Ошибка:\n{response.strip()}", parse_mode="Markdown")
        if 1 in failed:
            await state.set_state(Form.Retry_Step1_Name)
            await message.answer("🔁 Введите имя заново:")
        elif 2 in failed:
            await state.set_state(Form.Retry_Step1_Quality)
            await message.answer("🔁 Введите негативное качество заново:")
        elif 3 in failed:
            await state.set_state(Form.Retry_Step1_Action)
            await message.answer("🔁 Что делал этот человек?")
        elif 4 in failed:
            await state.set_state(Form.Retry_Step1_Reaction)
            await message.answer("🔁 Какая у вас была реакция?")

@dp.message(Form.Retry_Step1_Name)
async def retry_step1_name(message: Message, state: FSMContext):
    await state.update_data(who=message.text.strip())
    await check_step1_all_and_send(message, state)

@dp.message(Form.Retry_Step1_Quality)
async def retry_step1_quality(message: Message, state: FSMContext):
    await state.update_data(quality=message.text.strip())
    await check_step1_all_and_send(message, state)

@dp.message(Form.Retry_Step1_Action)
async def retry_step1_action(message: Message, state: FSMContext):
    await state.update_data(what_was_he_doing=message.text.strip())
    await check_step1_all_and_send(message, state)

@dp.message(Form.Retry_Step1_Reaction)
async def retry_step1_reaction(message: Message, state: FSMContext):
    await state.update_data(reaction=message.text.strip())
    await check_step1_all_and_send(message, state)
# === STEP 2 ===
@dp.message(Form.Step2_Quality)
async def step2_quality(message: Message, state: FSMContext):
    await state.update_data(new_quality=message.text.strip())
    await message.answer("🔹 *Какое действие теперь будет вашим новым паттерном?*", parse_mode="Markdown")
    await state.set_state(Form.Step2_Action)

@dp.message(Form.Step2_Action)
async def step2_action(message: Message, state: FSMContext):
    await state.update_data(new_action=message.text.strip())
    user_data = await state.get_data()
    payload = {
        "scenery": user_data.get("new_quality"),
        "positive_reaction": user_data.get("new_action"),
        "id": str(message.from_user.id)
    }
    response = await send_data_to_server(2, payload)
    failed = extract_failed_fields(response)
    if not failed:
        await state.set_state(Form.Step3_Acceptance)
        await message.answer(f"""✅ *Шаг 2 завершён!*\n\n Ваш новый паттерн:\n— *{user_data['new_quality']}*, *{user_data['new_action']}*\nПримите свободу другого человека быть таким, какой он есть, и поступать так, как он считают нужным.\nИскренне поблагодарите челевека за то, что благодаря этой ситуации вы увидели, над чем вам можно поработать:\nДорогой(Имя)! Я принимаю твою свободу выбора быть (качество) и делать (действие). Я благодарю тебя за возможность мне улучшить себя и стать (качество)\nНапишите благодарность человеку за урок,а потом прочтите это вслух.🔹 *Напишите принятие*""", parse_mode="Markdown")
    else:
        await message.answer(f"⛔ Ошибка:\n{response.strip()}", parse_mode="Markdown")
        if 1 in failed:
            await state.set_state(Form.Retry_Step2_Quality)
            await message.answer("🔁 Повторите позитивное качество:")
        elif 2 in failed:
            await state.set_state(Form.Retry_Step2_Action)
            await message.answer("🔁 Повторите новое действие:")

@dp.message(Form.Retry_Step2_Quality)
async def retry_step2_quality(message: Message, state: FSMContext):
    await state.update_data(new_quality=message.text.strip())
    await step2_action(message, state)

@dp.message(Form.Retry_Step2_Action)
async def retry_step2_action(message: Message, state: FSMContext):
    await state.update_data(new_action=message.text.strip())
    await step2_action(message, state)

# === STEP 3 ===
@dp.message(Form.Step3_Acceptance)
async def step3_acceptance(message: Message, state: FSMContext):
    await state.update_data(acceptance=message.text.strip())
    await message.answer("🔹 *За что вы можете поблагодарить этого человека или эту ситуацию?*", parse_mode="Markdown")
    await state.set_state(Form.Step3_Thank)

@dp.message(Form.Step3_Thank)
async def step3_thank(message: Message, state: FSMContext):
    await state.update_data(thank=message.text.strip())
    user_data = await state.get_data()
    payload = {
        "acceptance": user_data.get("acceptance"),
        "thank": user_data.get("thank"),
        "id": str(message.from_user.id)
    }
    response = await send_data_to_server(3, payload)
    failed = extract_failed_fields(response)
    if not failed:
        await message.answer("🎯 *Разворот завершён!*\n\n"
            f"📄 *Шаг 1:*\n{user_data['who']} — {user_data['quality']}, {user_data['what_was_he_doing']} ➡️ {user_data['reaction']}\n\n"
            f"📄 *Шаг 2:*\nЯ всегда {user_data['new_quality']} и {user_data['new_action']}\n\n"
            f"📄 *Шаг 3:*\nПринятие: {user_data['acceptance']}\nБлагодарность: {user_data['thank']}",
            parse_mode="Markdown")
        await state.clear()
    else:
        await message.answer(f"⛔ Ошибка:\n{response.strip()}", parse_mode="Markdown")
        if 1 in failed:
            await state.set_state(Form.Retry_Step3_Acceptance)
            await message.answer("🔁 Повторите, что вы принимаете:")
        elif 2 in failed:
            await state.set_state(Form.Retry_Step3_Thank)
            await message.answer("🔁 Повторите благодарность:")

@dp.message(Form.Retry_Step3_Acceptance)
async def retry_step3_acceptance(message: Message, state: FSMContext):
    await state.update_data(acceptance=message.text.strip())
    await step3_thank(message, state)

@dp.message(Form.Retry_Step3_Thank)
async def retry_step3_thank(message: Message, state: FSMContext):
    await state.update_data(thank=message.text.strip())
    await step3_thank(message, state)

# === RUN ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
