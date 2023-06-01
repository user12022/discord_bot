import discord, json, time

with open("database.json","r",encoding="utf-8") as file:
    Users = json.loads(file.read())[0]
    file.close()

with open("database.json","r",encoding="utf-8") as file:
    Tasks = json.loads(file.read())[1]
    file.close()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(command_prefix='!', intents=intents)
prefix = "!" 
priveleged = ["admin","owner"]

'''
User:
status:???
user_id:???
tasks_id:???
extra:???
money:???
Task:
id:???
author:???
music:???
link:???
done:???
time:???
money:???
approved:???
links:???
'''

@client.event
async def on_ready():
    print("start")
 
async def error(channel, content):
    await channel.send(embed=discord.Embed(
        title="Ошибка",
        description=content,
        color=discord.Color.red())
    )

async def money(message):
    await message.channel.send(embed=discord.Embed(
        title="Выплаты",
        description="- " + "\n- ".join([str(value["user_id"]) + " - " + str(value["money"]) + "€" for (value) in Users]),
        color=discord.Color.blue()
    ))

async def applies(message):
    await message.channel.send(embed=discord.Embed(
        title="Запросы на вступление",
        description="- " + "\n- ".join([str(value["user_id"]) for value in Users if (value["status"] == "applied")]),
        color=discord.Color.blue()
    ))

async def finished(message, User):
    try:
        soundLink = message.content.split(" ")[1]
        videoLink = message.content.split(" ")[2]
        Task = [value for value in Tasks if (value["link"] == soundLink)]
        if (Task) and (Task[0]["id"] in User["tasks_id"]):
            Task = Task[0]
            Task["links"].append({
                "link":videoLink,
                "approved":False,
                "user":message.author.id
            })
            User["tasks_id"].remove(Task["id"])
            if ((time.time()-Task["time"][-1])/3600>24):
                User["extra"] += "|late:" + str(24-((time.time()-Task["time"][-1])/3600)) + "h"
                await message.channel.send(embed=discord.Embed(
                    title=":X:",
                    description="опоздание на " + str(24-((time.time()-Task["time"][-1])/3600)).split(".")[0] + " часов!",
                    color=discord.Color.green()
                ))
            await message.channel.send(embed=discord.Embed(
                title="Успешно :white_check_mark:",
                description="Спасибо за коорпорацию!\nВидео проверяется...",
                color=discord.Color.green()
            ))
        else: await error(message.channel, "Такой задачи нету")
    except: await error(message.channel, "Неправильный синтаксис, !help для больше информации")

async def get_task(message, User):
    Task = []
    for (value) in Tasks:
        if (len(value["done"]) < 3):
            Task = value
            break
    if (Task) and (len(User["tasks_id"]) < 3):
        await message.channel.send(embed=discord.Embed(
            title="Вам назначена задача",
            description="Время: **24 часа**\nПлата: **" + str(Task["money"]) + "€**\nCсылка:\n" + Task["link"] + "\n**" + Task[
                "music"] + " - " + Task["author"] + "**",
            color=discord.Color.green()
        ))
        Task["time"].append(time.time())
        User["tasks_id"].append(Task["id"])
    else: 
        if (len(User["tasks_id"]) == 2): await error(message.channel, "У вас не может быть больше двух открытых задач")
        else: await error(message.channel, "На данный момент нету открытых задач")

async def add_task(message, channel):
    newTasks = [value.split(",") for value in message.split("|")]
    for (value) in newTasks:
        Tasks.append({
            "id":Tasks[-1]["id"] + 1,
            "author":value[0],
            "music":value[1],
            "link":value[2],
            "done":[],
            "time":[],
            "money":value[3],
            "links":[]
        })
        await channel.send(embed=discord.Embed(
            title="Добавлена задача :white_check_mark:",
            description="Плата: **" + str(value[3]) + "€**\nCсылка:\n" + value[2] + "\n**" + value[1] + " - " + value[0] + "**",
            color=discord.Color.green()
        ))

async def accept(message):
    try:
        userId = message.content.split(" ")[1]
        found = False
        for (User) in [value for (value) in Users if (value["status"] == "applied")]:
            
            if (int(userId) == User["user_id"]):
                found = True
                User["status"] = "content_creator"
                await message.channel.send(embed=discord.Embed(
                    title="Пользователь успешно принят :white_check_mark:",
                    color=discord.Color.green()
                ))
                user = await client.fetch_user(int(userId))
                await user.send(embed=discord.Embed(
                    title="Добро пожаловать!",
                    description="Вы приняты",
                    color=discord.Color.green()
                ))
        if (not found): await error(message.channel, "Пользователь на найден")
    except: await error(message.channel, "Правильный синтаксис:\n" + prefix + "accept [ID]")

async def join(message):
    if (message.author.id not in [value["user_id"] for value in Users if (value["status"] != "owner")]):
        await message.channel.send(embed=discord.Embed(
            title="Заявка",
            description="Заявка на вступление была успешно отправлена.",
            color=discord.Color.green()
        ))
        Users.append({
            "status":"applied",
            "user_id":message.author.id,
            "tasks_id":[],
            "money":0,
            "extra":""
        })
    else:
        await error(message.channel, "Запрос на отправление заявки был отклонен.")

