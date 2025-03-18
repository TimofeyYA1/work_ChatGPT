from fastapi import APIRouter, HTTPException, status, Security, UploadFile
from g4f import Client
from fastapi.security import HTTPBearer
from models.schemas import Razvorot1,Razvorot2,Razvorot3
import mimetypes
import shutil
import g4f
import base64
import os
from gigachat import GigaChat

giga = GigaChat(
   credentials="ZGE2NmFmYTYtNjkxYS00ZjMzLWI3ZjUtZTdiMzgwY2NkNGNiOmFiM2MzNmQ2LWJmY2ItNDAxYy1hNTQ1LWQ2ZWExZmUwNmM2Yg==",
   scope="GIGACHAT_API_PERS",
   model="GigaChat",
)
# token = giga.get_token()
router = APIRouter()
Bear = HTTPBearer(auto_error=False)
client = Client()

@router.post("/razvorot/1")
async def negative_scenario(data: Razvorot1):
    # response = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[{"role": "user",
    response = giga.chat(f"Проверь, соответствует ли текст ниже требуемому формату,Если ты уже отвечал на это верни тоже смаое. Формат ответа должен включать три части:Кто? — указание на человека или группу людей.Что делал? — описание действия или события.Моя реакция на это? — описание твоей реакции или эмоций.Если текст соответствует формату, напиши 'Да'. Если нет Верни 'нет',тебе нельзя изменять пример.Пример текста для проверки:({data.who},{data.quality},{data.what_was_he_doing},{data.reaction}),тпакжне проверь,что каждое слово употребляется в русском языке,иначе верни только нет,НЕ ОБЪЯСНЯЙ СВОЙ ОТВЕТ")
    #response = giga.chat(f"Верни только 'Да' , если выполняются все условия, учти каждое условие влияет на результата,если хотя бы одно не выполняется надо вернуть 'нет',также тебе нельзя изменять форму слово (Например, слово 'поддерживающаяся' является только прилагательным) : 1)Если '{data.quality}' являются моральными/психологическими качествами человека 2)Если каждое из слов '{data.quality}' является осмысленным,а не просто буквой или символом 3)Если каждое из слов '{data.quality}' относится к одной из частей речи (прилагательное ИЛИ союз),слова могут относится к разным частям речи 4)Если '{data.what_was_he_doing}' дает ответ на вопрос что делала ИЛИ что делает? 5)Если каждое из слов '{data.what_was_he_doing}' имеет смысл 6)Если среди слов '{data.what_was_he_doing}' есть глагол,проверь хорошо если глагола нет,то это условие не выполняется  7)Если '{data.reaction}' конкретно описывает мою реакцию на что-либо,а не просто уточняет объект действия  8)Если среди слов '{data.reaction}' есть глагол,если глагола нет,то это условие не выполняется    иначе верни только 'нет',не объясняй")
    #     timeout=100
    # )
    title = response.choices[0].message.content
    return {"result": title}

# {
#   "data0": {
#     "who": "Федя",
#     "quality": "Назойливый",
#     "what_was_he_doing": "Все время пристает",
#     "reaction": "Меня это выводит из себя"
#   },
#   "data": {
#     "acceptance": "Дорогой Федя! Я принимаю тебя таким, какой ты есть",
#     "thank": "Спасибо тебе за возможность мне улучшить себя и стать добрее"
#   }
# }
@router.post("/razvorot/2")
async def b_scenario(data0:Razvorot1,data: Razvorot2):
    # response = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[{"role": "user",
    #                 "content": f"Верни только 'Да' , если выполняются все условия, учти каждое условие влияет на результат,если хотя бы одно не выполняется надо вернуть 'нет',также тебе нельзя изменять форму слово (Например, слово 'поддерживающаяся' является только прилагательным),учти имена в примерах не влияют на результат,пример может отличаться от данной информации: 1)Если '{data.scenery}' описывает отношение к кому-либо, например: 'Я всегда добр к Диме' 2)Если {data.scenery} содержит {data0.who} 3)Если {data.reaction} конкретно описывает мою реакцию на что-либо      иначе верни только 'нет',объясни только одно невыполняющееся условие и верни итоговый ответ в конце в формате <Да или <Нет"}],
    #     timeout=100
    # )
    # response = giga.chat(f"Верни только 'Да' , если выполняются все условия, учти каждое условие влияет на результат,если хотя бы одно не выполняется надо вернуть 'нет',также тебе нельзя изменять форму слово (Например, слово 'поддерживающаяся' является только прилагательным),учти имена в примерах не влияют на результат,пример может отличаться от данной информации: 1)Если '{data.scenery}' описывает отношение к кому-либо, например: 'Я всегда добр к Диме' ИЛИ 'Я всегда зол к Вере' 2)Если {data.scenery} содержит имя {data0.who} в любой форме 3)Если {data.reaction} хотя бы косвенно описывает мою реакцию на действие или отношение к нему или описывает мои эмоции     иначе верни только 'нет',объясни только одно невыполняющееся условие и верни итоговый ответ в конце в формате <Да или <Нет")
    response = giga.chat(f"учти ты не можешь изменять это предложение '{data.scenery}' ,верни 'да', если ('{data.scenery}' объясняет мое отношение к '{data0.who}',оно может звучат абстрактно и не давать четкого понимания  ) И  ('{data.scenery}' является понятным и предложением и соответствует нормам русского языка) И  (каждое слово из '{data.scenery}' имеет смысл ,иначе верни 'нет')  иначе верни 'нет'")
    response2 = giga.chat(f"Верни 'да',если,учти что тебе нельзя изменять предложение {data.action}: ('{data.action}' описывает какое-либо действие) И ('{data.action}' является понятным и предложением и соответствует нормам русского языка,иначе верни 'нет') И  (каждое слово из '{data.action}' имеет смысл ,иначе верни 'нет')  иначе верни 'нет'")
    print(response)
    title = response.choices[0].message.content
    title2 = response2.choices[0].message.content
    if "Нет" in title or "Нет" in title2:
        return  {"result": title}
    return {"result": "Да"}


