import os
from datetime import date

import yt_dlp as youtube_dl
from discord.ext import commands, tasks
from dotenv import load_dotenv

from Games import *
from load_json import *

# https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#bots
# https://discordpy.readthedocs.io/en/stable/api.html#discord.Message

load_dotenv()
TOKEN = os.getenv("TOKEN")
#john_pork_calling = "audio/john_pork_calling.mp3"
john_pork_calling = "donne.mp3"
message_reward = 1
daily_reward = 20
bad_word_penalty = 10

intents = discord.Intents.default()
intents.messages = True
intents.members = True  # Enable the members intent
intents.message_content = True  # Required for reading message content
intents.reactions = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

song_queue = asyncio.Queue()
is_playing = False
voice_client = None
active_users = set()

def in_allowed_channel(ctx):
    return ctx.channel.id == channels["commands"]

def get_user_from_id(id: int) -> User:
    try:
        return users[str(id)]
    except:
        return None

def play_sound(voice_client: discord.VoiceClient, sound: str):
    if os.path.isfile(john_pork_calling):
        audio_source = discord.FFmpegPCMAudio(john_pork_calling)
        voice_client.play(audio_source, after=lambda e: print(f"Finished playing sound: {e}"))
    else:
        print("File " + sound + " not found")

#region BOT EVENT
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="Devant ta porte..."))
    bot.loop.create_task(porklard_voc())
    periodic_save.start()

@bot.event
async def on_reaction_add(reaction, user):
    if str(reaction.emoji) == '🔫' and not user.bot:
        await reaction.remove(user)
    print(f"reaction is {reaction}\n")

@bot.event
async def on_message(message):
    print("MESSAGE SENT : ", message.content)

    rand = rd.random()
    threshold = 0.025  # once every 40 messages

    if not message.attachments and message.content[0] in ['!', ',', '/']:
        print('Processing command')
        await bot.process_commands(message)  # Allow command processing
        return

    print(f"message guild :  {message.guild}")
    if not message.author.bot and message.guild is not None:
        user = get_user_from_id(message.author.id)
        if message.channel.id == channels["daily"] and user.get_daily() != date.today() or user.get_daily() == 0:
            give_money(user, message,True)
            user.use_daily(date.today())
            print("give daily_reward")
        else :
            give_money(user, message)
        user.set_previous_message(message.content)

        if rand <= threshold:
            await message.reply(answers[rd.choice(list(answers.keys()))])

        if not message.attachments and (" tg " in message.content.lower() or "ta gueule" in message.content.lower()):
            print("Sent private message to :", message.author.id)
            for _ in range(5):
                await message.author.send("C'EST QUI QUI FERME SA GUEULE MAINTENANT ???")
                await message.author.send(answers["john_pork"])



    print("user id = ", message.author.id)
    print("random number = ", rand)
    print("____________")

@bot.event
async def on_voice_state_update(member, before, after):
    voice_client = member.guild.voice_client

    general = discord.utils.get(member.guild.text_channels, id=channels["general"])

    # Check if the member joined a voice channel
    if not before.channel and after.channel and not member.bot:
        user = get_user_from_id(member.id)

        if user and user.get_porklards() < 0:
            await member.move_to(None)
            await general.send(f'{member.mention} t\'as pas la thune gros mdrr donc tu voc pas. POV ton argent : {user.get_porklards()}. Ptet falloir faire un emprunt ;)')

    # Check if the member deafened themselves
    elif not before.self_deaf and after.self_deaf:
        target_channel = discord.utils.get(member.guild.voice_channels, id=channels["lecons_sage"])

        if target_channel:
            await member.move_to(target_channel)
        if not voice_client:  # If the bot isn't in any voice channel
            await target_channel.connect()  # Bot joins the target channel
            print("Bot has joined the channel.")
        elif voice_client.channel != target_channel:
            await voice_client.move_to(target_channel)

        else:
            print("Target channel not found!")

    # Check if user undeafened themselves
    elif before.self_deaf and not after.self_deaf:
        target_channel = discord.utils.get(member.guild.voice_channels, id=channels["lecons_sage"])
        print(f"voice client : {voice_client}")
        if target_channel and member.voice.channel == target_channel and voice_client and voice_client.channel == target_channel:
            print("Sound can be played")
            play_sound(voice_client, john_pork_calling)
            while voice_client.is_playing():
                await asyncio.sleep(1)
            await voice_client.disconnect()
            print("Bot disconnected")

        else:
            print("At least one condition was not met")

    # Check if user left a channel
    elif before.channel and not after.channel and not member.bot:  # The member was in a channel and now left
        if before.channel.guild.me in before.channel.members and len([m for m in before.channel.members if not m.bot]) == 1:
            await voice_client.disconnect()
        if general:
            rand = rd.random()
            threshold = 0.02  # 1 every 50 disconnects
            if rand <= threshold:
                await general.send(f"{member.mention} bah alors ça rage mdrrrrr")

