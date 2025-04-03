from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer
from models.schemas import Razvorot1, Razvorot2, Razvorot3
from adapters.db_source import DatabaseAdapter
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os
import httpx
from pydantic import BaseModel
load_dotenv()

router = APIRouter()
Bear = HTTPBearer(auto_error=False)
http_client = httpx.Client(
    transport=httpx.HTTPTransport(proxy="http://user166198:dsolnu@176.223.181.66:4932"),
    timeout=30.0
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"),http_client=http_client)  # Замените на ваш реальный ключ
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  
class WhoInput(BaseModel):
    id: str
    who: str

class QualityInput(BaseModel):
    id: str
    quality: str

class ActionInput(BaseModel):
    id: str
    what_was_he_doing: str

class ReactionInput(BaseModel):
    id: str
    reaction: str
class SceneryInput(BaseModel):
    id: str
    scenery: str

class PositiveReactionInput(BaseModel):
    id: str
    positive_reaction: str
class AcceptanceInput(BaseModel):
    id: str
    acceptance: str

class ThankInput(BaseModel):
    id: str
    thank: str


@router.post("/razvorot/1/who")
async def check_who(data: WhoInput):
    prompt = f"""
Ты психолог. Проверь:
1. Имя на русском языке
2. Слово осмысленно (не абракадабра)
3. Нет лишних слов или описаний

Ответ: <Кто?> — {data.who}

Если всё в порядке, ответь: Да
Иначе: Укажи, что исправить (до 5 слов)
""".strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=50
        )
        result = response.choices[0].message.content

        if "Да" in result:
            db = DatabaseAdapter()
            db.connect()
            db.initialize_tables()
            db.insert_or_update("reverse", {"id": data.id, "who": data.who})

        return {"result": result}

    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/razvorot/1/quality")
async def check_quality(data: QualityInput):    
    id = data.id
    quality = data.quality

    if not id or not quality:
        raise HTTPException(status_code=400, detail="Нужны 'id' и 'quality'")

    db = DatabaseAdapter()
    db.connect()
    db.initialize_tables()
    partial = db.get_by_id("reverse", id)
    who = partial[0]["who"] if partial else "тот человек"

    prompt = f"""
Ты психолог. Проверь:
1. Корректность русского языка
2. Осмысленность слов
3. дает ли ответ на вопрос
4. Нет ли имени, кроме '{who}',но имя может отсутствовать
Учти,ответ МОЖЕТ содержать нецензурную лексику и оскорбления,не проверяй на грубость
<Какой этот человек?> - {quality}

Если всё в порядке, ответь: Да
Иначе: Кратко укажи, что исправить (до 7 слов)
""".strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=50
        )
        result = response.choices[0].message.content

        if "Да" in result:
            db.insert_or_update("reverse", {"id": id, "quality": quality})
        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/razvorot/1/action")
async def check_action(data: ActionInput):
    db = DatabaseAdapter()
    db.connect()
    db.initialize_tables()
    existing = db.get_by_id("reverse", data.id)
    who = existing[0]["who"] if existing else "человек"

    prompt = f"""
Ты — психолог. Проверь ответ пользователя по следующим критериям:

1. Корректность русского языка.
2. Ответ должен быть конкретным описанием действий другого человека, без лишних оценок и чувств.
3. Ответ действительно отвечает на вопрос "Что делал человек?" — например: *манипулировал, игнорировал, кричал, обвиняла* и т.п.
4. В ответе не должно быть имён, кроме '{who}' (имя может вообще не упоминаться).
5. Ответ осмыслен — это не набор случайных слов.

Учитывай:
— Ответ может содержать ненормативную или разговорную лексику.
— Ответ может быть неполным по структуре предложения.

Пример верного ответа: *Писал гадости в чат*, *Накручивал всех против меня*, *Игнорирует мои просьбы*.

Данные:
<Что делал?> — {data.what_was_he_doing}

Если всё корректно, верни: Да  
Иначе — кратко поясни, что не так (не более 7 слов).
"""
#Укажи, что исправить (до 10 слов),если ответ не соответствует вопросу,тоо 
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=20
        )
        result = response.choices[0].message.content

        if "Да" in result:
            db.insert_or_update("reverse", {
                "id": data.id,
                "what_was_he_doing": data.what_was_he_doing
            })

        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/razvorot/1/reaction")
