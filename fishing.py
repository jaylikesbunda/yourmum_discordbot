import discord
from discord.ext import commands
import discord.app_commands as app_commands
import json
from discord.ui import View, Button
import math
import random
import time
import logging

# Import necessary functions from yourmumbot.py
from yourmumbot import check_item_availability, add_item_to_user_inventory, get_user_currency, update_user_currency

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


class PaginationView(discord.ui.View):
    def __init__(self, items, items_per_page, bot):
        super().__init__()
        self.items = items
        self.items_per_page = items_per_page
        self.current_page = 0
        self.total_pages = math.ceil(len(items) / items_per_page)
        self.bot = bot  # Reference to the bot

        # Initialize buttons with disabled states as needed
        self.previous_button = discord.ui.Button(label='Previous', style=discord.ButtonStyle.grey, disabled=self.current_page == 0)
        self.next_button = discord.ui.Button(label='Next', style=discord.ButtonStyle.grey, disabled=self.current_page >= self.total_pages - 1)

        # Add buttons to the view
        self.add_item(self.previous_button)
        self.add_item(self.next_button)

    async def on_timeout(self):
        # Disable buttons when the view times out
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)  # Update the message to reflect the disabled state
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Allow any user to interact with the pagination
        return True

    async def previous_page(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            embed, file = self.create_embed_and_file()
            await interaction.response.edit_message(embed=embed, view=self, attachments=[file if file else []])

    async def next_page(self, interaction: discord.Interaction):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            embed, file = self.create_embed_and_file()
            await interaction.response.edit_message(embed=embed, view=self, attachments=[file if file else []])

    def create_embed_and_file(self):
        # Calculate the file path based on the current page
        file_path = f"./store_items/shelf_{self.current_page + 1}_store.png"
        file = discord.File(file_path, filename=f"shelf_{self.current_page + 1}_store.png")

        embed = discord.Embed(title="General Store", color=discord.Color.blue())
        
        # Add item descriptions in the order they appear on the shelf image
        item_descriptions = []
        for index, item in enumerate(self.items, start=1):
            name, description, price = item['name'], item['description'], item['price']
            item_descriptions.append(f"{index}. **{name}** - *{description}* - ${price}")
        
        # Join all item descriptions with a newline
        embed_description = "\n".join(item_descriptions)
        embed.description = embed_description

        embed.set_image(url=f"attachment://shelf_{self.current_page + 1}_store.png")  # Set the image of the shelf
        embed.set_footer(text=f"Page {self.current_page + 1} of {self.total_pages}")

        return embed, file
    
    
    # Update the buttons based on the current page
    def update_buttons(self):
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == (self.total_pages - 1)

    async def handle_previous_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Ensure to respond to the interaction
        await interaction.response.defer()

        if self.current_page > 0:
            self.current_page -= 1
            embed, file = self.create_embed_and_file()
            await interaction.followup.edit_message(interaction.message.id, embed=embed, view=self, attachments=[file] if file else [])
            self.update_buttons()

    async def handle_next_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        # Ensure to respond to the interaction
        await interaction.response.defer()

        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            embed, file = self.create_embed_and_file()
            await interaction.followup.edit_message(interaction.message.id, embed=embed, view=self, attachments=[file] if file else [])
            self.update_buttons()
       
        
        
class FishingGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.item_flavour_text = self.load_item_data()
        # Access the db_connection from the bot instance directly
        self.db_connection = self.bot.db_connection




    @staticmethod
    def load_item_data():
        try:
            with open('store_items/item_flavour_text.json', 'r') as file:
                # Load and transform data for easier access
                data = json.load(file)
                # Ensure data is in list format even if there's only one item
                if isinstance(data, dict):
                    data = [data]
                return {item['name'].lower(): item for item in data}
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading item data: {e}")
            return {}

        
    @app_commands.command(name='buy', description='Buy items or get a loan')
    async def buy(self, interaction: discord.Interaction, item: str):
        user_id = interaction.user.id

        # Implement cooldown check
        async with self.bot.db_connection.execute("SELECT last_used FROM buy_command_usage WHERE user_id = ?", (user_id,)) as cursor:
            last_used_record = await cursor.fetchone()

        if last_used_record:
            last_used = last_used_record[0]
            cooldown = 5  # Cooldown in seconds (5 minutes)
            if (time.time() - last_used) < cooldown:
                await interaction.response.send_message("You've used this command too recently. Please wait before trying again.", ephemeral=True)
                return

        # Update the last used time
        await self.bot.db_connection.execute("INSERT OR REPLACE INTO buy_command_usage (user_id, last_used) VALUES (?, ?)", (user_id, int(time.time())))
        await self.bot.db_connection.commit()

        # Handle item purchase or loan
        await self.handle_purchase_or_loan(interaction, user_id, item.lower())


    async def get_user_balance(self, db_connection, user_id):
        # Use get_user_currency from yourmumbot.py
        return await get_user_currency(db_connection, user_id)

    async def handle_purchase_or_loan(self, interaction, user_id, item_name):
        logging.info(f"Handling purchase or loan for user {user_id} with item {item_name}")

        item_name_lower = item_name.lower()

        if item_name_lower == "loan":
            logging.info("Processing a loan request")
            # Loan functionality
            amount_to_add = 500  # Define the loan amount
            success = await self.update_user_balance(user_id, amount_to_add)
            if success:
                logging.info(f"Loan processed successfully for user {user_id}")
                joke = await self.fetch_joke()  # Assuming fetch_joke is defined elsewhere
                response_text = f"You've successfully taken a loan of ${amount_to_add}!\n {joke}"
            else:
                logging.error(f"Failed to process loan for user {user_id}")
                response_text = "Failed to process your loan."
            await interaction.response.send_message(response_text, ephemeral=True)

        elif item_name_lower in self.item_flavour_text:
            logging.info(f"Processing item purchase for {item_name_lower}")
            # Buy item functionality
            item_details = self.item_flavour_text[item_name_lower]
            await self.process_item_purchase(interaction, user_id, item_name_lower, item_details)

        else:
            logging.warning(f"Item {item_name} not found for user {user_id}")
            await interaction.response.send_message("Item not found.", ephemeral=True)            


    async def add_item_to_inventory(self, user_id, item_id):
        """
        Add an item to the user's inventory.
        """
        # Call the standalone function with the bot's db_connection
        await add_item_to_user_inventory(self.bot.db_connection, user_id, item_id)

    async def fetch_joke(self):
        # Assume SLASH_COMMAND_JOKES is a list of jokes
        joke = random.choice(SLASH_COMMAND_JOKES)
        return joke


    async def process_item_purchase(self, interaction, user_id, item_name, item_details):
        price = item_details["price"]
        # Call get_user_currency directly with db_connection and user_id
        user_balance = await get_user_currency(self.bot.db_connection, user_id)

        if user_balance >= price:
            # Deduct price and add item to inventory
            success = await self.update_user_balance(user_id, -price)
            if success:
                await self.add_item_to_inventory(user_id, item_name)
                response_text = f"You've successfully purchased {item_details['name']} for ${price}!"
            else:
                response_text = "Failed to process your purchase."
        else:
            response_text = "You do not have enough balance to purchase this item."
        await interaction.response.send_message(response_text, ephemeral=True)



    async def check_and_update_user_balance(self, interaction, user_id, item_name):
        # Check if item exists and get its details
        item_record = await check_item_availability(item_name)

        if not item_record:
            await interaction.response.send_message("Item not found or not available for purchase.", ephemeral=True)
            return False

        item_id, item_price = item_record

        # Check user's current currency
        current_currency = await get_user_currency(user_id)

        if current_currency < item_price:
            await interaction.response.send_message("You do not have enough currency to buy this item.", ephemeral=True)
            return False

        # Deduct the item's price from user's currency and update
        await update_user_currency(user_id, -item_price)

        # Add the item to user's inventory
        await add_item_to_user_inventory(user_id, item_id)

        await interaction.response.send_message(f"You have successfully purchased {item_name}.", ephemeral=True)
        return True
    
    async def update_user_balance(self, user_id, amount):
        # Make sure this function returns True if the update is successful, False otherwise
        try:
            await update_user_currency(self.bot.db_connection, user_id, amount)
            return True
        except Exception as e:
            logging.error(f"Error updating user balance for {user_id}: {e}")
            return False

    @app_commands.command(name='store', description='Browse items available for purchase')
    async def store(self, interaction: discord.Interaction):
        # Load items from the JSON file
        with open('store_items/item_flavour_text.json', 'r') as json_file:
            items_data = json.load(json_file)

        # Check if the store has items
        if not items_data:
            await interaction.response.send_message("The store is currently empty.", ephemeral=True)
            return

        ITEMS_PER_PAGE = 2
        view = PaginationView(items_data, ITEMS_PER_PAGE, self.bot)  # Pass the bot instance here
        embed, file = view.create_embed_and_file()
        await interaction.response.send_message(embed=embed, view=view, file=file)

    @app_commands.command(name='steal', description='Attempt to steal from another user')
    async def steal(self, interaction: discord.Interaction, target: discord.User):
        user_id = interaction.user.id
        target_id = target.id

        # Check if the user has the Fast Hands perk
        if not await self.check_user_has_item(user_id, "fast hands"):
            embed = discord.Embed(title="Failed Steal Attempt", 
                                  description="You need the Fast Hands perk to use this command.", 
                                  color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        success_chance = 0.5  # 50% chance to succeed
        steal_amount = await self.calculate_steal_amount(target_id)

        if random.random() < success_chance:
            # Successful steal
            await update_user_currency(self.bot.db_connection, user_id, steal_amount)
            await update_user_currency(self.bot.db_connection, target_id, -steal_amount)
            embed = discord.Embed(title="Successful Steal", 
                                  description=f"You successfully stole ${steal_amount} from {target.display_name}!",
                                  color=0x00FF00)
        else:
            # Failed steal
            embed = discord.Embed(title="Failed Steal", 
                                  description="Your attempt to steal was unsuccessful.", 
                                  color=0xFF0000)
        await interaction.response.send_message(embed=embed)

    async def check_user_has_item(self, user_id, item_name):
        async with self.bot.db_connection.execute("SELECT * FROM user_inventory WHERE user_id = ? AND item_id = ?", (user_id, item_name)) as cursor:
            record = await cursor.fetchone()
        return record is not None

    async def calculate_steal_amount(self, target_id):
        # Function to calculate the steal amount from a target user
        target_balance = await get_user_currency(self.bot.db_connection, target_id)
        steal_percentage = 0.1  # 10% of the target's balance
        return int(target_balance * steal_percentage)

async def setup(bot):
    fishing_game_cog = FishingGame(bot)
    await bot.add_cog(fishing_game_cog)  # Correctly using await here
    await bot.tree.sync()

