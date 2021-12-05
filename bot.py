# bot.py
'''
author : lemon-cake123
This file is meant to be the main logic of the bot
You are allowed to edit this file
'''

import os
import discord
import requests
from discord.ext import commands
import random

import psycopg2
from dotenv import load_dotenv
insert_sad_query = """ INSERT INTO sad_words (words)
VALUES (%s)"""
delete_sad_query = """ DELETE FROM sad_words WHERE words= (%s) """
insert_better_query = """ INSERT INTO get_better_words (words)
VALUES (%s)"""
delete_better_query = """ DELETE FROM get_better_words WHERE words = (%s)"""

DATABASE_URL = os.environ['DATABASE_URL']

load_dotenv()
try:
    with psycopg2.connect(
        DATABASE_URL,
        sslmode='require'
        ) as connection:

        sad_words = []
        get_better_words = []
        cursor = connection.cursor()
        
        cursor.execute("SELECT * FROM sad_words")
        sad_words = [sad_word for sad_word,_ in cursor.fetchall()]
        cursor.execute("SELECT * FROM get_better_words")
        get_better_words = [get_better_word for get_better_word,_ in cursor.fetchall()]
        

            
        
        TOKEN = os.getenv('DISCORD_TOKEN')

        bot = commands.Bot(command_prefix='-')

        @bot.event
        async def on_ready():
            print(f'{bot.user.name} is now online')



        @bot.event
        async def on_message(message):
            if message.author == bot.user:
                return

            if message.author.bot:
                return
        
            if message.content.startswith('-'):
                await bot.process_commands(message)
                return
            
            for sad_word in sad_words:
                if sad_word in message.content.lower():
                    await message.channel.send(f'{random.choice(get_better_words)} {message.author.mention}')

            await bot.process_commands(message)

        @bot.command(name="add-sad-word", help = "add a sad word to the database")
        async def add(ctx,sad_word):
            if sad_word in sad_words:
                await ctx.send(f'{sad_word} is already in the database')
                return
            
            cursor.execute(insert_sad_query, (sad_word.lower(),))

            connection.commit()
            
            await ctx.send(f"Added {sad_word} to the database")
            sad_words.append(sad_word)

            

            print(sad_words)
            

            

        @bot.command(name="remove-sad-word", help = "remove a sad word from the database")
        async def remove(ctx,sad_word):
            if not sad_word in sad_words:
                await ctx.send(f'{sad_word} is not in the database')
                return

            
            cursor.execute(delete_sad_query, (sad_word.lower(),))

            connection.commit()
            
            await ctx.send(f"removed {sad_word} from the database")


            
            sad_words.remove(sad_word)
            
            print(sad_words)

        @bot.command(name="list-sad-words", help = "list sad words on the database")
        async def list(ctx):
            embed = discord.Embed(title="Sad words", description="the list of sad words on the database")
            embed.add_field(name="list",value = "\n".join(sad_words),inline = False)

            await ctx.send(embed=embed)

        @bot.command(name="add-encouraging-word", help = "add a encouraging word to the database")
        async def add(ctx,encouraging_word):
            if encouraging_word in get_better_words:
                await ctx.send(f'{encouraging_word} is already in the database')
                return
            
            cursor.execute(insert_better_query, (encouraging_word,))
            
            await ctx.send(f"Added {encouraging_word} to the database")
            
            connection.commit()
            
            get_better_words.append(encouraging_word) 
            print(get_better_words)
            

        @bot.command(name="remove-encouraging-word", help = "remove a encouraging word from the database")
        async def remove(ctx,encouraging_word):
            if not encouraging_word in get_better_words:
                await ctx.send(f'{encouraging_word} is not in the database')
                return
                
            cursor.execute(delete_better_query, (encouraging_word,))
            await ctx.send(f"removed {encouraging_word} from the database")
            
            
            connection.commit()
            
            
            get_better_words.remove(encouraging_word)
            print(get_better_words)

        @bot.command(name="list-encouraging-words", help = "list all encouraging words")
        async def list(ctx):

            print(get_better_words)
            embed = discord.Embed(title="encouraging words", description="the list of encouraging words on the database")
            embed.add_field(name="list",value = "\n".join(get_better_words),inline = False)

            await ctx.send(embed=embed)        
            
        @bot.command(name="inspire",help="gets a random inspirational quote")
        async def inspire(ctx):
            response = requests.get('http://api.quotable.io/random')
            response = response.json()
            await ctx.send(f'''
        >>> {response['content']}
        
-{response['author']}

''')
                    
                
        @bot.event
        async def on_command_error(ctx, error):
            with open('err.log','a') as f:
                f.write(f'Unhandled Exception: {error} \n')
                
            await ctx.send(error)
            
            
        bot.run(TOKEN)
except psycopg2.Error as e:
    print(f"error : {e}")
