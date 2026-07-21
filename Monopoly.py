import random
import asyncio
from typing import Dict, List
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# ==========================================
# ТОКЕН ВАШЕГО БОТА (Вставьте свой токен от @BotFather)
TOKEN = "8425000689:AAFAozXyyKREJLKmdWJ7lSUnKye5C57Kv2c"
# ==========================================

BOARD = [
    {"name": "Вперед (GO)", "type": "special", "icon": "🏁"},
    {"name": "Средиземноморский проспект", "type": "street", "price": 60, "rent": 2, "color": "🟫"},
    {"name": "Общественная казна", "type": "chest", "icon": "🧳"},
    {"name": "Балтийский проспект", "type": "street", "price": 60, "rent": 4, "color": "🟫"},
    {"name": "Подоходный налог", "type": "tax", "fee": 200, "icon": "💸"},
    {"name": "Железная дорога Чита", "type": "station", "price": 200, "rent": 25, "icon": "🚂"},
    {"name": "Восточный проспект", "type": "street", "price": 100, "rent": 6, "color": "🟦"},
    {"name": "Шанс", "type": "chance", "icon": "❓"},
    {"name": "Коннектикутский проспект", "type": "street", "price": 100, "rent": 6, "color": "🟦"},
    {"name": "Массачусетский проспект", "type": "street", "price": 120, "rent": 8, "color": "🟦"},
    {"name": "Тюрьма", "type": "special", "icon": "🔒"},
    {"name": "Санкт-Петербургский проспект", "type": "street", "price": 140, "rent": 10, "color": "🟪"},
    {"name": "Электрическая компания", "type": "utility", "price": 150, "icon": "💡"},
    {"name": "Вирджинский проспект", "type": "street", "price": 140, "rent": 10, "color": "🟪"},
    {"name": "Пенсильванский проспект", "type": "street", "price": 160, "rent": 12, "color": "🟪"},
    {"name": "Железная дорога Пенсильвании", "type": "station", "price": 200, "rent": 25, "icon": "🚂"},
    {"name": "Сент-Джеймс Плейс", "type": "street", "price": 180, "rent": 14, "color": "🟧"},
    {"name": "Общественная казна", "type": "chest", "icon": "🧳"},
    {"name": "Теннесси проспект", "type": "street", "price": 180, "rent": 14, "color": "🟧"},
    {"name": "Нью-Йорк проспект", "type": "street", "price": 200, "rent": 16, "color": "🟧"},
    {"name": "Бесплатная парковка", "type": "special", "icon": "🅿️"},
    {"name": "Кентукки проспект", "type": "street", "price": 220, "rent": 18, "color": "🟥"},
    {"name": "Шанс", "type": "chance", "icon": "❓"},
    {"name": "Индиана проспект", "type": "street", "price": 220, "rent": 18, "color": "🟥"},
    {"name": "Иллинойс проспект", "type": "street", "price": 240, "rent": 20, "color": "🟥"},
    {"name": "Железная дорога Б. и О.", "type": "station", "price": 200, "rent": 25, "icon": "🚂"},
    {"name": "Атлантик проспект", "type": "street", "price": 260, "rent": 22, "color": "🟨"},
    {"name": "Вентиляционная компания", "type": "utility", "price": 150, "icon": "🚰"},
    {"name": "Вентнор проспект", "type": "street", "price": 260, "rent": 22, "color": "🟨"},
    {"name": "Марвин Гарденс", "type": "street", "price": 280, "rent": 24, "color": "🟨"},
    {"name": "Иди в тюрьму", "type": "go_to_jail", "icon": "👮‍♂️"},
    {"name": "Тихоокеанский проспект", "type": "street", "price": 300, "rent": 26, "color": "🟩"},
    {"name": "Северокаролинский проспект", "type": "street", "price": 300, "rent": 26, "color": "🟩"},
    {"name": "Общественная казна", "type": "chest", "icon": "🧳"},
    {"name": "Пенсильвания-авеню", "type": "street", "price": 320, "rent": 28, "color": "🟩"},
    {"name": "Короткая железная дорога", "type": "station", "price": 200, "rent": 25, "icon": "🚂"},
    {"name": "Шанс", "type": "chance", "icon": "❓"},
    {"name": "Парк-Плейс", "type": "street", "price": 350, "rent": 35, "color": "🟦"},
    {"name": "Сверхналог", "type": "tax", "fee": 100, "icon": "💸"},
    {"name": "Бродвей", "type": "street", "price": 400, "rent": 50, "color": "🟦"}
]

