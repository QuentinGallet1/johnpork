import asyncio
import random as rd

import discord

import load_json


#region Russian_roulette
async def start_rr(ctx, targeted_member: discord.Member, amount: int, bot, get_user_from_id):
    target = get_user_from_id(targeted_member.id)
    author = get_user_from_id(ctx.author.id)
    print('roulette?')
    if target is None:
        await ctx.send("Deso gros il existe pas ce type")
    elif amount <= 0:
        await ctx.send("T'as pas de couilles")
    elif author.get_porklards() < amount:
        await ctx.send("Tu fais le mec mais t'as pas les thunes qui suivent")
    elif target.get_porklards() < amount:
        await ctx.send("Tu peux t'attaquer à un mec qui a des thunes ouuuu ?")
    elif author == target:
        await ctx.send("T'es con ou t'es con ? ")
    else:
        await ctx.message.add_reaction('✅') #green checkmark
        await ctx.message.add_reaction('❌') #red cross

        def check(reaction, user):
            return str(reaction.emoji) in ['✅','❌'] and user.id == targeted_member.id and reaction.message.id == ctx.message.id

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60, check=check)
            print(reaction)
        except asyncio.TimeoutError:
            return await ctx.message.reply("MAIS QU'IL EST LENT CE LAIT")

        if str(reaction.emoji) == '❌':
            await ctx.message.reply("Tapette spotted")
        elif str(reaction.emoji) == '✅':

            turns = 6

            bullet_index = rd.randint(0, turns - 1)


            is_game_lost = False
            turn_count = 0
            msg = await ctx.message.reply('uwu')
            await msg.add_reaction('🔫')

            while is_game_lost == False:
                current_user = author if turn_count % 2 == 0 else target

                gun = ['[:black_circle:]' for i in range(turns-turn_count)]
                roulette_animation = [emoji for emoji in gun]
                roulette_current_user_message = f"A `{current_user.get_username()}` de presser la gachette\n"
                roulette_asci_art = "(\\-_•)︻デ═一                 (•\\_•)"
                roulette_message = roulette_current_user_message + " ".join(roulette_animation) + "         " + roulette_asci_art

                msg = await msg.edit(content=roulette_message)


                def check(reaction, user):
                    return str(reaction.emoji) == '🔫' and user.id == current_user.get_id() and reaction.message.id == msg.id

                try:
                    reaction, user = await bot.wait_for('reaction_add', timeout=60, check=check)
                except asyncio.TimeoutError:
                    await ctx.send("TROP LENT LE LAIT")
                    is_game_lost = True

                for i in range(turns-turn_count):
                    roulette_animation[i%(turns-turn_count)] = '[:boom:]'
                    roulette_message = roulette_current_user_message + " ".join(roulette_animation) + "         " + roulette_asci_art
                    await msg.edit(content=roulette_message)
                    await asyncio.sleep(0.1)
                    if turn_count != bullet_index:
                        roulette_animation[i%(turns-turn_count)] = '[:black_circle:]'

                if turn_count == bullet_index:
                    print(f"End of the game, loser is {current_user.get_username()}")
                    is_game_lost = True

                print(f"bullet index : {bullet_index}")
                print(f"turn_count : {turn_count}")
                turn_count += 1


            loser = current_user
            if current_user == target:
                winner = author
            else:
                winner = target

            winner.add_porklards(amount)
            loser.add_porklards(-amount)
            await msg.edit(content=f'`{winner.get_username()}` a gagné mtn il a {winner.get_porklards()} et l\'autre bouff est à {loser.get_porklards()}' + '\n' + " ".join(roulette_animation) + "         " + roulette_asci_art)


