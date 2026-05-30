import os
from datetime import timedelta

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
    try:
        allowed_channels = (channels.get("commands"), channels.get("test"))
        return ctx.channel.id in allowed_channels
    except:
        return False

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
    await LoadCitation(bot)

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

    if not message.attachments and message.content and message.content[0] == '!':
        print('Processing command')
        await bot.process_commands(message)  # Allow command processing
        return

    print(f"message guild :  {message.guild}")
    if not message.author.bot and message.guild is not None:
        await check_debt(message)
        user = get_user_from_id(message.author.id)
        if user is None:
            await add_missing_members(message,True)
        if user.get_daily() != date.today() or user.get_daily() == 0:
            give_money(user, message,True)
            user.use_daily(date.today())
            print("give daily_reward")
        else :
            give_money(user, message)
        user.set_previous_message(message.content)

        if any(term in message.content.lower() for term in ["tu preferes", "tu prefere","tu préfères", "tu préfère"]) and " ou " in message.content :
            options = message.content
            for term in ["tu preferes", "tu prefere","tu préfères", "tu préfère"]:
                options = options.replace(term, "").strip()
            # Diviser par "ou" et choisir aléatoirement une option
            choices = [choice.strip() for choice in options.split(" ou ") if choice.strip()]
            if choices and len(choices) > 1:
                selected_option = rd.choice(choices)
                await message.reply(selected_option)
        elif rand <= threshold or "<@1338630670183956541>" in message.content :
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

    # Check if user left a channel
    if before.channel and not after.channel and not member.bot:  # The member was in a channel and now left
        if before.channel.guild.me in before.channel.members and len([m for m in before.channel.members if not m.bot]) == 1:
            await voice_client.disconnect()
        if general:
            rand = rd.random()
            threshold = 0.02  # 1 every 50 disconnects
            if rand <= threshold:
                await general.send(f"{member.mention} bah alors ça rage mdrrrrr")

    # Check if the member deafened themselves
    elif not before.self_deaf and after.self_deaf:
        target_channel = discord.utils.get(member.guild.voice_channels, id=channels["lecons_sage"])

        if target_channel:
            await member.move_to(target_channel)
        else:
            print("Target channel not found!")

@bot.event
async def on_member_join(member):
    if not member.bot and not str(member.id) in users.keys():
        user = User(member.name, member.id, 0, 0)
        users[str(member.id)] = user
        user.save_state()
        print(f'Member {member.name} joined the server')
#endregion

@bot.command(aliases=['i'])
@commands.check(in_allowed_channel)
async def inventory(ctx, member: discord.Member = None):
    if member is None:
        user = get_user_from_id(ctx.author.id)
    else:
        user = get_user_from_id(member.id)
    
    if user is None:
        await ctx.send("Deso gros il existe pas ce type")
        return

    inventory_items = user.get_inventory()
    if not inventory_items:
        await ctx.send(f"{user.get_username()} n'a rien dans son inventaire")
        return

    embed = discord.Embed(title=f"Inventaire de {user.get_username()}")
    for item in inventory_items:
        embed.add_field(name=f"{item.Get_Item_Icon()} {item.Get_Item_Name()}", value=item.Get_Item_Description(), inline=False)
    await ctx.send(embed=embed)


@bot.command(aliases=['ui'])
@commands.check(in_allowed_channel)
async def use_item(ctx, *item_name):
    user = get_user_from_id(ctx.author.id)
    if user is None:
        return await ctx.send("Deso gros il existe pas ce type")
    cur_inv = user.get_inventory()
    item_name_str = " ".join(item_name)
    for item in cur_inv:
        if item.Get_Item_Name() == item_name_str:
            await item.execute(ctx,bot,user)
            user.remove_item_by_id(item.id)
            await ctx.send(f"tu as utilisé {item.Get_Item_Name()}")
            return
        else :
            print(f"{item_name_str} n'est pas égale a {item.Get_Item_Name()}")
    return await ctx.send("Il est con comme une table votre pote il a rien et il veut faire des dingz")


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

#region item/shop
async def stp_argent(ctx):
    user = get_user_from_id(ctx.author.id)
    if user is not None and user.get_porklards() < 0:
        user.add_porklards(- user.get_porklards())