PLAYER_ICONS = ["🔴", "🟢", "🔵", "🟡", "🟣", "🟠"]
GAMES: Dict[int, dict] = {}

def get_map_render(game: dict, override_positions: dict = None) -> str:
    """Генерация карты с именами игроков рядом с их фишками"""
    map_lines = ["🗺 **ТЕКУЩАЯ КАРТА ПОЛЯ:**"]
    for i, field in enumerate(BOARD):
        players_here = ""
        for p in game["players"]:
            pos = override_positions.get(p["id"], p["position"]) if override_positions else p["position"]
            if pos == i:
                players_here += f" {p['icon']}({p['name']})"
        
        prefix = field.get("color") or field.get("icon") or "⬜"
        owner_marker = ""
        
        if str(i) in game["properties"]:
            owner_id = game["properties"][str(i)]
            owner_p = next((p for p in game["players"] if p["id"] == owner_id), None)
            if owner_p:
                owner_marker = f" [Владелец: {owner_p['icon']}]"

        if players_here or owner_marker or i % 3 == 0:  
            map_lines.append(f"{i:02d}. {prefix} {field['name']}{owner_marker}{players_here}")
            
    return "\n".join(map_lines)


async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Наберите /play в группе для создания лобби.\nИспользуйте команду /my, чтобы тайно узнать свой баланс.", parse_mode="Markdown")


async def play_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    if chat_id in GAMES and GAMES[chat_id]["status"] == "active":
        await update.message.reply_text("Здесь уже идет игра!")
        return

    if chat_id in GAMES and GAMES[chat_id]["status"] == "lobby":
        if any(p["id"] == user.id for p in GAMES[chat_id]["players"]):
            await update.message.reply_text(f"⚠️ {user.first_name}, вы уже в лобби.")
            return
        if len(GAMES[chat_id]["players"]) >= 6:
            await update.message.reply_text("❌ Нет свободных мест.")
            return

        idx = len(GAMES[chat_id]["players"])
        GAMES[chat_id]["players"].append({
            "id": user.id, "name": user.first_name, "balance": 1500, "position": 0,
            "jail_turns": 0, "icon": PLAYER_ICONS[idx]
        })
        
        players_str = "\n".join([f"{p['icon']} {p['name']}" for p in GAMES[chat_id]["players"]])
        await update.message.reply_text(f"➕ **{user.first_name}** вошел!\n**Лобби:**\n{players_str}\n\n/start_game — запуск матча.")
        return

    GAMES[chat_id] = {
        "status": "lobby", "creator_id": user.id, "current_turn": 0, "properties": {},
        "players": [{
            "id": user.id, "name": user.first_name, "balance": 1500, "position": 0, "jail_turns": 0, "icon": PLAYER_ICONS[0]
        }]
    }
    await update.message.reply_text(f"🎮 **Монополия готова к сбору!**\nОрганизатор: {user.first_name} {PLAYER_ICONS[0]}\nПишите `/play` для входа.\nНачало через `/start_game`.")


async def start_game_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    if chat_id not in GAMES or GAMES[chat_id]["status"] != "lobby":
        await update.message.reply_text("Лобби не создано. Пишите /play!")
        return

    lobby = GAMES[chat_id]
    if lobby["creator_id"] != user.id:
        await update.message.reply_text("Только создатель лобби запускает матч.")
        return
    if len(lobby["players"]) < 2:
        await update.message.reply_text("Нужно хотя бы 2 игрока.")
        return

    random.shuffle(lobby["players"])
    for i, p in enumerate(lobby["players"]):
        p["icon"] = PLAYER_ICONS[i]

    lobby["status"] = "active"
    
    order_text = "\n".join([f"{p['icon']} {p['name']}" for p in lobby["players"]])
    await update.message.reply_text(f"🎲 **Матч начался!**\n\n**Очередь ходов:**\n{order_text}\n\nПервым ходит: {lobby['players'][0]['icon']} **{lobby['players'][0]['name']}** (/roll)")