async def profile(channel, User):
    await channel.send(embed = discord.Embed(
        title="Твой профиль",
        description="Статус: **" + User["status"] + "**\nОжидаемая суммa: **" + str(User["money"]) + "€**\nЗадания:\n- " + "\n- ".join(
            (value["link"] + "\n**" + value[
            "music"] + " - " + value["author"]) + "**"  for value in Tasks if (value["id"] in User["tasks_id"])),
        color=discord.Color.blue()
    ))

async def tasks(message):
    if (Tasks):
        links = []
        for (value) in Tasks:
            for (value2) in value["links"]:
                if (value2["approved"] == False):
                    links.append(value2["link"])
        await message.channel.send(embed=discord.Embed(
            title="Новые задачи на рассмотрение",
            description="- " + "\n- ".join(links) + "",
            color=discord.Color.blue()
        ))
    else: await error(message.channel, "Нету новых задач на рассмотрение")

async def approve(message):
    try:
        link = message.content.split(" ")[1]
        for (value) in Tasks:
            for (value2) in value["links"]:
                if (value2["link"] == link):
                    if (value2["approved"]): await error(message.channel, "Видео уже принято")
                    else:
                        value2["approved"] = True
                        User = [value3 for value3 in Users if (value3["user_id"] == value2["user"])][0]
                        value["done"].append(User["user_id"])
                        User["money"] += float(value["money"])
                        user = await client.fetch_user(value2["user"])
                        await user.send(embed=discord.Embed(
                            title="Вашо видео принято:white_check_mark:",
                            description="Теперь ваше видео должно собрать как минимум 100 просмотров за следующие 5 дня\n**+" + str(value["money"]) + "€**",
                            color=discord.Color.green()
                        ))
                        await message.channel.send(embed=discord.Embed(
                            description="Видео успешно принято",
                            color=discord.Color.green()
                        ))
    except: await error(message.channel, "неправильный синтаксис")

async def decline(message):
    try:
        link = message.content.split(" ")[1]
        for (value) in Tasks:
            for (value2) in value["links"]:
                if (value2["link"] == link):
                    user = await client.fetch_user(value2["user"])
                    del value2
                    await user.send(embed=discord.Embed(
                        title=":X:",
                        description="Вашо видео не принято",
                        color=discord.Color.red()
                    ))
                    await user.send(embed=discord.Embed(
                        description="Видео успешно отклонено",
                        color=discord.Color.red()
                    ))
    except: await error(message.channel, "неправильный синтаксис")

async def null(message):
    for (value) in Users:
        value["money"] = 0.
    await message.channel.send("**все счета обнулены**")

@client.event
async def on_message(message):
    if (message.author == client.user):
        return
 
    if (message.content == (prefix + "apply")):
        await join(message)

    if (message.content == prefix + "help"):
        await message.channel.send(embed=discord.Embed(
            title="Инструкция",
            description="!apply - подать заявку на вступление\n!get task - получить задание\n!finished [ссылка на песню] [ссылка на видео]\n!profile - посмотреть свой профиль",
            color=discord.Color.blue()
        ))

    # users
    
    Continue = False
    for (value) in ["add task", "finished", "accept", "approve", "decline", "set"]:
        if (message.content.startswith(prefix + value)):
            Continue = True

    if (message.content in [prefix + value for value in [
        "applies", "get task", "profile" ,"tasks", "save", "money","null"
            ]]) or (Continue):
        User = [value for value in Users if (value["user_id"] == (message.author.id))]
        if (User):
            User = User[0]
            if (User["status"] in priveleged + ["content_creator"]):
                if (message.content == prefix + "get task"):
                    await get_task(message, User)
                if (message.content.startswith(prefix + "finished ")):
                    await finished(message, User)
                if (message.content == prefix + "profile"):
                    await profile(message.channel, User)
            else: await error(message.channel, "У вас не достаточно прав, чтобы использовать эту команду")
            if (User["status"] in priveleged):
                if (message.content == prefix + "applies"):
                    await applies(message)
                if (message.content.startswith(prefix + "add task ")):
                    await add_task(message.content.replace(prefix + "add task ",""), message.channel)
                if (message.content.startswith(prefix + "accept ")):
                    await accept(message)
                if (message.content == prefix + "tasks"):
                    await tasks(message)
                if (message.content == prefix + "money"):
                    await money(message)
                if (message.content.startswith(prefix + "approve ")):
                    await approve(message)
                if (message.content.startswith(prefix + "decline ")):
                    await decline(message)
                if (message.content == prefix + "null"):
                    await null(message)

                if (User["status"] == "owner"):
                    if (message.content.startswith(prefix + "set")):
                        userId = message.content.split(" ")[1]
                        newRole = message.content.split(" ")[2]
                        for (value) in Users:
                            if (value["user_id"] == int(userId)):
                                value["status"] = newRole
                        await message.channel.send(userId + " теперь " + newRole + "!")
                
                if (message.content == prefix + "save"):
                    with open("database.json","w",encoding="utf-8") as file:
                        json.dump([Users, Tasks], file)
                        file.close()
                    await message.channel.send("Saved.")
    
client.run('MTExMzgwOTUyMjA3OTgyNjA1Mg.G2RVNd.wsutBuyaneMCb1ukmFPifI7h7Us07lkgpZrt4Y')