#endregion
#region Gamble
async def start_gamble(ctx, amount, get_user_from_id):
    amount = (int) (amount)
    rand = rd.random()
    user = get_user_from_id(ctx.author.id)
    win_threshold = 0.4 if user.get_enhanced_gambles() == 0 else 0.6
    print(f' User {user.get_username()} is gambling with a {win_threshold} win probability and has {user.get_enhanced_gambles()} enhanced gambles\n')
    if user is None:
        message = "Deso gros t'existes pas"
    if user.get_porklards() < amount or amount <= 0:
        message = "Mais tu te prends pour qui en vrai ? T'es juste pauvre mgl \n"
    else:
        if rand <= 0.01:
            gain = amount*3
            message = "JACK PUTAIN DE POT\n"
        elif rand <= win_threshold and rand > 0.01:
            gain = amount
            message = "Bj gros bj\n"
        elif rand >= 0.99:
            gain = -amount*3
            message = "Oh le malaise, enjoy de ne plus aller en voc :)\n"
        else:
            gain = -amount
            message = "Ah ça c'est pas de bol\n"

        user.add_porklards(gain)
        message += f"T'as gagné {gain} porklards ! Mtn t'es à {user.get_porklards()}"

        if user.get_enhanced_gambles() > 0:
            user.set_enhanced_gambles(user.get_enhanced_gambles() - 1)
    await ctx.send(message)
#endregion
#region BlackJack
cartes = []
symbole = ["♥","♦","♣","♠"]
num = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]

async def generateDeck():
    cartes.clear()
    for i in symbole:
        for j in num:
            cartes.append(str(j)+i)

async def drawCard(deck,hand,ctx,embed,currentuser,isPlayer = True):
    value =  rd.choice(deck)
    hand.append(value)
    index = len(hand)-1
    deck.remove(hand[index])
    valueToDisplay = await DisplayCard(hand)
    valueToDisplay += "\n Total = " + str(await CalculateHand(hand))
    embed.set_field_at(index=1 if isPlayer else 0,name=currentuser.get_username() if isPlayer else "John Pork", value=valueToDisplay, inline=False)
    await ctx.edit(embed=embed)

async def CalculateHand(cards):
    totalValue = 0
    aces = 0
    for card in cards:
        if card[0] == 'J' or card[0] == 'Q' or card[0] == 'K':
            totalValue += 10
        elif card[0] == 'A':
            totalValue += 11
            aces += 1
        else:
            totalValue += int(card[:-1])

    while totalValue > 21 and aces > 0:
        totalValue -= 10
        aces -= 1
    return totalValue

async def DisplayCard(hand):
    a=""
    for i in hand:
        a+=str(i)+" - "
    a=a[:-3]
    return a

async def CheckResult(currentHand,opponentHand):
    curHand = await CalculateHand(currentHand)
    oppHand = await CalculateHand(opponentHand)
    if len(currentHand) == 2 and curHand == 21:
        return 4
    if len(opponentHand) == 2 and oppHand == 21:
        return 3
    if curHand > 21:
        return 0
    elif oppHand > 21:
        return 1
    elif curHand > oppHand:
        return 1
    elif curHand == oppHand:
        return 2
    else :
        return 0

