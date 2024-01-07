from requests import get as HttpGet
from json import dumps as DumpJSON
from typing import TypedDict, Literal

CLDR_ANNOTATIONS_URL = "https://raw.githubusercontent.com/unicode-org/cldr-json/main/cldr-json/cldr-annotations-full/annotations/en/annotations.json" # Source of keywords
EMOJI_LATEST_URL = "https://unpkg.com/emoji.json/emoji.json" # General Emoji Data, from https://www.npmjs.com/package/emoji.json

CLDR_ANNOTATIONS = HttpGet(CLDR_ANNOTATIONS_URL).json()["annotations"]["annotations"]
EMOJI_LATEST = HttpGet(EMOJI_LATEST_URL).json()

FINAL_FILE_PATH = "unicode-emoji.json"

EmojiListItem = TypedDict("emoji-list-item", { "codepoint": str, "name": str, "keywords": list[str] })
EmojiSubcategory = TypedDict("emoji-subcategory", { "category": str, "contents": list[EmojiListItem] })
EmojiCategory = TypedDict("emoji-category", { "category": str, "contents": list[EmojiSubcategory] })
EmojiRoot = TypedDict("emoji-root", { "comment": list[str], "category": Literal["root"], "contents": list[EmojiCategory] })

def GetCodepoint(emojiCodes: str) -> str:
    codes = emojiCodes.split(" ")
    codepoint = "U+" + " U+".join(codes)
    return codepoint

def JSONDumpsUTF8(Object: any, indent=4) -> bytes:
    return DumpJSON(Object, ensure_ascii=False, indent=indent).encode("utf-8")

def ParseEmojiList():
    InfoBuild: dict[str, dict[str, list[EmojiListItem]]] = {}
    for emoji in EMOJI_LATEST:
        if emoji["char"] not in CLDR_ANNOTATIONS:
            continue
        if emoji["group"] not in InfoBuild:
            InfoBuild[emoji["group"]] = {}
        if emoji["subgroup"] not in InfoBuild[emoji["group"]]:
            InfoBuild[emoji["group"]][emoji["subgroup"]] = []
        NewEmoji: EmojiListItem = {
            "codepoint": GetCodepoint(emoji["codes"]),
            "name": emoji["name"],
            "keywords": CLDR_ANNOTATIONS[emoji["char"]]["default"]
        }
        InfoBuild[emoji["group"]][emoji["subgroup"]].append(NewEmoji)
    FinalDisplay: EmojiRoot = {
        "comment": [
            "STOP!",

            "This is the official Emoji 15.0 list from Unicode,",
            "which can be found at https://unicode.org/emoji/charts/emoji-list.html",
            "It should never be changed unless the official list does,",
            "and even then, only if you know what you're doing.",

            "The list of images for Forumoji is kept in forumoji.json"
        ],
        "category": "root",
        "contents": []
    }
    for index, category in enumerate(InfoBuild.keys()):
        FinalDisplay["contents"].append({ "category": category, "contents": [] })
        for subcategory, contents in InfoBuild[category].items():
            FinalDisplay["contents"][index]["contents"].append({ "category": subcategory.replace("-", "_"), "contents": contents })
    DumpedJSON = JSONDumpsUTF8(FinalDisplay)
    with open(FINAL_FILE_PATH, "wb") as file:
        file.write(DumpedJSON)

if __name__ == "__main__":
    ParseEmojiList()