async def check_reaction(data: ReactionInput):
    prompt = f"""
Проверь:
1. На русском   
2. Реакция должна быть эмоциональной или физической
3. Является ли это ответом на вопрос: "Какая у меня была реакция?"

<Как вы на это реагировали?> — {data.reaction}

Если всё в порядке, верни: Да
Иначе: кратко поясни (до 7 слов)
"""

    try:
        db = DatabaseAdapter()
        db.connect()
        db.initialize_tables()

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=20
        )

        result = response.choices[0].message.content
        if "Да" in result:
            db.insert_or_update("reverse", {
                "id": data.id,
                "reaction": data.reaction
            })

        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/razvorot/2/scenery")
async def check_scenery(data: SceneryInput):
    db = DatabaseAdapter()
    db.connect()
    db.initialize_tables()

    prompt = f"""
Проверь:
1. На русском языке
2. Описывает позитивную характеристику или качество человека.
3. Это позитивное качество,которое человек хочет развивать в себе
4. Предложение может быть не полным и соднржать только одно слово
5. Хотя бы одно прилагательно в предложении

<Какое позитивное качество вы хотите развивать в себе?> — {data.scenery}

Если корректно — верни: Да
Иначе: кратко поясни (до 7 слов)
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=30
        )

        result = response.choices[0].message.content
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/razvorot/2/reaction")
async def check_positive_reaction(data: PositiveReactionInput):
    db = DatabaseAdapter()
    db.connect()
    db.initialize_tables()

    data0 = db.get_by_id("reverse", data.id)
    if not data0:
        print("sql")
        raise HTTPException(status_code=403, detail="Сначала пройдите первый шаг анкеты")
    data0 = Razvorot1(**data0[0])

    prompt = f"""
Проверь:
1. На русском
2. Действие должно быть позитивным ИЛИ приносить пользу человеку
3. действие должно противоречить {data0.reaction}

<Каково ваше новое действие?> - {data.positive_reaction}

Если корректно — верни: Да
Иначе: Укажи, что исправить (до 7 слов)
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=30
        )
        return {"result": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/razvorot/3/acceptance")
async def check_acceptance(data: AcceptanceInput):
    db = DatabaseAdapter()
    db.connect()
    db.initialize_tables()

    data0 = db.get_by_id("reverse", data.id)
    who = data0[0]["who"] if data0 else "этот человек"

    prompt = f"""
Проверь принятие:
1. На русском
2. Без агрессии
3. Смысл — принять {who} или ситуацию
4. Нет ли имени кроме '{who}'(может вовсе отсутствовать)

<Что вы принимаете в данной ситуации> - {data.acceptance}

Если корректно — верни: Да
Иначе: кратко поясни (до 7 слов)
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=30
        )
        return {"result": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/razvorot/3/thank")
async def check_thank(data: ThankInput):
    prompt = f"""
Проверь,учти,что ответы могут содержать ненормативную лексику:
1. Благодарность должна быть уместной
2. Написана на русском
3. Не содержит сарказма или пассивной агрессии
Учти,Ответы могут содержать ненормативную и разговорную лексику.Предложения могут быть неполными.
<Выразите благодарность человеку> - {data.thank}

Если подходит — Да
Иначе: кратко поясни (до 7 слов)
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=30
        )
        return {"result": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/razvorot/1")
async def negative_scenario(data: Razvorot1):
    try:
        # Проверка ответов через GPT
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content":f"Мы - психологический сайт,который помогает людям разобраться в свои взаимоотношениях с другими людьми,сайт помогает поменять свою реакцию на действия этих людей методом психологического Разворота.Представь,что ты психолог и тебе надо проверить корректность формата ответов пользователя на конкретные вопросы.Ты должен проверить,что каждое предложение соответствует правилам русского языка,а каждое слово является осмысленным,а не просто набором букв.Проверь,что все ответы написаны на русском языке.Также убедись,что пользователь дает понятный ответ на поставленный вопрос.Также проверь,что ни в одном предложении нету имени,отличного от {data.who}.Ответы могут содержать ненормативную и разговорную лексику.Предложения могут быть неполными.Дальше ты увидишь данные в формате: <Вопрос?-Ответ пользователя>\nДанные:\n<Кто?-{data.who}>\n<Какой этот человек?-{data.quality}>\n<Что делал?-{data.what_was_he_doing}>\n<Какова моя реакция на это?-{data.reaction}>\nВерни ТОЛЬКО «Да» если все ответы пользователя соответствуют описанным мною правилам,иначе верни номер неправильного ответа в формате: <номер вопроса> И коротко объясни человеку,что ему надо изменить,про каждый пункт не больше одного предложения,предложение до 7 слов "
            }],
            temperature=0.3,
            max_tokens=30
        )
        print("J")
        result = response.choices[0].message.content
        
        if "Да" in result:
            db = DatabaseAdapter()
            db.connect()
            db.initialize_tables()
            try:
                db.delete("reverse", data.id)
            except:
                pass
            db.insert("reverse", {
                "id": data.id,
                "who": data.who,
                "quality": data.quality,
                "what_was_he_doing": data.what_was_he_doing,
                "reaction": data.reaction
            })
        
        return {"result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/razvorot/2")
