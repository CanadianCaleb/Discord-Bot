import discord
from discord.ext import commands
from discord.utils import get
import asyncio
import time

from datetime import datetime

from mods import chatbot, autocomplete
from data import logging, sql_manip

from commands import help, clear, uptime, russianroulette, lb, streak, stats

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='/', intents=intents)

prefix = '/'

bot.remove_command('help')

log = logging.log(datetime.now())
roles = sql_manip.roles()

message_count = 0

@bot.event
async def on_ready():
    d = str(datetime.now())
    print(f'bot has launched - {d}')

@bot.event
async def on_member_join(member):
    """
    This happens whenever the bot recieves the update that someone joins a server.

    : member : Discord.member.
    """
    print(F"{member.name} has joined")

    # Connect to database
    lbconn = sqlite3.connect("lb.db")
    lbc = lbconn.cursor()

    #Simple sqlite commands to gather the roles from the database
    #On member rejoin clear them from the leaderboard
    lbc.execute("SELECT id FROM lb")
    user_ids = [int(x[0]) for x in lbc.fetchall()]
    lbc.execute("SELECT score FROM lb")
    win_counts = [int(x[0]) for x in lbc.fetchall()]
    lbArray = {user_ids[i] : win_counts[i] for i in range(len(user_ids))}
    if member.id in list(lbArray.keys()): lbArray.pop(member.id)
    await lbupdate(lbArray)


    conn = sqlite3.connect('rolestorage.db')
    c = conn.cursor()
    # Gather roles form database
    c.execute("SELECT role_ids FROM roles WHERE id = '{}'".format(member.id))
    user_roles = str(c.fetchone())
    #Reprocess the data gathered into readable format (Yes this is ugly.)
    user_roles = user_roles.replace('(', '').replace(')', '').replace("'", '').replace('[', '').replace(']', '').replace(',', '').split(' ')

    guild = bot.get_guild(799144167728480288)

    user_roles = [get(guild.roles, id=int(x)) for x in user_roles]

    #Reset roles of user if they exist.
    for i in range(len(user_roles)):
        if user_roles[i].id != 799152926433607681:
            await member.add_roles(user_roles[i])

async def genroles(message, ext, log):
    """
    Stores all roles for each user in the server where message is typed.
    """
    global roles
    await roles.create_roles_table()
    await roles.gen_roles(message)
    return log

# The commands dictionary contains the descriptions and the functions connected to each command
commands = {
    "help" : help,
    "uptime" : uptime,
    "clear" : clear,
    "russianroulette": russianroulette,
    "lb" : lb,
    "genroles" : genroles,
    "streak": streak,
    "stats" : stats
}

@bot.event
async def on_message(message):
    """
    This is where messages are processed.
    """
    global message_count
    global roles
    global log
    # Log the message, aswell as count command usage
    print(await log.log(message))

    # Counts messages to see if it should regenerate roles (To compensate for changes)
    message_count += 1

    if message_count >= 30:
        roles.gen_roles()
        message_count = 0

    # Cut message into simpler forms
    content = message.content.lower()
    command, ext = content[1:].split(' ')[0], content[1:].split(' ')[1:]

    # Check if the message is coming from a server (In case of starting hang man)
    if not isinstance(message.channel, discord.channel.DMChannel):

        # If the bot is @'d 
        if content.split(' ')[0] in ['<@!799152926433607681>', '<@799152926433607681>']: await ball8(message, ext)

        elif not message.author.bot and len(content) > 0: # Only looks at message if it is not from a bot and is not an embed
            if content[0] == prefix: # if is command
                # Run the function set to the command in the commands dictionary
                if command in list(commands.keys()): log = await commands[command](message, ext, log)
                else :
                    # Autocomplete found no close matches.
                    if await auto.autocomp(command) == None: await message.channel.send("Sorry, That command does not exist!")
                    else: # Autocomplete found match
                        if await auto.autocomp(command) != 'russianroulette': # Match was not russianroulette, so process command
                            await message.channel.send("You may have mistyped something, here is what I think you meant")
                            log = await commands[await auto.autocomp(command)](message, ext, log)
                        else: await message.channel.send("We think you may have mistyped russianroulette\nPlease type it again (Usually would auto-correct but this is too dangerous) ")

bot.run('BOT-KEY')