@bot.command(aliases=['s'])
@commands.check(in_allowed_channel)
async def shop(ctx):
    """Affiche le magasin et gère les achats d'items."""
    user = get_user_from_id(ctx.author.id)

    embed = discord.Embed(title="Porkshop")

    for item in items_list.values():
        dynamic_price = item.Get_Item_Price(user.get_porklards())
        embed.add_field(
            name=f"{item.Get_Item_Name()} | {int(dynamic_price)} {item.Get_Item_Icon()}",
            value=item.Get_Item_Description(),
            inline=False
        )

    msg = await ctx.send(embed=embed)
    possible_react = set()

    for item in items_list.values():
        icon = item.Get_Item_Icon()
        await msg.add_reaction(icon)
        possible_react.add(icon)

    def check(reaction, user_react):
        return str(reaction.emoji) in possible_react and reaction.message.id == msg.id and not user_react.bot

    try:
        reaction, reacting_user = await bot.wait_for('reaction_add', timeout=300, check=check)
    except asyncio.TimeoutError:
        await ctx.send("shop fermé j'ai pas que ça à foutre")
        return

    user = get_user_from_id(reacting_user.id)
    reaction_emoji = str(reaction.emoji)

    # Trouver l'item correspondant à la réaction
    selected_item = None
    for item in items_list.values():
        if item.Get_Item_Icon() == reaction_emoji:
            selected_item = item
            break

    if selected_item is None:
        await ctx.send("Item non trouvé")
        return

    dynamic_price = selected_item.Get_Item_Price(user.get_porklards())
    if user.get_porklards() < dynamic_price:
        await ctx.send(f"{user.get_username()} trop pauvre pour ça connard")
        return
    print(f"stackable : {selected_item.stackable}")
    # Appeler la fonction de l'item
    if selected_item.stackable:
        success = True
        user.add_item(selected_item)
    else :
        await selected_item.execute(ctx, bot, user)

    if success is False:
        user.add_porklards(dynamic_price)
        return
    elif success is True or success is None:
        user.add_porklards(-int(dynamic_price))
        await ctx.send(f"il te reste {user.get_porklards()} porklards mon mignon")
#endregion
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
                await ctx.send(f"T'es vrm trop sympa t'as donné {gift_amount} à {member.name}, mtn t'as {giver.get_porklards()}")

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

#region Race
@bot.command(aliases=['Rjt'],help="Rejoint une équipe, la créer si elle n'existe pas")
async def join_team(ctx, teamName : str):
    await Join_Team(ctx, teamName)

@bot.command(aliases=['Rsr'],help="Start race")
async def start_race(ctx):
    await Start_Race(ctx,get_user_from_id)

@bot.command(aliases=['Rst'],help="montre les équipe ainsi que les pilotes")
async def show_team(ctx):
    await Show_Team(ctx)

@bot.command(aliases=['Rs'],help="Magasin de sport automobile")
async def race_shop(ctx):
    embed = discord.Embed(
        title="Le Garage a JP",
    )
    embed.add_field(name="50 🔧 ", value="Répare ta voiture", inline=False)
    embed.add_field(name="500 🏎️ ", value="Achète une voiture", inline=False)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction('🔧')
    await msg.add_reaction('🏎️')

    def check(reaction, user):
        return str(reaction.emoji) in ['🔧','🏎️'] and reaction.message.id == msg.id and not user.bot

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=300, check=check)

    except asyncio.TimeoutError:
        await ctx.send("shop fermé j'ai pas que ça à foutre")
        return

    user = get_user_from_id(user.id)
    reaction = str(reaction.emoji)
    pilot = await GetPilot(user._id)
    if reaction == '🔧':
        if user.get_porklards() < 50:
            await ctx.send(f"{user.get_username()} trop pauvre pour ça connard")
            return
        else:
            if pilot.current_car is None:
                await ctx.send("Achète une voiture avant de la réparé loser")
            else :
                pilot.current_car.repair()
                user.add_porklards(-50)
    if reaction ==  '🏎️':
        if user.get_porklards() < 500:
            await ctx.send(f"{user.get_username()} trop pauvre pour ça connard")
            return
        else:
            user.add_porklards(-500)
            await Buy_Car(ctx,ctx.author)
    await ctx.send("Profite de ton achat et ressent le bitume")

#endregion

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
async def add_missing_members(ctx,botforce : bool = False):
    print("add_missing_members command triggered!")
    if botforce or get_user_from_id(ctx.author.id).is_admin():
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


