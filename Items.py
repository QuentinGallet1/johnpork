from typing import Optional, Callable

class Item:
    id = 0
    name = ""
    icon = ""
    description = ""
    achat = ""
    price = 0
    percent = 100

    def __init__(self, p_id, p_name, p_icon, p_description, p_price, p_percent=100, p_achat="", on_use: Optional[Callable] = None, action_name: str = None):
        self.id = p_id
        self.name = p_name
        self.icon = p_icon
        self.description = p_description
        self.achat = p_achat
        self.price = p_price
        self.percent = p_percent
        self.on_use = on_use  # Fonction personnalisée appelée lors de l'utilisation
        self.action_name = action_name

    def Get_Item_Name(self):
        return self.name
    def Get_Item_Icon(self):
        return self.icon
    def Get_Item_Description(self):
        return self.description
    def Get_Item_Price(self, user_porklards: int = None):
        """Retourne le prix de l'item, éventuellement ajusté selon les porklards de l'user."""
        base_price = self.price
        if user_porklards is None:
            return base_price

        dynamic_price = int(user_porklards *self.percent/100)
        final_price = max(dynamic_price, base_price)
        return final_price
    async def execute(self, ctx, bot, user):
        """Exécute la fonction personnalisée de l'item si elle existe."""
        if self.on_use:
            return await self.on_use(ctx, bot, user, self)
        return False