from typing import List

import disnake


class Paginator(disnake.ui.View):
    def __init__(self, embeds: List[disnake.Embed], embed_per_page: int = 1):
        """
        Creates a paginator, modified from.
        https://github.com/disnake/master/examples/views/button/paginator.py

        This version works with a list of embeds instead of just one per page.
        Each page will have a single embed by default but can be modified
        with the `embed_per_page` variable.

        :param embeds: List of embeds
        :param embed_per_page: Number of embeds to show in each page
        """
        super().__init__(timeout=None)
        self.embed_chunks = []
        for embed_chunk in range(0, len(embeds), embed_per_page):
            self.embed_chunks.append(embeds[embed_chunk:embed_chunk + embed_per_page])

        self.embed_count = 0

        self.first_page.disabled = True
        self.prev_page.disabled = True
        print(len(self.embed_chunks))
        if len(self.embed_chunks) == 1:
            self.next_page.disabled = True
            self.last_page.disabled = True

        for i, embed in enumerate(self.embed_chunks):
            embed[-1].set_footer(text=f"Page {i + 1} of {len(self.embed_chunks)}")

    @property
    def embed(self) -> List[disnake.Embed]:
        """Sends the first embed stack to start off the paginator"""
        return self.embed_chunks[self.embed_count]

    @disnake.ui.button(emoji="⏪", style=disnake.ButtonStyle.blurple)
    async def first_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.embed_count = 0
        embeds = self.embed_chunks[self.embed_count]
        embeds[-1].set_footer(text=f"Page 1 of {len(self.embed_chunks)}")

        self.first_page.disabled = True
        self.prev_page.disabled = True
        self.next_page.disabled = False
        self.last_page.disabled = False
        await interaction.response.edit_message(embeds=embeds, view=self)

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary)
    async def prev_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.embed_count -= 1
        embeds = self.embed_chunks[self.embed_count]

        self.next_page.disabled = False
        self.last_page.disabled = False
        if self.embed_count == 0:
            self.first_page.disabled = True
            self.prev_page.disabled = True
        await interaction.response.edit_message(embeds=embeds, view=self)

    @disnake.ui.button(emoji="❌", style=disnake.ButtonStyle.red)
    async def remove(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.edit_message(view=None)

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary)
    async def next_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.embed_count += 1
        embeds = self.embed_chunks[self.embed_count]

        self.first_page.disabled = False
        self.prev_page.disabled = False
        if self.embed_count == len(self.embed_chunks) - 1:
            self.next_page.disabled = True
            self.last_page.disabled = True
        await interaction.response.edit_message(embeds=embeds, view=self)

    @disnake.ui.button(emoji="⏩", style=disnake.ButtonStyle.blurple)
    async def last_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.embed_count = len(self.embed_chunks) - 1
        embeds = self.embed_chunks[self.embed_count]

        self.first_page.disabled = False
        self.prev_page.disabled = False
        self.next_page.disabled = True
        self.last_page.disabled = True
        await interaction.response.edit_message(embeds=embeds, view=self)