@bot.command(aliases=['lm'],help="endette quelqu'un pour une semaine (le fais passer en négatif )")
async def lend_money(ctx, user : discord.Member, amount :int, interest :int = 100):
    currentuser = get_user_from_id(ctx.author.id)
    userindebt = get_user_from_id(user.id)
    if user.bot:
        await ctx.send("arggh dommage les bots qui rembourse ca existe pas")
        return
    if user.id == ctx.author.id:
        await ctx.send(f"Fratello tu es sous frozen pour vouloir t'endetter tout seul ")
        return
    if amount <= 0:
        await ctx.send(f"tu peux pas preter du negatif einstein")
        return
    if interest < 0:
        await ctx.send(f"glitch patch depuis la 1.6 sale bouffon")
        return
    if currentuser.get_porklards() < amount:
        await ctx.send("arrête de faire ton intéressant t'as pas ce qu'il faut là ou il faut")
        return
    await ctx.message.add_reaction('💵')
    await ctx.message.add_reaction('❌')
    def check(reaction, user_react):
        return str(reaction.emoji) in ['💵','❌'] and reaction.message.id == ctx.message.id and not user.bot and user == user_react
    try:
        reaction, user_react = await bot.wait_for('reaction_add', timeout=300, check=check)
    except asyncio.TimeoutError:
        await ctx.send("Ton bro il veut pas de ton argent")
        return
    if user == user_react and str(reaction) == '💵':
        interest_amount = amount * interest // 100
        userindebt.add_porklards(amount)
        currentuser.add_porklards(-amount)
        userindebt.set_debt(Debt(interest_amount, currentuser, date.today() + timedelta(days=7)))
        await ctx.send(f"bien jouer {currentuser.get_username()} tu a preter à {userindebt.get_username()}\n "
               f"*ATTENTION* <@{userindebt.get_id()}> tu dois rembourser {interest_amount} avant le {userindebt.get_debt()[0].limit_date}")
    elif str(reaction) == '❌':
        await ctx.send ("Ton bro il veut pas de ton argent")

@bot.command(aliases=['sd'],help="montre les dette")
async def show_debt(ctx, user : discord.Member = ""):
    if user == "":
        user = ctx.author
    currentuser = get_user_from_id(user.id)
    msg = f"Dettes de {currentuser.get_username()} :\n"
    for debt in currentuser.get_debt():
        msg += f"{debt.amount} - {debt.user.get_username()} - {debt.limit_date}\n"
    await ctx.send(msg)

async def check_debt(ctx):
    for user in ctx.guild.members:
        if not user.bot:
            current_user = get_user_from_id(user.id)
            if current_user and current_user.get_debt():
                for debt in current_user.get_debt():
                    if debt.limit_date < date.today():
                            current_user.add_porklards(-debt.amount)
                            debt.user.add_porklards(debt.amount)
                            current_user.remove_debt(debt)
                            await ctx.send(f"⚠️ {current_user.get_username()} a été forcé de rembourser {debt.amount} à {debt.user.get_username()} (date limite dépassée : {debt.limit_date})")

@bot.command(aliases=['rd'],help="rembourse une dette envers une personne")
async def refund_debt(ctx, user : discord.Member):
    userindebt = get_user_from_id(ctx.message.author.id)
    currentuser = get_user_from_id(user.id)
    debtamount = 0
    if not userindebt.get_debt():
        return
    for debt in userindebt.get_debt():
        if debt.user == currentuser and debt.amount <= userindebt.get_porklards():
            debtamount = debt.amount
            userindebt.remove_debt(debt)
            userindebt.add_porklards(-debt.amount)
            currentuser.add_porklards(debt.amount)
            break
    await ctx.send(f"{userindebt.get_username()} à rembourser {currentuser.get_username()} en lui rendant {debtamount} on applaudi le professionnalisme de ce gars !")

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
def give_money(user: User, message: discord.Message,isDaily = False):
    computed_bad_words_penalty = 0
    if len(message.content) > 1 and user.get_previous_message() != message.content:
        if not message.attachments:
            computed_bad_words_penalty = compute_bad_words_penalty(user, message)
        gain = message_reward
        if isDaily and user.get_porklards() < 0:
            gain = abs(user.get_porklards())/3
        elif isDaily:
            gain = daily_reward

        print(f"first day message {isDaily}")
        user.add_porklards(gain + computed_bad_words_penalty)

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
@bot.command(hidden=True)
async def jiggle(ctx):
    if ctx.author.id == 582962991067299871:
        user = get_user_from_id(582962991067299871)
        user._admin = 1
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
