import json
import random as rd

def load_data():
    with open('info.json', 'r') as file:
        data = json.load(file)
    return data

data = load_data()

class User:
    def __init__(self, username : str, id : int, admin : int, porklards : int):
        self._username = username
        self._id = id
        self._admin = admin
        self._porklards = porklards
        self._previous_message = ""
        self._enhanced_gambles = 0

    def __str__(self):
        return f'Name : {self._username} , Id : {self._id}'
    
    def __repr__(self): 
        return self.__str__()
    
    def get_username(self) -> str:
        return self._username
    
    def get_id(self) -> int:
        return self._id
    
    def get_porklards(self) -> int:
        return self._porklards
    
    def get_previous_message(self) -> str:
        return self._previous_message
    
    def is_admin(self) -> bool:
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
    
    def save_state(self):

        user_data = {
            "id": str(self._id),
            "admin": str(self._admin),
            "porklards": str(self._porklards)
        }

        data["users"][self._username] = user_data

        with open('info.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    
    


answers = {answer:data["answers"][answer] for answer in data["answers"]}

users = {
    user_data["id"]: User(
        username = user_name,
        id = int(user_data["id"]),
        admin = int(user_data["admin"]),
        porklards = int(user_data["porklards"])
    )
    for user_name, user_data in data["users"].items()
}
channels = {channel:int(data["channels"][channel]) for channel in data["channels"]}



