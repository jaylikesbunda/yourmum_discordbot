import discord
import re
from discord.ui import Button, View
from discord.ext import commands
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
    'small':[ 'That might be small, but your mum\'s appetite sure isn\'t!', ],
    'soft': ['Not as soft as your mum\'s ass!',],
    'huge': ['Almost as huge as my undying love for your mother.','Talking of huge have you seen your mama\'s ass lately?',],
    'hairy': ['Hairy as your mum!',],
    'old': ['Couldn\'t be as old as your mum!',],
    'fat': ['Not as fat as your mum!',],
    'cute': ['Just like your mum!', 'Could say the same about your mum',],
    'sucks': ['sucks like your mum on a friday night',],
    'loose': ['yo mama pussy loose ah hell',],
    'dinner': ['Speaking of dinnner where is your mum ;)',],
    'heavy': ['Heavy? I guess you haven\'t lifted your mum lately! :rofl:',],
    'slow': ['Not as slow as your mum on a treadmill!',],
    'fast': ['Couldn\'t be as fast as your mum makes me bust',],
    'tight': ['Tighter than your mum\'s yoga pants!',],
    'hard': ['Not as hard as me when I see your mum!','Just like me when I see your mum'],
    'hot': ['Couldn\'t be hotter than your mum last night!','Not as hot as your mum!',],
    'weak': ['Weaker than your mum\'s dieting schedule!',],
    'bright': ['Not as bright as your mum’s smile - bless her! :blush:',],
    'thin': ['Thin? Couldn\'t be your mum!',],
    'deep': ['Almost as deep as I am in your mama',],
    'food': ['talking bout food, tell ur mum daddy wants his milky ;)',],
    'help': ['if anyone needs help it\'s your mum. she needs to lose some weight :)',],
    ('would', 'you'): ['Would you get your mum for me so she can bounce on deez nuts!',],
    ('get', 'on'): ['I\'ll get on just like your mum got on this dick!',],
    ('deez', 'nuts'): ['deez nuts in yo mama!',],
    ('hop', 'on'): ['Hop on deez nuts!','Get ur mum to hop on deez nuts!',],
    ('this', 'sucks', True): ['Yeah sucks more than your mum!',],
    ('u', 'should'): ['u should tell ur mum she lookin kinda cute today','u should suck yo mama',],
    ('is', 'ass'): ['Your mum is ass.',],
    ('not', 'easy'): ['Unlike yo mama!',],
    ('are', 'ass'): ['Your mums titties are ass.',],
    ('my', 'perms'): ['Stop complaining','Shut up'],
    ('should', 'i'): ['yes.','no.','maybe.','without a doubt',],
    ('loading'): ['loading up your mum with goodness',],
    ('thanks', 'bot'): ['you\'re welcome','all good', 'don\'nt even worry about it'],
    ('good', 'bot'): ['thank you','appreciate it',],
    ('bad', 'bot'): ['damn','k','https://tenor.com/view/waah-waa-sad-wah-waaah-gif-25875771','https://tenor.com/view/ishizuka-akari-crying-girl-gif-27076775'],
    ('i\'m', 'getting'): ['and i\'m getting lucky with yo mama!','and i\'m getting good ass top from yo mama!',],
    ('im', 'getting', True): ['i\'m getting lucky with yo mama!','i\'m getting good ass top from yo mama!',],
    ('good', 'morning'): ['Good Morning yourself! Is your mum walking alright after last night?',],
    ('hate', 'you'): ['https://tenor.com/view/damn-kendrick-lamar-%EC%BC%84%EB%93%9C%EB%A6%AD-%EB%9D%BC%EB%A7%88-gif-9061375','damn.',],
    ('shut', 'up', 'bot'): ['make me','damn.','fine :cry:','k','https://tenor.com/view/waah-waa-sad-wah-waaah-gif-25875771',],
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
    '{member}\'s mama smells like ham.',
]
 
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True  # Necessary for member-related features
intents.message_content = True
intents.voice_states = True  # Important for voice channel interactions

