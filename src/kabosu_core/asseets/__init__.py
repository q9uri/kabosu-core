import os
from pathlib import Path

ASSETS_PATH = Path( os.path.dirname(__file__) )
YOMIKATA_PATH = ASSETS_PATH / "yomikata"
MARINE_PATH =  ASSETS_PATH / "marine"
VIBRATO_DIR = ASSETS_PATH / "vibrato"

UNIDIC_LITE_DIR = VIBRATO_DIR / "unidic-mecab-2-1-2/system.dic.zst"
IPADIC_DIR = VIBRATO_DIR / "ipadic-mecab-2-7-0/system.dic.zst"
JUMANDIC_DIR = VIBRATO_DIR / "jumandic-mecab-7-0/system.dic.zst"
