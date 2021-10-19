import logging
from logging import Logger
from typing import Dict, Union, List, Optional

from discord import Embed, Role, Member
from discord.ext.commands import Context, NotOwner, BadArgument

EMBED_DESCRIPTION_LIMIT = 4096
EMBED_TITLE_LIMIT = 256
EMBED_CHARACTER_LIMIT = 5400 # Leaving 600 characters as a buffer for titles
EMBED_FILED_LIMIT = 1024

def get_field_batch(payload: List[str]):
    character_counter = 0
    batch = []
    for item in payload:
        if len(item) + len(batch) + character_counter > EMBED_FILED_LIMIT:
            yield_batch = batch.copy()
            batch = []
            character_counter = 0
            yield yield_batch
        character_counter += len(item)
        batch.append(item)
    yield batch

def within_title_limit(title: str) -> bool:
    if len(title) <= EMBED_TITLE_LIMIT:
        return True
    return False

def get_field(value: str, name: str="\u200b") -> Dict[str, str]:
    return {"name": name, "value": value}


def split_text(payload: str):
    payload_lines = payload.split("\n")
    embed_char_counter = 0
    description = []

    field = []
    field_limit = 0
    payload_index = 0


    # Iterate over the payload, saving all the characters
    # into the description list
    for index, line in enumerate(payload_lines):
        new_lines_needed = len(description)
        projected_description_size = len(line) + embed_char_counter
        if new_lines_needed + \
                projected_description_size >= EMBED_DESCRIPTION_LIMIT:
            break

        description.append(line)
        embed_char_counter += len(line)
        payload_index = index + 1

    # Set the description field
    description = "\n".join(description)
    embed = {"description": description, "fields": []}
    embed_char_counter = len(description)

    return embed

    for index, line in enumerate(payload_lines[payload_index:]):
        if len(line) + field_limit > EMBED_FILED_LIMIT:
            break
        field.append(line)
        embed_char_counter += len(line)
        field_limit += len(line)
        payload_index = index + 1

    embed["fields"].append(get_field("\n".join(field)))

    for index, line in enumerate(payload_lines[payload_index:]):
        if len(line) + field_limit > EMBED_CHARACTER_LIMIT:
            break
        field.append(line)
        embed_char_counter += len(line)
        field_limit += len(line)
        payload_index = index + 1

    embed["fields"].append(get_field("\n".join(field)))
    return embed



class BotExt:
    INFO = 0x000080  # blue
    ERROR = 0xff0010  # red
    SUCCESS = 0x00ff00  # green
    WARNING = 0xff8000  # orange

    def __init__(self, settings):
        self.settings = settings
        self.log = logging.getLogger('root.bot_ext')

    async def new_send(
            self,
            ctx: Optional[Context],
            description: str,
            title: Optional[str] = None,
            color: str = INFO,
            code_block: bool = False,
            return_embed: bool = False
    ) -> Optional[Embed]:
        """
        Custom method for printing embeds to discord. Method automatically
        handles breaking the text size to fit in the embed text size limit.

        :NOTE:
            - Embed title is limited to 256 characters
            - Embed description is limited to 4096 characters
            - An embed can contain a maximum of 25 fields
            - A field name/title is limited to 256 character and the
                value of the field is limited to 1024 characters
            - Embed footer is limited to 2048 characters
            - Embed author name is limited to 256 characters
            - The total of characters allowed in an embed is 6000

        :param ctx: Represents the context in which a command
                    is being invoked under
        :param description: Text to display
        :param title: Title of the embed, default is empty string
        :param color: Color of the embed, by default it is INFO
        :param code_block: Whether the text should be in a code block or not
        :param return_embed: If true, the embed is returned to caller otherwise
                             the embed is printed
        :return:
        """
        if description is None:
            raise BadArgument("No text provided to wrap in a embed")

        # Create the base embed
        embed = {"color": color}

        # Add title if exists
        if title is not None:
            if within_title_limit(title):
                embed["title"] = title
            else:
                raise BadArgument(f"Title {title} exceeds character limit "
                                  f"of {EMBED_TITLE_LIMIT} characters")

        # Add description
        if len(description) < EMBED_DESCRIPTION_LIMIT:
            embed["description"] = (
                f"```{description}```" if code_block else description
            )

        else:
            embed.update(split_text(description))


        await ctx.send(embed=Embed.from_dict(embed))
        return None

    async def test(self):
        print("Test")

    async def send(self, ctx: Union[Context, None], description, title='',
                   color=INFO, code_block=False, _return=False,
                   footnote=True, author: Union[list, None] = None) -> Optional[list]:
        if not description:
            raise BadArgument("No value to encapsulate in a embed")

        blocks = await self.text_splitter(description, code_block)
        embed_list = [Embed(
            title=f'{title}',
            description=blocks[0],
            color=color
        )]
        for i in blocks[1:]:
            embed_list.append(Embed(
                description=i,
                color=color
            ))
        if footnote:
            embed_list[-1].set_footer(text=self.settings.bot_config['version'])
        if author:
            embed_list[0].set_author(name=author[0], icon_url=author[1])

        if _return:
            return embed_list
        else:
            for i in embed_list:
                await ctx.send(embed=i)
        return

    @staticmethod
    async def text_splitter(text: str, code_block: bool) -> list:
        """Split text into blocks and return a list of blocks"""
        blocks = []
        block = ''
        for i in text.split('\n'):
            if (len(i) + len(block)) > 4000:
                block = block.rstrip('\n')
                if code_block:
                    print("got it ")
                    blocks.append(f'```{block}```')
                else:
                    blocks.append(block)
                block = f'{i}\n'
            else:
                block += f'{i}\n'
        if block:
            if code_block:
                blocks.append(f'```{block}```')
            else:
                blocks.append(block)
        return blocks

    def is_owner(self, ctx):
        if ctx.author.id == self.settings.owner:
            return True
        else:
            raise NotOwner("Please ask a developer to run this command")

    @staticmethod
    def log_role_change(member: Member, role: Union[List[Role], Role], log: Logger, removed: bool = False) -> None:
        """
        Simple centralized place to log role changes. The input will either be a list of roles or
        a single role
        Parameters
        ----------
        member: Member
            Member whose role has changed
        role: Role
            Role or roles that have changed
        log: Logger
            Logger root to log to
        removed: bool
            Bool stating if the role or roles have been removed

        Returns
        -------
        None
        """
        if isinstance(role, Role):
            msg = 'lost role' if removed else 'received role'
            log.info(f'`{member.display_name}` {msg} `{role.name}`')

        else:
            msg = 'lost role' if removed else 'received role'
            for _role in role:
                log.info(f'`{member.display_name}` {msg} `{_role.name}`')

    @staticmethod
    def log_user_commands(log: Logger, **kwargs) -> None:
        """
        Centralized command line logging

        Parameters
        ----------
        log: Logger
            Logger root used for the cog
        kwargs
            user=ctx.author.display_name,
            command="donation",
            args=None,
            arg_string=arg_string

        Returns
        -------
        None
        """
        msg = f'''
```
User:        {kwargs["user"]}               
Executed:    {kwargs["command"]}
Arg Passed:  {kwargs["arg_string"]}
Args Parsed: {kwargs["args"]}
```
'''
        log.warning(msg)
