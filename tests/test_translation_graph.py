import pytest
from spatrem_parser.translations import (
    Translation,
    create_translation_graph,
    create_magazine_graph,
    create_publication_graph,
)

row: Translation = Translation(
    Journal="KA",
    Year="1946",
    Issue_ID="2",
    Vol="1",
    No="2",
    Listed_Translator="Wagenseil, Hans Beppo",
    Translator="Wagenseil, Hans Beppo",
    Author="Somerset Maugham, W.",
    Title="Louise",
    Genre="fictional prose",
    SL="EN-BE",
    TL="DE",
    Notes="Short story in collection: Cosmopolitans, 1936; B: Stimmen der Völker, Meisternovellen der Weltliteratur: England, tr. Wagenseil (Bavaria-Verlag: Gauting, 1947), here story illustrated by Claus Hansmann; Slight difference between tr. in KA und in short story collection; Slightly later competing translation by Mimi Zoff, Weltbürger (Zürich: Rascher, 1948)",
)

translation_graph = create_translation_graph(row)
magazine_graph = create_magazine_graph(row)
publication_graph = create_publication_graph(row)