async def my_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    found_any = False
    msg_text = "📊 **Ваша личная статистика из всех активных игр:**\n\n"
    
    for chat_id, game in GAMES.items():
        if game["status"] != "active":
            continue
        
        p = next((player for player in game["players"] if player["id"] == user_id), None)
        if p:
            found_any = True
            owned = []
            for pos_str, owner_id in game["properties"].items():
                if owner_id == user_id:
                    owned.append(BOARD[int(pos_str)]["name"])
            
            properties_str = ", ".join(owned) if owned else "Нет имущества"
            msg_text += f"🔹 **Игра в чате** `{chat_id}`:\n"
            msg_text += f" 💰 Баланс: {p['balance']} у.е.\n"
            msg_text += f" 📍 Позиция на поле: {p['position']} клетка\n"
            msg_text += f" 🏠 Ваша собственность: {properties_str}\n\n"

    if not found_any:
        msg_text = "❌ Вы сейчас не участвуете ни в одной активной игре."

    try:
        await context.bot.send_message(chat_id=user_id, text=msg_text, parse_mode="Markdown")
        if update.effective_chat.type != "private":
            await update.message.reply_text(f"📬 {update.effective_user.first_name}, отправил статистику вам в личные сообщения!")
    except Exception:
        await update.message.reply_text("❌ Бот не смог написать вам в ЛС! Сначала активируйте бота (нажмите старт в ЛС).")


