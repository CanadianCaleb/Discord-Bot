from data import logging
import sqlite3

import random
import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import time

commands = {
    "help" :"will define/give extra info about a command",
    "uptime" :"Returns the duration the bot has been online",
    "clear" :"Will purge the current chat by amount + 1 (the command itself)",
    "russianroulette" :"This command will allow you to spin the chambers of fate.\nThere is a 1/6 chance you will get banned upon use.",
    "lb" :"Shows the leaderboard for russian roulette",
    "genroles" :"Generates the database that stores all user roles."
}

async def help(message, ext, log):
    channel = message.channel
    if len(ext) == 0: # This means no part after help
        help_embed = discord.Embed(title = 'Anarchy-Bot Commands :') # Generate the embed for the command list.
        help_embed.add_field(name='Info : ', value='There is no need for capitalization, but if you do, the bot will still process the message.')
        for i in commands: help_embed.add_field(name = f'{i}', value=f'{commands[i]}', inline=False)
        await channel.send(embed=help_embed)
    else:
        if ext in list(commands.keys()):
            out_embed = discord.Embed(title = 'Anarchy-Bot Command :')
            out_embed.add_field(name=f'{commands[ext]}')
            await channel.send(out_embed)
        else: await channel.send("Sorry, That command does not exist!")
    return log

async def clear(message, ext, log):
    if 799144626908954635 in [i.id for i in message.author.roles] and int(ext[0]) <= 100: # Checks for mod role and limits the amount of messages that can be deleted
        try: await message.channel.purge(limit=int(ext[0]) + 1)
        except: await message.channel.send(f"an error has occured deleting messages {ext[0]}")
    else: await message.channel.send("You are not allowed to use this command.")
    return log

async def uptime(message, ext, log):
    await message.channel.send(log.get_uptime())
    return log

async def get_leaderboard():
    lbconn = sqlite3.connect("lb.db")
    lbc = lbconn.cursor()
    try:
        lbc.execute("SELECT id FROM lb")
        user_ids = [int(x[0]) for x in lbc.fetchall()]
        lbc.execute("SELECT score FROM lb")
        win_counts = [int(x[0]) for x in lbc.fetchall()]
        lbArray = {user_ids[i] : win_counts[i] for i in range(len(user_ids))}
        orderedLB = list(lbArray.items())
        orderedLB = sorted(orderedLB, key = lambda x: x[1])
        orderedLB = [i for i in reversed(orderedLB)]
        return orderedLB
    except:
        lbc.execute("""CREATE TABLE lb (

        id text,
        score text

        )""")

async def lbupdate(lbArray):
    lbconn = sqlite3.connect("lb.db")
    lbc = lbconn.cursor()
    lbc.execute("DELETE FROM lb")
    for i in list(lbArray.keys()):
        lbc.execute("INSERT INTO lb (id, score) VALUES ('{}', '{}')".format(i, lbArray[i]))
        lbconn.commit()

async def lb(message, ext, log):
        orderedLB = await get_leaderboard()
        if len(orderedLB) > 0 :
            lb_embed = discord.Embed( 
                title = 'Russian Roulette Leaderboard'
            )
            lb_embed.add_field(name='These are the top 5 survival streaks', value='Can you beat them?', inline=False)
            [lb_embed.add_field(name='\u200B', value=f'{str(i + 1)}. <@{orderedLB[i][0]}>  -  {orderedLB[i][1]} streak', inline=False) for i in range(len(orderedLB)) if i <5]
            await message.channel.send(embed=lb_embed)
        else:
            await message.channel.send("No one is currently on the leaderboard.")
        return log

async def streak(message, ext, log):
    lbc.execute("SELECT id FROM lb")
    user_ids = [int(x[0]) for x in lbc.fetchall()]
    lbc.execute("SELECT score FROM lb")
    win_counts = [int(x[0]) for x in lbc.fetchall()]
    lbArray = {user_ids[i] : win_counts[i] for i in range(len(user_ids))}
    if message.author.id in list(lbArray.keys()):
        await message.channel.send(f"<@{message.author.id}> you have a streak of {lbArray[message.author.id]}.")
    else:
        await message.channel.send(F"<@{message.author.id}> you are not on the leaderboard.")

    return log

async def russianroulette(message, ext, log):
    lbconn = sqlite3.connect("lb.db")
    lbc = lbconn.cursor()
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

    return log
