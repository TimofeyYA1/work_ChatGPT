
import asyncio
import g4f

async def get_chatgpt_response():
    response = await g4f.ChatCompletion.create_async(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Привет!"}],
        proxy="user166198:dsolnu@154.16.68.39:5030"


    )
    return response

# Запуск асинхронной функции
response = asyncio.run(get_chatgpt_response())
print(response)