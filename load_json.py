import json
from datetime import date


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

users_data = load_data("users.json")
answers_data = load_data("answers.json")
channels_data = load_data("channels.json")
sounds_data = load_data("sounds.json")



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
                    "limit_date": str(debt.limit_date)
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
        return date == self._limit_date

sounds = {sound:sounds_data[sound] for sound in sounds_data}
answers = {answer:answers_data[answer] for answer in answers_data}

users = {
    user_data["id"]: User(
        username=user_name,
        id=int(user_data["id"]),
        admin=int(user_data.get("admin", "0")),
        porklards=int(user_data.get("porklards", "0"))
    )
    for user_name, user_data in users_data.items()
}

for user_name, user_data in users_data.items():
    user_id = user_data["id"]
    if user_id in users:
        user = users[user_id]
        debts = user_data.get("debts", [])
        for debt_data in debts:
            debt = Debt(
                _amount=debt_data["amount"],
                _user=user,
                _limit_date=date.fromisoformat(debt_data["limit_date"])
            )
            user.set_debt(debt)


channels = {channel:int(channels_data[channel]) for channel in channels_data}



