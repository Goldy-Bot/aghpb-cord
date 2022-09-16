from __future__ import annotations
from genericpath import isdir
import time
import GoldyBot
from GoldyBot.utility.commands import send as send_msg, mention

import os
import random
import nextcord
from colorthief import ColorThief

from .book import ProgrammingBook

AUTHOR = 'Dev Goldy'
AUTHOR_GITHUB = 'https://github.com/THEGOLDENPRO'
OPEN_SOURCE_LINK = 'https://github.com/THEGOLDENPRO/cat_ears'

class ProgrammingBooks(GoldyBot.Extension):
    def __init__(self, package_module=None):
        self.language_not_found_embed = GoldyBot.Embed(
            title="⛔ Programming Language Not Found",
            description="Did you spell it correctly?",
            colour=GoldyBot.colours.RED
        )

        self.programming_book_embed = GoldyBot.Embed(
            title="📔 Anime Girl Holding Programming Book",
            description="""
*Anime girl holding programming book of* **``{}``**.
            """,
            colour=GoldyBot.colours.AKI_BLUE
        )

        super().__init__(self, package_module_name=package_module)

        self.path_to_folder = f"{self.module.path_to_module}/assets/Anime-Girls-Holding-Programming-Books"

    async def random_language(self) -> str:
        language_list = os.listdir(self.path_to_folder)
        language = language_list[random.randint(0, len(language_list) - 1)]

        if language in [".git", "CONTRIBUTING.md", "README.md"]:
            return "Python"
        else:
            return language

    async def random_book(self, language:str) -> ProgrammingBook|None:
        """Returns random book from a specific language."""
        for actual_language in os.listdir(f"{self.path_to_folder}/"):
            if language.upper() == actual_language.upper():
                actual_pictures_list = os.listdir(f"{self.path_to_folder}/{actual_language}/")

                picture_name = actual_pictures_list[random.randint(0, len(actual_pictures_list) - 1)]

                return ProgrammingBook(
                    file_name=picture_name,
                    file_path=f"{self.path_to_folder}/{actual_language}/{picture_name}",
                    language=actual_language,
                )

            else:
                pass

        return None

    def loader(self):

        @GoldyBot.command(slash_cmd_only=True)
        async def programming_books(self:ProgrammingBooks, ctx):
            #random.seed(time.process_time())
            pass

        @programming_books.sub_command(help_des="Sends image of anime girl holding a programming language book.", required_roles=["anime"], slash_options={
            "language": nextcord.SlashOption(required=False)
        })
        async def get(self:ProgrammingBooks, ctx, language=None):
            
            if language == None:
                language = await self.random_language()

            book = await self.random_book(language)

            if book == None:
                message = await send_msg(ctx, embed=self.language_not_found_embed)
                await GoldyBot.asyncio.sleep(3)
                await message.delete()
            else:
                book_embed = self.programming_book_embed.copy()
                
                book_embed.description = book_embed.description.format(book.language)
                book_embed.set_footer(text=f"File Name: {book.file_name}")
                book_embed.set_image(f"attachment://book_image.png")
                book_embed.colour = GoldyBot.colours().custom_colour(rgb=ColorThief(book.file_path).get_color(quality=5))

                await send_msg(ctx, embed=book_embed, file=GoldyBot.nextcord.File(book.file_path, filename="book_image.png"))

                del book_embed

        @programming_books.sub_command(help_des="Sends image of anime girl holding a programming language book to a member. 😈", required_roles=["bot_dev", "nova_staff", "anime", "bot_admin"])
        async def send_to_member(self:ProgrammingBooks, ctx, target_member):
            author = GoldyBot.Member(ctx)
            target_member = GoldyBot.Member(ctx, mention_str=target_member)

            # IGNORE this piece of BAD CODE, lmao
            #programming_lang=(lambda programming_language_list: (programming_language_list[random.randint(0, len(programming_language_list) - 1)]))(os.listdir(f'{self.module.path_to_module}/assets/Anime-Girls-Holding-Programming-Books')); picture_list=(lambda programming_lang: os.listdir(f"{self.module.path_to_module}/assets/Anime-Girls-Holding-Programming-Books/{programming_lang}"))(programming_lang); picture_name=(lambda picture_list : picture_list[random.randint(0, len(picture_list) - 1)])(picture_list); picture_path = f"{self.module.path_to_module}/assets/Anime-Girls-Holding-Programming-Books/{programming_lang}/{picture_name}"

            book = await self.random_book(await self.random_language())

            await send_msg(target_member, file=GoldyBot.nextcord.File(book.file_path))

            await send_msg(ctx, f"💚 **{mention(author)} Book sent! They got ``{book.language}``.**")

        
def load():
    ProgrammingBooks(package_module=__name__)
