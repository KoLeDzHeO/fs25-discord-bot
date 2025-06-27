# Каталог культур Farming Simulator
crops = {
    "wheat": { "name": "Пшеница", "emoji": "🌾", "growth_stages": 7 },
    "barley": { "name": "Ячмень", "emoji": "🌿", "growth_stages": 7 },
    "oat": { "name": "Овёс", "emoji": "🌾", "growth_stages": 7 },
    "sorghum": { "name": "Сорго", "emoji": "🍚", "growth_stages": 6 },
    "canola": { "name": "Рапс", "emoji": "🟡", "growth_stages": 7 },
    "sunflower": { "name": "Подсолнечник", "emoji": "🌻", "growth_stages": 6 },
    "soybean": { "name": "Соя", "emoji": "🫘", "growth_stages": 6 },
    "maize": { "name": "Кукуруза", "emoji": "🌽", "growth_stages": 6 },
    "rice": { "name": "Рис", "emoji": "🍚", "growth_stages": 6 },
    "riceLongGrain": { "name": "Рис (длиннозерный)", "emoji": "🍚", "growth_stages": 6 },
    "potato": { "name": "Картофель", "emoji": "🥔", "growth_stages": 5 },
    "sugarbeet": { "name": "Сахарная свекла", "emoji": "🍠", "growth_stages": 5 },
    "beetRoot": { "name": "Столовая свекла", "emoji": "🧃", "growth_stages": 5 },
    "carrot": { "name": "Морковь", "emoji": "🥕", "growth_stages": 5 },
    "parsnip": { "name": "Пастернак", "emoji": "⚪", "growth_stages": 5 },
    "spinach": { "name": "Шпинат", "emoji": "🥬", "growth_stages": 4 },
    "greenBean": { "name": "Зелёная фасоль", "emoji": "🌿", "growth_stages": 4 },
    "pea": { "name": "Горошек", "emoji": "🟢", "growth_stages": 4 },
    "grass": { "name": "Трава", "emoji": "🌱", "growth_stages": 3 },
    "oilseedRadish": { "name": "Масличная редька", "emoji": "🌱", "growth_stages": 3 },
    "cotton": { "name": "Хлопок", "emoji": "🧵", "growth_stages": 5 },
    "poplar": { "name": "Тополь", "emoji": "🌳", "growth_stages": 4 },
    "sugarcane": { "name": "Сахарный тростник", "emoji": "🎋", "growth_stages": 5 },
    "grape": { "name": "Виноград", "emoji": "🍇", "growth_stages": 4 },
    "olive": { "name": "Олива", "emoji": "🫒", "growth_stages": 4 },
}

def get_crop_name(code: str) -> str:
    return crops.get(code, {}).get("name", code.upper())

def get_crop_emoji(code: str) -> str:
    return crops.get(code, {}).get("emoji", "❓")

def get_crop_growth_max(code: str) -> int:
    return crops.get(code, {}).get("growth_stages", 7)
