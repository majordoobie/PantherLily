from packages.private.secrets import *

COG_LOCATION='packages.cogs'
VERSION='3.0.0'

class Settings:
    """
    Class is used to set up the configuration for the bot
    """
    def __init__(self, bot_mode):
        self.webhook_url = WEBHOOK_URL
        self.bot_mode = bot_mode
        self.emojis = emoji_dict
        self.bot_config = self.get_config()

        # Paths
        self.cog_path = COG_LOCATION
        self.enabled_cogs = self.get_cogs()

        # TODO: keep logging settings here
        # Logging

        # Server IDs
        self.zulu_server = ZULU_SERVER

    def get_config(self):
        if self.bot_mode == 'live_mode':
            return {
                'bot_name': 'Panther Lily',
                'bot_token': LIVE_TOKEN,
                'bot_prefix': ['p.', 'P.', 'Panther.', 'panther.'],
                'version': f'Panther Lily Version: {VERSION}',
                }
        elif self.bot_mode == 'dev_mode':
            return {
                'bot_name': 'Panther Lily [Dev Shell]',
                'bot_token': DEV_TOKEN,
                'bot_prefix': ['dev.', 'd.', 'D.'],
                'version': 'Panther 3 rewrite',
                }

    def get_cogs(self):
        return (
            'tester',
        )


emoji_dict = {
    "one": "<:one:531449976891637770>",
    "two": "<:two:531450019711025162>",
    "three": "<:three:531450035422887936>",
    "four": "<:four:531450049553760296>",
    "fill": "<:fill:531451914106175509>",
    "minus": "<:minus:598623392522043402>",
    "plus": "<:plus:598630358296297472>",
    "waze": "<:waze:602266059583782913>",
    "doublecheck": "<:doublecheck:681908801909293137>",
    "delete": "<:delete:681908801947041908>",
    "add": "<:add:681908802077196299>",
    "approved": "<:approved:681908802089517058>",
    "complete": "<:complete:681908802106425378>",
    "reset": "<:reset:681908802152562828>",
    "check": "<:check:681908802161082474>",
    "cancel": "<:cancel:681908802181922817>",
    "rcs48": "<:rcs48:569362943884656664>",
    "rcs49": "<:rcs49:569362943951503386>",
    "rcs47": "<:rcs47:569362944241172491>",
    "rcs50": "<:rcs50:569362944312475676>",
    "rcs45": "<:rcs45:569371105752514572>",
    "rcs46": "<:rcs46:569371105874280459>",
    "rcs42": "<:rcs42:569371105953972225>",
    "rcs44": "<:rcs44:569371105966686210>",
    "rcs37": "<:rcs37:569371106096447498>",
    "rcs38": "<:rcs38:569371106142715904>",
    "rcs36": "<:rcs36:569371106176270345>",
    "rcs43": "<:rcs43:569371106205499402>",
    "rcs40": "<:rcs40:569371106356756491>",
    "rcs41": "<:rcs41:569371106373402650>",
    "rcs39": "<:rcs39:569371106377596949>",
    "rcs1": "<:rcs1:570030365146873858>",
    "rcs3": "<:rcs3:570030366128340993>",
    "rcs2": "<:rcs2:570030366186930219>",
    "rcs9": "<:rcs9:570030366308564993>",
    "rcs6": "<:rcs6:570030366400839701>",
    "rcs4": "<:rcs4:570030366543577098>",
    "rcs17": "<:rcs17:570030366581063711>",
    "rcs13": "<:rcs13:570030366593908797>",
    "rcs8": "<:rcs8:570030366648434698>",
    "rcs5": "<:rcs5:570030366652366858>",
    "rcs7": "<:rcs7:570030366656823296>",
    "rcs27": "<:rcs27:570030366656823348>",
    "rcs20": "<:rcs20:570030366669275163>",
    "rcs12": "<:rcs12:570030366690377733>",
    "rcs21": "<:rcs21:570030366690377779>",
    "rcs10": "<:rcs10:570030366719606814>",
    "rcs11": "<:rcs11:570030366740447280>",
    "rcs14": "<:rcs14:570030366761680906>",
    "rcs15": "<:rcs15:570030366820270081>",
    "rcs16": "<:rcs16:570030366820270100>",
    "rcs18": "<:rcs18:570030366824333332>",
    "rcs19": "<:rcs19:570030366870470677>",
    "rcs24": "<:rcs24:570030366979653645>",
    "rcs22": "<:rcs22:570030367067865088>",
    "rcs23": "<:rcs23:570030367084380160>",
    "rcs30": "<:rcs30:570030367084380221>",
    "rcs31": "<:rcs31:570030367084511233>",
    "rcs26": "<:rcs26:570030367097094165>",
    "rcs32": "<:rcs32:570030367109808158>",
    "rcs34": "<:rcs34:570030367118065664>",
    "rcs29": "<:rcs29:570030367118065684>",
    "rcs33": "<:rcs33:570030367122128901>",
    "rcs35": "<:rcs35:570030367134973962>",
    "rcs25": "<:rcs25:570030367399084042>",
    "rcs28": "<:rcs28:570030368422363136>",
    "unchecked": "<:unchecked:682641854432542725>",
    "checked": "<:checked:682641854554177579>",
    "right": "<:right:682765217410711687>",
    "left": "<:left:682765217414775013>",
    "save": "<:save:682765217528152065>"
}