@bot.event
async def on_member_join(member):
    if not member.bot and not str(member.id) in users.keys():
        user = User(member.name, member.id, 0, 0)
        users[str(member.id)] = user
        user.save_state()
        print(f'Member {member.name} joined the server')
#endregion


def get_audio_source(url):
    ydl_opts = {
        'format': 'bestaudio',
        'noplaylist': True,
        'nocheckcertificate': True,
        'outtmpl': 'temp/temp_audio.%(ext)s',
        'max_filesize': 50 * 1024 * 1024,  # 50 MB
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }]
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_file = ydl.prepare_filename(info)
            base, ext = os.path.splitext(audio_file)
            return f"{base}.m4a"
    except youtube_dl.DownloadError as e:
        print(f"Download error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

async def play_next(ctx):
    global is_playing, voice_client
    is_playing = True
    while not song_queue.empty():
        url = await song_queue.get()
        audio_file = get_audio_source(url)
        if audio_file is None:
            await ctx.send("A pas marché, choisis de meilleures musiques ptet ? ")
            continue
        if voice_client is None or not voice_client.is_connected():
            await ctx.send("Bot pas connecté au voc")
            is_playing = False
            return
        if voice_client.is_playing():
            voice_client.stop()
        try:
            voice_client.play(discord.FFmpegPCMAudio(audio_file), after=lambda e: bot.loop.call_soon_threadsafe(asyncio.create_task, play_next(ctx)))
            while voice_client is not None and voice_client.is_connected() and voice_client.is_playing():
                await asyncio.sleep(1)
        except Exception as e:
            await ctx.send(f"A pas marché, choisis de meilleures musiques ptet ?: {e}")
            print(f"Playback error: {e}")
    is_playing = False


@bot.command()
async def play(ctx, url: str):
    global voice_client
    if ctx.author.voice is None:
        await ctx.send("Faut être dans un voc chacal")
        return
    channel = ctx.author.voice.channel
    if voice_client is None:
        voice_client = await channel.connect()
    elif voice_client.channel != channel:
        await voice_client.move_to(channel)
    await song_queue.put(url)
    if not is_playing:
        bot.loop.create_task(play_next(ctx))

@bot.command()
async def skip(ctx):
    global voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send('Hop ça dégage la musique de merde')
    else:
        await ctx.send('Pas de musique en cours, faut suivre :) ')

@bot.command()
async def stop(ctx):
    global voice_client
    if voice_client:
        await voice_client.disconnect()
        voice_client = None
        await ctx.send('Me casse')
    else:
        await ctx.send('Jsuis pas dans un voc mon reuf')

@bot.command(aliases=['p'])
@commands.check(in_allowed_channel)
async def porklards(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    user = get_user_from_id(member.id)
    if user is not None:
        await ctx.send(f'Porklards : {user.get_porklards()}')
    else:
        await ctx.send("Deso gros il existe pas ce type")

""" @bot.command()
async def stp_argent(ctx):
    user = get_user_from_id(ctx.author.id)
    if user is not None and user.get_porklards() < 0:
        user.add_porklards(- user.get_porklards()) """
@bot.command(aliases=['s'])
async def shop(ctx):

    embed = discord.Embed(
        title="Porkshop",
    )
    embed.add_field(name="200 🍀", value="+20% de chance de gagner au gamble sur les 5 prochains tirages (ne stack pas)", inline=False)
    embed.add_field(name="1019 📨", value="Discute avec john pork", inline=False)
    embed.add_field(name="5001 📃", value="Apprend quelque chose a john pork", inline=False)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction('🍀')
    await msg.add_reaction('📨')
    await msg.add_reaction('📃')

    def check(reaction, user):
        return str(reaction.emoji) in ['🍀','📃','📨'] and reaction.message.id == msg.id and not user.bot
    
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=300, check=check)

    except asyncio.TimeoutError:
        await ctx.send("shop fermé j'ai pas que ça à foutre")
    
    user = get_user_from_id(user.id)
    reaction = str(reaction.emoji)
    if reaction == '🍀':
        if user.get_porklards() < 200:
            await ctx.send(f"{user.get_username()} trop pauvre pour ça connard")
        else:
            user.add_porklards(-200)
            user.set_enhanced_gambles(5)
    if reaction ==  '📨':
        if user.get_porklards() < 1019:
            await ctx.send(f"{user.get_username()} trop pauvre pour ça connard")
        else:
            user.add_porklards(-1019)
            await ctx.author.send("Dis moi ce que tu veux que je dise dans le général")
            def check(m):
                return m.author == ctx.author and m.guild is None

            try:
                message = await bot.wait_for('message', timeout=30.0, check=check)
                general = discord.utils.get(ctx.guild.text_channels, id=channels["general"]) 
                if general: 
                    await general.send(message.content)
            except asyncio.TimeoutError:
                await ctx.send("Trop lent, annulé !")
                user.add_porklards(1000)
    if reaction == '📃':
        if user.get_porklards() < 5001:
            await ctx.send(f"{user.get_username()} trop pauvre pour ça connard")
        else:
            user.add_porklards(-5001)
            await ctx.author.send("Dis moi ce que tu veux que j'apprenne'")
            def check(m):
                return m.author == ctx.author and m.guild is None

            try:
                message = await bot.wait_for('message', timeout=30.0, check=check)
                add_data(message.content,message.content, "answers.json")
            except asyncio.TimeoutError:
                await ctx.send("Trop lent, annulé !")
                user.add_porklards(1000)


@bot.command(aliases=['c','lb'])
async def classement(ctx, depth=10):
    message = "```Classement des plus gros porcs du serveur : \n"
    users_copy = list(users.values())
    for i in range(depth):
        maxi_user = max(users_copy, key=lambda user: user.get_porklards(), default=None)
        if maxi_user:
            message += f"{i + 1}. {maxi_user.get_username()} : {maxi_user.get_porklards()}\n"
            users_copy.remove(maxi_user)
    message += "```"
    await ctx.send(message)


@bot.command()
@commands.check(in_allowed_channel)
async def give(ctx, member: discord.Member, gift_amount: int):
    user = get_user_from_id(member.id)
    if user is None:
        await ctx.send("Deso gros il existe pas ce type")
    else:
        if (gift_amount <= 0):
            await ctx.send("MAIS T'ES CON ??? RAT DE MERDE DONNE AU MOINS 1 ???")
        else:
            giver = get_user_from_id(ctx.author.id)
            if (giver.get_porklards() < gift_amount):
                await ctx.send("Mais tu te prends pour qui en vrai ? T'es juste pauvre")
            else:
                giver.add_porklards(-gift_amount)
                user.add_porklards(gift_amount)
                await ctx.send(f"T'es vrm trop sympa t'as donné {gift_amount}, mtn t'as {giver.get_porklards()}")

@bot.command(aliases=['rr'])
async def russian_roulette(ctx, targeted_member: discord.Member, amount : int):
    await start_rr(ctx, targeted_member, amount, bot, get_user_from_id)

@bot.command(aliases=['g'])
@commands.check(in_allowed_channel)
async def gamble(ctx, amount=10):
    await start_gamble(ctx, amount, get_user_from_id)

@bot.command(aliases=['bj'],help="play blackjack")
async def blackjack(ctx, amount : int = 10):
    await playBJ(ctx, amount,bot,get_user_from_id)
#region Admin Command
@bot.command()
async def pork(ctx):
    if not get_user_from_id(ctx.author.id).is_admin():
        await ctx.author.send("On rigole on met des Gifs mais la vie de ma mère la prochaine fois que t'envoies un message je te retrouve et je vide ton frigo")
        return

    channel = await bot.fetch_channel(channels["voice_main"])
    for user in channel.members:
        await user.edit(mute=True)
@bot.command()
async def unpork(ctx):
    if not get_user_from_id(ctx.author.id).is_admin():
        await ctx.author.send("On rigole on met des Gifs mais la vie de ma mère la prochaine fois que t'envoies un message je te retrouve et je vide ton frigo")
        return

    channel = await bot.fetch_channel(channels["voice_main"])
    for user in channel.members:
        await user.edit(mute=False)
@bot.command(name='add_missing_members', help="add missing members")
async def add_missing_members(ctx):
    print("add_missing_members command triggered!")
    if (get_user_from_id(ctx.author.id).is_admin()):
        for guilde in bot.guilds:
            for member in guilde.members:
                if not member.bot and not str(member.id) in users:
                    user = User(member.name, member.id, 0, 0)
                    users[member.id] = user
                    user.save_state()
@bot.command(aliases=['cc'],help="remove user from classement")
async def clearclassement(ctx):
    if not get_user_from_id(ctx.author.id).is_admin():
        await ctx.author.send("On rigole on met des Gifs mais la vie de ma mère la prochaine fois que t'envoies un message je te retrouve et je vide ton frigo")
        return
    member_ids = {str(member.id) for member in ctx.guild.members}
    memberToRemove = []
    for user in users.keys():
        if user not in member_ids:
            memberToRemove.append(user)
    for user in memberToRemove:
        del users[user]
    print("clear effectue")
#endregion
@bot.command()
async def call(ctx):
    global voice_client
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if voice_client is None or voice_client.channel != channel:
            voice_client = await channel.connect()
        if sounds:
            first_sound_url = list(sounds.values())[0]
            await song_queue.put(first_sound_url)
            if not is_playing:
                bot.loop.create_task(play_next(ctx))
        else:
            await ctx.send("Aucun son disponible")
    else:
        await ctx.send("Tu dois être dans un voc")


def give_money(user: User, message: discord.Message,isDaily = False):
    if len(message.content) > 1 and user.get_previous_message() != message.content:
        if not message.attachments:
            computed_bad_words_penalty = compute_bad_words_penalty(user, message)
        gain = daily_reward if isDaily else message_reward
        print(isDaily)
        user.add_porklards(gain + computed_bad_words_penalty)

def compute_bad_words_penalty(user: User, message: discord.Message) -> int:
    with open("insults.txt", 'r', encoding='utf-8') as file:
        bad_words = {line.strip().lower() for line in file}

    bad_words_count = 0
    words = message.content.lower().split(" ")
    for word in words:
        if word in bad_words:
            bad_words_count += 1
    print(f'Bad words detected : {bad_words_count}')
    return -bad_words_count * bad_word_penalty

def save_users():
    for user in users.values():
        user.save_state()
    print("User data saved")

@tasks.loop(minutes=15)
async def periodic_save():
    await bot.wait_until_ready()
    save_users()

@bot.command()
async def force_save(ctx):
    if (get_user_from_id(ctx.author.id).is_admin()):
        save_users()
    else:
        await ctx.author.send("On rigole on met des Gifs et tout mais la vie de ma ptn de mère la prochaine fois que t'essaies de faire une commande admin je te retrouve et je vide ton frigo")

@bot.listen('on_voice_state_update')
async def check_empty_channel(member, before, after):
    if before.channel and not after.channel:
        voice_client = member.guild.voice_client
        if voice_client and voice_client.channel == before.channel:
            humans = [m for m in before.channel.members if not m.bot]
            if len(humans) == 0:
                await voice_client.disconnect()

async def porklard_voc(delay = 60):
    while True:
        if active_users:
            for user_id in active_users:
                currUser = get_user_from_id(user_id)
                currUser.add_porklards(1)
        await asyncio.sleep(delay)

@bot.listen('on_voice_state_update')
async def add_porklard_voc(member,before,after):
    if member.bot :
        return
    if (not before.self_mute and not before.self_deaf ) and (after.self_mute or after.self_deaf )and active_users.__contains__(member.id):
        active_users.discard(member.id)
    if (before.self_mute or  before.self_deaf) and (not after.self_mute and not after.self_deaf):
        active_users.add(member.id)

    if not before.channel and after.channel:
        active_users.add(member.id)

    elif before.channel and not after.channel:
        active_users.discard(member.id)


@bot.command()
async def start_v_serv(ctx):
    valheim_service_status = os.system('systemctl is-active --quiet valheim.service')
    if valheim_service_status != 0: #aka is inactive
        os.system('sudo systemctl start valheim.service')
    else:
        await ctx.send("Le serveur est deja lance mgl")

bot.run(TOKEN)
