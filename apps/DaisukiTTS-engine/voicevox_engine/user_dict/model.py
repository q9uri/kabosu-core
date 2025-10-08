"""
ユーザー辞書機能に関して API と ENGINE 内部実装が共有するモデル（データ構造）

モデルの注意点は `voicevox_engine/model.py` の module docstring を確認すること。
"""

from __future__ import annotations

from re import findall, fullmatch
from typing import Annotated, Self

from jaconv import jaconv
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator
from pydantic.json_schema import SkipJsonSchema
from style_bert_vits2.nlp.japanese.normalizer import normalize_text

from voicevox_engine.user_dict.constants import (
    PART_OF_SPEECH_DATA,
    USER_DICT_MAX_PRIORITY,
    USER_DICT_MIN_PRIORITY,
    WordProperty,
    WordTypes,
)


def _check_newlines_and_null(text: str) -> str:
    if "\n" in text or "\r" in text:
        raise ValueError("ユーザー辞書データ内に改行が含まれています。")
    if "\x00" in text:
        raise ValueError("ユーザー辞書データ内にnull文字が含まれています。")
    return text


def _check_comma_and_double_quote(text: str) -> str:
    if "," in text:
        raise ValueError("ユーザー辞書データ内にカンマが含まれています。")
    if '"' in text:
        raise ValueError("ユーザー辞書データ内にダブルクォートが含まれています。")
    return text


def _convert_to_zenkaku(surface_or_stem: str) -> str:
    # 例外として、原型に "*" が指定されている場合は半角をそのまま保持する
    if surface_or_stem == "*":
        return surface_or_stem
    return surface_or_stem.translate(
        str.maketrans(
            "".join(chr(0x21 + i) for i in range(94)),
            "".join(chr(0xFF01 + i) for i in range(94)),
        )
    )


def _check_is_katakana(yomi_or_pronunciation: str) -> str:
    if not fullmatch(r"[ァ-ヴー]+", yomi_or_pronunciation):
        raise ValueError("発音は有効なカタカナでなくてはいけません。")
    sutegana = ["ァ", "ィ", "ゥ", "ェ", "ォ", "ャ", "ュ", "ョ", "ヮ", "ッ"]
    for i in range(len(yomi_or_pronunciation)):
        if yomi_or_pronunciation[i] in sutegana:
            # 「キャット」のように、捨て仮名が連続する可能性が考えられるので、
            # 「ッ」に関しては「ッ」そのものが連続している場合と、「ッ」の後にほかの捨て仮名が連続する場合のみ無効とする
            if i < len(yomi_or_pronunciation) - 1 and (
                yomi_or_pronunciation[i + 1] in sutegana[:-1]
                or (
                    yomi_or_pronunciation[i] == sutegana[-1]
                    and yomi_or_pronunciation[i + 1] == sutegana[-1]
                )
            ):
                raise ValueError("無効な発音です。(捨て仮名の連続)")
        if yomi_or_pronunciation[i] == "ヮ":
            if i != 0 and yomi_or_pronunciation[i - 1] not in ["ク", "グ"]:
                raise ValueError("無効な発音です。(「くゎ」「ぐゎ」以外の「ゎ」の使用)")
    return yomi_or_pronunciation


CsvSafeStr = Annotated[
    str,
    AfterValidator(_check_newlines_and_null),
    AfterValidator(_check_comma_and_double_quote),
]