async def roll_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user

    if chat_id not in GAMES or GAMES[chat_id]["status"] != "active":
        await update.message.reply_text("В этом чате нет активной игры.")
        return

    game = GAMES[chat_id]
    player = game["players"][game["current_turn"]]

    if player["id"] != user.id:
        await update.message.reply_text(f"Сейчас не ваш ход! Ходит {player['icon']} {player['name']}.")
        return

    if player["jail_turns"] > 0:
        keyboard = [
            [
                InlineKeyboardButton("🎲 Бросить кубик", callback_data=f"jail_roll_{chat_id}"),
                InlineKeyboardButton("💵 Заплатить 50 у.е.", callback_data=f"jail_pay_{chat_id}")
            ]
        ]
        await update.message.reply_text(
            f"🔒 {player['icon']} **{player['name']}**, вы в тюрьме! (Ходов осталось: {player['jail_turns']}). Выберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    dice1, dice2 = random.randint(1, 6), random.randint(1, 6)
    total = dice1 + dice2
    
    status_msg = await update.message.reply_text(f"🎲 {player['icon']} **{player['name']}** бросает кубики: **{dice1}** и **{dice2}**! Начинаем движение...")

    old_pos = player["position"]
    current_anim_pos = old_pos
    
    for step in range(1, total + 1):
        await asyncio.sleep(0.4)
        current_anim_pos = (old_pos + step) % 40
        anim_map = get_map_render(game, override_positions={player["id"]: current_anim_pos})
        try:
            await status_msg.edit_text(
                f"🎲 Бросок: {dice1}:{dice2} | {player['icon']} {player['name']} шагает по полю... (Клетка {current_anim_pos})\n\n{anim_map}",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    player["position"] = current_anim_pos
    field = BOARD[player["position"]]
    
    res = f"🏁 {player['icon']} Закончил ход на клетке {player['position']}: *{field['name']}*\n"
    
    if player["position"] < old_pos:
        player["balance"] += 200
        res += "💰 Пройдена клетка ВПЕРЕД! +200 у.е.\n"

    if field["type"] in ["street", "station", "utility"]:
        pos_str = str(player["position"])
        if pos_str not in game["properties"]:
            res += f"🏠 Недвижимость свободна! Цена: **{field['price']} у.е.**\nВаш баланс: {player['balance']} у.е."
            keyboard = [[
                InlineKeyboardButton("✅ Купить поле", callback_data=f"buy_{chat_id}_{player['position']}"),
                InlineKeyboardButton("❌ Сохранить деньги", callback_data=f"skip_{chat_id}")
            ]]
            await update.message.reply_text(res, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            return
        else:
            owner_id = game["properties"][pos_str]
            if owner_id != player["id"]:
                owner_p = next(p for p in game["players"] if p["id"] == owner_id)
                keyboard = [[InlineKeyboardButton("💵 Оплатить аренду", callback_data=f"rent_{chat_id}_{player['position']}")]]
                res += f"💳 Поле принадлежит {owner_p['icon']} {owner_p['name']}. Нужно оплатить аренду: **{field['rent']} у.е.**"
                await update.message.reply_text(res, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
                return
            else:
                res += "✨ Вы встали на свою клетку."
    elif field["type"] == "tax":
        keyboard = [[InlineKeyboardButton("💸 Уплатить налог", callback_data=f"tax_{chat_id}_{field['fee']}")]]
        res += f"🛑 Налоговая инспекция! Обязательный платеж: **{field['fee']} у.е.**"
        await update.message.reply_text(res, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return
    elif field["type"] == "go_to_jail":
        player["position"] = 10
        player["jail_turns"] = 3
        res += "👮‍♂️ Вас поймала полиция! Вы отправлены в Тюрьму."
    else:
        res += "ℹ️ Безопасная клетка."

    game["current_turn"] = (game["current_turn"] + 1) % len(game["players"])
    next_p = game["players"][game["current_turn"]]
    final_map = get_map_render(game)
    await update.message.reply_text(f"{res}\n\n{final_map}\n\n➡️ Очередь игрока: {next_p['icon']} **{next_p['name']}** (/roll)", parse_mode="Markdown")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data.split("_")
    action = data[0]
    
    if action == "jail":
        sub_action = data[1]
        chat_id = int(data[2])
        game = GAMES[chat_id]
        player = game["players"][game["current_turn"]]
        
        if query.from_user.id != player["id"]:
            return

        if sub_action == "pay":
            if player["balance"] >= 50:
                player["balance"] -= 50
                player["jail_turns"] = 0
                res_text = f"🔓 {player['icon']} **{player['name']}** оплатил штраф 50 у.е. и освободился!"
            else:
                res_text = f"❌ Недостаточно средств для выкупа!"
        else:
            d1, d2 = random.randint(1, 6), random.randint(1, 6)
            if d1 == d2:
                player["jail_turns"] = 0
                res_text = f"🎲 {player['icon']} Бросок: {d1}:{d2}. **ДУБЛЬ!** Вы свободны!"
            else:
                player["jail_turns"] -= 1
                res_text = f"🎲 {player['icon']} Бросок: {d1}:{d2}. Дубли не совпали. Осталось ходов в тюрьме: {player['jail_turns']}"
                if player["jail_turns"] == 0:
                    player["balance"] -= 50
                    res_text += "\n💸 Срок вышел, списано 50 у.е. пошлины. Вы на свободе."

        game["current_turn"] = (game["current_turn"] + 1) % len(game["players"])
        next_p = game["players"][game["current_turn"]]
        await query.edit_message_text(f"{res_text}\n\n➡️ Очередь ходов: {next_p['icon']} **{next_p['name']}** (/roll)", parse_mode="Markdown")
        return

    chat_id = int(data[1])
    game = GAMES[chat_id]
    player = game["players"][game["current_turn"]]

    if query.from_user.id != player["id"]:
        return

    res_text = ""
    
    if action == "buy":
        pos = int(data[2])
        field = BOARD[pos]
        if player["balance"] >= field["price"]:
            player["balance"] -= field["price"]
            game["properties"][str(pos)] = player["id"]
            res_text = f"🎉 {player['icon']} **{player['name']}** купил *{field['name']}* за {field['price']} у.е.!"
        else:
            res_text = f"❌ Недостаточно средств!"
            
    elif action == "skip":
        res_text = f"🏳️ {player['icon']} **{player['name']}** решил сохранить деньги и пропустил покупку."
        
    elif action == "rent":
        pos = int(data[2])
        field = BOARD[pos]
        owner_id = game["properties"][str(pos)]
        owner_p = next(p for p in game["players"] if p["id"] == owner_id)
        
        player["balance"] -= field["rent"]
        owner_p["balance"] += field["rent"]
        res_text = f"💸 Аренда выплачена владельцу! {player['icon']} ➡️ {owner_p['icon']} (**{field['rent']} у.е.**)"
        
    elif action == "tax":
        fee = int(data[2])
        player["balance"] -= fee
        res_text = f"💸 {player['icon']} **{player['name']}** уплатил налог государству ({fee} у.е.)."

    game["current_turn"] = (game["current_turn"] + 1) % len(game["players"])
    next_p = game["players"][game["current_turn"]]
    final_map = get_map_render(game)
    
    await query.edit_message_text(
        text=f"{res_text}\n\n{final_map}\n\n➡️ Следующий ход: {next_p['icon']} **{next_p['name']}** (/roll)",
        parse_mode="Markdown"
    )

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_cmd))
    application.add_handler(CommandHandler("play", play_cmd))
    application.add_handler(CommandHandler("start_game", start_game_cmd))
    application.add_handler(CommandHandler("my", my_cmd))
    application.add_handler(CommandHandler("roll", roll_cmd))
    application.add_handler(CallbackQueryHandler(button_callback))

    print("Монополия успешно запущена!")
    application.run_polling()

if __name__ == "__main__":
    main()