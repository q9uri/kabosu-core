from pathlib import Path

ASSETS_PATH = Path(__file__).parent
YOMIKATA_PATH = ASSETS_PATH / "yomikata"
MARINE_PATH =  ASSETS_PATH / "marine"

MLASK_DIR = ASSETS_PATH / "mlask"
OSETI_DIR = ASSETS_PATH / "oseti"

ASARI_MODEL_PATH = ASSETS_PATH / "asari/pipeline.onnx"

ASAPY_JSON_DIR = ASSETS_PATH / "asapy/json"
ASAPY_TSV_DIR = ASSETS_PATH / "asapy/tsv"

VIBRATO_DIR = ASSETS_PATH / "vibrato"
UNIDIC_LITE_DIR = VIBRATO_DIR / "unidic-mecab-2-1-2/system.dic.zst"
IPADIC_DIR = VIBRATO_DIR / "ipadic-mecab-2-7-0/system.dic.zst"
JUMANDIC_DIR = VIBRATO_DIR / "jumandic-mecab-7-0/system.dic.zst"
