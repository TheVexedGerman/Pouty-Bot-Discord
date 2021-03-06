from discord.ext import commands
from discord import User
from .utils import checks
import json
import subprocess
import os
import asyncio
import re
import sys
import importlib

class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if os.path.exists("data/ignores.json"):
            with open("data/ignores.json") as f:
                self.global_ignores = json.load(f)
        else:
            self.global_ignores = []
        if os.path.exists("data/disabled_commands.json"):
            with open('data/disabled_commands.json') as f:
                self.disabled_commands = json.load(f)
        else:
            self.disabled_commands = []
        self.disabled_commands_file = 'data/disabled_commands.json'
        self.confirmation_reacts = [
            '\N{WHITE HEAVY CHECK MARK}', '\N{CROSS MARK}'
        ]


    #
    #
    # loading and unloading command by Rapptz
    #       https://github.com/Rapptz/
    #
    @commands.command(hidden=True)
    @checks.is_owner_or_moderator()
    async def load(self, ctx, *, module: str):
        """Loads a module"""
        try:
            self.bot.load_extension('cogs.'+module)
        except Exception as e:
            await ctx.send('\N{THUMBS DOWN SIGN}')
            await ctx.send('`{}: {}`'.format(type(e).__name__, e))
        else:
            await ctx.send('\N{THUMBS UP SIGN}')

    @commands.command(hidden=True)
    @checks.is_owner_or_moderator()
    async def unload(self, ctx, *, module:str):
        """Unloads a module"""
        if module == "owner" or module == "default":
            await ctx.send("This cog cannot be unloaded")
            return
        try:
            self.bot.unload_extension('cogs.'+module)
        except Exception as e:
            await ctx.send('\N{THUMBS DOWN SIGN}')
            await ctx.send('`{}: {}`'.format(type(e).__name__, e))
        else:
            await ctx.send('\N{THUMBS UP SIGN}')

    @commands.command(name='reload', hidden=True)
    @checks.is_owner_or_moderator()
    async def _reload(self, ctx, *, module : str):
        """Reloads a module."""
        try:
            self.bot.reload_extension('cogs.'+module)
        except Exception as e:
            try:
                self.bot.load_extension('cogs.'+module)
                await ctx.send('\N{THUMBS UP SIGN}')
            except Exception as inner_e:
                await ctx.send('\N{THUMBS DOWN SIGN}')
                await ctx.send('{}: {}'.format(type(e).__name__, e))
        else:
            await ctx.send('\N{THUMBS UP SIGN}')

    @commands.command(name='shutdown', hidden=True)
    @checks.is_owner_or_admin()
    async def _shutdown(self, ctx):
        """Shutdown bot"""
        await ctx.send('Shutting down...')
        await self.bot.logout()

    @commands.group(pass_context=True, aliases=['bl'])
    @checks.is_owner_or_moderator()
    async def blacklist(self, ctx):
        """
        Blacklist management commands
        :return:
        """
        if ctx.invoked_subcommand is None:
            await ctx.send("use `blacklist add` or `global_ignores remove`")

    async def run_process(self, command):
        try:
            process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await process.communicate()
        except NotImplementedError:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = await self.bot.loop.run_in_executor(None, process.communicate)

        return [output.decode() for output in result]

    _GIT_PULL_REGEX = re.compile(r'\s*(?P<filename>.+?)\s*\|\s*[0-9]+\s*[+-]+')

    def find_modules_from_git(self, output):
        files = self._GIT_PULL_REGEX.findall(output)
        ret = []
        for file in files:
            root, ext = os.path.splitext(file)
            if ext != '.py':
                continue

            if root.startswith('cogs/'):
                # A submodule is a directory inside the main cog directory for
                # my purposes
                ret.append((root.count('/') - 1, root.replace('/', '.')))

        # For reload order, the submodules should be reloaded first
        ret.sort(reverse=True)
        return ret

    def reload_or_load_extension(self, module):
        try:
            self.bot.reload_extension(module)
        except commands.ExtensionNotLoaded:
            self.bot.load_extension(module)

    @commands.command()
    @commands.is_owner()
    async def update(self, ctx):
        """Reloads all modules, while pulling from git."""

        async with ctx.typing():
            stdout, stderr = await self.run_process('git pull')

        # progress and stuff is redirected to stderr in git pull
        # however, things like "fast forward" and files
        # along with the text "already up-to-date" are in stdout

        if stdout.startswith('Already up-to-date.'):
            return await ctx.send(stdout)

        modules = self.find_modules_from_git(stdout)
        mods_text = '\n'.join(f'{index}. `{module}`' for index, (_, module) in enumerate(modules, start=1))
        prompt_text = f'This will update the following modules, are you sure?\n{mods_text}'
        mes = await ctx.send(prompt_text)

        def user_check(reaction, user_):
            return reaction.emoji in self.confirmation_reacts and ctx.author.id == user_.id
        for reactions in self.confirmation_reacts:
            await mes.add_reaction(reactions)
        confirm, user = await self.bot.wait_for('reaction_add', check=user_check, timeout=60)
        if confirm.emoji == self.confirmation_reacts[1]:
            return await ctx.send('Aborting.')

        statuses = []
        for is_submodule, module in modules:
            if is_submodule:
                try:
                    actual_module = sys.modules[module]
                except KeyError:
                    statuses.append((ctx.tick(None), module))
                else:
                    try:
                        importlib.reload(actual_module)
                    except Exception as e:
                        statuses.append((self.confirmation_reacts[1], module))
                    else:
                        statuses.append((self.confirmation_reacts[0], module))
            else:
                try:
                    self.reload_or_load_extension(module)
                except commands.ExtensionError:
                    statuses.append((self.confirmation_reacts[1], module))
                else:
                    statuses.append((self.confirmation_reacts[0], module))

        await ctx.send('\n'.join(f'{status}: `{module}`' for status, module in statuses))



    @blacklist.command(name="add", pass_context=True)
    async def _blacklist_add(self, ctx, user: User):
        if ctx.message.author.id == user.id:
            await ctx.send("Don't blacklist yourself, dummy")
            return
        if user.id not in self.global_ignores:
            self.global_ignores.append(user.id)
            with open("data/ignores.json", "w") as f:
                json.dump(self.global_ignores,f)
            await ctx.send('User {} has been blacklisted'.format(user.name))
        else:
            await ctx.send("User {} already is blacklisted".format(user.name))


    @blacklist.command(name="remove")
    async def _blacklist_remove(self, ctx, user:User):
        if user.id in self.global_ignores:
            self.global_ignores.remove(user.id)
            with open("data/ignores.json", "w") as f:
                json.dump(self.global_ignores, f)
            await ctx.send("User {} has been removed from blacklist".format(user.name))
        else:
            await ctx.send("User {} is not blacklisted".format(user.name))

    @commands.group(name="command", pass_context=True)
    @checks.is_owner()
    async def _commands(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("use `command help`")

    @_commands.command(name='disable', pass_context=True)
    async def _commands_disable(self, ctx, command:str ):
        server = ctx.message.guild
        self.disabled_commands.append({"server": server.id, "command": command})
        with open(self.disabled_commands_file, 'w') as f:
            json.dump(self.disabled_commands, f)
        await ctx.send("command {} disabled".format(command))

    @_commands.command(name='enable', pass_context=True)
    async def _commands_enable(self, ctx, command:str ):
        server = ctx.message.guild
        self.disabled_commands.remove({"server": server.id, "command": command})
        with open(self.disabled_commands_file, 'w') as f:
            json.dump(self.disabled_commands, f)
        await ctx.send("command {} enabled".format(command))

def setup(bot):
    bot.add_cog(Owner(bot))
