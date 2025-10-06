from pathlib import Path



ASSETS_DIR = Path(__file__).parent

JA_NLP_ASSETS_DIR = ASSETS_DIR / "ja/nlp"
MLASK_DIR = JA_NLP_ASSETS_DIR / "mlask"

VIBRATO_DICT_DIR = ASSETS_DIR / "multi/nlp/vibrato"
UNIDIC_LITE_PATH = VIBRATO_DICT_DIR / "unidic-mecab-2-1-2/system.dic.zst"
IPADIC_PATH = VIBRATO_DICT_DIR / "ipadic-mecab-2-7-0/system.dic.zst"
JUMANDIC_PATH = VIBRATO_DICT_DIR / "jumandic-mecab-7-0/system.dic.zst"
KO_DIC_PATH = VIBRATO_DICT_DIR / "ko-dic-mecab-2.1.1/system.dic.zst"