from cmath import log
from distutils.sysconfig import PREFIX
from dotenv import load_dotenv
import os
import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
import time
import asyncio
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from discord.utils import get
from discord import FFmpegPCMAudio
import lxml

load_dotenv()

PREFIX = os.environ['PREFIX']
TOKEN = os.environ['TOKEN']

client = discord.Client()
intents = discord.Intents.all()

prefix = '!'
intents = discord.Intents.all()

def main():
    prefix = '!'
    intents = discord.Intents.all()

    client = commands.Bot(command_prefix=prefix, intents = intents, help_command=None)

    bot = discord.Client(intents=discord.Intents.default())

    user = [] #유저가 입력한 노래 정보
    musictitle = [] # 가공된 정보의 노래 제목
    song_queue = [] # 가공된 정보의 노래 링크
    musicnow = [] # 현재 출력되는 노래 배열

    userF = [] #유저 정보 저장 배열
    userFlist = [] #유저 개인 노래 저장 배열
    allplaylist = [] #플레이리스트 배열

    number = 1

    def title(msg):
        global music

        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        options = webdriver.ChromeOptions()
        options.add_argument("headless")

        chromedriver_dir = "C:/Users/정병찬/Desktop/chromedriver_win32/chromedriver.exe"
        driver = webdriver.Chrome(chromedriver_dir, options = options)
        driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
        source = driver.page_source
        bs = BeautifulSoup(source, 'lxml')
        entire = bs.find_all('a', {'id': 'video-title'})
        entireNum = entire[0]
        music = entireNum.text.strip()
    
        musictitle.append(music)
        musicnow.append(music)
        test1 = entireNum.get('href')
        url = 'https://www.youtube.com'+test1
        with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']

        driver.quit()
    
        return music, URL

    def play(ctx):
        global vc
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        URL = song_queue[0]
        del user[0]
        del musictitle[0]
        del song_queue[0]
        vc = get(bot.voice_clients, guild=ctx.guild)
        if not vc.is_playing():
            vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx)) 
    
    def play_next(ctx):
        if len(musicnow) - len(user) >= 2:
            for i in range(len(musicnow) - len(user) - 1):
                del musicnow[0]
        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        if len(user) >= 1:
            if not vc.is_playing():
                del musicnow[0]
                URL = song_queue[0]
                del user[0]
                del musictitle[0]
                del song_queue[0]
                vc.play(discord.FFmpegPCMAudio(URL,**FFMPEG_OPTIONS), after=lambda e: play_next(ctx))

        else:
            if not vc.is_playing():
                client.loop.create_task(vc.disconnect())

    def load_chrome_driver():
      
        options = webdriver.ChromeOptions()

        options.binary_location = os.getenv('GOOGLE_CHROME_BIN')

        options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')

        return webdriver.Chrome(executable_path=str(os.environ.get('CHROME_EXECUTABLE_PATH')), chrome_options=options)

    @client.event
    async def on_ready():
        print("다음으로 로그인합니다")
        print(client.user.name)
        print('connection was succesful')
        await client.change_presence(status=discord.Status.online, activity=discord.Game("""
        !help를 입력해 도움말 보기
        \ncreator by. 따안"""))

    @client.command()
    async def join(ctx):
        try:
            global vc
            vc = await ctx.message.author.voice.channel.connect()
        except:
            try:
                await vc.move_to(ctx.message.author.voice.channel)
            except:
                await ctx.send("먼저 음성채널에 접속해주세요.")

    @client.command()
    async def leave(ctx):
        try:
            await vc.disconnect()
        except:
            await ctx.send("이미 그 채널에 속해있지 않아요.")

    @client.command()
    async def help(ctx):
        await ctx.send(embed = discord.Embed(title='도움말',description="""
    \n!help -> 뮤직봇의 모든 명령어를 볼 수 있습니다.
    \n!join -> 뮤직봇을 자신이 속한 채널로 부릅니다.
    \n!leave -> 뮤직봇을 자신이 속한 채널에서 내보냅니다.
    \n!URL재생 [노래링크] -> 유튜브URL를 입력하면 뮤직봇이 노래를 틀어줍니다.
    (목록재생에서는 사용할 수 없습니다.)
    \n!play [노래이름] -> 뮤직봇이 노래를 검색해 틀어줍니다.
    \n!end -> 현재 재생중인 노래를 끕니다.
    !stop -> 현재 재생중인 노래를 일시정지시킵니다.
    !restart -> 일시정지시킨 노래를 다시 재생합니다.
    \n!지금노래 -> 지금 재생되고 있는 노래의 제목을 알려줍니다.
    \n!즐겨찾기 -> 자신의 즐겨찾기 리스트를 보여줍니다.
    !즐겨찾기추가 [노래이름] -> 뮤직봇이 노래를 검색해 즐겨찾기에 추가합니다.
    !즐겨찾기삭제 [숫자] ->자신의 즐겨찾기에서 숫자에 해당하는 노래를 지웁니다.
    \n!목록 -> 이어서 재생할 노래목록을 보여줍니다.
    !목록재생 -> 목록에 추가된 노래를 재생합니다.
    !목록초기화 -> 목록에 추가된 모든 노래를 지웁니다.
    \n!대기열추가 [노래] -> 노래를 대기열에 추가합니다.
    !대기열삭제 [숫자] -> 대기열에서 입력한 숫자에 해당하는 노래를 지웁니다.
    \nCreator by. Sina#4229 
    \n문의는 Discord Sina#4229
            Email o060907@citizen.seoul.kr로 주시기 바랍니다.
    \n이 뮤직봇은 Zombie High School의 클랜 Signus를 위하여 제작되었습니다.
    \n since : 2023.02.04  테스트""", color = 0x00ff00))
    
    @client.command()
    async def URL재생(ctx, *, url):

        try:
            global vc
            vc = await ctx.message.author.voice.channel.connect()
        except:
            try:
                await vc.move_to(ctx.message.author.voice.channel)
            except:
                await ctx.send("먼저 음성채널에 접속해주세요.")

        YDL_OPTIONS = {'format': 'bestaudio','noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        if not vc.is_playing():
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
            URL = info['formats'][0]['url']
            vc.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
            await ctx.send(embed = discord.Embed(title= "노래 재생", description = "현재 " + url + "을(를) 재생하고 있습니다.", color = 0x00ff00))
        else:
            await ctx.send("이미 노래가 재생되고 있어요!")
    
    @client.command()
    async def play(ctx, *, msg):

        try:
            global vc
            vc = await ctx.message.author.voice.channel.connect()
        except:
            try:
                await vc.move_to(ctx.message.author.voice.channel)
            except:
                await ctx.send("먼저 음성채널에 접속해주세요.")

        if not vc.is_playing():

            options = webdriver.ChromeOptions()
            options.add_argument("headless")

            global entireText
            YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
            FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            
            chromedriver_dir = "C:/Users/정병찬/Desktop/chromedriver_win32/chromedriver.exe"
            driver = webdriver.Chrome(chromedriver_dir, options = options)
            driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
            source = driver.page_source
            bs = BeautifulSoup(source, 'lxml')
            entire = bs.find_all('a', {'id': 'video-title'})
            entireNum = entire[0]
            entireText = entireNum.text.strip()
            musicurl = entireNum.get('href')
            url = 'https://www.youtube.com'+musicurl 

            driver.quit()

            musicnow.insert(0, entireText)
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url, download=False)
            URL = info['formats'][0]['url']
            await ctx.send(embed = discord.Embed(title= "노래 재생", description = "현재 " + musicnow[0] + "을(를) 재생하고 있습니다.", color = 0x00ff00))
            vc.play(discord.FFmpegPCMAudio(URL, **FFMPEG_OPTIONS), after=lambda e: play_next(ctx))
        else:
            user.append(msg)
            result, URLTEST = title(msg)
            song_queue.append(URLTEST)
            await ctx.send("이미 노래가 재생 중이라 " + result + "을(를) 대기열로 추가시켰어요!")
    
    @client.command()
    async def stop(ctx):
        if vc.is_playing():
            vc.pause()
            await ctx.send(embed = discord.Embed(title= "일시정지", description = musicnow[0] + "을(를) 일시정지 했습니다.", color = 0x00ff00))
        else:
            await ctx.send("지금 노래가 재생되지 않네요.")

    @client.command()
    async def restart(ctx):
        try:
            vc.resume()
        except:
            await ctx.send("지금 노래가 재생되지 않네요.")
        else:
            await ctx.send(embed = discord.Embed(title= "다시재생", description = musicnow[0]  + "을(를) 다시 재생했습니다.", color = 0x00ff00))

    @client.command()
    async def end(ctx):
        if vc.is_playing():
            vc.stop()
            global number
            number = 0
            await ctx.send(embed = discord.Embed(title= "노래끄기", description = musicnow[0]  + "을(를) 종료했습니다.", color = 0x00ff00))
        else:
            await ctx.send("지금 노래가 재생되지 않네요.")

    @client.command()
    async def 지금노래(ctx):
        if not vc.is_playing():
            await ctx.send("지금은 노래가 재생되지 않네요..")
        else:
            await ctx.send(embed = discord.Embed(title = "지금노래", description = "현재 " + musicnow[0] + "을(를) 재생하고 있습니다.", color = 0x00ff00))

    @client.command()
    async def 대기열추가(ctx, *, msg):
        user.append(msg)
        result, URLTEST = title(msg)
        song_queue.append(URLTEST)
        await ctx.send(result + "를 재생목록에 추가했어요!")

    @client.command()
    async def 대기열삭제(ctx, *, number):
        try:
            ex = len(musicnow) - len(user)
            del user[int(number) - 1]
            del musictitle[int(number) - 1]
            del song_queue[int(number)-1]
            del musicnow[int(number)-1+ex]
            
            await ctx.send("대기열이 정상적으로 삭제되었습니다.")
        except:
            if len(list) == 0:
                await ctx.send("대기열에 노래가 없어 삭제할 수 없어요!")
            else:
                if len(list) < int(number):
                    await ctx.send("숫자의 범위가 목록개수를 벗어났습니다!")
                else:
                    await ctx.send("숫자를 입력해주세요!")

    @client.command()
    async def 목록(ctx):
        if len(musictitle) == 0:
            await ctx.send("아직 아무노래도 등록하지 않았어요.")
        else:
            global Text
            Text = ""
            for i in range(len(musictitle)):
                Text = Text + "\n" + str(i + 1) + ". " + str(musictitle[i])
            
            await ctx.send(embed = discord.Embed(title= "노래목록", description = Text.strip(), color = 0x00ff00))

    @client.command()
    async def 목록초기화(ctx):
        try:
            ex = len(musicnow) - len(user)
            del user[:]
            del musictitle[:]
            del song_queue[:]
            while True:
                try:
                    del musicnow[ex]
                except:
                    break
            await ctx.send(embed = discord.Embed(title= "목록초기화", description = """목록이 정상적으로 초기화되었습니다. 이제 노래를 등록해볼까요?""", color = 0x00ff00))
        except:
            await ctx.send("아직 아무노래도 등록하지 않았어요.")

    @client.command()
    async def 목록재생(ctx):

        YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    
        if len(user) == 0:
            await ctx.send("아직 아무노래도 등록하지 않았어요.")
        else:
            if len(musicnow) - len(user) >= 1:
                for i in range(len(musicnow) - len(user)):
                    del musicnow[0]
            if not vc.is_playing():
                play(ctx)
            else:
                await ctx.send("노래가 이미 재생되고 있어요!")

    @client.command()
    async def 즐겨찾기(ctx):
        global Ftext
        Ftext = ""
        correct = 0
        global Flist
        for i in range(len(userF)):
            if userF[i] == str(ctx.message.author.name): #userF에 유저정보가 있는지 확인
                correct = 1 #있으면 넘김
        if correct == 0:
            userF.append(str(ctx.message.author.name)) #userF에다가 유저정보를 저장
            userFlist.append([]) #유저 노래 정보 첫번째에 유저이름을 저장하는 리스트를 만듬.
            userFlist[len(userFlist)-1].append(str(ctx.message.author.name))
        
        for i in range(len(userFlist)):
            if userFlist[i][0] == str(ctx.message.author.name):
                if len(userFlist[i]) >= 2: # 노래가 있다면
                    for j in range(1, len(userFlist[i])):
                        Ftext = Ftext + "\n" + str(j) + ". " + str(userFlist[i][j])
                    titlename = str(ctx.message.author.name) + "님의 즐겨찾기"
                    embed = discord.Embed(title = titlename, description = Ftext.strip(), color = 0x00ff00)
                    embed.add_field(name = "목록에 추가\U0001F4E5", value = "즐겨찾기에 모든 곡들을 목록에 추가합니다.", inline = False)
                    embed.add_field(name = "플레이리스트로 추가\U0001F4DD", value = "즐겨찾기에 모든 곡들을 새로운 플레이리스트로 저장합니다.", inline = False)
                    Flist = await ctx.send(embed = embed)
                    await Flist.add_reaction("\U0001F4E5")
                    await Flist.add_reaction("\U0001F4DD")
                else:
                    await ctx.send("아직 등록하신 즐겨찾기가 없어요.")

    @client.command()
    async def 즐겨찾기추가(ctx, *, msg):
        correct = 0
        for i in range(len(userF)):
            if userF[i] == str(ctx.message.author.name): #userF에 유저정보가 있는지 확인
                correct = 1 #있으면 넘김
        if correct == 0:
            userF.append(str(ctx.message.author.name)) #userF에다가 유저정보를 저장
            userFlist.append([]) #유저 노래 정보 첫번째에 유저이름을 저장하는 리스트를 만듦.
            userFlist[len(userFlist)-1].append(str(ctx.message.author.name))

        for i in range(len(userFlist)):
            if userFlist[i][0] == str(ctx.message.author.name):
            
                options = webdriver.ChromeOptions()
                options.add_argument("headless")

                chromedriver_dir = "C:/Users/정병찬/Desktop/chromedriver_win32/chromedriver.exe"
                driver = webdriver.Chrome(chromedriver_dir, options = options)
                driver.get("https://www.youtube.com/results?search_query="+msg+"+lyrics")
                source = driver.page_source
                bs = BeautifulSoup(source, 'lxml')
                entire = bs.find_all('a', {'id': 'video-title'})
                entireNum = entire[0]
                music = entireNum.text.strip()

                driver.quit()

            userFlist[i].append(music)
            await ctx.send(music + "(이)가 정상적으로 등록되었어요!")

    @client.command()
    async def 즐겨찾기삭제(ctx, *, number):
        correct = 0
        for i in range(len(userF)):
            if userF[i] == str(ctx.message.author.name): #userF에 유저정보가 있는지 확인
                correct = 1 #있으면 넘김
        if correct == 0:
            userF.append(str(ctx.message.author.name)) #userF에다가 유저정보를 저장
            userFlist.append([]) #유저 노래 정보 첫번째에 유저이름을 저장하는 리스트를 만듦.
            userFlist[len(userFlist)-1].append(str(ctx.message.author.name))

        for i in range(len(userFlist)):
            if userFlist[i][0] == str(ctx.message.author.name):
                if len(userFlist[i]) >= 2: # 노래가 있다면
                    try:
                        del userFlist[i][int(number)]
                        await ctx.send("정상적으로 삭제되었습니다.")
                    except:
                        await ctx.send("입력한 숫자가 잘못되었거나 즐겨찾기의 범위를 초과하였습니다.")
                else:
                    await ctx.send("즐겨찾기에 노래가 없어서 지울 수 없어요!")

    @client.event
    async def on_reaction_add(reaction, users):
        if users.bot == 1:
            pass
        else:
            try:
                await Flist.delete()
            except:
                pass
            else:
                if str(reaction.emoji) == '\U0001F4E5':
                    await reaction.message.channel.send("잠시만 기다려주세요. (즐겨찾기 갯수가 많으면 지연될 수 있습니다.)")
                    print(users.name)
                    for i in range(len(userFlist)):
                        if userFlist[i][0] == str(users.name):
                            for j in range(1, len(userFlist[i])):
                                try:
                                    driver.close()
                                except:
                                    print("NOT CLOSED")

                                user.append(userFlist[i][j])
                                result, URLTEST = title(userFlist[i][j])
                                song_queue.append(URLTEST)
                                await reaction.message.channel.send(userFlist[i][j] + "를 재생목록에 추가했어요!")
                elif str(reaction.emoji) == '\U0001F4DD':
                    await reaction.message.channel.send("플레이리스트가 나오면 생길 기능이랍니다.")

    try:
    client.run(TOKEN)
except discord.errors.LoginFailure as e:
    print("Improper token has been passed.")

if __name__ == '__main__':
    main()