async def playBJ(context, amount : int ,bot,get_user_from_id):
    await generateDeck()
    currentuser = get_user_from_id(context.author.id)
    if currentuser.get_porklards() < amount:
        await context.send("BAHAHAHA sale pauvre reviens quand tu pourras te payer un tacos")
        return
    if amount <= 0:
        await context.send("Fraudeur de merde xdddd")
        return
    currentuser.add_porklards(-amount)
    currentHand = []
    opposantHand = []
    embed = discord.Embed(
        title="BlackJack ",
        color=discord.Color.red()
    )
    embed.add_field(name="John Pork", value=await DisplayCard(opposantHand), inline=False)
    embed.add_field(name=currentuser.get_username(), value=await DisplayCard(currentHand), inline=False)
    ctx = await context.channel.send(embed = embed)
    await ctx.add_reaction("⬆️")
    await ctx.add_reaction("↔️")
    await drawCard(cartes,currentHand,ctx,embed,currentuser)
    await drawCard(cartes,opposantHand,ctx,embed,currentuser,False)
    await drawCard(cartes,currentHand,ctx,embed,currentuser)
    isPlaying = True
    result = 0
    while isPlaying :
        def check(reaction, user):
            return str(reaction.emoji) in ['⬆️','↔️'] and user == context.author and reaction.message.id == ctx.id

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=120.0, check=check)
            await reaction.remove(user)
            if str(reaction.emoji) == '⬆️':
                await drawCard(cartes,currentHand,ctx,embed, currentuser)
                result = await CheckResult(currentHand,opposantHand)
                isPlaying = result != 0
            elif str(reaction.emoji) == '↔️':
                while int(await CalculateHand(opposantHand)) < 17:
                    await drawCard(cartes,opposantHand,ctx,embed,currentuser,False)
                result = await CheckResult(currentHand,opposantHand)
                isPlaying = False
            if int(await CalculateHand(currentHand)) == 21:
                while int(await CalculateHand(opposantHand)) < 17:
                    await drawCard(cartes,opposantHand,ctx,embed,currentuser,False)
                result = await CheckResult(currentHand,opposantHand)
                isPlaying = False

        except asyncio.TimeoutError:
            await context.channel.send("Branle ton oncle j'ai pas ton temps et j'ai quand meme pris ta thune")
            return

    gain = 0
    gived = 0
    #simple loose
    if result == 0:
        gain = -amount
        gived = 0
        result = "perdu"
    #simple win
    elif result == 1:
        gain = amount
        gived = amount*2
        result = "gagné"
    #draw
    elif result == 2:
        result = "égalisé un dieu mais bon tu gagnes"
        gived = amount
    #jp blackjack
    elif result == 3:
        gain = -(amount*2)
        gived = -amount
        result = "perdu car dans la manche de jp ce cache un cinquième ace donc tu perds"
    elif result == 4:
        gain = amount*2
        gived = amount*3
        result = "blackjack bg donc tu gagnes"
    
    currentuser.add_porklards(gived)
    await ctx.channel.send(f"tu as {str(await CalculateHand(currentHand))} et John Pork a {str(await CalculateHand(opposantHand))} donc tu as {result} {str(abs(gain))} porklards, tu as maintenant {currentuser.get_porklards()} porklards en tout" )
#endregion
#region Race
circuits = ['Monza','Spa','Le Mans','Daytona','Monte-Carlo','Nürburgring','Laguna','Mount Panorama','Zolder','Paul Ricard']
teams = []
pilots = []

def GetPercent(value : int) -> float:
    return value/100
class Stats:
    def __init__(self,vitesse=1,accel=1,maniabilite =1,dura = 100):
        self.speed = vitesse
        self.acceleration = accel
        self.maniability = maniabilite
        self.durability = dura

    def repair(self):
        self.durability = 100

class Car:
    def __init__(self, model: str, _stats: Stats, sprite: str):
        self._model = model
        self.stats = _stats
        self._sprite = sprite

    def calcul_percent_stat(self) -> float:
        return (self.stats.speed + self.stats.acceleration + self.stats.maniability)*GetPercent(self.stats.durability)

    def add_damage(self,amount : int):
        self.stats.durability -= amount

class RaceTeam:
    def __init__(self, teamname: str, teampoint: int = 0):
        self.name = teamname
        print("new team")

class Pilot:
    def __init__(self, user: str, id: int, from_load: bool = False):
        self.name = user
        self._id = id
        self.race_team = None
        self.current_car = None
        self.victory_points = 0
        self.prev_pos = 0
        if not from_load:
            pilots.append(self)

    def add_current_car(self, car: Car):
        self.current_car = car

    def add_victory_points(self, points: int):
        self.victory_points += points

    def add_team(self, team: RaceTeam):
        print(f"pilot join team {team.name}")
        self.race_team = team

def get_pilot_by_id(id) -> Pilot | None:
    for pilot in pilots:
        if pilot._id == id:
            return pilot

async def Join_Team(ctx, teamName):
    if get_pilot_by_id(ctx.author.id) is None:
        await Create_Pilot(ctx)
    if not any(t.name == teamName for t in teams):
        newTeam = RaceTeam(teamName)
        teams.append(newTeam)
        new_team = newTeam
    else:
        new_team = next(t for t in teams if t.name == teamName)
    get_pilot_by_id(ctx.author.id).add_team(new_team)
async def Show_Team(ctx):
    embed = discord.Embed(
        title="Équipes :",
        color=discord.Color.blurple()
    )
    for team in teams:
        pilot_in_team = ""
        for pilot in pilots:
            if team == pilot.race_team:
                safe_name = discord.utils.escape_markdown(pilot.name)
                pilot_in_team += safe_name + "\n"
        embed.add_field(name="**__" + team.name.upper() + "__**: ", value=pilot_in_team, inline=False)
    await ctx.send(embed=embed)
