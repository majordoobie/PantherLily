from typing import List

import asyncpg
from disnake.ext import commands
import disnake
import asyncio

from packages.utils.paginator import Paginator
from packages.utils.utils import is_leader
import packages.utils.bot_sql as sql


class RowButtons(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # Creates a row of buttons and when one of them is pressed, it will send a message with the number of the button.

    @disnake.ui.button(label="Hi", style=disnake.ButtonStyle.red)
    async def first_button(
            self, button: disnake.ui.Button,
            interaction: disnake.MessageInteraction
    ):
        await interaction.response.edit_message("New massage")

    @disnake.ui.button(label="this is", style=disnake.ButtonStyle.red)
    async def second_button(
            self, button: disnake.ui.Button,
            interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "This is the second button.")

    @disnake.ui.button(label="a row of", style=disnake.ButtonStyle.blurple,
                       row=1)
    async def third_button(
            self, button: disnake.ui.Button,
            interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "This is the third button.")

    @disnake.ui.button(label="buttons.", style=disnake.ButtonStyle.blurple,
                       row=1)
    async def fourth_button(
            self, button: disnake.ui.Button,
            interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "This is the fourth button.")

    @disnake.ui.button(emoji="🥳", style=disnake.ButtonStyle.green, row=2)
    async def fifth_button(
            self, button: disnake.ui.Button,
            interaction: disnake.MessageInteraction
    ):
        await interaction.response.send_message(
            "This is the fifth button.")


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
    async def test(self, inter: disnake.ApplicationCommandInteraction):
        for i in inter.guild.emojis:
            print(f"<{i.name}:{i.id}>")
        #await inter.send("Tic Tac Toe: X goes first", view=TicTacToe())
        # await inter.send("Here are some buttons!", view=RowButtons())

class TicTacToeButton(disnake.ui.Button["TicTacToe"]):
    def __init__(self, x: int, y: int):
        # A label is required, but we don't need one so a zero-width space is used
        # The row parameter tells the View which row to place the button under.
        # A View can only contain up to 5 rows -- each row can only have 5 buttons.
        # Since a Tic Tac Toe grid is 3x3 that means we have 3 rows and 3 columns.
        super().__init__(style=disnake.ButtonStyle.secondary,
                         label="\u200b", row=y)
        self.x = x
        self.y = y

    # This function is called whenever this particular button is pressed
    # This is part of the "meat" of the game logic
    async def callback(self, interaction: disnake.MessageInteraction):
        assert self.view is not None  # noqa: S101
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            self.style = disnake.ButtonStyle.danger
            self.label = "X"
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = "It is now O's turn"
        else:
            self.style = disnake.ButtonStyle.success
            self.label = "O"
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = "It is now X's turn"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = "X won!"
            elif winner == view.O:
                content = "O won!"
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)

    # This is our actual board View
class TicTacToe(disnake.ui.View):
    # This tells the IDE or linter that all our children will be TicTacToeButtons
    # This is not required
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        # Our board is made up of 3 by 3 TicTacToeButtons
        # The TicTacToeButton maintains the callbacks and helps steer
        # the actual game.
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    # This method checks for the board winner -- it is used by the TicTacToeButton
    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + \
                    self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None

    # Creates the embeds as a list.
def setup(bot):
    bot.add_cog(Tester(bot))
