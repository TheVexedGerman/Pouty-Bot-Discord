import random
from discord.ext import commands
from discord import User

class Penis:
    """cog for finding the 100% accurate penis length of a user"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def penis(self, ctx, *, users: str = None):
        """accurately measure a user's penis size or compare the penis size of multiple users"""
        if users is None:
            message = ctx.message
            seed = message.author.id
            random.seed(seed)
            length = random.randint(0, 20)
            await self.bot.say("**{0}'s size:**\n8{1}D".format(message.author.name, "=" * length))
        else:
            user_list = users.split()
            length_list = []
            message_string = ""
            for user in user_list:
                converter = commands.UserConverter(ctx, user)
                current_user = converter.convert()
                random.seed(current_user.id)
                length = random.randint(0, 20)
                length_list.append({"username": current_user.name, "length": length})
            for entry in length_list:
                message_string += "**{0}'s size:**\n8{1}D\n".format(entry["username"], "=" * entry["length"])
            await self.bot.say(message_string)


def setup(bot):
    bot.add_cog(Penis(bot))