@router.post("/razvorot/3")
async def b_scenario(data0:Razvorot1,data: Razvorot3):
    # response = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[{"role": "user",
    #                 "content": f"Верни только 'Да' , если выполняются все условия, учти каждое условие влияет на результат,если хотя бы одно не выполняется надо вернуть 'нет',также тебе нельзя изменять форму слово (Например, слово 'поддерживающаяся' является только прилагательным),учти имена в примерах не влияют на результат,пример может отличаться от данной информации: 1)Если '{data.scenery}' описывает отношение к кому-либо, например: 'Я всегда добр к Диме' 2)Если {data.scenery} содержит {data0.who} 3)Если {data.reaction} конкретно описывает мою реакцию на что-либо      иначе верни только 'нет',объясни только одно невыполняющееся условие и верни итоговый ответ в конце в формате <Да или <Нет"}],
    #     timeout=100
    # )
    # response = giga.chat(f"Верни только 'Да' , если выполняются все условия, учти каждое условие влияет на результат,если хотя бы одно не выполняется надо вернуть 'нет',также тебе нельзя изменять форму слово (Например, слово 'поддерживающаяся' является только прилагательным),учти имена в примерах не влияют на результат,пример может отличаться от данной информации: 1)Если '{data.scenery}' описывает отношение к кому-либо, например: 'Я всегда добр к Диме' ИЛИ 'Я всегда зол к Вере' 2)Если {data.scenery} содержит имя {data0.who} в любой форме 3)Если {data.reaction} хотя бы косвенно описывает мою реакцию на действие или отношение к нему или описывает мои эмоции     иначе верни только 'нет',объясни только одно невыполняющееся условие и верни итоговый ответ в конце в формате <Да или <Нет")
    response = giga.chat(f"учти ты не можешь изменять это предложение '{data.acceptance}',Верни 'да',если: ({data.acceptance} содержит это имя: {data0.who} в любой форме) И ({data.acceptance} является принятием {data0.who} таким,какой он есть) И ({data.acceptance} несет позитивный смысл) И ('{data.acceptance}' является понятным и предложением и соответствует нормам русского языка,иначе верни 'нет') И  (каждое слово из '{data.acceptance}' имеет смысл ,иначе верни 'нет')  иначе верни 'нет'")
    response2 = giga.chat(f"учти ты не можешь изменять это предложение '{data.thank}',Верни 'да',если: ({data.thank} является благодарностью,именно является ,а не подразумевает благодарность,объясни ответ) И ({data.thank} несет позитивный смысл) И ('{data.thank}' является понятным и предложением и соответствует нормам русского языка,иначе верни 'нет') И  (каждое слово из '{data.thank}' имеет смысл ,иначе верни 'нет')  иначе верни 'нет'")
    title = response.choices[0].message.content
    title2 = response2.choices[0].message.content
    return {"result": title,"result2":title2}
# @router.post("/recognition", response_model=str, status_code=status.HTTP_200_OK)
# async def get_movie_by_screenshot(file: UploadFile):
#     allowed_extensions = [
#         "jpg",
#         "jpeg",
#         "png",
#         "gif",
#         "bmp",
#         "tiff",
#         "webp",
#         "ico",
#         "svg"
#     ]

#     mime_type, _ = mimetypes.guess_type(file.filename)
#     file_extension = mime_type.split("/")[1]
#     if file_extension not in allowed_extensions:
#         raise HTTPException(status_code=400, detail="your file is not a valid image")

#     file_location = f"temporary_images/{file.filename}"

#     with open(file_location, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     with open(file_location, "rb") as image_file:
#         base64_image = base64.b64encode(image_file.read()).decode("utf-8")

#     response = g4f.ChatCompletion.create(
#         model=g4f.models.gpt_4,
#         messages=[{
#             "role": "user",
#             "content": [
#                 {"type": "text", "text": "Дай мне только название фильма, скриншот из которого на изображении "},
#                 {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
#             ]
#         }],

#         timeout=10,  # in secs
#     )
#     os.remove(file_location)

#     print(f"Result:", response)

#     return response