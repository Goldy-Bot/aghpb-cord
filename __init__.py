from __future__ import annotations
from typing import List, Dict

import GoldyBot
from GoldyBot import SlashOptionChoice, front_end_errors

import aiohttp
from io import BytesIO
from datetime import datetime
from .category_emojis import CATEGORY_EMOJIS

BASE_URL = "https://api.devgoldy.xyz/aghpb/v1"

RANDOM = "/random"
CATEGORIES = "/categories"
SEARCH = "/search"
GET_ID = "/get/id"

class ProgrammingBooks(GoldyBot.Extension):
    def __init__(self):
        super().__init__()

        self.programming_book_embed = GoldyBot.Embed(
            title = "📔 {name}",
            description = """
            #### __Metadata__:
            -- **{category_emoji} Category: ``{category}``**
            -- **📅 Date Added: <t:{date_added_timestamp}:D>**
            -- **🏷 Commit ID: [``{commit_hash}``]({commit_url})**
            -- **🧑 Commit Author: ``{commit_author}``**
            """
        )

        self.ads = [
            "✨ The programming books API is open source, check it out at: https://github.com/THEGOLDENPRO/aghpb_api",
            "💛 Big thanks to the aghpb repo: https://github.com/cat-milk/Anime-Girls-Holding-Programming-Books"
        ]

    programming_books = GoldyBot.GroupCommand("programming_books", description = "Get images of anime girls holding programming books.")

    async def dynamic_categories(self, typing_value: str) -> List[SlashOptionChoice]:
        r = await self.goldy.http_client._session.get(BASE_URL + CATEGORIES)
        categories: List[str] = await r.json()

        choices: List[SlashOptionChoice] = []

        for category in categories:
            if typing_value.lower() in category.lower():
                choices.append(SlashOptionChoice(category, category))

        return choices

    async def dynamic_search(self, typing_value: str) -> List[SlashOptionChoice]:
        r = await self.goldy.http_client._session.get(BASE_URL + SEARCH, params = {"query": typing_value})
        books: List[Dict[str, str]] = await r.json()

        return [SlashOptionChoice(book["name"], book["search_id"]) for book in books]
    
    async def send_book(self, platter: GoldyBot.GoldPlatter, response: aiohttp.ClientResponse) -> None:
        embed = self.programming_book_embed.copy()

        embed.format_title(name = response.headers["book-name"])

        category_emoji = CATEGORY_EMOJIS.get(response.headers["book-category"], "")
        embed.format_description(
            category = response.headers["book-category"],
            category_emoji = category_emoji if not category_emoji == "" else "📖",
            date_added_timestamp = int(datetime.fromisoformat(response.headers["book-date-added"]).timestamp()),
            commit_hash = response.headers["book-commit-url"].split("/")[-1],
            commit_url = response.headers["book-commit-url"],
            commit_author = response.headers["book-commit-author"]
        )

        book_bytes = await response.read()
        book_file = GoldyBot.File(BytesIO(book_bytes), file_name = "image.png")

        embed["image"] = GoldyBot.EmbedImage(book_file.attachment_url)
        embed["color"] = GoldyBot.Colours.from_image(book_file)

        embed.set_random_footer(self.ads)

        await platter.send_message(
            embeds = [embed], files = [book_file]
        )


    @programming_books.sub_command(
        description = "Sends a random book.", 
        slash_options = {
            "category": GoldyBot.SlashOptionAutoComplete(
                description = "The programming languages and categories you may filter by.",
                callback = dynamic_categories,
                required = False
            )
        },
        wait = True
    )
    async def random(self, platter: GoldyBot.GoldPlatter, category: str = None):
        params = {}
        url = BASE_URL + RANDOM

        if category is not None:
            params["category"] = category

        book_response = await self.goldy.http_client._session.get(url, params = params)

        await self.send_book(platter, book_response)


    @programming_books.sub_command(
        description = "Allows you to search and get a specific book.", 
        slash_options = {
            "query": GoldyBot.SlashOptionAutoComplete(
                description = "✨ Look up your favorite book!",
                callback = dynamic_search
            )
        },
        wait = True
    )
    async def search(self, platter: GoldyBot.GoldPlatter, query: str):
        if not query.isnumeric():
            choices = await self.dynamic_search(query)

            if choices == []:
                raise BookNotFound(platter, self.logger)

            query = choices[0]["value"]

        url = BASE_URL + f"{GET_ID}/{query}"

        book_response = await self.goldy.http_client._session.get(url)

        await self.send_book(platter, book_response)


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


class BookNotFound(front_end_errors.FrontEndErrors):
    def __init__(self, platter: GoldyBot.GoldPlatter, logger: GoldyBot.log.Logger = None):
        super().__init__(
            embed = GoldyBot.Embed(
                title = "❤️📔 Book Not Found", 
                description = "Sorry, we couldn't find a book with that name.",
                colour = GoldyBot.Colours.RED
            ),
            message = "Member searched for book that couldn't be found.",
            platter = platter, 
            logger = logger
        )

def load():
    ProgrammingBooks()
