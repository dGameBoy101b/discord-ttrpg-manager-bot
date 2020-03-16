import discord
import sys
import os
from dotenv import load_dotenv
import logger

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
LOG_FOLDER = os.getenv('TTRPGM_BOT_LOGS')

class TTRPGMBotClient(discord.Client):
    ROLE_NAME = 'TTRPGM Commander'
    REQUIRED_PERMISSIONS = discord.Permissions(manage_channels=True,
                                               manage_roles=True,
                                               read_messages=True)
    EVERYONE_PERMISSIONS = discord.PermissionOverwrite(read_messages=False,
                                                       connect=False)
    PLAYER_PERMISSIONS = discord.PermissionOverwrite(read_messages=True,
                                                     send_messages=True,
                                                     read_message_history=True,
                                                     connect=True,
                                                     speak=True,
                                                     change_nickname=True,
                                                     priority_speaker=False)
    GM_PERMISSIONS = discord.PermissionOverwrite(read_messages=True,
                                                 send_messages=True,
                                                 read_message_history=True,
                                                 connect=True,
                                                 speak=True,
                                                 priority_speaker=True,
                                                 mute_members=True,
                                                 deafen_members=True,
                                                 move_members=True,
                                                 manage_nicknames=True,
                                                 manage_messages=True,
                                                 manage_channels=True,
                                                 manage_permissions=True)

    async def add_commander_role(self, guild):
        #search for existing commander role
        role = discord.utils.find(lambda r: r.name == TTRPGMBotClient.ROLE_NAME, guild.roles)
        if role != None:
            logger.info(f'Commander role already exists in the guild {guild}')
            return role
        #create commander role
        try:
            bot_manager_role = await guild.create_role(name=TTRPGMBotClient.ROLE_NAME,
                                                       mentionable=False,
                                                       reason=f'Created Commander role to allow members to command {guild.me}')
            logger.debug(f'My highest role in {guild} is {guild.me.top_role} at the position {guild.me.top_role.position}')
            await bot_manager_role.edit(position=guild.me.top_role.position - 1,
                                        reason=f'Moved Commander role to highest possible position to prevent channel spamming')
            logger.info(f'Created commander role in the guild {guild}')
            logger.debug(f'The position of the new commander role in the guild {guild} is {bot_manager_role.position}')
            return bot_manager_role
        except discord.errors.Forbidden:
            logger.warning(f'Denied permission to create command role in the guild {guild}')
            raise

    async def create_GM_role(self, message, name):
        gm_role_name = f'{name} GM'
        #search for existing role
        role = discord.utils.find(lambda r: r.name == gm_role_name, message.guild.roles)
        if role != None:
            logger.info(f'GM role already exists for {name} campaign in the guild {message.guild}')
            return role
        #create role
        try:
            gm_role = await message.guild.create_role(name=gm_role_name,
                                                      mentionable=True,
                                                      reason=f'Created GM role for {name} campaign as commanded by {message.author}')
            logger.info(f'Created GM role for campaign named {name} in the guild {message.guild}')
            return gm_role
        except discord.errors.Forbidden:
            logger.warning(f'Denied permission to create GM role in the guild {message.guild}')
            raise

    async def create_player_role(self, message, name):
        player_role_name = f'{name} Player'
        #search for existing role
        role = discord.utils.find(lambda r: r.name == player_role_name, message.guild.roles)
        if role != None:
            logger.info(f'GM role already exists for {name} campaign in the guild {message.guild}')
            return role
        #create role
        try:
            player_role = await message.guild.create_role(name=player_role_name,
                                                          mentionable=True,
                                                          reason=f'Created player role for {name} campaign as commanded by {message.author}')
            logger.info(f'Created player role for campaign named {name} in the guild {message.guild}')
            return player_role
        except discord.errors.Forbidden:
            logger.warning(f'Denied permission to create player role in the guild {message.guild}')
            raise

    async def create_campaign_category(self, message, name, gm_role, player_role):
        #search for existing category
        category = discord.utils.find(lambda c: c.name == name, message.guild.categories)
        if category != None:
            logger.info(f'Category already exists for {name} campaign in the guild {message.guild}')
            return category
        #create category
        try:
            game_category = await message.guild.create_category(name=name,
                                                                overwrites={gm_role: TTRPGMBotClient.GM_PERMISSIONS,
                                                                            player_role: TTRPGMBotClient.PLAYER_PERMISSIONS,
                                                                            message.guild.default_role: TTRPGMBotClient.EVERYONE_PERMISSIONS},
                                                                reason=f'Created category for {name} campaign as commanded by {message.author}')
            logger.info(f'Created category for campaign named {name} in the guild {message.guild}')
            return game_category
        except discord.errors.Forbidden:
            logger.warning(f'Denied permissions to create category in the guild {message.guild}')
            raise

    async def create_campaign_text_channel(self, message, name, gm_role, player_role, category):
        #search for existing text channel
        text_channel = discord.utils.find(lambda tc: tc.name == name, filter(lambda tc: tc.category.name == name, message.guild.text_channels))
        if text_channel != None:
            logger.info(f'Text channel already exists for campaign {name} in the guild {message.guild}')
            return text_channel
        #create text channel
        try:      
            game_text = await message.guild.create_text_channel(name=name,
                                                                category=category,
                                                                reason=f'Created text channel for {name} campaign as commanded by {message.author}')
            logger.info(f'Created text channel for campaign named {name} in the guild {message.guild}')
            return game_text
        except discord.errors.Forbidden:
            logger.warning(f'Denied permissions to create text channels for {name} campaign in the guild {message.guild}')
            raise

    async def create_campaign_voice_channel(self, message, name, gm_role, player_role, category):
        #search for existing voice channel
        voice_channel = discord.utils.find(lambda vc: vc.name == name, filter(lambda vc: vc.category.name == name, message.guild.voice_channels))
        if voice_channel != None:
            logger.info(f'Voice channel already exists for {name} campaign in the guild {message.guild}')
            return voice_channel
        #create voice channel
        try:                
            game_voice = await message.guild.create_voice_channel(name=name,
                                                          category=category,
                                                          reason=f'Created voice channel for {name} campaign as commanded by {message.author}')
            logger.info(f'Created voice channel for {name} campaign in the guild {message.guild}')
            return game_voice
        except discord.errors.Forbidden:
            logger.warning(f'Denied permissions to create a voice channel for {name} campaign in the guild {mesage.guild}')
            raise
        
    async def create_campaign(self, message, com_role):
        #check author permissions
        if not message.author in com_role.members:
            logger.info(f'{message.author} attempted to create a campaign in the guild {message.guild} without the commander role')
            return
        #check bot permissions
        if not message.guild.me.guild_permissions.is_superset(TTRPGMBotClient.REQUIRED_PERMISSIONS):
            logger.warning(f'Insufficient permissions to create campaigns in the guild {message.guild}')
            return
        #calculate campaign name
        name = message.content
        for mention in message.mentions:
            name = name.replace(f'<@!{mention.id}>', '')
        for mention in message.channel_mentions:
            name = name.replace(f'<#{mention.id}>', '')
        for mention in message.role_mentions:
            name = name.replace(f'<@&{mention.id}>', '')
        name = name.strip()
        logger.info(f'Commanded to create campaign named {name} in the guild {message.guild}')
        #create roles
        try:
            gm_role = await self.create_GM_role(message, name)
            player_role = await self.create_player_role(message, name)
            #create channels
            try:
                game_category = await self.create_campaign_category(message, name, gm_role, player_role)
                game_text = await self.create_campaign_text_channel(message, name, gm_role, player_role, game_category)
                game_voice = await self.create_campaign_voice_channel(message, name, gm_role, player_role, game_category)
                logger.info(f'Created channels for campaign named {name} in the guild {message.guild}')
                #assign gm role to author
                try:
                    await message.author.add_roles(gm_role, reason=f'Assigned {message.author} GM role for {name} campaign')
                    logger.info(f'Added GM role for {name} campaign to {message.author}')
                except discord.errors.Forbidden:
                    logger.warning(f'Denied permission to assign GM role in the guild {message.guild}')
            except discord.errors.Forbidden:
                logger.warning(f'Denied permission to create channels in the guild {message.guild}')
        except discord.errors.Forbidden:
            logger.warning(f'Denied permission to create roles in the guild {message.guild}')
                
    async def on_connect(self):
        logger.debug('This bot is in guilds with the following ids:')
        for guild in client.guilds:
            logger.debug(f'{guild.id}')

    async def on_guild_join(self, guild):
        logger.debug(f'Joined the guild {guild}')
        await self.add_commander_role(guild)

    async def on_message(self, message):
        logger.debug(f'Message recieved from {message.author} in the guild {message.guild}')
        if message.author != message.guild.me and message.guild.me.mentioned_in(message):
            com_role = await self.add_commander_role(message.guild)
            await self.create_campaign(message, com_role)

logger = logger.initialise_logger(LOG_FOLDER, __name__)
client = TTRPGMBotClient()
client.run(TOKEN)
