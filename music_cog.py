import discord
from discord.ext import commands
# from youtube_dl import YoutubeDL
import yt_dlp


class music_cog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.playing, self.is_paused = False, False

        self.music_queue = []
        # self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.YDL_OPTIONS = {
            'format': 'm4a/bestaudio/best',
            'ratelimit': 500000,
            'throttledratelimit': 100000,
            'ignoreerrors': True,
            'buffersize': 32,
            # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
            'postprocessors': [{  # Extract audio using ffmpeg
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }]}

        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.vc = None

    def search_yt(self, item):
        with yt_dlp.YoutubeDL(params=self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(item, download=False)

            except Exception:
                return False
        return {'source': info['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.playing = True
            url = self.music_queue[0][0]['source']
            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(
                url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.playing = False

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.playing = True
            url = self.music_queue[0][0]['source']
            if self.vc == None or not self.vc.is_connected():  # sprawdanie czy połączyliśmy się do kanału głosowego
                self.vc = await self.music_queue[0][1].connect()

                if self.vc == None:
                    await ctx.send("Couldn't conenct to the voice channel")
                    return
            else:
                # po zmianie kanału głosowego przestaje grać muzyka
                await self.vc.move_to(self.music_queue[0][1])

            self.music_queue.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(
                url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next())
        else:
            self.playing = False

    @commands.command(name="play", aliases=["p"], help="play song from yt")
    async def play(self, ctx, *args):
        que = " ".join(args)  # przechowywanie danych o utworze w kolejce

        # sprawdzenie czy osoba wywołująca metodę jest na kanale głosowym
        try:
            voice_channel = ctx.author.voice.channel
            if voice_channel is None:
                raise Exception
            elif self.is_paused:  # jesli urzytkownik zapauzował utwór to w takim wypadku włączy ponownie dany utwór
                self.vc.resume()
            else:
                song = self.search_yt(que)  # wyszukanie danego utworzu

                if type(song) == type(True):
                    await ctx.send("couldn't download the song, Incorrect format, try diffrent keyword")
                else:
                    await ctx.send("song added to queue")
                    # dodanie do kolejni danego utworu który będzie grał w danym kanale głosowym
                    self.music_queue.append([song, voice_channel])

                    if self.playing == False:  # jeśli nie gra żaden utwór to włacz utwór
                        await self.play_music(ctx)
        except Exception:
            await ctx.send(f"{ctx.message.author.mention} Please connect to the voice channels to play songs")

    @commands.command(name="pause", aliases=["ps"], help="pause song from yt")
    async def pause(self, ctx, *args):
        if self.playing:
            self.playing = False
            self.is_paused = True
            self.vc.pause()
        else:
            self.is_paused = False
            self.playing = True
            self.vc.resume()

    @commands.command(name="resume", aliases=["rs", "r"], help="resume song from yt")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.playing = True
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="skip song from yt")
    async def skip(self, ctx, *args):
        if self.vc != None and self.vc:
            self.vc.stop()
            self.play_music(ctx)

    @commands.command(name="queue", aliases=["q", "que"], help="queue song from yt")
    async def queue(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue)):
            if i > 4:
                break
            retval += self.music_queue[i][0]['title']+'\n'

        if retval != '':
            await ctx.send(retval)
        else:
            await ctx.send("queue is empty")

    @commands.command(name="clear", aliases=["clr", "c"], help="stop song from yt and clear queue")
    async def clear(self, ctx, *args):
        if self.vc != None and self.playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Cleared music queue")

    @commands.command(name="leave", aliases=["disconnect", "quit"], help="Quit bot from chanel")
    async def leave(self, ctx):
        self.playing = False
        self.is_paused = False
        await self.vc.disconnect()