class UserDictWord(BaseModel):
    """
    ユーザー辞書のビルドに必要な単語情報。

    単語登録・変更リクエストで受け取った単語情報のバリデーションと JSON への保存に用いる。
    """

    model_config = ConfigDict(validate_assignment=True)

    surface: Annotated[
        CsvSafeStr,
        AfterValidator(_convert_to_zenkaku),
    ] = Field(description="表層形")
    priority: int = Field(
        description="優先度", ge=USER_DICT_MIN_PRIORITY, le=USER_DICT_MAX_PRIORITY
    )
    context_id: int = Field(description="文脈 ID", default=1348)
    part_of_speech: CsvSafeStr = Field(description="品詞")
    part_of_speech_detail_1: CsvSafeStr = Field(description="品詞細分類1")
    part_of_speech_detail_2: CsvSafeStr = Field(description="品詞細分類2")
    part_of_speech_detail_3: CsvSafeStr = Field(description="品詞細分類3")
    word_type: WordTypes = Field(description="品詞種別", default=WordTypes.PROPER_NOUN)
    inflectional_type: CsvSafeStr = Field(description="活用型")
    inflectional_form: CsvSafeStr = Field(description="活用形")
    stem: list[
        Annotated[
            CsvSafeStr,
            AfterValidator(_convert_to_zenkaku),
        ]
    ] = Field(description="原形")
    yomi: list[Annotated[CsvSafeStr, AfterValidator(_check_is_katakana)]] = Field(
        description="読み"
    )
    pronunciation: list[Annotated[CsvSafeStr, AfterValidator(_check_is_katakana)]] = (
        Field(description="発音")
    )
    accent_type: list[int] = Field(description="アクセント型")
    mora_count: list[int] = Field(description="モーラ数", default=[])
    accent_associative_rule: CsvSafeStr = Field(description="アクセント結合規則")

    @model_validator(mode="after")
    def _compute_word_type(self) -> Self:
        # 品詞情報から WordTypes (品詞種別) を自動算出する
        # 品詞種別は品詞情報から自動算出できるため、外部からの入力値に頼るべきではない
        # このバリデーターの処理により、word_type には常に品詞情報に対応する WordTypes の値が設定される
        for word_type, part_of_speech_detail in PART_OF_SPEECH_DATA.items():
            if (
                self.part_of_speech == part_of_speech_detail.part_of_speech
                and self.part_of_speech_detail_1
                == part_of_speech_detail.part_of_speech_detail_1
                and self.part_of_speech_detail_2
                == part_of_speech_detail.part_of_speech_detail_2
                and self.part_of_speech_detail_3
                == part_of_speech_detail.part_of_speech_detail_3
            ):
                # 変更がある時のみセットしないと RecursionError が発生する
                if self.word_type != word_type:
                    self.word_type = word_type
                return self
        raise ValueError("不明な品詞です。")

    @model_validator(mode="after")
    def _check_mora_count_and_accent_type(self) -> Self:
        # モデル初期化時にセットされた値に関わらず、常にモーラ数を自動算出する
        # モーラ数は発音表記から自動算出できるため、外部からの入力値に頼るべきではない
        # このバリデーターの処理により、mora_count には常に1以上の要素を持つ list[int] が設定される
        generated_mora_count: list[int] = []
        # アクセント句ごとに発音表記からモーラ数を計算し、対応するインデックスのモーラ数リストに格納
        for pronunciation in self.pronunciation:
            rule_others = "[イ][ェ]|[ヴ][ャュョ]|[クグトド][ゥ]|[テデ][ィャュョ]|[デ][ェ]|[クグ][ヮ]"
            rule_line_i = "[キシチニヒミリギジヂビピ][ェャュョ]|[シ][ィ]"
            rule_line_u = (
                "[クツフヴグ][ァ]|[ウクスツフヴグズ][ィ]|[ウクツフヴグ][ェォ]|[フ][ュ]"
            )
            rule_one_mora = "[ァ-ヴー]"
            generated_mora_count.append(
                len(
                    findall(
                        f"(?:{rule_others}|{rule_line_i}|{rule_line_u}|{rule_one_mora})",
                        pronunciation,
                    )
                )
            )
        # 計算したモーラ数リストを設定
        # 変更がある時のみセットしないと RecursionError が発生する
        if sum(self.mora_count) != sum(generated_mora_count):
            self.mora_count = generated_mora_count

        # アクセント型とモーラ数の要素数が一致しない
        if len(self.accent_type) != len(self.mora_count):
            raise ValueError("アクセント型とモーラ数の要素数が一致しません。")

        # アクセント句ごとに、アクセント型とモーラ数の整合性が取れない場合はエラーとする
        # アクセント型を表す数値の最大値はモーラ数と一致する (0 は平板型を表す)
        for i in range(len(self.accent_type)):
            if not 0 <= self.accent_type[i] <= self.mora_count[i]:
                raise ValueError(
                    f"誤ったアクセント型です({self.accent_type[i]})。 expect: 0 <= accent_type <= {self.mora_count[i]}"
                )

        return self

    @staticmethod
    def from_word_property(word_property: WordProperty) -> UserDictWord:
        """WordProperty から UserDictWord を生成する。"""

        # surface, pronunciation, accent_type の長さが一致しない
        if not (
            len(word_property.surface)
            == len(word_property.pronunciation)
            == len(word_property.accent_type)
        ):
            raise UserDictInputError(
                "表層形・発音・アクセント型のリストの長さが一致しません。"
            )

        # surface のリスト要素数が空
        # この時点で他も同じ要素数だと確定しているので、pronunciation や accent_type の要素数チェックは不要
        if len(word_property.surface) == 0:
            raise UserDictInputError("表層形が空です。")

        # word_type が part_of_speech_data のキーに含まれていない
        if word_property.word_type not in PART_OF_SPEECH_DATA.keys():
            raise UserDictInputError("不明な品詞です。")

        # priority が 0 から 10 の範囲外
        if (
            not USER_DICT_MIN_PRIORITY
            <= word_property.priority
            <= USER_DICT_MAX_PRIORITY
        ):
            raise UserDictInputError("優先度の値が無効です。")

        # WordTypes に対応する品詞情報を取得
        pos_detail = PART_OF_SPEECH_DATA[word_property.word_type]

        # 「表層形」は一つの文字列に結合した上で、Style-Bert-VITS2 側の正規化処理を適用する（内部で自動的に半角化される）
        # 辞書を引くためのキーが表層形なので、正規化しておかないと単語によっては辞書登録しても引っかからないケースがある
        # 正規化後は基本英単語はカタカナ語に変換されるはずだが、英字が残っていた時のため、再度全角英数記号に戻す
        # (OpenJTalk の辞書は表層形が全角英数記号でないと引っかからない仕様)
        normalized_surface = jaconv.h2z(
            normalize_text("".join(word_property.surface)),
            kana=False,
            ascii=True,
            digit=True,
        )

        # ユーザー辞書のビルドに必要な単語情報を生成し、同時にバリデーションも行う
        # バリデーション処理は Pydantic によって行われる
        return UserDictWord(
            surface=normalized_surface,
            # 「左・右文脈 ID」は PART_OF_SPEECH_DATA から WordTypes に対応する定数を取得して設定
            context_id=pos_detail.context_id,
            # 「優先度」はユーザー辞書の優先度をそのまま設定
            priority=word_property.priority,
            # 「品詞」「品詞細分類1/2/3」は PART_OF_SPEECH_DATA から WordTypes に対応する定数を取得して設定
            part_of_speech=pos_detail.part_of_speech,
            part_of_speech_detail_1=pos_detail.part_of_speech_detail_1,
            part_of_speech_detail_2=pos_detail.part_of_speech_detail_2,
            part_of_speech_detail_3=pos_detail.part_of_speech_detail_3,
            # 「活用型」「活用形」は常に "*" 固定
            inflectional_type="*",
            inflectional_form="*",
            # 「原型」には表層形をリスト形式のまま保持し、アクセント句が複数ある場合は CSV 生成時に半角コロンで結合する
            stem=word_property.surface,
            # 「読み」には発音をリスト形式のまま保持し、アクセント句が複数ある場合は CSV 生成時に半角コロンで結合する
            yomi=word_property.pronunciation,
            # 「発音」には発音をリスト形式のまま保持し、アクセント句が複数ある場合は CSV 生成時に半角コロンで結合する
            pronunciation=word_property.pronunciation,
            # 「アクセント型」はアクセント位置をリスト形式のまま保持し、
            # アクセント句が複数ある場合は CSV 生成時にモーラ数と共に半角コロンで結合する
            accent_type=word_property.accent_type,
            # 「アクセント結合規則」は常に "*" 固定
            accent_associative_rule="*",
        )

    @staticmethod
    def from_user_dict_word_for_compat(
        user_dict_word_for_compat: UserDictWordForCompat,
    ) -> UserDictWord:
        """UserDictWordForCompat から UserDictWord を生成する。"""
        return UserDictWord(
            surface=user_dict_word_for_compat.surface,
            priority=user_dict_word_for_compat.priority,
            context_id=user_dict_word_for_compat.context_id,
            part_of_speech=user_dict_word_for_compat.part_of_speech,
            part_of_speech_detail_1=user_dict_word_for_compat.part_of_speech_detail_1,
            part_of_speech_detail_2=user_dict_word_for_compat.part_of_speech_detail_2,
            part_of_speech_detail_3=user_dict_word_for_compat.part_of_speech_detail_3,
            inflectional_type=user_dict_word_for_compat.inflectional_type,
            inflectional_form=user_dict_word_for_compat.inflectional_form,
            stem=[user_dict_word_for_compat.stem],
            yomi=[user_dict_word_for_compat.yomi],
            pronunciation=[user_dict_word_for_compat.pronunciation],
            accent_type=[user_dict_word_for_compat.accent_type],
            accent_associative_rule=user_dict_word_for_compat.accent_associative_rule,
        )


