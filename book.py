import GoldyBot

class ProgrammingBook:
    def __init__(self, file_name:str, file:GoldyBot.WebFile, language:str) -> None:
        self.file_name = file_name
        self.file = file
        self.language = language