class MyBot(commands.Bot):
    async def close(self):
        global db_connection
        if db_connection:
            await db_connection.close()

        await super().close()


bot = MyBot(command_prefix="/", intents=intents)

db_connection = None

async def get_database_connection():
    global db_connection
    return db_connection


async def initialize_database():
    try:
        global db_connection
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
            -- Additional tables if needed
        ''')
        await db_connection.commit()
    except Exception as e:
        logging.error(f"Error initializing database: {e}")

async def update_command_usage(guild_id, command_name):
    logging.info(f"update_command_usage called for server: {guild_id}, command: {command_name}")
    try:
        global db_connection
        await db_connection.execute('''
            INSERT INTO commands_usage (guild_id, command_name, usage_count)
            VALUES (?, ?, 1)
            ON CONFLICT(guild_id, command_name) DO UPDATE 
            SET usage_count = usage_count + 1, last_used = CURRENT_TIMESTAMP
        ''', (guild_id, command_name))
        await db_connection.commit()
    except Exception as e:
        logging.error(f"Error updating command usage stats: {e}")


async def update_stats(server_id, keyword):
    logging.info(f"update_stats called for server: {server_id}, keyword: {keyword}")

    try:
        global db_connection
        await db_connection.execute('''
            INSERT INTO jokes_usage (server_id, keyword, count)
            VALUES (?, ?, 1)
            ON CONFLICT(server_id, keyword) DO UPDATE 
            SET count = count + 1, last_used = CURRENT_TIMESTAMP
        ''', (server_id, keyword))
        await db_connection.commit()
    except Exception as e:
        logging.error(f"Error updating joke stats: {e}")

# Database function to save message counts for a guild
async def save_message_count(guild_id):
    try:
        global db_connection
        await db_connection.execute('''
            INSERT INTO guild_stats (guild_id, message_count)
            VALUES (?, 1)
            ON CONFLICT(guild_id) DO UPDATE 
            SET message_count = message_count + 1
        ''', (guild_id,))
        await db_connection.commit()
    except Exception as e:
        logging.error(f"Error saving message count: {e}")


async def get_message_count(guild_id):
    try:
        global db_connection
        cursor = await db_connection.execute('SELECT message_count FROM guild_stats WHERE guild_id = ?', (guild_id,))
        row = await cursor.fetchone()
        await cursor.close()
        return row[0] if row else 0
    except Exception as e:
        logging.error(f"Error getting message count: {e}")
        return 0

async def reset_message_count(guild_id):
    try:
        global db_connection
        await db_connection.execute('''
            UPDATE guild_stats SET message_count = 0
            WHERE guild_id = ?
        ''', (guild_id,))
        await db_connection.commit()
    except Exception as e:
        logging.error(f"Error resetting message count: {e}")



async def get_stats(server_id):
    logging.info(f"Getting stats for server: {server_id}")
    try:
        global db_connection

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


@bot.event
async def on_ready():
    global db_connection
    db_connection = await aiosqlite.connect('my_bot_database.db')

    await initialize_database()

    await bot.change_presence(activity=discord.Game(name="with yo mama!"))
    logging.info(f'{bot.user.name} has connected to Discord!')

    # Load the MusicCommands cog
    await bot.load_extension('music_commands')

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    logging.info(f'Received message: "{message.content}" from {message.author} on server: {message.guild.id}')

    # Increment the message count for the guild
    guild_id = str(message.guild.id)  # Convert to string for JSON key compatibility
    await save_message_count(guild_id)

    # Load thresholds from JSON file
    thresholds = guild_thresholds.get(guild_id, {'poll': 49, 'joke': 20})
    poll_message_threshold = thresholds['poll']
    joke_message_threshold = thresholds['joke']

    # Check if the message count has reached any of the thresholds
    current_count = await get_message_count(guild_id)

    # Check for poll threshold
    if current_count >= poll_message_threshold:
        # Select a random member from the guild for the poll
        random_member = select_random_member(message.guild)  # This should return a Member object
        if random_member:
            # Call the poll creation function
            await create_and_send_poll(message.channel, random_member)
            # Reset the message count for the guild
            await reset_message_count(guild_id)

    # Check for joke threshold
    elif current_count % joke_message_threshold == 0:  # Using 'elif' to avoid double posting if both conditions meet
        # Select a random 'your_mum' joke from SLASH_COMMAND_JOKES
        joke = random.choice(SLASH_COMMAND_JOKES)
        # Reply to the message that triggered the joke
        await message.reply(joke)

    # Process keyword jokes
    message_content = message.content
    for keywords, jokes_list in KEYWORD_JOKES.items():
        pattern = KEYWORD_PATTERNS[keywords]
        if pattern.search(message_content):
            joke = random.choice(jokes_list)
            await message.reply(joke)
            await update_stats(guild_id, '_'.join(keywords) if isinstance(keywords, tuple) else keywords)
            break

    # Needed to process commands if the bot is also using command decorators
    await bot.process_commands(message)

@bot.tree.command(name='your_mum', description='Respond with a random your mum joke.')
async def your_mum(interaction: discord.Interaction, member_name: str = None):
    logging.info(f"'your_mum' command invoked on server: {interaction.guild_id}")
    start_time = time.time()  # Start time for execution measurement

    try:
        # Defer the response if processing might take some time
        await interaction.response.defer()

        guild = interaction.guild

        # Find a member based on the provided name or select a random member
        member = find_closest_member(guild, member_name) if member_name else select_random_member(guild)

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
        await update_command_usage(guild.id, 'your_mum')

    except Exception as e:
        logging.error(f"Error in 'your_mum' command: {e}")
        # Send error message as a follow-up if the initial response was deferred
        await interaction.followup.send("An error occurred while processing your request.", ephemeral=True)

    end_time = time.time()  # End time for execution measurement
    logging.info(f"'your_mum' command processed in {end_time - start_time} seconds")
    
@bot.tree.command(name='stats', description='Display usage stats.')
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
        


poll_votes = {}  # Global dictionary to track votes

class PollButton(discord.ui.Button):
    def __init__(self, label, value, poll_id):
        super().__init__(style=discord.ButtonStyle.primary, label=label)
        self.value = value
        self.poll_id = poll_id

    async def callback(self, interaction: discord.Interaction):
        # Acknowledge the interaction immediately
        await interaction.response.defer()

        user_id = interaction.user.id
        poll_data = poll_votes[self.poll_id]
        if user_id in poll_data['voters']:
            await interaction.followup.send("You have already voted.", ephemeral=True)
            return

        poll_data['votes'][self.value] += 1
        poll_data['voters'].add(user_id)
        await update_poll_message(interaction, self.poll_id)
        
async def update_poll_message(interaction, poll_id):
    poll_data = poll_votes[poll_id]
    votes_content = "\n".join([f"{label}: {count}" for label, count in poll_data['votes'].items()])
    embed = interaction.message.embeds[0]
    embed.clear_fields()
    embed.add_field(name="Votes", value=votes_content, inline=False)
    await interaction.message.edit(embed=embed)

def create_poll_view(poll_options, poll_id):
    view = discord.ui.View()
    for label, value in poll_options:
        view.add_item(PollButton(label, value, poll_id))
    return view

async def create_and_send_poll(channel, member, poll_key=None):
    # If poll_key is not provided, select a random key from the polls dictionary
    if not poll_key:
        poll_key = random.choice(list(polls.keys()))

    poll_config = polls[poll_key]
    poll_message_text = poll_config["text"].format(member.mention)
    embed = discord.Embed(title="Poll", description=poll_message_text, color=0x00ff00)

    poll_id = f"{poll_key}_{int(time.time())}"  # Unique poll identifier
    poll_votes[poll_id] = {
        'votes': {option[1]: 0 for option in poll_config["options"]},
        'voters': set(),
        'labels': {option[1]: option[0] for option in poll_config["options"]}  # Map values to labels
    }
    
    view = create_poll_view(poll_config["options"], poll_id)
    await channel.send(embed=embed, view=view)

# Command to create a poll
@bot.tree.command(name='poll', description='Create a poll about a specific or random member.')
async def poll(interaction: discord.Interaction, member_name: str = None, poll_key: str = None):
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message("This command can't be used outside of a server.", ephemeral=True)
        return
    await interaction.response.defer()

    # Select a random member and poll if not specified
    selected_member = find_closest_member(guild, member_name) if member_name else select_random_member(guild)
    poll_key = poll_key if poll_key in polls else random.choice(list(polls.keys()))

    if selected_member:
        await interaction.followup.send(f"A poll has been created for {selected_member.mention}.", ephemeral=True)
        await create_and_send_poll(interaction.channel, selected_member, poll_key)  
    else:
        await interaction.followup.send("No matching members found.", ephemeral=True)

    await update_command_usage(guild.id, 'poll')    
    
@bot.tree.command(name='set_thresholds', description='Set thresholds for polls and jokes in this server.')
async def set_thresholds_command(interaction: discord.Interaction, poll_threshold: int, joke_threshold: int):
    # Manual validation for threshold values
    if not 10 <= poll_threshold <= 100 or not 5 <= joke_threshold <= 50:
        await interaction.response.send_message("Poll threshold must be between 10 and 100, and joke threshold must be between 5 and 50.", ephemeral=True)
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

def load_user_data():
    try:
        with open('user_data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_user_data(data):
    with open('user_data.json', 'w') as file:
        json.dump(data, file, indent=4)

def get_user_data(user_id, user_data):
    user_id_str = str(user_id)
    if user_id_str not in user_data:
        # Initialize user data if not present
        user_data[user_id_str] = {"currency": 1000, "losses": 0, "bet_amount": 10}
    elif "bet_amount" not in user_data[user_id_str]:
        # Ensure 'bet_amount' field exists
        user_data[user_id_str]["bet_amount"] = 10
    return user_data[user_id_str]

def update_user_currency(user_id, amount, user_data):
    user_id_str = str(user_id)
    user = get_user_data(user_id_str, user_data)
    user["currency"] += amount
    if amount < 0:
        user["losses"] -= amount  # Track negative amounts as losses
    save_user_data(user_data)

def update_user_bet_amount(user_id, bet_amount, user_data):
    user_data = get_user_data(user_id, user_data)
    user_data["bet_amount"] = bet_amount
    save_user_data(user_data)
    
def get_user_currency(user_id, user_data):
    user = get_user_data(user_id, user_data)
    return user["currency"]
    

async def spin_slots(interaction, bet_amount, user_id, user_data, original_message=None):
    logger.info("Spinning slots for user_id: %s with bet_amount: %s", user_id, bet_amount)
    user = get_user_data(str(user_id), user_data)
    
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
    update_user_currency(str(user_id), winnings - bet_amount, user_data)

    # Prepare the results embed
    results_embed = prepare_slot_embed(result_str, winnings, bet_amount, user_id, user_data)

    # Edit the message with the results embed
    await slot_message.edit(embed=results_embed)

    # Update the view for the message
    view = SlotMachineView(user_id, user["bet_amount"], slot_message)
    await slot_message.edit(view=view)

async def show_spinning_reels(interaction, bet_amount):
    spinning_reel_embed = discord.Embed(title="🎰 Slot Machine 🎰", description="Spinning...")
    spinning_reel_embed.set_image(url="https://i.ibb.co/pXfspXC/Screenshot-2023-11-25-110438.gif")  # Replace with the direct link to your GIF
    spinning_reel_embed.add_field(name="Bet Amount", value=f"${bet_amount}", inline=False)
    
    # Send initial response
    await interaction.response.send_message(embed=spinning_reel_embed, ephemeral=False)
    
    # Get the message object for the initial response
    return await interaction.original_response()
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
        
def generate_reel():
    symbols = ["🍒", "🍇", "🍋", "🃏", "🍀", "🍑", "🔔", "❤", "💎"]
    symbol_weights = [0.18, 0.17, 0.16, 0.04, 0.07, 0.008, 0.15, 0.093, 0.03]
    return random.choices(symbols, weights=symbol_weights, k=3)

symbols = ["🍒", "🍇", "🍋", "🃏", "🍀", "🍑", "🔔", "❤", "💎"]

def check_paylines(grid, bet_amount, symbols):
    paylines = [
        [grid[0], grid[1], grid[2]],  # Top row
        [grid[3], grid[4], grid[5]],  # Middle row
        [grid[6], grid[7], grid[8]],  # Bottom row
        [grid[0], grid[3], grid[6]],  # Left column
        [grid[1], grid[4], grid[7]],  # Middle column
        [grid[2], grid[5], grid[8]],  # Right column
        [grid[0], grid[4], grid[8]],  # Diagonal top-left to bottom-right
        [grid[2], grid[4], grid[6]],  # Diagonal top-right to bottom-left
    ]

    winnings = 0
    wild_symbol = "🃏"
    peach_jackpot_multiplier = 50 
    base_payouts =   [1.1, 1.3, 1.35, 0, 3.0, 25, 2.0, 4.3, 9.9]
    standard_payouts = [payout * (1.3 + random.uniform(0.2, 0.1)) for payout in base_payouts]

    partial_match_multiplier = 0.03
    high_value_partial_match_multiplier = 0.11
    wild_multiplier = 1.2
    high_value_symbols = ["🍑", "💎", "❤", "🍀"]

    for payline in paylines:
        if wild_symbol in payline:
            most_common = max(set(payline), key=payline.count)
            payline = [most_common if symbol == wild_symbol else symbol for symbol in payline]

        unique_symbols = len(set(payline))
        if unique_symbols == 1:
            symbol = payline[0]
            if symbol == "🍑" and random.random() < 0.005:
                winnings += bet_amount * peach_jackpot_multiplier
            elif symbol != "🍑":
                symbol_index = symbols.index(symbol)
                payout = bet_amount * standard_payouts[symbol_index]
                winnings += payout * wild_multiplier if wild_symbol in payline else payout
        elif unique_symbols == 2 and payline.count(max(set(payline), key=payline.count)) == 2:
            most_common = max(set(payline), key=payline.count)
            if payline.count(most_common) == 2 and (most_common in high_value_symbols or wild_symbol in payline):
                symbol_index = symbols.index(most_common)
                winnings += bet_amount * high_value_partial_match_multiplier * standard_payouts[symbol_index]
    if winnings == 0 and random.random() < 0.000000000000005:
        winnings += bet_amount * (random.choice(standard_payouts) * partial_match_multiplier)

    return winnings
def calculate_slot_results(bet_amount):
    reel1 = generate_reel()
    reel2 = generate_reel()
    reel3 = generate_reel()

    grid = [reel1[0], reel2[0], reel3[0],
            reel1[1], reel2[1], reel3[1],
            reel1[2], reel2[2], reel3[2]]

    result_str = "\n".join([" | ".join(grid[i:i+3]) for i in range(0, 9, 3)])

    winnings = check_paylines(grid, bet_amount, symbols)

    # RTP adjustment
    rtp_adjustment = random.uniform(0.92, 0.97)
    winnings *= rtp_adjustment

    return result_str, int(winnings)

def prepare_slot_embed(result_str, winnings, bet_amount, user_id, user_data):
    # Define colors for win/lose
    color_win = 0x00ff00  # Green for win
    color_lose = 0xff0000  # Red for loss
    embed_color = color_win if winnings > 0 else color_lose

    # Create the embed object with the results
    embed = discord.Embed(title="🎰 Slot Machine Results 🎰", color=embed_color)
    embed.description = f"**Spin Results:**\n{result_str}"
    embed.add_field(name="Bet Amount", value=f"${bet_amount}", inline=False)

    # Add the result field based on winnings
    new_balance = get_user_currency(user_id, user_data)
    if winnings > 0:
        embed.add_field(name="💰 Result", value=f"🎉 You won ${winnings}!", inline=False)
    else:
        loss_amount = bet_amount - winnings  # Calculate the loss amount if any
        embed.add_field(name="💰 Result", value=f"😔 You lost ${loss_amount}. Better luck next time!", inline=False)

    embed.add_field(name="New Balance", value=f"${new_balance}", inline=False)

    # Add a footer for additional context if desired
    embed.set_footer(text="Spin again for a chance to win more!")

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
async def slots(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    user_data = load_user_data()

    user = get_user_data(user_id, user_data)
    if user["currency"] < user["bet_amount"]:
        await interaction.response.send_message("You don't have enough cash to play!", ephemeral=True)
        return

    # Start the slot machine for the user
    await spin_slots(interaction, user["bet_amount"], user_id, user_data)


       
@bot.tree.command(name='leaderboard', description='Display slots leaderboards.')
async def leaderboard(interaction: discord.Interaction):
    user_data = load_user_data()
    
    # Sort users by currency in descending order
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]['currency'], reverse=True)

    # Creating an embed for the leaderboard
    embed = discord.Embed(title="🏆 Global Leaderboard", description="Top balances and losses:", color=0x00ff00)
    
    # Add fields for top users
    for user_id, data in sorted_users[:10]:  # Adjust the number as needed
        user = await bot.fetch_user(int(user_id))
        embed.add_field(
            name=f"{user.name}", 
            value=f"💰 Cash: {data['currency']} | 📉 Losses: {data['losses']}", 
            inline=False
        )

    await interaction.response.send_message(embed=embed)


class SlotMachineView(discord.ui.View):
    def __init__(self, user_id, bet_amount, message=None):
        super().__init__()
        self.user_id = user_id
        self.bet_amount = bet_amount
        self.message = message

    async def update_bet_amount(self, interaction, amount_change):
        logger.info(f"Updating bet amount for user_id: {self.user_id}")
        user_data = load_user_data()
        user = get_user_data(self.user_id, user_data)

        new_bet_amount = max(10, user["bet_amount"] + amount_change)
        user["bet_amount"] = new_bet_amount
        save_user_data(user_data)
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

        if str(interaction.user.id) != self.user_id:
            # If this is not the correct user, send a follow-up message indicating the error
            await interaction.followup.send("This is not your machine!", ephemeral=True)
            return

        user_data = load_user_data()
        user = get_user_data(self.user_id, user_data)

        if user["currency"] < self.bet_amount:
            # If the user doesn't have enough currency, send a follow-up message indicating the error
            await interaction.followup.send("You don't have enough currency to spin!", ephemeral=True)
            return

        # Proceed with spinning slots
        if self.message:
            original_message = self.message
        else:
            try:
                original_message = await interaction.original_response()
            except discord.NotFound:
                # If the original message cannot be found, send a follow-up message indicating the error
                await interaction.followup.send("Can't spin again: original message not found.", ephemeral=True)
                return

        # Call the spin_slots function and pass the deferred original_message
        await spin_slots(interaction, self.bet_amount, self.user_id, user_data, original_message)

    @discord.ui.button(label="Increase Bet", style=discord.ButtonStyle.blurple)
    async def increase_bet(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_bet_amount(interaction, 10)

    @discord.ui.button(label="Decrease Bet", style=discord.ButtonStyle.red)
    async def decrease_bet(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.update_bet_amount(interaction, -10)
        
        
        
        
        
bot.run('INSERT BOT TOKEN HERE')


