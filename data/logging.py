from datetime import datetime

class log():
    def __init__(self, start_time):
        self.__messages = []
        self.__start_time = start_time

    async def log(self, message):
        try:
            self.__messages.append(message)
            return f"{message.guild} - {message.channel} - {message.author} : {message.content}"
        except: return "Message logging failed."

    async def get_messages(self): return self.__messages

    async def get_uptime(self): return f"Bot launched at {self.__start_time}\nand has been running for {datetime.now()-self.__start_time}"
