from disnake.ext import commands
import disnake
import asyncio

from packages.utils.utils import is_leader


class Tester(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.check(is_leader)
    @commands.slash_command(
        auto_sync=True,
        description="Tester")
    async def error(self, ctx):
        await self.bot.send(ctx=ctx, description='ponnnnnnnnng')

    @commands.slash_command(auto_sync=True)
    async def sync_thing(self, inter):
        guild: disnake.Guild = self.bot.get_guild(293943534028062721)
        for member in guild.members:
            if member.id == 265368254761926667:
                print(member.name, member.display_name, member.nick, member.discriminator, member.tag)

    @commands.slash_command(auto_sync=True)
    async def create_tag(self, inter: disnake.CommandInteraction):
        # Sends a modal using a high level implementation.
        await inter.response.send_modal(modal=MyModal())

    @commands.slash_command(auto_sync=True)
    async def create_tag_low(self, inter: disnake.CommandInteraction):
        # Works same as the above code but using a low level interface.
        # It's recommended to use this if you don't want to increase cache usage.
        await inter.response.send_modal(
            title="Create Tag",
            custom_id="create_tag_low",
            components=[
                disnake.ui.TextInput(
                    label="Name",
                    placeholder="The name of the tag",
                    custom_id="name",
                    style=disnake.TextInputStyle.short,
                    max_length=50,
                ),
                disnake.ui.TextInput(
                    label="Description",
                    placeholder="The description of the tag",
                    custom_id="description",
                    style=disnake.TextInputStyle.short,
                    min_length=5,
                    max_length=50,
                ),
                disnake.ui.TextInput(
                    label="Content",
                    placeholder="The content of the tag",
                    custom_id="content",
                    style=disnake.TextInputStyle.paragraph,
                    min_length=5,
                    max_length=1024,
                ),
            ],
        )

        # Waits until the user submits the modal.
        try:
            modal_inter: disnake.ModalInteraction = await bot.wait_for(
                "modal_submit",
                check=lambda
                    i: i.custom_id == "create_tag_low" and i.author.id == inter.author.id,
                timeout=300,
            )
        except asyncio.TimeoutError:
            # The user didn't submit the modal in the specified period of time.
            # This is done since Discord doesn't dispatch any event for when a modal is closed/dismissed.
            return

        embed = disnake.Embed(title="Tag Creation")
        for custom_id, value in modal_inter.text_values.items():
            embed.add_field(name=custom_id.capitalize(), value=value,
                            inline=False)
        await modal_inter.response.send_message(embed=embed)


class MyModal(disnake.ui.Modal):
    def __init__(self) -> None:
        components = [
            disnake.ui.TextInput(
                label="Name",
                placeholder="The name of the tag",
                custom_id="name",
                style=disnake.TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Description",
                placeholder="The description of the tag",
                custom_id="description",
                style=disnake.TextInputStyle.short,
                min_length=5,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Content",
                placeholder="The content of the tag",
                custom_id="content",
                style=disnake.TextInputStyle.paragraph,
                min_length=5,
                max_length=1024,
            ),
        ]
        super().__init__(title="Create Tag", custom_id="create_tag",
                         components=components)

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        embed = disnake.Embed(title="Tag Creation")
        for key, value in inter.text_values.items():
            embed.add_field(name=key.capitalize(), value=value, inline=False)
        await inter.response.send_message(embed=embed)

    async def on_error(self, error: Exception,
                       inter: disnake.ModalInteraction) -> None:
        await inter.response.send_message("Oops, something went wrong.",
                                          ephemeral=True)


def setup(bot):
    bot.add_cog(Tester(bot))
