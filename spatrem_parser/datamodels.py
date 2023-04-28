from typing import Optional
from pydantic import BaseModel


class Translator(BaseModel):
    Surname_Name: str
    Pseudonyms: Optional[str]
    Year_Birth: str
    Year_Death: str
    Nationality: str
    Gender: str
    Journals: Optional[str]
    Notes: str


class Translation(BaseModel):
    Journal: str
    Year: str
    Issue_ID: str
    Vol: str
    No: str
    Listed_Translator: str
    Translator: str
    Author: str
    Title: str
    Genre: str
    SL: str
    TL: str
    Notes: str


# with open('../../data/KA_Translators.csv', mode='r', encoding='utf-8-sig') as csvfile:
#     reader: DictReader = DictReader(csvfile, delimiter=';')
#     translators: list = []
#     for row in reader:
#         translator = Translator(**row)
#         translators.append(translator)

# with open('../../data/KA_Translations.csv', mode='r', encoding='utf-8-sig') as csvfile:
#     reader: DictReader = DictReader(csvfile, delimiter=';')
#     translations: list = []
#     for row in reader:
#         translation = Translation(**row)
#         translations.append(translation)
