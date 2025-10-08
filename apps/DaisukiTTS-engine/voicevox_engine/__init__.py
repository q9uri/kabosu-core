"""AivisSpeech Engine"""

import os

__version__ = "latest"


# 環境変数 TRANSFORMERS_NO_ADVISORY_WARNINGS を設定して transformers の warning_advice() を無効化
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
