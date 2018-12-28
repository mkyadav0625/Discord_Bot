import discord
import time
import asyncio
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
style.use("fivethirtyeight")

client = discord.Client()
token = open("token.txt", "r").read()


def community_report(guild):
    online = 0
    idle = 0
    offline = 0

    for m in guild.members:
        if str(m.status) == "online":
            online += 1
        if str(m.status) == "offline":
            offline += 1
        else:
            idle += 1

    return online, idle, offline


async def user_metrics_background_task():
    await client.wait_until_ready()
    global discordBot_guild
    discordBot_guild = client.get_guild(527612067138502677)
    while not client.is_closed():
        try:
            online, idle, offline = community_report(discordBot_guild)
            with open("usermetrics.csv","a") as f:
                f.write(f"{int(time.time())},{online},{idle},{offline}\n")

            plt.clf()
            df = pd.read_csv("usermetrics.csv", names=['time', 'online', 'idle', 'offline'])
            df['date'] = pd.to_datetime(df['time'],unit='s')
            df['total'] = df['online'] + df['offline'] + df['idle']
            df.drop("time", 1,  inplace=True)
            df.set_index("date", inplace=True)
            df['online'].plot()
            plt.legend()
            plt.savefig("online.png")

            await asyncio.sleep(5)

        except Exception as e:
            print(str(e))
            await asyncio.sleep(5)


@client.event  # event decorator/wrapper
async def on_ready():
    global discordBot_guild
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
	global discordBot_guild
	print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
	if "sentdebot.member_count()" == message.content.lower():
		await message.channel.send(f"```py\n{discordBot_guild.member_count}```")
	elif "hello" in message.content.lower():
		await message.channel.send('Hey there!')
	elif "how are you?" in message.content.lower():
		await message.channel.send('I am good, Thanks!')
		await message.channel.send('How are you doing?')
	elif "sentdebot.logout()" == message.content.lower():
		await client.close()
	elif "sentdebot.community_report()" == message.content.lower():
		online, idle, offline = community_report(discordBot_guild)
		await message.channel.send(f"```Online: {online}.\nIdle/busy/dnd: {idle}.\nOffline: {offline}```")

		file = discord.File("online.png", filename="online.png")
		await message.channel.send("online.png", file=file)

client.loop.create_task(user_metrics_background_task())
client.run(token)