from discord.ext import commands
from .utils import checks
from discord import Member, Embed, Role, utils
import discord
import time


class Userinfo:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def userinfo(self,ctx, member: Member=None):
        if member is None:
            member = ctx.message.author
        join_date = member.joined_at
        created_at = member.created_at
        user_color = member.color
        server = ctx.message.server
        if member.nick:
            nick = member.nick
        else:
            nick = member.name
        time_fmt = "%d %b %Y %H:%M"
        joined_number_of_days_diff = int((time.time() - time.mktime(join_date.timetuple())) // (3600 * 24))
        created_number_of_days_diff = int((time.time() - time.mktime(created_at.timetuple())) // (3600 * 24))
        member_number = sorted(server.members, key=lambda m: m.joined_at).index(member) + 1
        embed = Embed(description="[{0.name}#{0.discriminator} - {1}]({2})".format(member, nick, member.avatar_url), color=user_color)
        if member.avatar_url:
            embed.set_thumbnail(url=member.avatar_url)
        else:
            embed.set_thumbnail(url=member.default_avatar_url)
        embed.add_field(name="Joined Discord on",
                        value="{}\n({} days ago)".format(member.created_at.strftime(time_fmt),
                                                        created_number_of_days_diff),
                        inline=True)
        embed.add_field(name="Joined Server on",
                        value="{}\n({} days ago)".format(member.joined_at.strftime(time_fmt),
                                                        joined_number_of_days_diff),
                        inline=True)

        member.roles.pop(0)

        if member.roles:
            embed.add_field(name="Roles", value=", ".join([x.name for x in member.roles]), inline=True)
        embed.set_footer(text="Member #{} | User ID: {}".format(member_number, member.id))
        await self.bot.say(embed=embed)

    @commands.command(pass_context=True)
    async def serverinfo(self, ctx):
        server = ctx.message.server
        time_fmt = "%d %b %Y %H:%M"
        creation_time_diff = int(time.time() - time.mktime(server.created_at.timetuple())) // (3600 * 24)
        users_total = len(server.members)
        users_online = len([m for m in server.members if m.status == discord.Status.online or
                            m.status == discord.Status.idle])
        colour = server.me.colour
        if server.icon:
            embed = Embed(description="[{}]({})\nCreated {} ({} days ago)"
                          .format(server.name, server.icon_url, server.created_at.strftime(time_fmt), creation_time_diff),
                          color=colour)
            embed.set_thumbnail(url=server.icon_url)
        else:
            embed = Embed(description="{}\nCreated {} ({} days ago)"
                          .format(server.name, server.created_at.strftime(time_fmt), creation_time_diff))
        embed.add_field(name="Region", value=str(server.region))
        embed.add_field(name="Users", value="{}/{}".format(users_online, users_total))
        embed.add_field(name="Text Channels", value="{}"
                        .format(len([x for x in server.channels if x.type == discord.ChannelType.text])))
        embed.add_field(name="Voice Channels", value="{}"
                        .format(len([x for x in server.channels if x.type == discord.ChannelType.voice])))
        embed.add_field(name="Roles", value="{}".format(len(server.roles)))
        embed.add_field(name="Owner", value=str(server.owner))
        embed.set_footer(text="Server ID: {}".format(server.id))

        await self.bot.say(embed=embed)

    @checks.is_owner_or_moderator()
    @commands.command(pass_context=True)
    async def roleinfo(self,ctx, role=None):
        role_converter = commands.RoleConverter(ctx=ctx, argument=role)
        server = ctx.message.server
        roles = server.roles
        embed = Embed()
        embed.set_thumbnail(url=server.icon_url)
        if not role:
            for role in roles:
                if role.name == "@everyone":
                    continue
                member_with_role = [member for member in server.members if role in member.roles]
                embed.add_field(name=role.name, value="{} Member(s)".format(len(member_with_role)))
        else:
            role = role_converter.convert()
            member_with_role = [member for member in server.members if role in member.roles]
            embed.add_field(name=role.name, value="{} Member(s)".format(len(member_with_role)))
        await self.bot.say(embed=embed)

def setup(bot):
    bot.add_cog(Userinfo(bot=bot))
