import discord
from discord.ext import commands


class help_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.help_message = """
        >>> __***General commands:***__

***!&help***,***!&h*** - Show all comands in this bot
***!&play <keywords>***,*** !&p <keywords>*** - Play selected song from yt to voice channel where you are,
***!&pause***,***!&ps*** - Pause current song
***!&resume***,***!&rs***,***!&r*** - Resume current song
***!&skip***,***!&s*** - Skip current song
***!&queue***,***!&q***,***!&que*** - Show queue of added songs ( max 4 )
***!&clear***,***!&clr***,***!&c*** - Clear music queue
***!&leave***,***!&quit***,***!&disconnect*** - Kick out music bot from channel
"""
        self.text_channel_text = []

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for channel in guild.text_channels:
                self.text_channel_text.append(channel)
        await self.send_to_all(self.help_message)

    async def send_to_all(self, msg):
        for text_channels in self.text_channel_text:
            await text_channels.send(msg)

    @commands.command(name="help", aliases=["h"], help="Display all available commands")
    async def help(self, ctx):
        await ctx.send(self.help_message)
