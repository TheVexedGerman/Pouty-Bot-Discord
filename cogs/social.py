from discord.ext import commands
import random
import json


class Social:

    def __init__(self, bot):
        self.bot = bot


    async def find_file(self, command, mention):
        with open('data/social/{}.json'.format(command), 'r') as f:
            data = json.load(f)
        if mention:
            await self.bot.say("{}\n{}".format(mention.mention,random.choice(data)))
        else:
            await self.bot.say(random.choice(data))

    @commands.command(hidden=False, pass_context=True)
    async def pout(self,ctx, mood="none"):
        """ Posts a cute little pout for your viewing pleasure
            usage: .pout <mood>
            only available mood is angry currently
        """
        mood_list = ('angry','sad','embarrassed')
        file_name = 'pouts'
        if mood in mood_list:
            file_name = '{}_pouts'.format(mood)
        mentioned_users = ctx.message.mentions
        if mentioned_users and len(mentioned_users) == 1:
            await  self.find_file(file_name,mentioned_users[0])
        else:
            await  self.find_file(file_name,None)



    @commands.command(hidden=False,pass_context=True)
    async def hug(self,ctx):
        mentioned_users = ctx.message.mentions
        if mentioned_users and len(mentioned_users) == 1:
            await self.find_file('hug', mentioned_users[0])
        else:
            await self.bot.say('```\n.hug (at)user\n```')

    @commands.command(hidden=False, pass_context=True)
    async def smug(self, ctx):
        mentioned_users = ctx.message.mentions
        if mentioned_users and len(mentioned_users) == 1:
            await self.find_file('smug',mentioned_users[0])
        else:
            await  self.find_file('smug',None)
    @commands.command(hidden=False, pass_context=True)
    async def cuddle(self, ctx):
        mentioned_users = ctx.message.mentions
        if mentioned_users and len(mentioned_users) == 1:
            await self.find_file('cuddle',mentioned_users[0])
        else:
            await self.bot.say('```\n.cuddle (at)user\n```')


    @commands.command(hidden=False, pass_context=True)
    async def lewd(self, ctx):
        mentioned_users = ctx.message.mentions
        if mentioned_users and len(mentioned_users) == 1:
            await self.find_file('lewd',mentioned_users[0])
        else:
            await self.bot.say('```\n.lewd (at)user\n```')


    @commands.command(hidden=False, pass_context=True)
    async def pat(self,ctx):
        mentioned_users = ctx.message.mentions
        if mentioned_users and len(mentioned_users) == 1:
            await self.find_file('pat',mentioned_users[0])
        else:
            await self.bot.say('```\n.pat (at)user\n```')

    @commands.command(hidden=False, pass_context=True)
    async def bully(self,ctx):
        mentioned_users = ctx.message.mentions
        if mentioned_users and len(mentioned_users) == 1:
            await self.find_file('bully',mentioned_users[0])
        else:
            await self.bot.say('```\n.bully (at)user\n```')
    @commands.command(hidden=False, pass_context=True)
    async def nobully(self,ctx):
        mentioned_users = ctx.message.mentions
        if mentioned_users and len(mentioned_users) == 1:
            await self.find_file('nobullys',mentioned_users[0])
        else:
            await self.find_file('nobullys', None)
    @commands.command(hidden=False, pass_context=True)
    async def slap(self,ctx):
        mentioned_users = ctx.message.mentions
        if mentioned_users and len(mentioned_users) == 1:
            await self.find_file('slaps',mentioned_users[0])
        else:
            await self.bot.say('```\n.slap (at)user\n```')
def setup(bot):
    bot.add_cog(Social(bot))