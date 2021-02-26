import random
import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import socket
import time

import autocomplete as auto

import sqlite3

from datetime import date

import chatbot

conn = sqlite3.connect('rolestorage.db')
c = conn.cursor()
print('roles database loaded')

lbconn = sqlite3.connect("lb.db")
lbc = lbconn.cursor()
print("leaderboard database loaded")
'''
c.execute("""CREATE TABLE roles (

        id text,
        role_ids text

    )""")
'''
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='/', intents=intents)

prefix = '/'

bot.remove_command('help')

message_count = 0

russianRouletteActive = False

@bot.event
async def on_member_join(member):
    print(F"{member.name} has joined")

    lbc.execute("SELECT id FROM lb")
    user_ids = [int(x[0]) for x in lbc.fetchall()]
    lbc.execute("SELECT score FROM lb")
    win_counts = [int(x[0]) for x in lbc.fetchall()]
    lbArray = {user_ids[i] : win_counts[i] for i in range(len(user_ids))}
    if member.id in list(lbArray.keys()):
        lbArray.pop(member.id)
    await lbupdate(lbArray)

    c.execute("SELECT role_ids FROM roles WHERE id = '{}'".format(member.id))
    user_roles = str(c.fetchone())
    print(user_roles)
    user_roles = user_roles.replace('(', '').replace(')', '').replace("'", '').replace('[', '').replace(']', '').replace(',', '').split(' ')

    guild = bot.get_guild(799144167728480288)

    user_roles = [get(guild.roles, id=int(x)) for x in user_roles]

    print(user_roles)
    for i in range(len(user_roles)):
        if user_roles[i].id != 799152926433607681:
            await member.add_roles(user_roles[i])

@bot.event
async def on_ready():
    '''
    This function will print when bot has logged on
    '''
    today = date.today()
    d = today.strftime('%d/%m/%Y')
    print(f'bot has launched - {d}')

async def help(message, ext):
    channel = message.channel
    if len(ext) == 0:
        help_embed = discord.Embed(
            title = 'Anarchy-Bot Commands :'
        )
        help_embed.add_field(name='Info : ', value='There is no need for capitalization, but if you do, the bot will still process the message.')
        for i in commands:
            help_embed.add_field(name = f'{commands[i]["syn"]}', value=f'{commands[i]["def"]}', inline=False)
        await channel.send(embed=help_embed)
    else:
        if ext in list(commands.keys()):
            out_embed = discord.Embed(
                title = 'Anarchy-Bot Command :'
            )
            out_embed.add_field(name=f'{commands[ext]}')
            await channel.send(out_embed)
        else:
            await channel.send("Sorry, That command does not exist!")

async def clear(message, ext):
    valid_users = [171302222385119232, 272939268576378880, 749033247740002465, 547790984293908483, 294550496579026944, 707394939339800646]
    if message.author.id in valid_users:
        mgs = [] #Empty list to put all the messages in the log
        try:
            number = int(ext[0]) #Converting the amount of messages to delete to an integer
            await message.channel.purge(limit=number + 1)
        except:
            await message.channel.send(f"an error has occured deleting messages {ext[0]}")
    else:
        await message.channel.send("You are not allowed to use this command.")
'''
guild = bot.get_guild(799144167728480288)

streak_roles = {
    5 : get(guild.roles, id=803693656263491634),
    10 : get(guild.roles, id=803692447804031056),
    20 : get(guild.roles, id=803692303432155136),
    30 : get(guild.roles, id=803682524886335498),
    50 : get(guild.roles, id=803693112241291264),
    100 : get(guild.roles, id=803693408177618984)
}
'''

async def russianroulette(message, ext):
    global russianRouletteActive
    if russianRouletteActive == False:
        russianRouletteActive = True
        channel = message.channel
        randChance = random.randint(1, 6) # RANDOM CHANCE FROM 1-6 OF GETTING KILLED
    
        lbc.execute("SELECT id FROM lb")
        user_ids = [int(x[0]) for x in lbc.fetchall()]
        lbc.execute("SELECT score FROM lb")
        win_counts = [int(x[0]) for x in lbc.fetchall()]
        lbArray = {user_ids[i] : win_counts[i] for i in range(len(user_ids))}
        
        if randChance == 1 :
            if message.author.id in list(lbArray.keys()):
                await channel.send(f'<@{message.author.id}> You pull the trigger...')
                time.sleep(1) # GIVE DELAY
                russianRouletteActive = False
                latest_ban = message.author.id
                lbArray.pop(message.author.id)
                await lbupdate(lbArray)
                await message.guild.kick(message.author, reason='You shot yourself in the head')
                await channel.send('And die.')
            else:
                await channel.send(f'<@{message.author.id}> You pull the trigger...')
                time.sleep(1)
                await channel.send('You magically survive.')
                russianRouletteActive = False
                if message.author.id not in list(lbArray.keys()):
                    lbArray[message.author.id] = 1
                else:
                    lbArray[message.author.id] = lbArray[message.author.id]+1

                print(lbArray)
                await lbupdate(lbArray)
        else:
            await channel.send(f'<@{message.author.id}> You pull the trigger...')
            time.sleep(1)
            await channel.send('You survive.')
            russianRouletteActive = False
            if message.author.id not in lbArray.keys():
                lbArray[message.author.id] = 1
            else:
                lbArray[message.author.id] = lbArray[message.author.id]+1

            print(lbArray)
            await lbupdate(lbArray)
    else:
        await message.channel.send("Someone is shooting right now!")

