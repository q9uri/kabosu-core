from pathlib import Path

ASSETS_PATH = Path(__file__).parent




VIBRATO_DIR = ASSETS_PATH / "vibrato"

UNIDIC_LITE_DIR = VIBRATO_DIR / "unidic-mecab-2-1-2/system.dic.zst"
IPADIC_DIR = VIBRATO_DIR / "ipadic-mecab-2-7-0/system.dic.zst"
JUMANDIC_DIR = VIBRATO_DIR / "jumandic-mecab-7-0/system.dic.zst"
KO_DIC_DIR = VIBRATO_DIR / "ko-dic-mecab-2.1.1/system.dic.zst"

# Japanese

JA_NLP_ASSETS_DIR = ASSETS_PATH / "ja/nlp"

MLASK_DIR = JA_NLP_ASSETS_DIR / "mlask"
OSETI_DIR = JA_NLP_ASSETS_DIR / "oseti"

ASARI_MODEL_PATH = JA_NLP_ASSETS_DIR / "asari/pipeline.onnx"

ASAPY_JSON_DIR = JA_NLP_ASSETS_DIR / "asapy/json"
ASAPY_TSV_DIR = ASSETS_PATH / "asapy/tsv"

# japanese g2p
JA_G2P_ASSETS_DIR = ASSETS_PATH / "ja/g2p"

ITAIJI_DIR = JA_G2P_ASSETS_DIR / "pyopenjtalk/itaiji"
YOMI_MODEL_DIR = JA_G2P_ASSETS_DIR / "pyopenjtalk/yomi_model"

YOMIKATA_PATH = JA_G2P_ASSETS_DIR / "yomikata"
MARINE_PATH =  JA_G2P_ASSETS_DIR / "marine"

# korean
G2PK4_DICT_DIR = ASSETS_PATH / "g2pk4"

#english
EN_G2P_ASSETS_DIR = ASSETS_PATH / "en/g2p"

G2P_EN_DIR = EN_G2P_ASSETS_DIR / "g2p_en"
NLTK_DIR = EN_G2P_ASSETS_DIR / "nltk"