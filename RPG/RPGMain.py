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
    value = 0
    def __init__(self,name,stat_buffer = Stat(0,0),rarity = None,value = 10):
        self.name=name
        self.stat=stat_buffer
        self.value=value

class Entity:
    name=""
    def AddLife(self,amount):
        self.stat.health+=amount
    def AddAttack(self,amount):
        self.stat.damage+=amount


class Enemy(Entity):
    sure_drop = []
    rare_drop = []

    def __init__(self, name, stat, sure_drop, rare_drop):
        self.name=name
        self.stat=stat
        self.sure_drop=sure_drop if sure_drop else []
        self.rare_drop=rare_drop if rare_drop else []
    
    def clone(self):
        return Enemy(self.name, Stat(self.stat.damage, self.stat.health), list(self.sure_drop), list(self.rare_drop))

class Room:
    name=""
    enemies = []

    def __init__(self,name,enemies = None):
        self.name=name
        self.enemies=enemies if enemies is not None else []

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

#items
baril = Item("Baril de foutre",Stat(0,5),"porklaisque",25)
baton = Item("Baton de bois",Stat(1,0),"commun",5)
caillou = Item("Caillou",rarity="commun",value=3)

#ennemies
naingris = Enemy("Naingris",Stat(1,2),[baton,caillou],None)
jmlp = Enemy("Jean Marie Le Pen",Stat(2,5),None,[baril])
zemm = Enemy("Zemm Zemm",Stat(1,7),[baton,baton],[caillou])
async def GenerateRoom():
    room_name = ["le salon","la cuisine","la chambre","la salle BDSM de John Pork"]
    enemies = []
    possible_enemies = [naingris, jmlp, zemm]
    nbEnnemy = random.randint(1,3)
    for i in range (nbEnnemy):
        ennemiyToAdd = random.choice(possible_enemies).clone()
        enemies.append(ennemiyToAdd)
    random.shuffle(room_name)

    return Room(room_name[0],enemies)

async def LeaveDungeon(ctx,player,get_user_from_id):
    value = 0
    for item in player.inventory:
        value += item.value
    user = get_user_from_id(ctx.author.id)
    user.add_porklards(value)
    await ctx.send(content=f"{player.name} a quitté la maison de John Pork avec un total de {value} porklards et on espère ne jamais le revoir")

async def EnterDungeon(ctx,bot,get_user_from_id):
    msg = await ctx.send("Tu entres dans le donjon")
    player = Player(ctx.author.name,Stat(1,10))

    #define all emoji
    eattack = "⚔️"
    emoveup = "🔼"
    eleave = "❌"
    
    currentRoom = await GenerateRoom()
    inDugeon = True
    while inDugeon:
        await msg.clear_reactions()
        enemies = []
        if currentRoom.enemies:
            enemies = currentRoom.enemies

        while enemies:
            newItem = []
            await msg.edit( content=f"Tu te trouves dans {currentRoom.name}.\nIl y a actuellement {len(enemies)} ennemi dans la salle\nTu tombes sur un {enemies[0].name}.\n{eattack} pour attaquer")
            await msg.add_reaction(eattack)
            possible_react = [eattack]
            cur_ennemi = enemies[0]
            killed = False
            msg_ennemi = await ctx.send(content=f"{cur_ennemi.name} a {cur_ennemi.stat.health} de point de vie")
            def check(reaction, user_react):
                return str(reaction.emoji) in possible_react and reaction.message.id == msg.id and not user_react.bot
            try:
                reaction, reacting_user = await bot.wait_for('reaction_add', timeout=300, check=check)
            except asyncio.TimeoutError:
                await ctx.send("John Pork t'attrapes et te sodomise le fion, tu perds tout")
                return

            reaction_emoji = str(reaction.emoji)
            await reaction.remove(reacting_user)
            killed = False
            while not killed:
                if reaction_emoji == eattack:
                    killed = player.attack(cur_ennemi)
                    await msg_ennemi.edit(content=f"{cur_ennemi.name} a {cur_ennemi.stat.health} de point de vie\n{player.name} a {player.stat.health} de point de vie")
                    if killed:
                        droppedItem = cur_ennemi.sure_drop
                        if random.randint(1,100)>=85 and cur_ennemi.rare_drop:
                            droppedItem += cur_ennemi.rare_drop
                        player.addItems(droppedItem)
                        newItem.extend([item for item in droppedItem if item not in player.inventory])
                        enemies.remove(cur_ennemi)
                        await msg_ennemi.delete()
                        await msg.clear_reaction(eattack)
                        itemwin = "\n---\n"
                        for item in cur_ennemi.sure_drop:
                            itemwin += item.name+"\n"
                        await msg.edit( content=f"Tu as vaincu {cur_ennemi.name} et gagné {itemwin}")
                        await asyncio.sleep(2)
                    else:
                        player.AddLife(-cur_ennemi.stat.damage)
                        await msg_ennemi.edit(content=f"{cur_ennemi.name} a {cur_ennemi.stat.health} de point de vie\n{player.name} a {player.stat.health} de point de vie")
                        if player.stat.health <= 0:
                            await ctx.send("John Pork t'attrapes et te sodomise le fion, tu perds tout")
                            return
                for items in newItem:
                    for item in items:
                        player.AddLife(item.stat.health)
                        player.AddAttack(item.stat.damage)
                await asyncio.sleep(1)
        player.AddLife(2)
        await msg.edit( content=f"Tu as vaincu {cur_ennemi.name}.\n{emoveup} pour avancer\n{eleave} sortir")
        await msg.add_reaction(emoveup)
        await msg.add_reaction(eleave)
        possible_react = [emoveup,eleave]

        def check(reaction, user_react):
            return str(reaction.emoji) in possible_react and reaction.message.id == msg.id and not user_react.bot

        try:
            reaction, reacting_user = await bot.wait_for('reaction_add', timeout=300, check=check)
        except asyncio.TimeoutError:
            await ctx.send("John Pork t'attrapes et te sodomise le fion, tu perds tout")
            return
        reaction_emoji = str(reaction.emoji)
        await reaction.remove(reacting_user)
        if reaction_emoji == eleave:
            await LeaveDungeon(ctx,player,get_user_from_id)
            return
        if reaction_emoji == emoveup:
            currentRoom = await GenerateRoom()



