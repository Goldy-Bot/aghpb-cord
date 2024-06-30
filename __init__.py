from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional, List, Dict, Tuple

    from goldy_bot import Goldy

import aiohttp

from datetime import datetime, timedelta
from .category_emojis import CATEGORY_EMOJIS

from goldy_bot import (
    Extension, 
    Embed, 
    SlashOptionChoice, 
    Platter, 
    EmbedImage, 
    File, 
    Colours, 
    SlashOptionAutoComplete
)

BASE_URL = "https://api.devgoldy.xyz/aghpb/v1"

extension = Extension("aghpb_cord")

class ProgrammingBooks():
    def __init__(self, goldy: Goldy):
        self.goldy = goldy

        self.programming_book_embed = Embed(
            title = "📔 {name}",
            description = """
            #### Metadata:
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

        self.__session: Optional[aiohttp.ClientSession] = None

        self.__categories_cache: Tuple[float, List[str]] = (0, [])
        self.__categories_cache_expire = timedelta(days = 1)

    group = extension.group_command(
        class_name = __qualname__, 
        name = "programming_books", 
        description = "📖 Get images of anime girls holding programming books."
    )

    async def get_categories(self, typing_value: str, **kwargs) -> List[SlashOptionChoice]:
        current_timestamp = datetime.now().timestamp()

        cache_expire_timestamp, categories = self.__categories_cache

        if current_timestamp > cache_expire_timestamp:
            client = await self.get_session()
            r = await client.get(BASE_URL + "/categories")

            categories: List[str] = await r.json()

            self.__categories_cache = (
                current_timestamp + self.__categories_cache_expire.total_seconds(), categories
            )

        return [
            SlashOptionChoice(category, category) for category in categories if typing_value.lower() in category.lower()
        ]

    @group.sub_command(
        description = "📖 Sends a random book.", 
        slash_options = {
            "category": SlashOptionAutoComplete( # TODO: Change to auto complete once implemented.
                callback = get_categories, 
                description = "The languages/categories you may filter by.", 
                required = False
            )
        }
    )
    async def random(self, platter: Platter, category: Optional[str] = None):
        params = {}

        if category is not None:
            params["category"] = category

        client = await self.get_session()

        book_response = await client.get(BASE_URL + "/random", params = params)

        await self.send_book(platter, book_response)


    async def dynamic_search(self, typing_value: str, **kwargs) -> List[SlashOptionChoice]:
        client = await self.get_session()

        r = await client.get(BASE_URL + "/search", params = {"query": typing_value})

        books: List[Dict[str, str]] = await r.json()

        return [SlashOptionChoice(book["name"], book["search_id"]) for book in books]

    @group.sub_command(
        description = "📖 Allows you to search and get a specific book.", 
        slash_options = { # TODO: Change to auto complete once implemented.
            "query": SlashOptionAutoComplete(
                description = "✨ Look up your favorite book!",
                callback = dynamic_search
            )
        }
    )
    async def search(self, platter: Platter, query: str):
        if not query.isnumeric():
            choices = await self.dynamic_search(query)

            if choices == []:
                platter.error(
                    "Sorry, we couldn't find the book you tried searching.", "❤️ 📔 Book Not Found", Colours.RED
                )

            query = choices[0].data["value"]

        client = await self.get_session()

        book_response = await client.get(BASE_URL + f"/get/id/{query}")

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

    async def send_book(self, platter: Platter, response: aiohttp.ClientResponse) -> None:
        await platter.wait()

        embed = self.programming_book_embed.copy()

        embed.format_title(name = response.headers["book-name"])

        category_emoji = CATEGORY_EMOJIS.get(response.headers["book-category"], "📖")

        embed.format_description(
            category = response.headers["book-category"], 
            category_emoji = category_emoji, 
            date_added_timestamp = int(datetime.fromisoformat(response.headers["book-date-added"]).timestamp()), 
            commit_hash = response.headers["book-commit-url"].split("/")[-1], 
            commit_url = response.headers["book-commit-url"], 
            commit_author = response.headers["book-commit-author"]
        )

        book_file = await File.from_response(response)

        embed.set_image(EmbedImage(book_file.attachment_url))
        embed.data["color"] = Colours.from_image(book_file)

        embed.set_random_footer(self.ads)

        await platter.send_message(
            embeds = [embed], files = [book_file]
        )

    async def get_session(self) -> aiohttp.ClientSession:
        if self.__session is None:
            self.__session = aiohttp.ClientSession()

        return self.__session


def load(goldy: Goldy):
    extension.mount(goldy, ProgrammingBooks)
    return extension