async def b_scenario(data: Razvorot2):
    try:
        db = DatabaseAdapter()
        db.connect()
        db.initialize_tables()
        
        data0 = db.get_by_id("reverse", data.id)
        if not data0:
            raise HTTPException(status_code=403, detail="Сначала пройдите первый шаг анкеты")
            
        data0 = Razvorot1(**data0[0])
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content":f"Мы - психологический сайт,который помогает людям разобраться в свои взаимоотношениях с другими людьми,сайт помогает поменять свою реакцию на действия этих людей методом психологического Разворота.Представь,что ты психолог и тебе надо проверить корректность формата ответов пользователя на конкретные вопросы.Ты должен проверить,что каждое предложение соответствует правилам русского языка(Не проверяй заглавные буквы,это не важно),а каждое слово является осмысленным,а не просто набором букв.Также убедись,что пользователь дает ответ на поставленный вопрос,также проверь,что в предлжениях нету имени отличного от {data0.who} .Дальше ты увидишь данные в формате: <Вопрос?-Ответ пользователя>\nДанные:\n<Какое ваше неэфективное качество?-{data.scenery}>\n<Какова ваша ПОЛОЖИТЕЛЬНАЯ реакция противоположная этой: '{data0.reaction}' ?-{data.positive_reaction}>\nВерни ТОЛЬКО «Да» если все ответы пользователя соответствуют описанным мною правилам,иначе верни номер неправильного ответа в формате: <номер вопроса> И коротко объясни человеку,что ему надо изменить,про каждый пункт не больше одного предложения,предложение до 7 слов "
            }],
            temperature=0.3,
            max_tokens=50
        )
        
        return {"result": response.choices[0].message.content}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/razvorot/3")
async def b_scenario(data: Razvorot3):
    try:
        db = DatabaseAdapter()
        db.connect()
        db.initialize_tables()
        
        data0 = db.get_by_id("reverse", data.id)
        if not data0:
            raise HTTPException(status_code=403, detail="Сначала пройдите первый шаг анкеты")
            
        data0 = Razvorot1(**data0[0])
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "user",
                "content":f"Мы - психологический сайт,который помогает людям разобраться в свои взаимоотношениях с другими людьми,сайт помогает поменять свою реакцию на действия этих людей методом психологического Разворота.Представь,что ты психолог и тебе надо проверить корректность формата ответов пользователя на конкретные вопросы.Ты должен проверить,что каждое предложение соответствует правилам русского языка,а каждое слово является осмысленным,а не просто набором букв.Также убедись,что пользователь дает ответ на поставленный вопрос,также проверь,что в предлжениях есть имя {data0.who} в любой форме ИЛИ его вовсе нет,но могут присутствовать местоимения.Дальше ты увидишь данные в формате: <Вопрос?-Ответ пользователя>\nДанные:\n<Принимите {data0.who} таким,какой он есть(только положительный смысл)-{data.acceptance}>\n<Выразите благодарность человеку-{data.thank}>\nВерни ТОЛЬКО «Да» если все ответы пользователя соответствуют описанным мною правилам,иначе верни номер неправильного ответа в формате: <номер вопроса> И коротко объясни человеку,что ему надо изменить,про каждый пункт не больше одного предложения,предложение до 7 слов "
                # "content": f"""Проверь:
                # 1. Корректность русского языка
                # 2. Осмысленность слов
                # 3. Соответствие ответов вопросам
                # 4. Отсутствие других имен, кроме {data0.who}
                
                # Данные:
                # <Принятие {data0.who}-{data.acceptance}>
                # <Благодарность-{data.thank}>
                
                # Верни «Да» если все верно, иначе укажи вопрос с ошибкой."""
            }],
            temperature=0.3,
            max_tokens=50
        )
        
        return {"result": response.choices[0].message.content}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))