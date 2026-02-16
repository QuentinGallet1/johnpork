import json
import random as rd

def load_data(filename: str):
    with open(filename, 'r', encoding='utf-8') as file:
        content = file.read()
        print(f"Loading {filename}, first 100 chars: {content[:100]}")
        if not content.strip():
            raise ValueError(f"{filename} is empty")
        data = json.loads(content)
    return data

users = load_data("users.json")
answers = load_data("answers.json")
channels = load_data("channels.json")
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

    def save_state(self):
        with open('users.json', 'r', encoding='utf-8-sig') as file:
            all_users = json.load(file)

        all_users[self._username] = {
            "id": str(self._id),
            "admin": str(self._admin),
            "porklards": str(self._porklards)
        }
        with open('users.json', 'w', encoding='utf-8') as file:
            json.dump(all_users, file, indent=4, ensure_ascii=False)


    


answers = {answer:answers[answer] for answer in answers}

users = {
    user_data["id"]: User(
        username = user_name,
        id = int(user_data["id"]),
        admin = int(user_data["admin"]),
        porklards = int(user_data["porklards"])
    )
    for user_name, user_data in users.items()
}
channels = {channel:int(channels[channel]) for channel in channels}



