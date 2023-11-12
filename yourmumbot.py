import discord
from discord.ui import Button, View
from discord.ext import commands
import random
import asyncio
import logging
import time
import aiosqlite
# Setup logging
logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='w', 
                    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')

# List of polls
polls = [
    "{}'s mum looked pretty sexy lately, what do y'all think?",
    "Have you seen {}'s mum? If 'overweight' was a sport, she’d be an Olympian, right?",
    "Is it just me or is {}'s mum just the most majestic creature you've ever laid your eyes on",
    "Can someone confirm if {}'s mum has dropped her 'film' yet?",
    "Would you eat {}'s mum's booty hole for -$100?",
    "How does {}'s mum manage to look that sexy? Not a question, just saying.",
    " {}'s mum. Yes for Tits, No for Ass. You Decide.",
    ]

# Define your keywords and corresponding jokes
KEYWORD_JOKES = {
    'big': [
        'You know what else is big? Your mum!',
        'Big like your mum\'s asshole after i\'m done with her!',
    ],
    'small':[ 'That might be small, but your mum\'s appetite sure isn\'t!', ],
    'soft': ['Not as soft as your mum\'s ass!',],
    'hairy': ['Hairy as your mum!',],
    'old': ['Couldn\'t be as old as your mum!',],
    'fat': ['Not as fat as your mum!',],
    'loose': ['yo mama pussy loose ah hell',],
    'dinner': ['Speaking of dinnner where is your mum ;)',],
    'heavy': ['Heavy? I guess you haven\'t lifted your mum lately!',],
    'slow': ['Not as slow as your mum on a treadmill!',],
    'fast': ['Couldn\'t be as fast as your mum makes me bust',],
    'tight': ['Tighter than your mum\'s yoga pants!',],
    'hard': ['Not as hard as me when I see your mum!',],
    'hot': ['Couldn\'t be hotter than your mum last night!','Not as hot as your mum!',],
    'weak': ['Weaker than your mum\'s dieting schedule!',],
    'bright': ['Not as bright as your mum’s smile - bless her!',],
    'thin': ['Thin? Couldn\'t be your mum!',],
    'deep': ['Almost as deep as I am in your mama',],
    'food': ['talking bout food, tell ur mum daddy wants his milky ;)',],
    ('would', 'you'): ['Would you get your mum for me so she can bounce on deez nuts!',],
    ('get', 'on'): ['I\'ll get on just like your mum got on this dick!',],
    ('hop', 'on'): ['Hop on deez nuts!','Get ur mum to hop on deez nuts!',],
    ('this', 'sucks'): ['Yeah sucks more than your mum!',],
    ('u', 'should'): ['u should tell ur mum she lookin kinda cute today',],
    ('is', 'ass'): ['Your mum is ass.',],
    ('are', 'ass'): ['Your mums titties are ass.',],
    ('my', 'perms'): ['Stop complaining',],
    ('should', 'i'): ['yes.','no.','maybe.','without a doubt',],
    ('loading'): ['loading up your mum with goodness',],
    ('thanks', 'bot'): ['you\'re welcome','all good',],
    ('good', 'bot'): ['thank you','appreciate it',],
    ('i\'m', 'getting'): ['and i\'m getting lucky with yo mama!','and i\'m getting good ass top from yo mama!',],
    ('im', 'getting'): ['and i\'m getting lucky with yo mama!','and i\'m getting good ass top from yo mama!',],
    ('good', 'morning'): ['Good Morning yourself! Is your mum walking alright after last night?',],
    ('hate', 'you'): ['https://tenor.com/view/damn-kendrick-lamar-%EC%BC%84%EB%93%9C%EB%A6%AD-%EB%9D%BC%EB%A7%88-gif-9061375','damn.',],
}

# Define a separate list for slash command jokes
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
]
# Define the necessary intents
intents = discord.Intents.default()
intents.messages = True  # Assuming the bot needs access to message content
intents.guilds = True
intents.members = True  # Necessary for member-related features
intents.message_content = True  # This line enables the message content intent
class MyBot(commands.Bot):
    async def close(self):
        global db_connection
        if db_connection:
            await db_connection.close()

        await super().close()

# Initialize your bot
bot = MyBot(command_prefix="/", intents=intents)

db_connection = None

async def get_database_connection():
    global db_connection
    return db_connection


