import discord
import re
from discord.ui import Button, View
from discord.ext import commands
from discord.app_commands import checks
import random
import asyncio
import logging
import time
import aiosqlite
import difflib
import json
import time
import os


logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='w',
                    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')


polls = {
    "1": {
        "text": "{}'s mum looked pretty sexy lately, what do y'all think?",
        "options": [("Definitely", "definitely"), ("Eh", "eh"), ("Bro she is gorgeous", "she_is_gorgeous")]
    },
    "2": {
        "text": "Have you seen {}'s mum? If 'overweight' was a sport, she’d be an Olympian, right?",
        "options": [("Agree", "agree"), ("Disagree", "disagree")]
    },
    "3": {
        "text": "Would you eat {}'s mum's booty hole for -$100?",
        "options": [("I would need more.", "nah"), ("For sure", "for_sure")]
    },
    "4": {
        "text": "How does {}'s mum manage to look that sexy?",
        "options": [("Semen skincare", "semen_skincare"), ("She doesn't", "she_doesn't"), ("Good personality", "good_personality")]
    },
    "5": {
        "text": "{}'s mum.",
        "options": [("Tits", "tits"), ("Ass", "ass"), ("Personality", "personality")]
    },
    "6": {
        "text": "What's your best guess at {}'s mum's body count",
        "options": [("25", "25"), ("50", "50"), ("100", "100"), ("250+", "250+")]
    },
    "7": {
        "text": "What does {}'s mum smell most like?",
        "options": [("Ham", "ham"), ("Fish", "fish"), ("Rotten Eggs", "rotten_eggs"), ("Minty Fresh Extra® Gum", "extra®_Gum"), ("Period blood", "period_blood")]
    },
}

KEYWORD_JOKES = {
    'big': [
        'You know what else is big? Your mum!',
        'Big like your mum\'s asshole after i\'m done with her!',
    ],
    'small':[ 'That might be small, but your mum\'s appetite sure isn\'t!',],
    'kys':[ 'That\'s not very nice!',],
    'soft': ['Not as soft as your mum\'s ass!',],
    'slay': ['Slay yo mama\'s booty hole wide open!',],
    'huge': ['Almost as huge as my undying love for your mother.','Talking of huge have you seen your mama\'s ass lately?',],
    'hairy': ['Hairy as your mum!',],
    'old': ['Couldn\'t be as old as your mum!',],
    'fat': ['Not as fat as your mum!',],
    'cute': ['Just like your mum!', 'Could say the same about your mum',],
    'sucks': ['sucks like your mum on a friday night',],
    'loose': ['yo mama pussy loose ah hell',],
    'dinner': (["Speaking of dinner where is your mum ;)"], {'chance': 60}),
    'heavy': ['Heavy? I guess you haven\'t lifted your mum lately! :rofl:',],
    'slow': ['Not as slow as your mum on a treadmill!',],
    'fast': ['Couldn\'t be as fast as your mum makes me bust',],
    'tight': ['Tighter than your mum\'s yoga pants!',],
    'hard': ['Not as hard as me when I see your mum!','Hard like me when I see your mum'],
    'hot': ['Couldn\'t be hotter than your mum last night!','Not as hot as your mum!',],
    'weak': ['Weaker than your mum\'s dieting schedule!',],
    'bright': ['Not as bright as your mum’s smile - bless her! :blush:',],
    'thin': ['Thin? Couldn\'t be your mum!',],
    'deep': ['Almost as deep as I am in your mama',],
    'mistake': ['mistake like when your mum had you!',],
    'food': ['talking bout food, tell ur mum daddy wants his milky ;)',],
    'help': (["if anyone needs help it\'s your mum. she needs to lose some weight :)"], {'chance': 60}),
    ('would', 'you'): ['Would you get your mum for me so she can bounce on deez nuts!',],
    ('get', 'on'): ['I\'ll get on just like your mum got on this dick!',],
    ('deez', 'nuts'): ['deez nuts in yo mama!',],
    ('hop', 'on'): ['Hop on deez nuts!','Get ur mum to hop on deez nuts!',],
    ('this', 'sucks', True): ['Yeah sucks more than your mum!',],
    ('u', 'should'): ['u should tell ur mum she lookin kinda cute today','u should suck yo mama',],
    ('is', 'ass'): ['Your mum is ass.',],
    ('im', 'i\'m', 'ass', True): ['Your mum is ass.',],
    ('not', 'easy'): ['Unlike yo mama!',],
    ('are', 'ass'): ['Your mums titties are ass.',],
    ('my', 'perms'): ['Stop complaining','Shut up'],
    ('should', 'i'): ['yes.','no.','maybe.','without a doubt',],
    ('loading'): ['loading up your mum with goodness',],
    ('thanks', 'bot'): ['you\'re welcome','all good', 'don\'t even worry about it'],
    ('good', 'bot'): ['thank you','appreciate it',],
    ('silly', 'bot'): ['https://tenor.com/view/emoji-emojis-emoticon-mood-tongue-face-gif-16108971',':stuck_out_tongue_closed_eyes: ','https://tenor.com/view/cat-awful-meme-funny-gif-24724857',],
    ('bad', 'bot'): ['damn','k','https://tenor.com/view/waah-waa-sad-wah-waaah-gif-25875771','https://tenor.com/view/ishizuka-akari-crying-girl-gif-27076775'],
    ('i\'m', 'getting'): ['and i\'m getting lucky with yo mama!','and i\'m getting good ass top from yo mama!',],
    ('im', 'getting', True): ['i\'m getting lucky with yo mama!','i\'m getting good ass top from yo mama!',],
    ('good', 'morning'): ['Good Morning yourself! Is your mum walking alright after last night?',],
    ('hate', 'you'): ['https://tenor.com/view/damn-kendrick-lamar-%EC%BC%84%EB%93%9C%EB%A6%AD-%EB%9D%BC%EB%A7%88-gif-9061375','damn.',],
    ('shut', 'up', 'bot'): ['make me','damn.','fine :cry:','k','https://tenor.com/view/waah-waa-sad-wah-waaah-gif-25875771',],
    'mistakes': ['like your mum when she had you!','like your parent\'s when they had you!',],
    ('fuck', 'you', 'u', 'bot', True): ['make me','damn.','fine :cry:','k','https://tenor.com/view/waah-waa-sad-wah-waaah-gif-25875771',],
}