async def genroles(message, ext):
    for user in message.guild.members:
        if not user.bot:
            c.execute("INSERT INTO roles (id, role_ids) VALUES ('{}', '{}')".format(user.id, [i.id for i in user.roles if i.name!='@everyone']))
    conn.commit()

async def get_leaderboard():
    lbc.execute("SELECT id FROM lb")
    user_ids = [int(x[0]) for x in lbc.fetchall()]
    lbc.execute("SELECT score FROM lb")
    win_counts = [int(x[0]) for x in lbc.fetchall()]
    lbArray = {user_ids[i] : win_counts[i] for i in range(len(user_ids))}
    orderedLB = list(lbArray.items())
    orderedLB = sorted(orderedLB, key = lambda x: x[1])
    orderedLB = [i for i in reversed(orderedLB)]
    return orderedLB

async def lbupdate(lbArray):
    lbc.execute("DELETE FROM lb")
    for i in lbArray:
        lbc.execute("INSERT INTO lb (id, score) VALUES ('{}', '{}')".format(i[0], i[1]))
        lbconn.commit()

async def lb(message, ext):
        orderedLB = await get_leaderboard()
        print(orderedLB)
        if len(orderedLB) > 0 :
            lb_embed = discord.Embed( 
                title = 'Russian Roulette Leaderboard'
            )
            lb_embed.add_field(name='These are the top 5 survival streaks', value='Can you beat them?', inline=False)
            [lb_embed.add_field(name='\u200B', value=f'{str(i + 1)}. <@{orderedLB[i][0]}>  -  {orderedLB[i][1]} streak', inline=False) for i in range(len(orderedLB)) if i <5]
            await message.channel.send(embed=lb_embed)
        else:
            await message.channel.send("No one is currently on the leaderboard.")
        await lbupdate(orderedLB)

async def ball8(message, ext):
    await message.channel.send(f"<@{message.author.id}> {chatbot.chatbot_response(''.join(ext))}")

async def streak(message, ext):
    lbc.execute("SELECT id FROM lb")
    user_ids = [int(x[0]) for x in lbc.fetchall()]
    lbc.execute("SELECT score FROM lb")
    win_counts = [int(x[0]) for x in lbc.fetchall()]
    lbArray = {user_ids[i] : win_counts[i] for i in range(len(user_ids))}
    if message.author.id in list(lbArray.keys()):
        await message.channel.send(f"<@{message.author.id}> you have a streak of {lbArray[message.author.id]}.")
    else:
        await message.channel.send(F"<@{message.author.id}> you are not on the leaderboard.")

current_phrase = ""
hidden_phrase = ""

cur_user_id = 0

cur_channel = ''

wrong_count = 0

async def reset_hangman():
    global current_phrase
    global hidden_phrase

    global wrong_count
    global cur_user_id

    global cur_channel

    current_phrase = ""
    hidden_phrase = ""

    cur_channel = ''

    cur_user_id = 0

    wrong_count = 0

async def hangman(message, ext):
    global cur_user_id
    global cur_channel

    if cur_user_id == 0:
        cur_channel = message.channel
        cur_user_id = message.author.id

        await message.author.send(f"Respond to me with the message!")
        await message.channel.send(f"<@{message.author.id}> I have sent you a dm, respond with a phrase/word")
    else:
        await message.channel.send(f"<@{message.author.id}> A hangman game has already started")

async def proc_hangman(phrase):
    global current_phrase
    global hidden_phrase

    global cur_channel

    current_phrase = [i.lower() for i in phrase]
    hidden_phrase = ['_' if i != ' ' else i for i in phrase]

    await cur_channel.send("The game begins! art work done by kate")

    await cur_channel.send(file=discord.File(f'hangman/0.png'))

    await cur_channel.send(' '.join([f'\{i}' if i == '_' else i for i in hidden_phrase]))

