from pathlib import Path



ASSETS_DIR = Path(__file__).parent

JA_NLP_ASSETS_DIR = ASSETS_DIR / "ja/nlp"
MLASK_DIR = JA_NLP_ASSETS_DIR / "mlask"
OSETI_DIR = JA_NLP_ASSETS_DIR / "oseti"

JA_G2P_ASSETS_DIR = ASSETS_DIR / "ja/g2p"

YOMI_MODEL_DIR = JA_G2P_ASSETS_DIR / "pyopenjtalk/yomi_model"
ITAIJI_DIR = JA_G2P_ASSETS_DIR / "pyopenjtalk/itaiji"

MARINE_MODEL_DIR = str(JA_G2P_ASSETS_DIR / "marine/model")
MARINE_VOCAB_DIR = str(JA_G2P_ASSETS_DIR / "marine/dict")
YOMIKATA_MODEL_DIR = JA_G2P_ASSETS_DIR / "yomikata/dbert-artifacts"

VIBRATO_DICT_DIR = ASSETS_DIR / "multi/nlp/vibrato"
UNIDIC_LITE_PATH = VIBRATO_DICT_DIR / "unidic-mecab-2-1-2/system.dic.zst"
IPADIC_PATH = VIBRATO_DICT_DIR / "ipadic-mecab-2-7-0/system.dic.zst"
JUMANDIC_PATH = VIBRATO_DICT_DIR / "jumandic-mecab-7-0/system.dic.zst"
KO_DIC_PATH = VIBRATO_DICT_DIR / "ko-dic-mecab-2.1.1/system.dic.zst"

JAMO_DICT_DIR = ASSETS_DIR / "ko/g2p/jamo"
G2PK4_DICT_DIR = ASSETS_DIR / "ko/g2p/g2pk4"
NLTK_DIR = ASSETS_DIR / "en/g2p/nltk"