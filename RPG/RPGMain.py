import asyncio
import random


class Stat :
    #attack
    damage=0
    #defence
    health=0

    def __init__(self,damage,health):
        self.damage=damage
        self.health=health

    def AddDamage(self,amount):
        self.damage+=amount

    def AddHealth(self,amount):
        self.health+=amount
class Item :
    raritytab = ["commun","rare","épique","légendaire","porklaisque"]
    name=""
    rarity="",
    stat= Stat(0,0)
    def __init__(self,name,stat_buffer = Stat(0,0),rarity = None):
        self.name=name
        self.stat=stat_buffer

class Entity:
    name=""
    stat=Stat(0,0)
    def AddLife(self,amount):
        self.stat.health+=amount
    def AddAttack(self,amount):
        self.stat.damage+=amount


class Enemy(Entity):
    sure_drop = []
    rare_drop = []

    def __init__(self,name,stat,sure_drop,rare_drop):
        self.name=name
        self.stat=stat
        self.sure_drop=sure_drop,
        self.rare_drop=rare_drop


class Room:
    name=""
    precedent_room= None
    enemies = []

    def __init__(self,name,precedent_room = None,enemies = None):
        self.name=name
        self.precedent_room=precedent_room
        self.enemies=enemies if enemies is not None else []

    def AddPrecedentRoom(self,room):
        self.precedent_room = room

class Player(Entity):
    inventory=[]
    equipment=[]
    def __init__(self,name,stat):
        self.name=name
        self.stat=stat
    def equip(self,item):
        if item not in self.inventory:
            self.equipment.append(item)
            self.inventory.remove(item)
    def attack(self,enemy):
        enemy.AddLife(-self.stat.damage)
        if enemy.stat.health <=0:
            return True
        else:
            return False
    def addItem(self,item):
        self.inventory.append(item)

    def addItems(self,items):
        for item in items:
            self.addItem(item)



async def GenerateRoom():
    room_name = ["le salon","la cuisine","la chambre"]
    enemies = [Enemy("Gobelin",Stat(1,2),Item("Sword",Stat(1,0),"rare"),None)]
    random.shuffle(room_name)
    return Room(room_name[0],None,enemies)


async def EnterDungeon(ctx,bot):
    await ctx.send("Tu entres dans le donjon")
    player = Player(ctx.author.name,Stat(1,10))
    #define all emoji
    eattack = "⚔️"
    currentRoom = await GenerateRoom()
    msg = await ctx.send( f"Tu te trouves dans {currentRoom.name}.")
    enemies = []
    if currentRoom.enemies:
        enemies = currentRoom.enemies
        msg = await ctx.send( f"Tu tombes sur un {enemies[0].name}.\n{eattack} pour attaquer")
        await msg.add_reaction(eattack)
        possible_react = [eattack]

    while enemies:
        msg_ennemi = await ctx.send(content=f"{enemies[0].name} a {enemies[0].stat.health} de point de vie")
        def check(reaction, user_react):
            return str(reaction.emoji) in possible_react and reaction.message.id == msg.id and not user_react.bot
        try:
            reaction, reacting_user = await bot.wait_for('reaction_add', timeout=300, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Tu quittes le donjon")
            return

        reaction_emoji = str(reaction.emoji)
        await reaction.remove(reacting_user)
        killed = False
        while not killed:
            if reaction_emoji == eattack:
                killed = player.attack(enemies[0])
                await msg_ennemi.edit(content=f"{enemies[0].name} a {enemies[0].stat.health} de point de vie\n{player.name} a {player.stat.health} de point de vie")
                if killed:
                    player.addItems(enemies[0].sure_drop)
                    enemies.remove(enemies[0])
                else:
                    player.AddLife(-enemies[0].stat.damage)
                    if player.stat.health <= 0:
                        print("player killed")
            await asyncio.sleep(1)

    await msg.add_reaction("🔼")
    possible_react = ["🔼"]

    def check(reaction, user_react):
        return str(reaction.emoji) in possible_react and reaction.message.id == msg.id and not user_react.bot

    try:
        reaction, reacting_user = await bot.wait_for('reaction_add', timeout=300, check=check)
    except asyncio.TimeoutError:
        await ctx.send("Tu quittes le donjon")
        return
    reaction_emoji = str(reaction.emoji)