KEYWORD_PATTERNS = {
    keywords: re.compile(
        r'\b' + (r'\b \b'.join(keywords[:-1]) if isinstance(keywords, tuple) and keywords[-1] is True else r'\b \b'.join(keywords) if isinstance(keywords, tuple) else keywords) + r'\b', 
        re.IGNORECASE
    ) for keywords in KEYWORD_JOKES.keys()
}

SLASH_COMMAND_JOKES = [
    'Yo mama is so fat that when she hauls ass, she has to make two trips.',
    'Yo mama is so poor she goes to KFC to lick other peoples fingers.',
    'Yo mama\'s so fat, her car has stretch marks.',
    'Your mama so fat, her memory foam mattress drinks to forget.',
    'Yo mama so beautiful I wish to gaze upon her heavenly body and make love to her until the dawn of tomorrow, her bosom awaits me...',
    'Yo mama\'s so stupid, she got locked in the grocery store and starved to death.',
    'Yo mama the global throat goat',
    'Yo mama so fat when I had a threesome with her I never met the other guy.',
    'Yo mama so nasty, she went swimming and made the Dead Sea.',
    'Your mother is a lovely woman and I have a great deal of respect for her',
    'Yo mama so ugly her blowjobs count as anal.',
    'Yo mama so fat, we’re getting increasingly concerned for her well being and only want to try and help her any way we can.',
    'I told yo mama to act her age and the bitch dropped dead.',
    'Yo mama so fat after I finished fucking her I rolled over three times and I was still on the bitch.',
    'Yo mama so nasty, she got fired from the sperm bank for drinking on the job',
    'Yo mama so fat she got a $1567 debt on Afterpay from ordering McDonalds',
    'Yo mama smells like ham.',
]
 
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True  # Necessary for member-related features
intents.message_content = True
intents.voice_states = True  # Important for voice channel interactions