async def guess(message, ext):
    global current_phrase
    global hidden_phrase

    global wrong_count
    global cur_user_id

    guess = ' '.join(ext)
    guess = guess.lower()

    if message.author.id != cur_user_id:
        if len(guess) == 1:
            #Guessed a character
            if guess in current_phrase and guess not in hidden_phrase and guess != ' ':
                for i, v in enumerate(current_phrase):
                    if v == guess:
                        hidden_phrase[i] = guess
                await message.channel.send(f"<@{message.author.id}> **{guess.upper()}** is found within the word/phrase! you have {6-wrong_count} tries left.")
                await message.channel.send(file=discord.File(f'hangman/{wrong_count}.png'))
                await message.channel.send(' '.join([f'\{i}' if i == '_' else i for i in hidden_phrase]))
            else:
                await message.channel.send(f"<@{message.author.id}> **{guess.upper()}** is not found within the word/phrase! you have {6-wrong_count} tries left.")
                if wrong_count < 6:
                    wrong_count += 1
                    await message.channel.send(file=discord.File(f'hangman/{wrong_count}.png'))
                    await message.channel.send(' '.join([f'\{i}' if i == '_' else i for i in hidden_phrase]))
                else:
                    await message.channel.send(file=discord.File('hangman/6.png'))
                    await message.channel.send(f"The man has hung for crimes he did not commit!\nAnd it's all the fault of <@{message.author.id}>")
                    await reset_hangman()
        
        else:
            #Guessed the phrase
            if list(guess) == current_phrase:
                await message.channel.send(f"<@{message.author.id}> has guessed the correct answer!\nAnswer: **{guess.upper()}**")
                await reset_hangman()
            else:
                
                if wrong_count < 6:
                    wrong_count += 1
                
                    await message.channel.send(f"<@{message.author.id}> your guess of **{guess.upper()}** was incorrect! you have {6-wrong_count} tries left.")
                
                    await message.channel.send(file=discord.File(f'hangman/{wrong_count}.png'))

                else:
                    await message.channel.send(file=discord.File('hangman/6.png'))
                    await message.channel.send(f"The man has hung for crimes he did not commit!\nAnd it's all the fault of <@{message.author.id}>\nThe answer was: {''.join(current_phrase)}")
                    await reset_hangman()

    else:
        await message.channel.send("You can't guess on your own phrase/word!")

commands = {
    "help" :{
        "syn" : "help or help (command)" ,
        "def" : "will define/give extra info about a command",
        "func" : help
    },
    "clear" :{
        "syn" : "clear (amount)",
        "def" : "Will purge the current chat by amount + 1 (the command itself)",
        "func" : clear
    },
    "russianroulette" :{
        "syn" : "russianroulette",
        "def" : "This command will allow you to spin the chambers of fate.\nThere is a 1/6 chance you will get banned upon use.",
        "func" : russianroulette
    },
    "lb" :{
        "syn" : "lb",
        "def" : "Shows the leaderboard for russian roulette",
        "func" : lb
    },
    "generateroles":{
        "syn" : "generateroles",
        "def" : "Generates the role database",
        "func" : genroles
    },
    "streak":{
        "syn":"streak",
        "def" : "gets your streak count from the database",
        "func": streak
    },
    "hangman":{
        "syn":"hangman",
        "def":"Starts a hangman game.",
        "func":hangman
    },
    "guess":{
        "syn":"guess",
        "def":"Guess the phrase or a character for hangman",
        "func":guess
    },
    "g":{
        "syn":"g",
        "def":"Guess the phrase or a character for hangman",
        "func":guess
    }
}

@bot.event
async def on_message(message):

    global message_count

    global cur_user_id

    if not message.author.bot:
        message_count += 1

    author = message.author
    channel = message.channel
    content = message.content.lower()
    command = content[1:].split(' ')[0]
    ext = content[1:].split(' ')[1:]

    print(f"{message.guild} - {message.channel} - {message.author} : {message.content}")

    if not isinstance(message.channel, discord.channel.DMChannel):

        if content.split(' ')[0] in ['<@!799152926433607681>', '<@799152926433607681>']:
            await ball8(message, ext)

        elif not author.bot and len(content) > 0:
            if content[0] == prefix: # if Is command
                print(f"{author} attempted to use command {content[1:]}")
                if command in list(commands.keys()):
                    await commands[command]["func"](message, ext)
                else :
                    if await auto.autocomp(command) == None:
                        await message.channel.send("Sorry, That command does not exist!")
                    else:
                        if await auto.autocomp(command) != 'russianroulette':
                            await message.channel.send("You may have mistyped something, here is what I think you meant")
                            await commands[await auto.autocomp(command)]["func"](message, ext)
                        else:
                            await message.channel.send("We think you may have mistyped russianroulette\nPlease type it again (Usually would auto-correct but this is too dangerous)")

        if message_count >= 5:
            c.execute("SELECT id FROM roles")
            user_ids = [int(x[0]) for x in c.fetchall()]
            if sorted([member.id for member in message.guild.members if not member.bot]) == sorted(user_ids):
                print("refreshing roles")
                try:
                    c.execute("DROP TABLE roles")
                    conn.commit()
                except:
                    print('table does not exist')
                c.execute("""CREATE TABLE roles (

                id text,
                role_ids text

                )""")
                conn.commit()

                await genroles(message, ext)

                print('roles refreshed')
                message_count = 0

    else:
        if message.author.id == cur_user_id:
            print('proc hangman')
            await proc_hangman(message.content)

bot.run('BOT-KEY')
