from fastapi import APIRouter, HTTPException
from g4f import Client
from fastapi.security import HTTPBearer
import g4f.Provider
from models.schemas import Razvorot1,Razvorot2,Razvorot3
from adapters.db_source import DatabaseAdapter
import g4f
import asyncio

router = APIRouter()
Bear = HTTPBearer(auto_error=False)
client = Client()
async def get_chatgpt_response():
    response = await g4f.ChatCompletion.create_async(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Привет!"}],
        proxy="user166198:dsolnu@154.16.68.39:5030"


    )
    return response
@router.post("/test_1")
def negative_scenario(data: Razvorot1):
    print(1)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user",
                "content":f"Мы - психологический сайт,который помогает людям разобраться в свои взаимоотношениях с другими людьми,сайт помогает поменять свою реакцию на действия этих людей методом психологического Разворота.Представь,что ты психолог и тебе надо проверить корректность формата ответов пользователя на конкретные вопросы.Ты должен проверить,что каждое предложение соответствует правилам русского языка,а каждое слово является осмысленным,а не просто набором букв.Проверь,что все ответы написаны на русском языке.Также убедись,что пользователь дает ответ на поставленный вопрос,также проверь,что ни в одном предложении нету имени,отличного от {data.who}.Дальше ты увидишь данные в формате: <Вопрос?-Ответ пользователя>\nДанные:\n<Кто?-{data.who}>\n<Какие у него есть качества?-{data.quality}>\n<Что делал?-{data.what_was_he_doing}>\n<Какова моя реакция на это?-{data.reaction}>\nВерни ТОЛЬКО «Да» если все ответы пользователя соответствуют описанным мною правилам,иначе верни вопрос,на который пользователь дал некорректный ответ."
        }],
           timeout=100
    )
    print(2)
    return {"result": response}

@router.post("/test_3")
async def negative_scenario(data: Razvorot1):
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Сколько будет 5 умножить на пять?"}],
        )
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

@router.post("/test_34")
async def negative_sc444enario(data: Razvorot1):
    try:
        response = await g4f.ChatCompletion.create_async(
            model="gpt-4",
            messages=[{"role": "user", "content": "Сколько будет 5 умножить на пять?"}],
            proxy="http://user166198:dsolnu@154.16.68.39:5030"
        )
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}
@router.post("test_2")
async def negative_scenario(data: Razvorot1):

    db = DatabaseAdapter()
    db.connect()
    db.initialize_tables()
    return {"result": "db is working at the moment"}



@router.post("/razvorot/1")
async def negative_scenario(data: Razvorot1):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user",
                "content":f"Мы - психологический сайт,который помогает людям разобраться в свои взаимоотношениях с другими людьми,сайт помогает поменять свою реакцию на действия этих людей методом психологического Разворота.Представь,что ты психолог и тебе надо проверить корректность формата ответов пользователя на конкретные вопросы.Ты должен проверить,что каждое предложение соответствует правилам русского языка,а каждое слово является осмысленным,а не просто набором букв.Проверь,что все ответы написаны на русском языке.Также убедись,что пользователь дает ответ на поставленный вопрос,также проверь,что ни в одном предложении нету имени,отличного от {data.who}.Дальше ты увидишь данные в формате: <Вопрос?-Ответ пользователя>\nДанные:\n<Кто?-{data.who}>\n<Какие у него есть качества?-{data.quality}>\n<Что делал?-{data.what_was_he_doing}>\n<Какова моя реакция на это?-{data.reaction}>\nВерни ТОЛЬКО «Да» если все ответы пользователя соответствуют описанным мною правилам,иначе верни вопрос,на который пользователь дал некорректный ответ."
        }],
           timeout=100
    )
    title = response.choices[0].message.content
    if "Да" in title:
        db = DatabaseAdapter()
        db.connect()
        db.initialize_tables()
        try:
            db.delete("reverse",data.id)
        except:
            pass
        db.insert("reverse",{"id":data.id,"who":data.who,"quality":data.quality,"what_was_he_doing":data.what_was_he_doing,"reaction":data.reaction})
    return {"result": title}




@router.post("/razvorot/2")
async def b_scenario(data: Razvorot2):
    db = DatabaseAdapter()
    db.connect()
    db.initialize_tables()
    data0 = db.get_by_id("reverse",data.id)
    if len(data0)>0:
        data0 = data0[0]
    else:
        raise HTTPException(status_code=403, detail="Походу вы еще не прошли первый шаг анкеты")
    data0 =  Razvorot1(**data0)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user",
                "content":f"Мы - психологический сайт,который помогает людям разобраться в свои взаимоотношениях с другими людьми,сайт помогает поменять свою реакцию на действия этих людей методом психологического Разворота.Представь,что ты психолог и тебе надо проверить корректность формата ответов пользователя на конкретные вопросы.Ты должен проверить,что каждое предложение соответствует правилам русского языка(Не проверяй заглавные буквы,это не важно),а каждое слово является осмысленным,а не просто набором букв.Также убедись,что пользователь дает ответ на поставленный вопрос,также проверь,что в предлжениях есть имя {data0.who} в любой форме ИЛИ его вовсе нет,но могут присутствовать местоимения.Дальше ты увидишь данные в формате: <Вопрос?-Ответ пользователя>\nДанные:\n<Какое ваше неэфективное качество?-{data.scenery}>\n<Какова ваша ПОЛОЖИТЕЛЬНАЯ реакция противоположная этой: '{data0.reaction}' ?-{data.positive_reaction}>\nВерни ТОЛЬКО «Да» если все ответы пользователя соответствуют описанным мною правилам,иначе верни вопрос,на который пользователь дал некорректный ответ."
        }],
           timeout=100
    )
    title = response.choices[0].message.content
    return {"result": title}
  

@router.post("/razvorot/3")
async def b_scenario(data0:Razvorot1,data: Razvorot3):
    db = DatabaseAdapter()
    db.connect()
    db.initialize_tables()
    data0 = db.get_by_id("reverse",data.id)
    if len(data0)>0:
        data0 = data0[0]
    else:
        raise HTTPException(status_code=403, detail="Походу вы еще не прошли первый шаг анкеты")
    data0 =  Razvorot1(**data0)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user",
                "content":f"Мы - психологический сайт,который помогает людям разобраться в свои взаимоотношениях с другими людьми,сайт помогает поменять свою реакцию на действия этих людей методом психологического Разворота.Представь,что ты психолог и тебе надо проверить корректность формата ответов пользователя на конкретные вопросы.Ты должен проверить,что каждое предложение соответствует правилам русского языка,а каждое слово является осмысленным,а не просто набором букв.Также убедись,что пользователь дает ответ на поставленный вопрос,также проверь,что ни в одном предложении нету имени,отличного от {data0.who}(ИЛИ имя может вовсе отсутствовать).Дальше ты увидишь данные в формате: <Вопрос?-Ответ пользователя>\nДанные:\n<Принимите {data0.who} таким,какой он есть(только положительный смысл)-{data.acceptance}>\n<Выразите благодарность человеку-{data.thank}>\nВерни ТОЛЬКО «Да» если все ответы пользователя соответствуют описанным мною правилам,иначе верни вопрос,на который пользователь дал некорректный ответ."
        }],
           timeout=100
    )
    title = response.choices[0].message.content
    return {"result": title}