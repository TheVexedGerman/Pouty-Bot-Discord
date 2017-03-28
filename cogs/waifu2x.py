from discord.ext import commands
import aiohttp
import os
import uuid
class Waifu2x:

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()

    def __unload(self):
        self.session.close()

    @commands.command(pass_context=True)
    async def upscale(self, ctx, scale='1x', url=None):
        """
        Upscale image via http://waifu2x.udp.jp
        :param scale: decide upscale factor (1x,1.6x,2x)
        :param url: image url, please write file if using file upload
        """
        scales = ('1x', '1.6x', '2x')
        await self.bot.type()
        if scale in scales:
            if scale == '1x':
                scale = 0
            elif scale == '1.6x':
                scale = 1
            elif scale == '2x':
                scale = 2
        else:
            scale = 1
        if ctx.message.attachments:
            link = ctx.message.attachments[0]['proxy_url']
        elif url:
            link = url
        else:
            await self.bot.say('need a file')
            return
        params = {'url': link, 'scale': str(scale)}
        async with self.session.post('http://waifu2x.udp.jp/api', params=params) as response:
            if response.status == 200:
                await self.bot.type()
                if not os.path.exists('data/temp'):
                    os.makedirs('data/temp')
                with open('data/temp/{}.png'.format(str(uuid.uuid4())), 'wb') as f:
                    f.write(await response.read())
                    file_path = f.name
                await self.bot.send_file(ctx.message.channel, file_path)
                os.remove(file_path)
            else:
                message = "Response Code from waifu2x server: {} \n".format(response.status)
                if response.status == 502:
                    message += "File probably too large \n"
                    message += "Please only upload files smaller than 5MB and 1500x1500px"
                await self.bot.say(message)


def setup(bot):
    bot.add_cog(Waifu2x(bot))
