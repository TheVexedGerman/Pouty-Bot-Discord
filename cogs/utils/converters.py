from discord.ext import commands
from discord.utils import find
from discord.ext.commands.errors import BadArgument


class RoleConverter(commands.Converter):

    async def convert(self, ctx, argument):
        server = ctx.message.guild
        role = find(lambda r: r.name.lower() == argument.lower(), server.roles)
        if role is None:
            raise BadArgument('Role {} not found'.format(argument))
        return role