class UserDictWordForCompat(BaseModel):
    """
    UserDictWord とほとんど同じだが、ユーザー辞書関連 API の後方互換性を保つための互換レイヤー。

    stem, yomi, pronunciation, accent_type, mora_count はリストではなく文字列/数値で表す。
    既に UserDictWord にバリデーションが実装されていることから、重複するバリデーション定義は削られている。
    """

    model_config = ConfigDict(validate_assignment=True)

    surface: str = Field(description="表層形")
    priority: int = Field(
        description="優先度", ge=USER_DICT_MIN_PRIORITY, le=USER_DICT_MAX_PRIORITY
    )
    context_id: int = Field(description="文脈 ID", default=1348)
    part_of_speech: str = Field(description="品詞")
    part_of_speech_detail_1: str = Field(description="品詞細分類1")
    part_of_speech_detail_2: str = Field(description="品詞細分類2")
    part_of_speech_detail_3: str = Field(description="品詞細分類3")
    inflectional_type: str = Field(description="活用型")
    inflectional_form: str = Field(description="活用形")
    stem: str = Field(description="原形")
    yomi: str = Field(description="読み")
    pronunciation: str = Field(description="発音")
    accent_type: int = Field(description="アクセント型")
    mora_count: int | SkipJsonSchema[None] = Field(default=None, description="モーラ数")
    accent_associative_rule: str = Field(description="アクセント結合規則")

    @staticmethod
    def from_user_dict_word(user_dict_word: UserDictWord) -> UserDictWordForCompat:
        """UserDictWord から UserDictWordForCompat を生成する。"""
        return UserDictWordForCompat(
            surface=user_dict_word.surface,
            priority=user_dict_word.priority,
            context_id=user_dict_word.context_id,
            part_of_speech=user_dict_word.part_of_speech,
            part_of_speech_detail_1=user_dict_word.part_of_speech_detail_1,
            part_of_speech_detail_2=user_dict_word.part_of_speech_detail_2,
            part_of_speech_detail_3=user_dict_word.part_of_speech_detail_3,
            inflectional_type=user_dict_word.inflectional_type,
            inflectional_form=user_dict_word.inflectional_form,
            # アクセント句が複数ある単語では、苦肉の策で原形・読み・発音表記を結合し単一アクセント句にして返す
            # これにより本来の登録意図と齟齬が生じるが、API 互換性のためやむを得ない…
            stem="".join(user_dict_word.stem),
            yomi="".join(user_dict_word.yomi),
            pronunciation="".join(user_dict_word.pronunciation),
            # 最初のアクセント句のアクセント位置を採用
            accent_type=user_dict_word.accent_type[0],
            # アクセント句ごとに算出されているモーラ数を合計した値をセット
            mora_count=sum(user_dict_word.mora_count),
            accent_associative_rule=user_dict_word.accent_associative_rule,
        )


class UserDictInputError(Exception):
    """受け入れ不可能な入力値に起因するエラー"""

    pass
