import discord
from discord.ext import commands
from flask import Flask
from threading import Thread
import os

# --- 1. WEB SERVER FOR RENDER/UPTIMEROBOT ---
app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. BOT SETUP ---
intents = discord.Intents.default()
intents.members = True 
bot = commands.Bot(command_prefix="!", intents=intents)

# --- 3. FONT TRANSFORMERS ---

def to_asian_style(text):
    mapping = str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "卂乃匚ᗪ乇千Ꮆ卄丨ﾌҜㄥ爪几ㄖ卩Ɋ尺丂ㄒㄩᐯ山乂ㄚ乙卂乃匚ᗪ乇千Ꮆ卄丨ﾌҜㄥ爪几ㄖ卩Ɋ尺丂ㄒㄩᐯ山乂ㄚ乙"
    )
    return text.translate(mapping)

def to_medieval(text):
    mapping = str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "𝕬𝕭𝕮𝕯𝕰𝕱𝕲𝕳𝕴𝕵𝕶𝕷𝕸𝕹𝕺𝕻𝕼𝕽𝕾𝕿𝖀𝖁𝖂𝖃𝖄𝖅𝖆𝖇𝖈𝖉𝖊𝖋𝖌𝖍𝖎𝖏𝖐𝖑𝖒𝖓𝖔𝖕𝖖𝖗𝖘𝖙𝖚𝖛𝖜𝖝𝖞𝖟"
    )
    return text.translate(mapping)

def to_antique(text):
    mapping = str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        "𝓐𝓑𝓒𝓓𝓔𝓕𝓖𝓗𝓘𝓙𝓚𝓛𝓜𝓝𝓞𝓟𝓠𝓡𝓢𝓣𝓤𝓥𝓦𝓧𝓨𝓩𝓪𝓫𝓬𝓭𝓮𝓯𝓰𝓱𝓲𝓳𝓴𝓵𝓶𝓷𝓸𝓹𝓺𝓻𝓼𝓽𝓾𝓿𝔀𝔁𝔂𝔃"
    )
    return text.translate(mapping)

def to_monospace(text):
    mapping = str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
        "𝙰𝙱𝙲𝙳𝙴𝙵𝙶𝙷𝙸𝙹𝙺𝙻𝙼𝙽𝙾𝙿𝚀𝚁𝚂𝚃𝚄𝚅𝚆𝚇𝚈𝚉𝚊𝚋𝚌𝚍𝚎𝚏𝚐𝚑𝚒𝚓𝚔𝚕𝚖𝚗𝚘𝚙𝚚𝚛𝚜𝚝𝚞𝚟𝚠𝚡𝚢𝚣𝟶𝟷𝟸𝟹𝟺𝟻𝟼𝟽𝟾𝟿"
    )
    return text.translate(mapping)

def to_circled(text):
    mapping = str.maketrans(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
        "ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ⓪①②③④⑤⑥⑦⑧⑨"
    )
    return text.translate(mapping)

# --- 4. ROLE CONFIGURATION ---

ROLE_STYLES = {
    "OWNER": {"prefix": "👑 ", "transform": to_medieval},
    "MC PLAYER": {"transform": to_antique},
    "IRON": {"prefix": "🧲","transform": to_asian_style},
    "DIAMOND": {"prefix": "💎 ", "transform": to_circled},
    "NETHERITE": {"prefix": "🔥 ", "transform": to_monospace},
    "SUS": {"prefix": "ඞ ", "transform": None},
    "NOOB": {"prefix": " [L] ", "transform": None},
    "COPPER": {"prefix": "🤎 ", "transform": None}
}

# --- 5. LOGIC ---

@bot.event
async def on_member_update(before, after):
    # Only trigger if roles were added or removed
    if before.roles != after.roles:
        
        # 1. Get the "Clean" base name. 
        # We use global_name (Display Name) first, then fallback to username.
        # This ignores the current 'Nickname' which might already have a font.
        base_name = after.global_name if after.global_name else after.name
        
        # 2. Check roles from highest to lowest
        for role in reversed(after.roles):
            if role.name in ROLE_STYLES:
                style = ROLE_STYLES[role.name]
                
                # 3. Apply font to the clean base name
                if style.get("transform"):
                    new_name = style["transform"](base_name)
                else:
                    new_name = base_name
                
                # 4. Add decoration
                prefix = style.get("prefix", "")
                final_nick = f"{prefix}{new_name}"[:32]

                # 5. Apply the change
                if after.nick != final_nick:
                    try:
                        await after.edit(nick=final_nick)
                        print(f"Updated {after.name} using Display Name: {base_name}")
                    except discord.Forbidden:
                        print(f"Forbidden: Bot cannot rename {after.name}")
                return 

        # 6. Reset to None (original Display Name) if no styled roles remain
        if after.nick is not None:
            try:
                await after.edit(nick=None)
            except discord.Forbidden:
                pass
# --- 6. RUN ---
if __name__ == "__main__":
    keep_alive()
    # It will look for your token in Render's Environment Variables
    bot.run(os.environ.get('DISCORD_TOKEN'))
