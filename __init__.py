from __future__ import annotations
from typing import List, Dict, Any

import GoldyBot
from GoldyBot import SlashOptionChoice

from io import BytesIO
from datetime import datetime

BASE_URL = "https://api.devgoldy.xyz/aghpb/v1"

RANDOM = "/random"
CATEGORIES = "/categories"

class ProgrammingBooks(GoldyBot.Extension):
    def __init__(self):
        super().__init__()

        self.programming_book_embed = GoldyBot.Embed(
            title = "📔 Anime Girls Holding Programming Books",
            fields = [
                GoldyBot.EmbedField(
                    name = "📖 Category:",
                    value = "- **``{book_category}``**",
                    inline = True 
                ),
                GoldyBot.EmbedField(
                    name = "📅 Date Added:",
                    value = "- **<t:{date_added_timestamp}:f>**",
                    inline = True 
                ),
                GoldyBot.EmbedField(
                    name = "🪪 Book Name:",
                    value = "- **``{book_name}``**"
                )
            ],
            colour = GoldyBot.Colours.INVISIBLE
        )

    programming_books = GoldyBot.GroupCommand("programming_books", description = "Get images of anime girls holding programming books.")

    async def dynamic_categories(self, typing_value: str) -> List[SlashOptionChoice]:
        r = await self.goldy.http_client._session.get(BASE_URL + CATEGORIES)
        categories: List[str] = await r.json()

        choices: List[SlashOptionChoice] = []

        for category in categories:
            if typing_value.lower() in category.lower():
                choices.append(SlashOptionChoice(category, category))

        return choices

    @programming_books.sub_command(description = "Sends a random book.", slash_options = {
        "category": GoldyBot.SlashOptionAutoComplete(
            callback = dynamic_categories,
            required = False
        )
    })
    async def random(self, platter: GoldyBot.GoldPlatter, category: str = None):
        url = BASE_URL + RANDOM

        if category is not None:
            url += f"?category={category}"

        embed = self.programming_book_embed.copy()

        await platter.wait()
        book = await self.goldy.http_client._session.get(url)

        embed.format_fields(
            book_category = book.headers["book-category"],
            date_added_timestamp = int(datetime.fromisoformat(book.headers["book-date-added"]).timestamp()),
            book_name = book.headers["book-name"]
        )

        book_file = await book.read()
        book_file = GoldyBot.File(BytesIO(book_file), file_name = "image.png")

        embed["image"] = GoldyBot.EmbedImage(book_file.attachment_url)

        await platter.send_message(
            embeds = [embed], files = [book_file]
        )

    """
    @programming_books.sub_command(help_des="Sends image of anime girl holding a programming language book to a member. 😈", required_roles=["bot_dev", "nova_staff", "anime", "bot_admin"])
    async def send_to_member(self:ProgrammingBooks, ctx, target_member):
        await think(ctx)

        author = GoldyBot.Member(ctx)
        target_member = GoldyBot.Member(ctx, mention_str=target_member)

        # IGNORE this piece of BAD CODE, lmao
        #programming_lang=(lambda programming_language_list: (programming_language_list[random.randint(0, len(programming_language_list) - 1)]))(os.listdir(f'{self.module.path_to_module}/assets/Anime-Girls-Holding-Programming-Books')); picture_list=(lambda programming_lang: os.listdir(f"{self.module.path_to_module}/assets/Anime-Girls-Holding-Programming-Books/{programming_lang}"))(programming_lang); picture_name=(lambda picture_list : picture_list[random.randint(0, len(picture_list) - 1)])(picture_list); picture_path = f"{self.module.path_to_module}/assets/Anime-Girls-Holding-Programming-Books/{programming_lang}/{picture_name}"

        book = await self.random_book(await self.random_language())

        await send(target_member, file=GoldyBot.nextcord.File(book.file.get_file()))

        await send(ctx, f"💚 **{mention(author)} Book sent! They got ``{book.language}``.**")
    """


def load():
    ProgrammingBooks()
