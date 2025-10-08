"""ユーザー辞書機能を提供する API Router"""

from typing import Annotated, cast

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from pydantic import ValidationError

from voicevox_engine.user_dict.constants import (
    USER_DICT_MAX_PRIORITY,
    USER_DICT_MIN_PRIORITY,
    WordProperty,
    WordTypes,
)
from voicevox_engine.user_dict.model import (
    UserDictInputError,
    UserDictWord,
    UserDictWordForCompat,
)
from voicevox_engine.user_dict.user_dict_manager import UserDictionary

from ..dependencies import VerifyMutabilityAllowed


def generate_user_dict_router(
    user_dict: UserDictionary, verify_mutability: VerifyMutabilityAllowed
) -> APIRouter:
    """ユーザー辞書 API Router を生成する"""
    router = APIRouter(tags=["ユーザー辞書"])

    @router.get(
        "/user_dict",
        summary="ユーザー辞書に登録されている単語の一覧を取得する",
        response_description="ユーザー辞書に登録されている単語情報のリスト",
    )
    def get_user_dict_words(
        enable_compound_accent: Annotated[
            bool,
            Query(
                description=(
                    "複数のアクセント句を持つ単語の扱いを指定する<br>"
                    "false の場合は API 互換性のため、最初のアクセント句の情報のみを返します。<br>"
                    "未指定時は `false` が設定されます。"
                ),
            ),
        ] = False,
    ) -> dict[str, UserDictWord | UserDictWordForCompat]:
        """
        ユーザー辞書に登録されている単語の一覧を返します。<br>
        複合語アクセントのサポートを有効にするか次第で、返されるデータ型が変化します。<br>
        デフォルトでは、従来の API と互換性のある `UserDictWordForCompat` を返します。<br>
        `?enable_compound_accent=true` を指定すると、AivisSpeech Engine 1.1.0 以降で利用可能な `UserDictWord` を返します。
        """
        try:
            all_words = user_dict.get_all_words()
            if enable_compound_accent is True:
                # enable_compound_accent=True の時は UserDictWord をそのまま返す
                return cast(dict[str, UserDictWord | UserDictWordForCompat], all_words)
            else:
                # enable_compound_accent=False の時は UserDictWordForCompat に変換してから返す
                return {
                    word_uuid: UserDictWordForCompat.from_user_dict_word(user_dict_word)
                    for word_uuid, user_dict_word in all_words.items()
                }
        except UserDictInputError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="辞書の読み込みに失敗しました。"
            ) from e

    # TODO: CsvSafeStrを使う
    @router.post(
        "/user_dict_word",
        dependencies=[Depends(verify_mutability)],
        summary="ユーザー辞書に単語を追加する",
        response_description="追加した単語の UUID",
    )
    def add_user_dict_word(
        surface: Annotated[list[str], Query(description="単語の表層形")],
        pronunciation: Annotated[
            list[str], Query(description="単語の発音（カタカナ）")
        ],
        accent_type: Annotated[
            list[int],
            Query(
                description=(
                    "東京式アクセントにおけるアクセント型<br>"
                    "音高が下がる直前のモーラのインデックスを 1-indexed で指定します。0 は平板型を意味します。<br>"
                    '例として、`surface: ["新田", "真剣佑"], pronunciation: ["あらた", "まっけんゆう"]` のとき、`accent_type: [1, 3]` (新田 → 頭高型, 真剣佑 → 中高型) のように指定します。'
                ),
            ),
        ],
        word_type: Annotated[
            WordTypes,
            Query(
                description=(
                    "単語の品詞<br>"
                    "固有名詞 / 地名 / 組織・施設名 / 人名 / 人名 (姓) / 人名 (名) / 普通名詞 / 動詞 / 形容詞 / 語尾 のいずれかを指定します。<br>"
                    "未指定時は `固有名詞` が設定されます。"
                ),
            ),
        ] = WordTypes.PROPER_NOUN,
        priority: Annotated[
            int,
            Query(
                ge=USER_DICT_MIN_PRIORITY,
                le=USER_DICT_MAX_PRIORITY,
                description=(
                    "単語の優先度 (1~9 の範囲を推奨)<br>"
                    "数値が大きいほど、辞書適用時に優先して利用されます。<br>"
                    "未指定時は `5` が設定されます。"
                ),
            ),
        ] = 5,
    ) -> str:
        """
        ユーザー辞書に単語を追加します。<br>
        複合語を辞書に追加するには、`?surface=新田&surface=真剣佑&pronunciation=あらた&pronunciation=まっけんゆう&accent_type=1&accent_type=3` のように、`surface`, `pronunciation`, `accent_type` を同じ長さのリストで指定します。
        """
        try:
            word_uuid = user_dict.add_word(
                WordProperty(
                    surface=surface,
                    pronunciation=pronunciation,
                    accent_type=accent_type,
                    word_type=word_type,
                    priority=priority,
                )
            )
            return word_uuid
        except ValidationError as e:
            raise HTTPException(
                status_code=422, detail="パラメータに誤りがあります。\n" + str(e)
            ) from e
        except UserDictInputError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="ユーザー辞書への追加に失敗しました。"
            ) from e

    @router.put(
        "/user_dict_word/{word_uuid}",
        status_code=204,
        dependencies=[Depends(verify_mutability)],
        summary="ユーザー辞書に登録されている単語を更新する",
    )
    def update_user_dict_word(
        word_uuid: Annotated[str, Path(description="更新する単語の UUID")],
        surface: Annotated[list[str], Query(description="単語の表層形")],
        pronunciation: Annotated[
            list[str], Query(description="単語の発音（カタカナ）")
        ],
        accent_type: Annotated[
            list[int],
            Query(
                description=(
                    "東京式アクセントにおけるアクセント型<br>"
                    "音高が下がる直前のモーラのインデックスを 1-indexed で指定します。0 は平板型を意味します。<br>"
                    '例として、`surface: ["新田", "真剣佑"], pronunciation: ["あらた", "まっけんゆう"]` のとき、`accent_type: [1, 3]` (新田 → 頭高型, 真剣佑 → 中高型) のように指定します。'
                ),
            ),
        ],
        word_type: Annotated[
            WordTypes,
            Query(
                description=(
                    "単語の品詞<br>"
                    "固有名詞 / 地名 / 組織・施設名 / 人名 / 人名 (姓) / 人名 (名) / 普通名詞 / 動詞 / 形容詞 / 語尾 のいずれかを指定します。<br>"
                    "未指定時は `固有名詞` が設定されます。"
                ),
            ),
        ] = WordTypes.PROPER_NOUN,
        priority: Annotated[
            int,
            Query(
                ge=USER_DICT_MIN_PRIORITY,
                le=USER_DICT_MAX_PRIORITY,
                description=(
                    "単語の優先度 (1~9 の範囲を推奨)<br>"
                    "数値が大きいほど、辞書適用時に優先して利用されます。<br>"
                    "未指定時は `5` が設定されます。"
                ),
            ),
        ] = 5,
    ) -> None:
        """
        ユーザー辞書に登録されている単語を更新します。<br>
        複合語を辞書に追加するには、`?surface=新田&surface=真剣佑&pronunciation=あらた&pronunciation=まっけんゆう&accent_type=1&accent_type=3` のように、`surface`, `pronunciation`, `accent_type` を同じ長さのリストで指定します。
        """
        try:
            user_dict.update_word(
                word_uuid,
                WordProperty(
                    surface=surface,
                    pronunciation=pronunciation,
                    accent_type=accent_type,
                    word_type=word_type,
                    priority=priority,
                ),
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=422, detail="パラメータに誤りがあります。\n" + str(e)
            ) from e
        except UserDictInputError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="ユーザー辞書の更新に失敗しました。"
            ) from e

    @router.delete(
        "/user_dict_word/{word_uuid}",
        status_code=204,
        dependencies=[Depends(verify_mutability)],
        summary="ユーザー辞書に登録されている単語を削除する",
    )
    def delete_user_dict_word(
        word_uuid: Annotated[str, Path(description="削除する単語の UUID")],
    ) -> None:
        """
        ユーザー辞書に登録されている単語を削除します。
        """
        try:
            user_dict.delete_word(word_uuid=word_uuid)
        except UserDictInputError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="ユーザー辞書の更新に失敗しました。"
            ) from e

    @router.post(
        "/import_user_dict",
        status_code=204,
        dependencies=[Depends(verify_mutability)],
        summary="ユーザー辞書をインポートする",
    )
    def import_user_dict_words(
        import_dict_data: Annotated[
            dict[str, UserDictWord | UserDictWordForCompat],
            Body(description="インポートするユーザー辞書のデータ"),
        ],
        override: Annotated[
            bool, Query(description="重複したエントリがあった場合、上書きするかどうか")
        ],
    ) -> None:
        """
        指定されたユーザー辞書をインポートします。<br>
        従来の API と互換性のある `UserDictWordForCompat` と、AivisSpeech Engine 1.1.0 以降で利用可能な `UserDictWord` の両方の型に対応しています。<br>
        `?override=true` を指定すると、UUID が重複したエントリはインポートしたデータで上書きされます。
        """
        try:
            converted_import_dict_data: dict[str, UserDictWord] = {}
            for word_uuid, user_dict_word in import_dict_data.items():
                # UserDictWordForCompat であれば UserDictWord に変換
                if isinstance(user_dict_word, UserDictWordForCompat):
                    converted_import_dict_data[word_uuid] = (
                        UserDictWord.from_user_dict_word_for_compat(user_dict_word)
                    )
                else:
                    converted_import_dict_data[word_uuid] = user_dict_word
            user_dict.import_dictionary(
                dict_data=converted_import_dict_data, override=override
            )
        except UserDictInputError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="ユーザー辞書のインポートに失敗しました。"
            ) from e

    return router
