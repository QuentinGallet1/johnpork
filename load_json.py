import json
from datetime import date

from Items import Item


def load_data(filename: str):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
        data = json.loads(content)
    return data
def add_data(key: str, value, filename: str):
    data = load_data(filename)
    data[key] = value
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def AddItemInJson(item: Item):
    data = load_data("items.json") or {}
    key = str(item.id)
    data[key] = {
        "id": str(item.id),
        "name": item.name,
        "icon": item.icon,
        "description": item.description,
        "price": item.price,
        "percent": item.percent,
        "achat": item.achat,
        "action": item.action_name
    }
    with open('items.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)



users_data = load_data("users.json")
answers_data = load_data("answers.json")
channels_data = load_data("channels.json")
sounds_data = load_data("sounds.json")
items_data = load_data("items.json")


#region Class
class User:
    def __init__(self, username : str, id : int, admin : int, porklards : int):
        self._username = username
        self._id = id
        self._admin = admin
        self._porklards = porklards
        self._previous_message = ""
        self._enhanced_gambles = 0
        self._useDaily = 0
        self.debt = []

    def __str__(self):
        return f'Name : {self._username} , Id : {self._id}'
    
    def __repr__(self): 
        return self.__str__()

    def use_daily(self, current_daily):
        self._useDaily = current_daily

    def get_daily(self):
        print(f"current daily =>{self._useDaily}")
        return self._useDaily

    def get_username(self) -> str:
        return self._username
    
    def get_id(self) -> int:
        return self._id
    
    def get_porklards(self) -> int:
        return self._porklards
    
    def get_previous_message(self) -> str:
        return self._previous_message
    
    def is_admin(self) -> int:
        return self._admin
    
    def get_enhanced_gambles(self) -> int:
        return self._enhanced_gambles
    
    def add_porklards(self, amount : int):
        self._porklards += amount
        print(f'Added {amount} porklards to {self._username}')
    
    def set_enhanced_gambles(self, amount : int):
        self._enhanced_gambles = amount

    def set_previous_message(self, message : str):
        self._previous_message = message

    def set_debt(self, debt : "Debt"):
        self.debt.append(debt)

    def get_debt(self):
        return self.debt
    def remove_debt(self,debt : "Debt"):
        return self.debt.remove(debt)

    def save_state(self):
        with open('users.json', 'r', encoding='utf-8-sig') as file:
            all_users = json.load(file)

        all_users[self._username] = {
            "id": str(self._id),
            "admin": str(self._admin),
            "porklards": str(self._porklards),
            "debts": [
                {
                    "amount": debt.amount,
                    "limit_date": str(debt.limit_date),
                    "user": debt.user.get_id()
                }
                for debt in self.debt
            ]
        }
        with open('users.json', 'w', encoding='utf-8') as file:
            json.dump(all_users, file, indent=4, ensure_ascii=False)
class Debt:
    def __init__(self, _amount : int, _user : User,_limit_date : date ):
        self.amount = _amount
        self.user = _user
        self.limit_date = _limit_date

    def check_date(self,date : date):
        return date == self.limit_date
#endregion

def get_user_from_id(id: int) -> User:
    try:
        return users[str(id)]
    except:
        return None

sounds = {sound:sounds_data[sound] for sound in sounds_data}
answers = {answer:answers_data[answer] for answer in answers_data}
channels = {channel:int(channels_data[channel]) for channel in channels_data}
items_list = {
    item["id"]: Item(
        p_id=item["id"],
        p_name=item["name"],
        p_icon=item["icon"],
        p_description=item["description"],
        p_price=int(item["price"]),
        p_percent=int(item.get("percent", 100)),
        p_achat=item.get("achat", "")
    )
    for item in items_data.values()
}
users = {
    user_data["id"]: User(
        username=user_name,
        id=int(user_data["id"]),
        admin=int(user_data.get("admin", "0")),
        porklards=int(user_data.get("porklards", "0"))
    )
    for user_name, user_data in users_data.items()
}


#Load citation
async def LoadCitation(bot):
    channel = bot.get_channel(channels.get("citations"))
    if channel is None:
        return []
    messages = [msg.content async for msg in channel.history(limit=500)]

    citations = []
    for msg in messages:
        msg_citations = []
        start = 0
        while True:
            start = msg.find('"', start)
            if start == -1:
                break
            end = msg.find('"', start + 1)
            if end == -1:
                break
            citation = msg[start+1:end]
            if len(citation) > 1:
                msg_citations.append(citation)
            start = end + 1

        if msg_citations:
            citation_text = "\n".join(msg_citations)
            citations.append(citation_text)
            answers[citation_text] = citation_text
            print(msg_citations)

        for group in citations:
            for citation in group:
                answers[citation] = citation

    return citations

for user_name, user_data in users_data.items():
    user_id = user_data["id"]
    if user_id in users:
        user = users[user_id]
        debts = user_data.get("debts", [])
        for debt_data in debts:
            debt = Debt(
                _amount=debt_data["amount"],
                _user=get_user_from_id(int(debt_data["user"])),
                _limit_date=date.fromisoformat(debt_data["limit_date"])
            )
            user.set_debt(debt)



# Importer item_commands pour enregistrer les actions dans AVAILABLE_ACTIONS
from item_commands import get_action_by_name

# Charger les actions des items à partir du JSON
for item_id, item in items_list.items():
    # Chercher le JSON correspondant à cet item
    for item_data in items_data.values():
        if item_data["id"] == item_id:
            action_name = item_data.get("action")
            if action_name:
                item.on_use = get_action_by_name(action_name)
                item.action_name = action_name
            break




