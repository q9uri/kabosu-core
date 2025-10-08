
from collections.abc import Sequence
from typing import Any

from kabosu_plus.sbv2.nlp import onnx_bert_models
from style_bert_vits2.constants import Languages

onnx_providers: Sequence[str | tuple[str, dict[str, Any]]] = [
            ("CPUExecutionProvider", {
                "arena_extend_strategy": "kSameAsRequested",
            }),
        ]  
BERT_MODEL_CACHE_DIR = "./resources/BertModelCaches"

def download():
    onnx_bert_models.load_model(
        language=Languages.ZH,
        pretrained_model_name_or_path="tsukumijima/chinese-roberta-wwm-ext-large-onnx",
        onnx_providers=onnx_providers,
        cache_dir=str(BERT_MODEL_CACHE_DIR),
        revision="d5bda299f34531204d510c3e0752b92635e9ee12",
    )
    onnx_bert_models.load_tokenizer(
        language=Languages.ZH,
        pretrained_model_name_or_path="tsukumijima/chinese-roberta-wwm-ext-large-onnx",
        cache_dir=str(BERT_MODEL_CACHE_DIR),
        revision="d5bda299f34531204d510c3e0752b92635e9ee12",
    )

    onnx_bert_models.load_model(
        language=Languages.EN,
        pretrained_model_name_or_path="tsukumijima/deberta-v3-large-onnx",
        onnx_providers=onnx_providers,
        cache_dir=str(BERT_MODEL_CACHE_DIR),
        revision="6ae8206c31b4305707346f5ca8d036b558dafe87",
    )

    onnx_bert_models.load_tokenizer(
        language=Languages.EN,
        pretrained_model_name_or_path="tsukumijima/deberta-v3-large-onnx",
        cache_dir=str(BERT_MODEL_CACHE_DIR),
        revision="6ae8206c31b4305707346f5ca8d036b558dafe87",
    )

    # load japanese bert model
    onnx_bert_models.load_model(
        language=Languages.JP,
        pretrained_model_name_or_path="tsukumijima/deberta-v2-large-japanese-char-wwm-onnx",
        onnx_providers=onnx_providers,
        cache_dir=str(BERT_MODEL_CACHE_DIR),
        revision="d701ec67708287b20d2063270f6b535e6eed09ab",
    )
    onnx_bert_models.load_tokenizer(
        language=Languages.JP,
        pretrained_model_name_or_path="tsukumijima/deberta-v2-large-japanese-char-wwm-onnx",
        cache_dir=str(BERT_MODEL_CACHE_DIR),
        revision="d701ec67708287b20d2063270f6b535e6eed09ab",
    )

if __name__ == "__main__":
    download()