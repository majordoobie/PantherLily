import discord
import json

class Help_Menu:
    def __init__(self, conf, botMode):
        """Display help menu"""
        self.conf = conf
        with open("utils/help/help_menu.json") as infile:
            self.help_menu = json.load(infile)
        self.botMode = botMode
        self.prefix = conf[self.botMode]["bot_prefix"][0]

    def utility(self, last=False):
        """Return the utility commands"""
        embed = discord.Embed(title="__Utility Commands__", url="https://discordapp.com")
        embed.add_field(name=f"**{self.prefix}help** [opt: __--all__, __admin__, __acc__]", value=self.help_menu["utility"]["help"])
        embed.add_field(name=f"**{self.prefix}donation** [opt: __d_user__]", value=self.help_menu["utility"]["donation"])
        embed.add_field(name=f"**{self.prefix}report** [opt: __--discord__]", value=self.help_menu["utility"]["report"])
        embed.add_field(name=f"**{self.prefix}stats** [opt: __d_user__, __--level__]", value=self.help_menu["utility"]["stats"])
        embed.add_field(name=f"**{self.prefix}top** [opt: __-t__, __-d__]", value=self.help_menu["utility"]["top"])
        embed.add_field(name=f"**{self.prefix}invite** [opt: __<int>__]", value=self.help_menu["utility"]["newinvite"])
        embed.add_field(name=f"**OPTIONS**", value=self.help_menu["utility"]["OPTIONS"])
        if last:
            embed = self.add_footer(embed)
        return embed
    
    def accountability(self, last=False):
        """Return the accountability commands"""
        embed = discord.Embed(title="__Accountability Commands__", url="https://discordapp.com")
        embed.add_field(name=f"**{self.prefix}listroles**", value=self.help_menu["acc"]["listroles"])
        embed.add_field(name=f"**{self.prefix}lcm**", value=self.help_menu["acc"]["lcm"])
        embed.add_field(name=f"**{self.prefix}roster**", value=self.help_menu["acc"]["roster"])
        if last:
            embed = self.add_footer(embed)
        return embed

    def administrator(self, last=False):
        """Return administrative commands"""
        embed = discord.Embed(title="__Administrative Commands__", url="https://discordapp.com")
        embed.add_field(name=f"**{self.prefix}user_add** <__clash_tag__> <__d_user__> [opt: __FIN int__]", value=self.help_menu["admin"]["user_add"])
        embed.add_field(name=f"**{self.prefix}user_remove** <__d_user__> [__opt: -m \"msg\"__]", value=self.help_menu["admin"]["user_remove"])
        embed.add_field(name=f"**{self.prefix}queue**", value=self.help_menu["admin"]["queue"])
        embed.add_field(name=f"**{self.prefix}lookup** <--__name__ or --__global__> <__d_user__ or <__tag__>", value=self.help_menu["admin"]["lookup"])
        embed.add_field(name=f"**{self.prefix}addnote** <__d_user__>", value=self.help_menu["admin"]["add_note"])
        embed.add_field(name=f"**{self.prefix}deletenote** <__d_user__>", value=self.help_menu["admin"]["delete_note"])
        embed.add_field(name=f"**{self.prefix}viewnote** <__d_user__>", value=self.help_menu["admin"]["view_note"])
        embed.add_field(name=f"**{self.prefix}getmessage** <__d_user__>", value=self.help_menu["admin"]["get_message"])
        if last:
            embed = self.add_footer(embed)
        return embed

    def add_footer(self, embed):
        """Return footer added embed"""
        embed.set_footer(text=self.conf[self.botMode]["version"]+" "+self.conf[self.botMode]["panther_url"])
        return embed

