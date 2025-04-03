from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer
from models.schemas import Razvorot1, Razvorot2, Razvorot3
from adapters.db_source import DatabaseAdapter
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os
import httpx
load_dotenv()

router = APIRouter()
Bear = HTTPBearer(auto_error=False)
# http_client = httpx.Client(
#     transport=httpx.HTTPTransport(proxy="http://user166198:dsolnu@176.223.181.66:4932"),
#     timeout=30.0
# )

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"),http_client=http_client)  # Замените на ваш реальный ключ
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  
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
            max_tokens=50
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