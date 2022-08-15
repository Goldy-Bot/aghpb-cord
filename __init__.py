import GoldyBot
from GoldyBot.utility.commands import send as send_msg, mention

import os
import random

AUTHOR = 'Dev Goldy'
AUTHOR_GITHUB = 'https://github.com/THEGOLDENPRO'
OPEN_SOURCE_LINK = 'https://github.com/THEGOLDENPRO/cat_ears'

class ProgrammingBooks(GoldyBot.Extenstion):

    def __init__(self, package_module=None):
        super().__init__(self, package_module_name=package_module)

    def loader(self):

        @GoldyBot.command(slash_cmd_only=True)
        async def programming_books(self:ProgrammingBooks, ctx):
            pass

        @programming_books.sub_command(help_des="Sends image of anime girl holding a programming language book.", required_roles=["anime"])
        async def get(self:ProgrammingBooks, ctx):
            author = GoldyBot.Member(ctx)

            programming_lang=(lambda programming_language_list: (programming_language_list[random.randint(0, len(programming_language_list) - 1)]))(os.listdir(f'{self.module.path_to_module}/assets/programming_books')); picture_list=(lambda programming_lang: os.listdir(f"{self.module.path_to_module}/assets/programming_books/{programming_lang}"))(programming_lang); picture_name=(lambda picture_list : picture_list[random.randint(0, len(picture_list) - 1)])(picture_list); picture_path = f"{self.module.path_to_module}/assets/programming_books/{programming_lang}/{picture_name}"

            await send_msg(ctx, f"📔 **{mention(author)} Anime girl holding programming book for ``{programming_lang}``.**")
            await send_msg(ctx, file=GoldyBot.nextcord.File(picture_path))

        @programming_books.sub_command(help_des="Sends image of anime girl holding a programming language book to a member. 😈", required_roles=["bot_dev"])
        async def send_to_member(self:ProgrammingBooks, ctx, target_member):
            author = GoldyBot.Member(ctx)
            target_member = GoldyBot.Member(ctx, mention_str=target_member)

            programming_lang=(lambda programming_language_list: (programming_language_list[random.randint(0, len(programming_language_list) - 1)]))(os.listdir(f'{self.module.path_to_module}/assets/programming_books')); picture_list=(lambda programming_lang: os.listdir(f"{self.module.path_to_module}/assets/programming_books/{programming_lang}"))(programming_lang); picture_name=(lambda picture_list : picture_list[random.randint(0, len(picture_list) - 1)])(picture_list); picture_path = f"{self.module.path_to_module}/assets/programming_books/{programming_lang}/{picture_name}"

            await send_msg(target_member, file=GoldyBot.nextcord.File(picture_path))

            await send_msg(ctx, f"💚 **{mention(author)} Book sent! They got ``{programming_lang}``.**")

def load():
    ProgrammingBooks(package_module=__name__)
