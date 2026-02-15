import discord
import asyncio
import random as rd


#region russian_roulette
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
#region gamble
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

async def drawCard(deck,hand,ctx,embed,isPlayer = True):
    value =  rd.choice(deck)
    hand.append(value)
    index = len(hand)-1
    deck.remove(hand[index])
    valueToDisplay = await DisplayCard(hand)
    valueToDisplay += "\n Total = " + str(await CalculateHand(hand))
    embed.set_field_at(index=1 if isPlayer else 0,name="Ta main" if isPlayer else "La main de John Pork", value=valueToDisplay, inline=False)
    await ctx.edit(embed=embed)

async def CalculateHand(cards):
    totalValue = 0
    haveAs = False
    for card in cards:
        if card[0] == 'J' or card[0] == 'Q' or card[0] == 'K':
            totalValue += 10
        elif card[0] == 'A':
            if totalValue > 10:
                totalValue += 1
            else:
                totalValue += 11
            haveAs = True
        else:
            totalValue += int(card[:-1])
    if totalValue > 21 and  haveAs:
        totalValue -= 10
    return totalValue

async def DisplayCard(hand):
    a=""
    for i in hand:
        a+=str(i)+" - "
    a=a[:-3]
    return a

async def CheckLose(currentHand,opponentHand):
    curHand = await CalculateHand(currentHand)
    oppHand = await CalculateHand(opponentHand)
    if curHand > 21:
        return True
    elif oppHand > 21:
        return False
    elif curHand >= oppHand:
        return False
    else :
        return True

async def playBJ(context, amount : int ,bot,get_user_from_id):
    await generateDeck()
    currentuser = get_user_from_id(context.author.id)
    currentHand = []
    opposantHand = []
    embed = discord.Embed(
        title="BlackJack ",
        color=discord.Color.red()
    )
    embed.add_field(name="La main de John Pork", value=await DisplayCard(opposantHand), inline=False)
    embed.add_field(name="Ta main", value=await DisplayCard(currentHand), inline=False)
    ctx = await context.channel.send(embed = embed)
    await ctx.add_reaction("⬆️")
    await ctx.add_reaction("↔️")
    await drawCard(cartes,currentHand,ctx,embed)
    await drawCard(cartes,opposantHand,ctx,embed,False)
    await drawCard(cartes,currentHand,ctx,embed)
    isPlaying = True
    isLose = False
    while isPlaying :
        def check(reaction, user):
            return str(reaction.emoji) in ['⬆️','↔️'] and user == context.author and reaction.message.id == ctx.id

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=120.0, check=check)
            await reaction.remove(user)
            if str(reaction.emoji) == '⬆️':
                await drawCard(cartes,currentHand,ctx,embed)
                isLose = await CheckLose(currentHand,opposantHand)
                isPlaying = not isLose
            elif str(reaction.emoji) == '↔️':
                while int(await CalculateHand(opposantHand)) <17:
                    await drawCard(cartes,opposantHand,ctx,embed,False)
                isLose = await CheckLose(currentHand,opposantHand)
                isPlaying = False

        except TimeoutError:
            await context.channel.send("Temps écoulé !")
            return

    result = "perdu " if isLose else "gagner"
    currentgain = -amount if isLose else amount
    currentuser.add_porklards(currentgain)
    await ctx.channel.send("tu as " +str(await CalculateHand(currentHand))+ " et John Pork à "+ str(await CalculateHand(opposantHand))+ " donc tu as "  + result + " " + str(amount))
#endregion