async def Create_Pilot(ctx):
    Pilot(ctx.author.name, ctx.author.id)
    print("pilot created")


#region Save and Load
def LoadRaceGame():
    race_data_raw = load_json.load_data("race.json")
    for username, data in race_data_raw.items():
        teamname = data.get('teamname')
        curcar = data.get('current_car')
        team = None
        car = None
        if teamname:
            team = next((t for t in teams if t.name == teamname), None)
            if team is None:
                team = RaceTeam(teamname)
                teams.append(team)
        if curcar:
            stats = Stats()
            stats.vitesse = curcar.get('vitesse', 1)
            stats.acceleration = curcar.get('acceleration', 1)
            stats.maniability = curcar.get('maniability', 1)
            stats.durability = curcar.get('durability', 100)
            car = Car(curcar.get('model'), stats, curcar.get('sprite', 0))
        pilot = Pilot(username, data.get('id'), from_load=True)
        pilot.victory_points = data.get('current_points', 0)
        if team:
            pilot.race_team = team
        if car:
            pilot.current_car = car
        pilots.append(pilot)
async def SaveRaceGame():
    all_racers = {}
    for pilot in pilots:
        car_data = None
        if pilot.current_car:
            car_data = {
                "model": pilot.current_car._model,
                "sprite": pilot.current_car._sprite,
                "vitesse": pilot.current_car.stats.speed,
                "acceleration": pilot.current_car.stats.acceleration,
                "maniability": pilot.current_car.stats.maniability,
                "durability": pilot.current_car.stats.durability,
            }
        all_racers[pilot.name] = {
            "id": pilot._id,
            "teamname": pilot.race_team.name if pilot.race_team else None,
            "current_points": pilot.victory_points,
            "current_car": car_data,
        }
    with open('race.json', 'w', encoding='utf-8') as file:
        load_json.json.dump(all_racers, file, indent=4, ensure_ascii=False)

LoadRaceGame()
#endregion

async def Buy_Car(ctx):
    if not get_pilot_by_id(ctx.author.id):
        await Create_Pilot(ctx)
    get_pilot_by_id(ctx.author.id).add_current_car(Car("voiture de base", Stats(),"aucun"))
    await SaveRaceGame()

async def GivePorklard(pilots,get_user_from_id):
    for pilot in pilots:
        user = get_user_from_id(pilot._id)
        print(pilots.index(pilot))

async def Start_Race(ctx, amount,get_user_from_id):
        cur_circuit = rd.choice(circuits)
        all_pilot_in_race = [p for p in pilots if p.race_team and p.current_car]
        if not all_pilot_in_race:
            await ctx.send("No pilot found")
            return
        proba_damage = 0.20
        embed = discord.Embed(
            title=f"Course : {cur_circuit}",
            color=discord.Color.blurple()
        )
        turn = 0
        max_turn = 10
        msg = None
        previous_order = list(all_pilot_in_race)
        while turn <= max_turn:
            embed.clear_fields()
            embed.add_field(name=f"Tour : {turn}/{max_turn}", value="", inline=True)
            all_pilot_in_race.sort(key=lambda x: x.current_car.calcul_percent_stat(), reverse=True)

            for pos, pilot in enumerate(all_pilot_in_race):
                prev_pos = previous_order.index(pilot)
                diff = prev_pos - pos
                emoji = "🔼" if diff > 0 else ("🔽" if diff < 0 else "")

                embed.add_field(
                    name=f"\n{discord.utils.escape_markdown(pilot.name)} :\n",
                    value=f"{emoji} {pilot.current_car.calcul_percent_stat()}",
                    inline=False
                )
                if rd.random() < proba_damage:
                    pilot.current_car.add_damage(rd.randrange(1, 10))
                    print("add damage on car")

            previous_order = list(all_pilot_in_race)

            if turn == 0:
                msg = await ctx.send(embed=embed)
            else:
                await msg.edit(embed=embed)
            turn += 1
            await asyncio.sleep(1)
        await GivePorklard(all_pilot_in_race,get_user_from_id)
        await SaveRaceGame()


#endregion