class MyBot(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db_connection = None  # Initialize here, no need for global variable
        
    async def setup_hook(self):
        self.db_connection = await aiosqlite.connect('my_bot_database.db')
        await self.load_extension('fishing')  # Load extensions like this
          

    async def close(self):
        if self.db_connection:
            await self.db_connection.close()
        await super().close()

bot = MyBot(command_prefix="/", intents=intents)


async def initialize_database(db_connection):
    try:
        await db_connection.executescript('''
            CREATE TABLE IF NOT EXISTS commands_usage (
                command_id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                command_name TEXT NOT NULL,
                usage_count INTEGER DEFAULT 0,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE UNIQUE INDEX IF NOT EXISTS idx_commands_usage ON commands_usage (guild_id, command_name);

            CREATE TABLE IF NOT EXISTS jokes_usage (
                joke_id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id TEXT NOT NULL,
                keyword TEXT NOT NULL,
                count INTEGER DEFAULT 0,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE UNIQUE INDEX IF NOT EXISTS idx_jokes_usage ON jokes_usage (server_id, keyword);

            CREATE TABLE IF NOT EXISTS guild_stats (
                guild_id INTEGER PRIMARY KEY,
                message_count INTEGER DEFAULT 0,
                last_message_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS polls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                message_id INTEGER,
                channel_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            );

            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                option TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(poll_id) REFERENCES polls(id)
            );

            CREATE TABLE IF NOT EXISTS buy_command_usage (
                user_id INTEGER NOT NULL,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id)
            );

            -- Updated user_currency table for storing user balance and related stats
            CREATE TABLE IF NOT EXISTS user_currency (
                user_id INTEGER PRIMARY KEY,
                currency INTEGER DEFAULT 1000,
                losses INTEGER DEFAULT 0,
                bet_amount INTEGER DEFAULT 10,
                consecutive_days INTEGER DEFAULT 0,
                last_reward_time TIMESTAMP,
                last_played TIMESTAMP
            );
        ''')
        await db_connection.commit()
    except Exception as e:
        logging.error(f"Error initializing database: {e}")



async def get_user_data(db_connection, user_id):
    async with db_connection.execute('SELECT * FROM user_currency WHERE user_id = ?', (user_id,)) as cursor:
        row = await cursor.fetchone()
    if row:
        return {
            "currency": row[1],
            "losses": row[2],
            "bet_amount": row[3],
            "consecutive_days": row[4],
            "last_reward_time": row[5],
            "last_played": row[6]
        }
    else:
        # User not found, insert them with a default balance
        await db_connection.execute('''
            INSERT INTO user_currency (user_id, currency, losses, bet_amount, consecutive_days, last_reward_time, last_played)
            VALUES (?, 1000, 0, 10, 0, NULL, NULL)
        ''', (user_id,))
        await db_connection.commit()
        return {
            "currency": 1000,
            "losses": 0,
            "bet_amount": 10,
            "consecutive_days": 0,
            "last_reward_time": None,
            "last_played": None
        }


async def load_user_data(db_connection, limit=10):
    try:
        query = 'SELECT user_id, currency, losses FROM user_currency ORDER BY currency DESC LIMIT ?'
        async with db_connection.execute(query, (limit,)) as cursor:
            rows = await cursor.fetchall()
        return [{"user_id": row[0], "currency": row[1], "losses": row[2]} for row in rows]
    except Exception as e:
        logging.error(f"Error in load_user_data: {e}")
        return []

async def update_command_usage(db_connection, guild_id, command_name):
    logging.info(f"update_command_usage called for server: {guild_id}, command: {command_name}")
    try:
        await db_connection.execute('''
            INSERT INTO commands_usage (guild_id, command_name, usage_count)
            VALUES (?, ?, 1)
            ON CONFLICT(guild_id, command_name) DO UPDATE 
            SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
        ''', (guild_id, command_name))
        await db_connection.commit()
    except Exception as e:
        logging.error(f"Error updating command usage stats: {e}")


async def update_stats(db_connection, server_id, keyword):
    logging.info(f"update_stats called for server: {server_id}, keyword: {keyword}")
    try:
        await db_connection.execute('''
            INSERT INTO jokes_usage (server_id, keyword, count)
            VALUES (?, ?, 1)
            ON CONFLICT(server_id, keyword) DO UPDATE 
            SET count = count + 1, last_used = CURRENT_TIMESTAMP
        ''', (server_id, keyword))
        await db_connection.commit()
    except Exception as e:
        logging.error(f"Error updating joke stats: {e}")


async def save_message_count(db_connection, guild_id):
    try:
        await db_connection.execute('''
            INSERT INTO guild_stats (guild_id, message_count)
            VALUES (?, 1)
            ON CONFLICT(guild_id) DO UPDATE 
            SET message_count = message_count + 1
        ''', (guild_id,))
        await db_connection.commit()
    except Exception as e:
        logging.error(f"Error saving message count: {e}")

async def get_message_count(db_connection, guild_id):
    try:
        cursor = await db_connection.execute('SELECT message_count FROM guild_stats WHERE guild_id = ?', (guild_id,))
        row = await cursor.fetchone()
        await cursor.close()
        return row[0] if row else 0
    except Exception as e:
        logging.error(f"Error getting message count: {e}")
        return 0

async def reset_message_count(db_connection, guild_id):
    try:
        await db_connection.execute('''
            UPDATE guild_stats SET message_count = 0
            WHERE guild_id = ?
        ''', (guild_id,))
        await db_connection.commit()
    except Exception as e:
        logging.error(f"Error resetting message count: {e}")



async def get_stats(db_connection, server_id):
    try:
        # Fetch command usage stats
        cursor = await db_connection.execute('''
            SELECT command_name, usage_count, last_used FROM commands_usage WHERE guild_id = ?
        ''', (server_id,))
        command_stats = await cursor.fetchall()
        await cursor.close()

        # Fetch joke keyword stats
        cursor = await db_connection.execute('''
            SELECT keyword, count, last_used FROM jokes_usage WHERE server_id = ?
        ''', (server_id,))
        joke_stats = await cursor.fetchall()
        await cursor.close()

        logging.info(f"Command stats: {command_stats}, Joke stats: {joke_stats}")
        return command_stats, joke_stats
    except Exception as e:
        logging.error(f"Error fetching stats: {e}")
        return None, None

async def update_poll_message(db_connection, interaction, poll_id):
    # Retrieve the poll configuration based on poll_id
    poll_key = poll_id.split("_")[0]  # Extract the poll key from the poll_id
    poll_config = polls.get(poll_key, {})

    # Create a mapping of option values to labels
    option_mapping = {value: label for label, value in poll_config.get("options", [])}

    # Query the database for the vote counts
    cursor = await db_connection.execute("SELECT option, COUNT(*) FROM votes WHERE poll_id = ? GROUP BY option", (poll_id,))
    vote_data = await cursor.fetchall()

    # Calculate total votes for percentage calculation
    total_votes = sum(count for _, count in vote_data)

    # Translate the vote data using the option mapping and format it
    translated_votes = []
    for option, count in vote_data:
        label = option_mapping.get(option, 'Unknown')
        percentage = (count / total_votes * 100) if total_votes > 0 else 0
        bar_length = int(percentage / 10)  # Adjust the length of the bar according to your preference
        bar = '▓' * bar_length + '░' * (10 - bar_length)
        translated_votes.append(f"{label}: {bar} {count} votes ({percentage:.1f}%)")

    # Format the vote content
    votes_content = "\n".join(translated_votes)

    # Update the embed with the new content
    embed = interaction.message.embeds[0]
    embed.clear_fields()
    embed.add_field(name="Poll Results", value=votes_content, inline=False)
    await interaction.message.edit(embed=embed)

async def update_user_currency(db_connection, user_id, amount):
    user_data = await get_user_data(db_connection, user_id)  # Corrected to pass only two arguments
    new_currency = user_data["currency"] + amount
    losses = user_data["losses"] - amount if amount < 0 else user_data["losses"]
    await db_connection.execute('''
        UPDATE user_currency SET currency = ?, losses = ? WHERE user_id = ?
    ''', (new_currency, losses, user_id))
    await db_connection.commit()

async def update_user_bet_amount(db_connection, user_id, bet_amount):
    await db_connection.execute('''
        UPDATE user_currency SET bet_amount = ? WHERE user_id = ?
    ''', (bet_amount, user_id))
    await db_connection.commit()

async def get_user_currency(db_connection, user_id):
    user_data = await get_user_data(db_connection, user_id)
    return user_data["currency"] if user_data else 0

async def update_last_played(db_connection, user_id):
    current_time = time.time()
    await db_connection.execute('''
        UPDATE user_currency SET last_played = ? WHERE user_id = ?
    ''', (current_time, user_id))
    await db_connection.commit()

async def check_daily_reward(db_connection, user_id):
    user_data = await get_user_data(db_connection, user_id)
    last_reward_time = user_data['last_reward_time'] or 0
    consecutive_days = user_data['consecutive_days']

    current_time = time.time()
    if current_time - last_reward_time >= 86400:  # 24 hours have passed
        consecutive_days = consecutive_days + 1 if current_time - last_reward_time < 172800 else 1  # Less than 48 hours
        daily_reward_amount = 1000 + 500 * consecutive_days

        await db_connection.execute('''
            UPDATE user_currency SET 
                currency = currency + ?,
                consecutive_days = ?, 
                last_reward_time = ? 
            WHERE user_id = ?
        ''', (daily_reward_amount, consecutive_days, current_time, user_id))
        await db_connection.commit()
        return True, daily_reward_amount

    return False, 0


# This function checks if an item is available and gets its price.
async def check_item_availability(db_connection, item_name):
    async with db_connection.execute("SELECT id, price FROM items WHERE name = ?", (item_name,)) as cursor:
        return await cursor.fetchone()

# This function adds an item to the user's inventory.
async def add_item_to_user_inventory(db_connection, user_id, item_id):
    await db_connection.execute("INSERT INTO user_inventory (user_id, item_id) VALUES (?, ?)", (user_id, item_id))
    await db_connection.commit()


@bot.event
async def on_ready():

    await bot.change_presence(activity=discord.Game(name="with yo mama!"))
    # Log the bot's connection
    logging.info(f'{bot.user.name} has connected to Discord!')



        
triggered_polls = set()

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    logging.info(f'Received message: "{message.content}" from {message.author} on server: {message.guild.id}')

    guild_id = str(message.guild.id)

    # Check if the user is whitelisted
    whitelisted_users = load_whitelist().get(str(message.guild.id), [])
    if message.author.id in whitelisted_users:
        logging.info(f"User {message.author} is whitelisted. Skipping joke responses.")
        return
    
    # Increment the message count for the guild
    await save_message_count(guild_id)

    # Load thresholds from the JSON file
    thresholds = load_thresholds().get(guild_id, {'poll': 50, 'joke': 20})
    poll_message_threshold = thresholds['poll']
    joke_message_threshold = thresholds['joke']

    # Retrieve current message count for the guild
    current_count = await get_message_count(guild_id)

    # Check for poll threshold
    if current_count >= poll_message_threshold:
        random_member = select_random_member(message.guild)
        if random_member:
            await create_and_send_poll(message.channel, random_member)
            await reset_message_count(guild_id)

    # Check for joke threshold
    elif current_count % joke_message_threshold == 0:
        joke = random.choice(SLASH_COMMAND_JOKES)
        await message.reply(joke)

    # Process keyword jokes
    message_content = message.content.lower()
    for keywords, jokes_data in KEYWORD_JOKES.items():
        # Extract jokes list and properties
        jokes_list, props = jokes_data if isinstance(jokes_data, tuple) else (jokes_data, {})
        pattern = KEYWORD_PATTERNS[keywords]
        if pattern.search(message_content):
            # Check for optional chance of sending a joke
            if props.get('chance', 100) >= random.randint(1, 100):
                joke = random.choice(jokes_list)
                await message.reply(joke)
                await update_stats(guild_id, '_'.join(keywords) if isinstance(keywords, tuple) else keywords)
            break

    # Process commands if the bot is using command decorators
    await bot.process_commands(message)

@bot.tree.command(name='your_mum', description='Respond with a random your mum joke.')
async def your_mum(interaction: discord.Interaction, member_name: str = None):
    logging.info(f"'your_mum' command invoked on server: {interaction.guild_id}")
    start_time = time.time()  # Start time for execution measurement

    try:
        # Defer the response if processing might take some time
        await interaction.response.defer()

        guild = interaction.guild
        guild_id = str(guild.id)

        # Load the whitelist data
        whitelist_data = load_whitelist()
        whitelisted_users = whitelist_data.get(guild_id, [])

        # Find a member based on the provided name or select a random member
        member = find_closest_member(guild, member_name) if member_name else select_random_member(guild)

        # Check if the member is whitelisted, if so, don't send a joke
        if member and member.id in whitelisted_users:
            await interaction.followup.send(f"{member.mention} is whitelisted and will not receive a joke.", ephemeral=True)
            return

        # Choose a random joke
        joke = random.choice(SLASH_COMMAND_JOKES)
        # If a member is found, format the joke with the member's mention
        if member:
            joke_text = joke.format(member=member.mention) if '{member}' in joke else f"{member.mention}, {joke}"
        else:
            # If no member is found or provided, use the joke as is
            joke_text = joke

        # Send the joke as a follow-up response
        await interaction.followup.send(joke_text)

        # Update command usage statistics
        await update_command_usage(guild_id, 'your_mum')

    except Exception as e:
        logging.error(f"Error in 'your_mum' command: {e}")
        # Send error message as a follow-up if the initial response was deferred
        await interaction.followup.send("An error occurred while processing your request.", ephemeral=True)

    end_time = time.time()  # End time for execution measurement
    logging.info(f"'your_mum' command processed in {end_time - start_time} seconds")
    
@bot.tree.command(name='stats', description='Display server command usage stats.')
async def stats(interaction: discord.Interaction):
    try:
        # Fetch stats for the guild
        guild_id = interaction.guild.id
        command_stats, joke_stats = await get_stats(guild_id)

        # Create an embed object for a richer message
        embed = discord.Embed(title=f"Stats for {interaction.guild.name}", color=discord.Color.blue())

        # Add command usage stats to embed
        if command_stats:
            embed.add_field(name="Command Usage", value="\u200B", inline=False)  # Add a field for commands
            for command_name, usage_count, last_used in command_stats:
                embed.add_field(name=command_name, value=f"Used {usage_count} times\nLast used: {last_used}", inline=True)
        else:
            embed.add_field(name="Command Usage", value="No command usage stats.", inline=False)

        # Add keyword jokes stats to embed
        if joke_stats:
            embed.add_field(name="Keyword Jokes", value="\u200B", inline=False)  # Add a field for jokes
            for keyword, count, last_used in joke_stats:
                embed.add_field(name=keyword, value=f"Triggered {count} times\nLast used: {last_used}", inline=True)
        else:
            embed.add_field(name="Keyword Jokes", value="No keyword jokes stats.", inline=False)

        # Send the embed message
        await interaction.response.send_message(embed=embed)

    except Exception as e:
        logging.exception("Error in 'stats' command")
        # It's a good idea to send errors as ephemeral messages so only the command caller can see it
        await interaction.response.send_message("An error occurred while fetching stats.", ephemeral=True)
        


class PollButton(discord.ui.Button):
    def __init__(self, label, value, poll_id, db_connection):
        super().__init__(style=discord.ButtonStyle.primary, label=label)
        self.value = value
        self.poll_id = poll_id
        self.db_connection = db_connection  # Pass the database connection to the button

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_id = interaction.user.id

        cursor = await self.db_connection.execute("SELECT * FROM votes WHERE poll_id = ? AND user_id = ?", (self.poll_id, user_id))
        if await cursor.fetchone():
            await interaction.followup.send("You have already voted.", ephemeral=True)
            return

        await self.db_connection.execute("INSERT INTO votes (poll_id, user_id, option) VALUES (?, ?, ?)", (self.poll_id, user_id, self.value))
        await self.db_connection.commit()
        await update_poll_message(self.db_connection, interaction, self.poll_id)


def create_poll_view(poll_options, poll_id, db_connection):
    view = discord.ui.View()
    for label, value in poll_options:
        view.add_item(PollButton(label, value, poll_id, db_connection))
    return view

async def create_and_send_poll(channel, member, db_connection, poll_key=None):
    # Load the whitelist
    whitelist_data = load_whitelist()
    guild_id = str(channel.guild.id)

    # Check if the member is whitelisted
    if member.id in whitelist_data.get(guild_id, []):
        await channel.send(f"{member.mention} is whitelisted and cannot be targeted by polls.", delete_after=10)
        return  # Exit the function if the member is whitelisted

    poll_key = poll_key or random.choice(list(polls.keys()))
    poll_config = polls[poll_key]
    poll_message_text = poll_config["text"].format(member.mention)
    embed = discord.Embed(title="Poll", description=poll_message_text, color=0x00ff00)
    poll_id = f"{poll_key}_{int(time.time())}"
    poll_message = await channel.send(embed=embed, view=create_poll_view(poll_config["options"], poll_id, db_connection))
    await db_connection.execute("INSERT INTO polls (key, message_id, channel_id, guild_id) VALUES (?, ?, ?, ?)", (poll_key, poll_message.id, channel.id, channel.guild.id))
    await db_connection.commit()

@bot.tree.command(name='poll', description='Create a poll about a specific or random member.')
async def poll(interaction: discord.Interaction, member_name: str = None, poll_key: str = None):
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message("This command can't be used outside of a server.", ephemeral=True)
        return

    # Load the whitelist
    whitelist_data = load_whitelist()
    guild_id = str(guild.id)

    # Defer the response if processing might take some time
    await interaction.response.defer()

    try:
        selected_member = find_closest_member(guild, member_name) if member_name else select_random_member(guild)
        
        # Exit if the selected member is whitelisted
        if selected_member.id in whitelist_data.get(guild_id, []):
            await interaction.followup.send(f"{selected_member.mention} is whitelisted and cannot be targeted by polls.", ephemeral=True)
            return

        poll_key = poll_key if poll_key and poll_key in polls else random.choice(list(polls.keys()))

        if selected_member:
            # Call a function to create and send the poll
            await create_and_send_poll(interaction.channel, selected_member, bot.db_connection, poll_key)
            await interaction.followup.send(f"A poll has been created for {selected_member.mention}.", ephemeral=True)
        else:
            await interaction.followup.send("No matching members found.", ephemeral=True)

    except Exception as e:
        logging.error(f"Error during poll creation: {e}")
        await interaction.followup.send("An error occurred while trying to create the poll.", ephemeral=True)

    # Update command usage statistics, assuming this function exists
    await update_command_usage(bot.db_connection, guild.id, 'poll')
     
@bot.tree.command(name='set_thresholds', description='Set thresholds for polls and jokes in this server.')
async def set_thresholds_command(interaction: discord.Interaction, poll_threshold: int, joke_threshold: int):
    # Manual validation for threshold values
    if not 1 <= poll_threshold <= 100 or not 1 <= joke_threshold <= 100:
        await interaction.response.send_message("Poll threshold must be between 1 and 100, and joke threshold must be between 1 and 100.", ephemeral=True)
        return

    guild_id = str(interaction.guild_id)  # JSON keys must be strings
    guild_thresholds[guild_id] = {'poll': poll_threshold, 'joke': joke_threshold}
    save_thresholds(guild_thresholds)

    confirmation_message = (
        f"Thresholds updated for this server:\n"
        f"- Poll Trigger Threshold: {poll_threshold} messages\n"
        f"- Joke Trigger Threshold: {joke_threshold} messages"
    )
    await interaction.response.send_message(confirmation_message)

def load_thresholds():
    try:
        with open('thresholds.json', 'r') as file:
            # Check if the file is empty
            content = file.read()
            if not content:
                return {}
            return json.loads(content)
    except FileNotFoundError:
        # Create a new JSON file with an empty dictionary if it doesn't exist
        with open('thresholds.json', 'w') as file:
            json.dump({}, file, indent=4)
        return {}
    except json.JSONDecodeError:
        # Handle any other JSON decode errors
        logging.error("Error decoding JSON from 'thresholds.json'. Using default thresholds.")
        return {}

def save_thresholds(thresholds):
    with open('thresholds.json', 'w') as file:
        json.dump(thresholds, file, indent=4)

guild_thresholds = load_thresholds()

def select_random_member(guild):
    return random.choice([member for member in guild.members if not member.bot]) if guild.members else None


def find_closest_member(guild, member_name):
    if not member_name:
        return None

    member_name = member_name.lower()
    best_match = None
    highest_similarity = 0

    for member in guild.members:
        if member.bot:
            continue

        # Consider both the member's display name and username
        names_to_compare = [member.display_name.lower(), member.name.lower()]

        for name in names_to_compare:
            similarity = difflib.SequenceMatcher(None, member_name, name).ratio()
            if similarity > highest_similarity:
                best_match = member
                highest_similarity = similarity

    # Adjust the similarity threshold if needed
    similarity_threshold = 0.2

    return best_match if highest_similarity >= similarity_threshold else None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Fetch a joke from the SLASH_COMMAND_JOKES database
def fetch_joke():
    # Assume SLASH_COMMAND_JOKES is a list of jokes
    joke = random.choice(SLASH_COMMAND_JOKES)
    return joke


def load_whitelist():
    try:
        with open('whitelist.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        logging.error("Error decoding JSON from whitelist.json")
        return {}

def save_whitelist(whitelist_data):
    with open('whitelist.json', 'w') as file:
        json.dump(whitelist_data, file, indent=4)

class WhitelistCommands(discord.app_commands.Group):
    @discord.app_commands.command(name='whitelist', description='Manage joke whitelist for users.')
    @discord.app_commands.describe(
        user='The user to add or remove from the whitelist',
        action='Specify "add" to add a user or "remove" to remove a user'
    )
    @discord.app_commands.choices(action=[
        discord.app_commands.Choice(name="add", value="add"),
        discord.app_commands.Choice(name="remove", value="remove")
    ])
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def manage_whitelist(self, interaction: discord.Interaction, user: discord.User, action: str):
        whitelist_data = load_whitelist()
        guild_id = str(interaction.guild_id)

        if action == "add":
            # Add user to the whitelist
            if guild_id not in whitelist_data:
                whitelist_data[guild_id] = []
            if user.id not in whitelist_data[guild_id]:
                whitelist_data[guild_id].append(user.id)
                save_whitelist(whitelist_data)
                message = f"{user.mention} has been added to the whitelist."
            else:
                message = f"{user.mention} is already whitelisted."

        elif action == "remove":
            # Remove user from the whitelist
            if guild_id in whitelist_data and user.id in whitelist_data[guild_id]:
                whitelist_data[guild_id].remove(user.id)
                save_whitelist(whitelist_data)
                message = f"{user.mention} has been removed from the whitelist."
            else:
                message = f"{user.mention} is not in the whitelist."

        await interaction.response.send_message(message, ephemeral=True)

bot.tree.add_command(WhitelistCommands())







async def spin_slots(interaction, bet_amount, user_id, original_message=None):
    logger.info("Spinning slots for user_id: %s with bet_amount: %s", user_id, bet_amount)

    # Fetch user data from the database
    user = await get_user_data(bot.db_connection, user_id)  # Pass bot.db_connection here

    # Check for daily reward
    reward_eligible, reward_amount = await check_daily_reward(bot.db_connection, user_id)
    if reward_eligible:
        reward_message = f"You've received your daily reward of ${reward_amount}!"
        if not original_message:
            await interaction.response.send_message(reward_message, ephemeral=True)
        else:
            await interaction.followup.send_message(reward_message, ephemeral=True)

    if user["currency"] < bet_amount:
        response_text = "You don't have enough currency to play!"
        if interaction.response.is_done():
            await interaction.followup.send(response_text, ephemeral=True)
        else:
            await interaction.response.send_message(response_text, ephemeral=True)
        return

    if not original_message:
        # If original_message is not passed, this is a new spin
        slot_message = await show_spinning_reels(interaction, bet_amount)
    else:
        # If original_message is passed, this is a 'Spin Again' action, so we edit the original message
        slot_message = original_message
        spinning_reel_embed = get_spinning_reels_embed(bet_amount)
        await slot_message.edit(embed=spinning_reel_embed)

    await asyncio.sleep(2)  # Simulate spinning time

    # Calculate and show slot results
    result_str, winnings = calculate_slot_results(bet_amount)
    await update_user_currency(bot.db_connection, user_id, winnings - bet_amount)

    # Re-fetch user data to get updated currency
    user = await get_user_data(bot.db_connection, user_id)

    # Prepare the results embed
    results_embed = await prepare_slot_embed(result_str, winnings, bet_amount, user_id)

    # Edit the message with the results embed
    await slot_message.edit(embed=results_embed)

    # Update the view for the message
    view = SlotMachineView(user_id, user["bet_amount"], bot.db_connection, slot_message)
    await slot_message.edit(view=view)

    # Update last played time
    await update_last_played(bot.db_connection, user_id)

        
async def show_spinning_reels(interaction, bet_amount):
    spinning_reel_embed = discord.Embed(title="🎰 Slot Machine 🎰", description="Spinning...")
    spinning_reel_embed.set_image(url="https://i.ibb.co/pXfspXC/Screenshot-2023-11-25-110438.gif")  # Replace with your GIF
    spinning_reel_embed.add_field(name="Bet Amount", value=f"${bet_amount}", inline=False)
    
    # Check if the interaction has already been responded to
    if interaction.response.is_done():
        # If response is already done, use followup to send the message
        message = await interaction.followup.send(embed=spinning_reel_embed, ephemeral=False)
    else:
        # Send initial response
        await interaction.response.send_message(embed=spinning_reel_embed, ephemeral=False)
        message = await interaction.original_response()

    return message


def get_spinning_reels_embed(bet_amount):
    spinning_reel_embed = discord.Embed(title="🎰 Slot Machine 🎰", description="Spinning...")
    spinning_reel_embed.set_image(url="https://i.ibb.co/pXfspXC/Screenshot-2023-11-25-110438.gif")  # Replace with the direct link to your GIF
    spinning_reel_embed.add_field(name="Bet Amount", value=f"${bet_amount}", inline=False)
    return spinning_reel_embed

# async def show_slot_results(interaction, result_str, winnings, bet_amount, user_id, user_data):
#     new_balance = get_user_currency(user_id, user_data)
#     result_embed = prepare_slot_embed(result_str, winnings, bet_amount)
#     result_embed.add_field(name="New Balance", value=f"${new_balance}", inline=False)
#     view = SlotMachineView(str(user_id), bet_amount)
# 
#     # Edit the original response with the slot results
#     await interaction.edit_original_response(embed=result_embed, view=view)

symbols = ["🍒", "🍇", "🍋", "🃏", "🍀", "🍑", "🔔", "❤", "💎"]
        
def generate_reel():
    # Slightly increased weights for lower value symbols
    symbols = ["🍒", "🍇", "🍋", "🃏", "🍀", "🍑", "🔔", "❤", "💎"]
    symbol_weights = [0.22, 0.22, 0.22, 0.03, 0.09, 0.006, 0.18, 0.06, 0.05]
    return random.choices(symbols, weights=symbol_weights, k=3)

def check_paylines(grid, bet_amount):
    paylines = [
        [grid[0], grid[1], grid[2]], [grid[3], grid[4], grid[5]], [grid[6], grid[7], grid[8]],
        [grid[0], grid[3], grid[6]], [grid[1], grid[4], grid[7]], [grid[2], grid[5], grid[8]],
        [grid[0], grid[4], grid[8]], [grid[2], grid[4], grid[6]]
    ]
    WILD_SYMBOL = "🃏"
    PEACH_JACKPOT_MULTIPLIER = 45  # Adjusted jackpot multiplier
    HIGH_VALUE_PARTIAL_MATCH_MULTIPLIER = 0.55  # Adjusted multiplier for partial matches
    WILD_MULTIPLIER = 1.15  # Adjusted wild multiplier
    HIGH_VALUE_SYMBOLS = ["🍑", "💎", "❤", "🍀"]
    BASE_PAYOUTS = {'🍒': 1.2, '🍇': 1.2, '🍋': 1.2, '🃏': 0, '🍀': 1.9, '🍑': 22, '🔔': 1.8, '❤': 3.2, '💎': 8.5}  # Adjusted payouts
    
    winnings = 0
    for payline in paylines:
        symbol_count = {symbol: payline.count(symbol) for symbol in set(payline)}
        if WILD_SYMBOL in symbol_count:
            for symbol, count in symbol_count.items():
                if symbol != WILD_SYMBOL and count + symbol_count[WILD_SYMBOL] == 3:
                    winnings += bet_amount * BASE_PAYOUTS[symbol] * WILD_MULTIPLIER
                    break
        else:
            if len(set(payline)) == 1:
                symbol = payline[0]
                if symbol == "🍑":
                    winnings += bet_amount * PEACH_JACKPOT_MULTIPLIER
                else:
                    winnings += bet_amount * BASE_PAYOUTS[symbol]
            elif len(set(payline)) == 2:
                most_common = max(set(payline), key=payline.count)
                if payline.count(most_common) == 2 and most_common in HIGH_VALUE_SYMBOLS:
                    winnings += bet_amount * HIGH_VALUE_PARTIAL_MATCH_MULTIPLIER * BASE_PAYOUTS[most_common]
    return winnings

def calculate_slot_results(bet_amount):
    reel1 = generate_reel()
    reel2 = generate_reel()
    reel3 = generate_reel()

    grid = [reel1[0], reel2[0], reel3[0],
            reel1[1], reel2[1], reel3[1],
            reel1[2], reel2[2], reel3[2]]

    result_str = "\n".join([" | ".join(grid[i:i+3]) for i in range(0, 9, 3)])

    winnings = check_paylines(grid, bet_amount)  # Corrected to pass only two arguments

    # RTP adjustment
    rtp_adjustment = random.uniform(0.92, 0.97)
    winnings *= rtp_adjustment

    return result_str, int(winnings)

async def prepare_slot_embed(result_str, winnings, bet_amount, user_id):
    # Define colors for win/lose
    color_win = 0x00ff00  # Green for win
    color_lose = 0xff0000  # Red for loss
    embed_color = color_win if winnings > 0 else color_lose

    # Create the embed object with the results
    embed = discord.Embed(title="🎰 Slot Machine 🎰", color=embed_color)
    embed.description = f"**Spin Results:**\n{result_str}"
    embed.add_field(name="Bet Amount", value=f"${bet_amount}", inline=False)

    # Fetch the user's new balance from the database
    new_balance = await get_user_currency(bot.db_connection, user_id)

    # Calculate the net change in currency
    net_change = winnings - bet_amount

    # Add the result field based on net change
    if net_change > 0:
        embed.add_field(name="💰 Result", value=f"🎉 You won ${net_change}!", inline=False)
    elif net_change < 0:
        loss_amount = abs(net_change)  # Calculate the loss amount
        embed.add_field(name="💰 Result", value=f"😔 You lost ${loss_amount}. Better luck next time!", inline=False)
    else:
        embed.add_field(name="💰 Result", value="Break even. No win or loss.", inline=False)

    embed.add_field(name="New Balance", value=f"${new_balance}", inline=False)

    # Add a thumbnail image
    embed.set_thumbnail(url="https://i.ibb.co/xD66N7C/FY3q1-Wt-UUAIf-Vs-G.jpg")

    # Add a footer with an icon
    embed.set_footer(text="Spin again for a chance to win more!", icon_url="https://i.ibb.co/Ld0NmQz/SLOT-Machine-handle.png")

    return embed


async def handle_message_sending(ctx_or_interaction, message, embed, view):
    if message:
        await message.edit(embed=embed, view=view)
    else:
        if isinstance(ctx_or_interaction, discord.Interaction):
            if ctx_or_interaction.response.is_done():
                # Retrieve the message_id from the interaction's message
                message_id = ctx_or_interaction.message.id
                await ctx_or_interaction.followup.edit_message(message_id, embed=embed, view=view)
            else:
                # Send a new response
                message = await ctx_or_interaction.response.send_message(embed=embed, view=view)
                view.message = message  # Set the message in the view


@bot.tree.command(name='slots', description='Play slots with real casino odds!')
async def slots(interaction: discord.Interaction, bet_amount: str = None):
    user_id = interaction.user.id
    user_currency = await get_user_currency(bot.db_connection, user_id)  # Pass bot.db_connection here

    # Determine the bet amount
    if bet_amount is not None:
        if bet_amount.isdigit():
            bet = min(int(bet_amount), user_currency)
        elif bet_amount.lower() == 'all':
            bet = user_currency
        else:
            await interaction.response.send_message("Invalid bet amount!", ephemeral=True)
            return
        await update_user_bet_amount(bot.db_connection, user_id, bet)  # Pass db_connection here
    else:
        # Fetch user data to use the existing bet amount
        user_data = await get_user_data(bot.db_connection, user_id)  # Pass db_connection here
        bet = user_data['bet_amount'] if user_data else 10  # Default bet amount

    if user_currency < bet:
        await interaction.response.send_message("You don't have enough cash to play!", ephemeral=True)
        return

    # Proceed with spinning the slots
    # Make sure spin_slots is correctly implemented and called
    await spin_slots(interaction, bet, user_id)

       
@bot.tree.command(name='leaderboard', description='Display slots leaderboards.')
async def leaderboard(interaction: discord.Interaction):
    # Fetch all user data from the database
    all_user_data = await load_user_data(bot.db_connection)  # Fetches all users' data

    # Creating an embed for the leaderboard
    embed = discord.Embed(title="🏆 Global Leaderboard", description="Top balances and losses:", color=0x00ff00)

    # Add fields for top users
    for data in all_user_data[:5]:  # Adjust the number as needed
        user_id = data['user_id']
        user = await bot.fetch_user(user_id)
        embed.add_field(
            name=f"{user.name}", 
            value=f"💰 Cash: {data['currency']} | 📉 Losses: {data['losses']}",
            inline=False
        )

    await interaction.response.send_message(embed=embed)




class SlotMachineView(discord.ui.View):
    def __init__(self, user_id, bet_amount, db_connection, message=None):
        super().__init__()
        self.user_id = user_id
        self.bet_amount = bet_amount
        self.message = message
        self.db_connection = db_connection
        
    async def update_bet_amount(self, interaction, amount_change):
        logger.info(f"Updating bet amount for user_id: {self.user_id}")

        # Fetch user data from the database
        user = await get_user_data(self.db_connection, self.user_id)  # Pass db_connection here

        # Calculate new bet amount
        new_bet_amount = max(10, user["bet_amount"] + amount_change)

        # Update the bet amount in the database
        await update_user_bet_amount(self.db_connection, self.user_id, new_bet_amount)  # Pass db_connection here


        # Update the class attribute
        self.bet_amount = new_bet_amount

        if self.message:
            await self.edit_message_bet_amount(interaction, new_bet_amount)
        else:
            logger.warning("No message available to update bet amount.")

        # Acknowledge the interaction without triggering a new spin
        await interaction.response.defer()

    async def edit_message_bet_amount(self, interaction, new_bet_amount):
        try:
            if self.message.embeds:
                embed = self.message.embeds[0]

                # Find and update the 'Bet Amount' field
                for i, field in enumerate(embed.fields):
                    if field.name == "Bet Amount":
                        embed.set_field_at(i, name="Bet Amount", value=f"${new_bet_amount}", inline=False)
                        break

                # Check if the last spin results are being displayed
                results_displayed = any(field.name == "💰 Result" for field in embed.fields)

                # If results are displayed, do not change the embed title or description
                if not results_displayed:
                    embed.title = "🎰 Slot Machine 🎰"
                    embed.description = "Adjust your bet and spin again!"
                    # Ensure no spinning image is set
                    embed.set_image(url="")

                await self.message.edit(embed=embed)
                logger.info(f"Bet amount updated to: {new_bet_amount} for user_id: {self.user_id}")
        except Exception as e:
            logger.error(f"Failed to update bet amount: {e}")
            
    @discord.ui.button(label="Spin Again", style=discord.ButtonStyle.green)
    async def spin_again(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Acknowledge the interaction first
        await interaction.response.defer()

        if interaction.user.id != self.user_id:
            await interaction.followup.send("This is not your machine!", ephemeral=True)
            return

        # Fetch user data from the database
        user = await get_user_data(self.db_connection, self.user_id)

        if user["currency"] < self.bet_amount:
            await interaction.followup.send("You don't have enough currency to spin!", ephemeral=True)
            return

        # Proceed with spinning slots
        if self.message:
            original_message = self.message
        else:
            try:
                original_message = await interaction.original_response()
            except discord.NotFound:
                await interaction.followup.send("Can't spin again: original message not found.", ephemeral=True)
                return

        await spin_slots(interaction, self.bet_amount, self.user_id, original_message)


    @discord.ui.button(label="Increase Bet", style=discord.ButtonStyle.blurple)
    async def increase_bet(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You cannot change the bet amount of another player's game.", ephemeral=True)
            return
        await self.update_bet_amount(interaction, 10)

    @discord.ui.button(label="Decrease Bet", style=discord.ButtonStyle.red)
    async def decrease_bet(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("You cannot change the bet amount of another player's game.", ephemeral=True)
            return
        await self.update_bet_amount(interaction, -10)




if __name__ == "__main__":
    bot.run('INSERT BOT TOKEN HERE')
