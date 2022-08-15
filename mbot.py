import discord
from discord.ext.commands import Bot
from settings import BOT_TOKEN

from help_cog import help_cog
from music_cog import music_cog
bot = Bot(command_prefix=['!&'])
bot.remove_command('help')
bot.add_cog(help_cog(bot))
bot.add_cog(music_cog(bot))

bot.run(BOT_TOKEN)