# This should be called once at the start of your application to initialize the database
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

    # Sync application commands globally
    await bot.tree.sync()

    logging.info(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    logging.info(f'Received message: "{message.content}" from {message.author} on server: {message.guild.id}')

    # Increment the message count for the guild
    guild_id = message.guild.id
    await save_message_count(guild_id)

    # Threshold for triggering the poll
    poll_message_threshold = 49  # Adjust this number to the desired threshold for polls

    # Threshold for triggering a 'your_mum' joke
    joke_message_threshold = 20  # Adjust this number to the desired threshold for jokes

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

    # Needed to process commands if the bot is also using command decorators
    await bot.process_commands(message)
    
    # The message handler will need to check for both single keywords and tuples with order.
    message_content = message.content.lower()  # We'll keep the original message content here
    for keywords, jokes_list in KEYWORD_JOKES.items():
        if isinstance(keywords, tuple):  # If the key is a tuple, we'll check for the exact sequence
            # Join the tuple into a phrase and check if it appears in the message
            keyword_phrase = ' '.join(keywords)
            if keyword_phrase in message_content:
                # Select a random joke from the list of jokes for these keywords
                joke = random.choice(jokes_list)
                await message.reply(joke)
                # Update keyword stats
                await update_stats(guild_id, '_'.join(keywords))
                break
        else:  # If the key is a string, it's a single keyword
            if keywords in message_content.split():  # Splitting to match whole words only
                # Select a random joke from the list of jokes for this keyword
                joke = random.choice(jokes_list)
                await message.reply(joke)
                # Update keyword stats
                await update_stats(guild_id, keywords)
                break


@bot.tree.command(name='your_mum', description='Respond with a random your mum joke.')
async def your_mum(interaction: discord.Interaction):
    try:
        start_time = time.time()  # Start time for execution measurement
        logging.info(f"'your_mum' command invoked on server: {interaction.guild_id}")

        # Defer the response if the processing might take some time
        await interaction.response.defer()

        joke = random.choice(SLASH_COMMAND_JOKES)

        # Followup since the response has been deferred
        await interaction.followup.send(joke)

        # Update command usage statistics
        await update_command_usage(interaction.guild.id, 'your_mum')

        end_time = time.time()  # End time for execution measurement
        logging.info(f"'your_mum' command processed in {end_time - start_time} seconds")
    except Exception as e:
        logging.error(f"Error in 'your_mum' command: {e}")

        # Since we've deferred, we should always use followup here
        await interaction.followup.send("An error occurred while processing your request.", ephemeral=True)
            
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
        

# Select menu for the poll
class PollSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Yes", value="yes"),
            discord.SelectOption(label="No", value="no")
        ]
        super().__init__(placeholder='Choose your answer...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Check if the user has already voted
        user_id = interaction.user.id
        if user_id in self.view.voters:
            await interaction.response.send_message("You have already voted.", ephemeral=True)
            return

        # Increment vote counters based on the selected value
        if self.values[0] == "yes":
            self.view.yes_count += 1
        elif self.values[0] == "no":
            self.view.no_count += 1
        
        # Record the user's vote
        self.view.voters.add(user_id)

        # Inside your callback method
        original_content = interaction.message.content.split('\n\n')[0]
        votes_content = f"Votes: Yes - {self.view.yes_count} | No - {self.view.no_count}"
        content = f"{original_content}\n\n{votes_content}"
        await interaction.message.edit(content=content)
        await interaction.response.send_message("Your vote has been counted.", ephemeral=True)

# View that contains the select menu
class PollView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.yes_count = 0
        self.no_count = 0
        self.voters = set()  # Set to track who has voted
        self.add_item(PollSelect())  # No arguments

    def get_poll_content(self):
        # Return the current poll message with the vote counts
        return f'Votes: Yes - {self.yes_count} | No - {self.no_count}'

# Function to create and send a new poll
async def create_and_send_poll(channel, member):
    poll_message_text = random.choice(polls).format(member.mention)
    view = PollView()  # No arguments 
    await channel.send(poll_message_text, view=view)
   
def select_random_member(guild):
    return random.choice([member for member in guild.members if not member.bot]) if guild.members else None

# Create a slash command for the poll
@bot.tree.command(name='poll', description='Create a poll about a random member.')
async def poll(interaction: discord.Interaction):
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message("This command can't be used outside of a server.", ephemeral=True)
        return

    random_member = select_random_member(guild)
    if random_member:
        await create_and_send_poll(interaction.channel, random_member)
        await interaction.response.send_message(f"A poll has been created for {random_member.mention}.", ephemeral=True)
    else:
        await interaction.response.send_message("No members found to create a poll about.", ephemeral=True)
    
    # Update the command usage stats once, after the poll has been created or failed.
    await update_command_usage(interaction.guild.id, 'poll')

bot.run('INSERT APP TOKEN HERE')


