from disnake.ext import commands
import disnake

from bot import BotClient


class Tester(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot

    @commands.slash_command(
        name="ttest",
        auto_sync=True,
        dm_permission=False
    )
    async def ttest(self, inter: disnake.ApplicationCommandInteraction) -> None:
        for i in inter.guild.roles:
            if i.name.startswith("th"):
                print(i.name, i.id)
        a = [
         "SuperBarbarian"
        ,"SuperArcher"
        ,"SuperGiant"
        ,"SneakyGoblin"
        ,"SuperWallBreaker"
        ,"RocketBalloon"
        ,"SuperWizard"
        ,"SuperDragon"
        ,"InfernoDragon"
        ,"SuperMinion"
        ,"SuperValkyrie"
        ,"SuperWitch"
        ,"IceHound",
         "SuperBowler"]

        b = {}
        for i in inter.bot.guilds:
            print(i.name)
            for j in i.emojis:
                print(f"\"{j.name}\": \"<:{j.name}:{j.id}>\"")
                if j.name in a:
                # "h1": "<:h1:531458162931269653>"
                #     print(f"<:{j.name}:{j.id}>")
                    b[j.name] = f"<:{j.name}:{j.id}>"
            print("\n\n")
        c = []
        for i in a:
            c.append(b.get(i))

        for i in c:
            print(i)


    # Creates the embeds as a list.
def setup(bot):
    bot.add_cog(Tester(bot))
