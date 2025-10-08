"""インストール済み音声合成モデルのスキャンとメタデータの取得、キャッシュの管理を行うリポジトリ"""

import asyncio
import glob
import hashlib
import sys
import threading
import time
from pathlib import Path
from typing import Final, Literal

import binascii
import aivmlib
import httpx
from aivmlib.schemas.aivm_manifest import ModelArchitecture
from pydantic import TypeAdapter
from semver.version import Version

from voicevox_engine.library.model import LibrarySpeaker
from voicevox_engine.logging import logger
from voicevox_engine.metas.Metas import (
    Speaker,
    SpeakerInfo,
    SpeakerStyle,
    SpeakerSupportedFeatures,
    StyleId,
    StyleInfo,
)
from voicevox_engine.model import AivmInfo
from voicevox_engine.utility.path_utility import get_save_dir
from voicevox_engine.utility.user_agent_utility import generate_user_agent

__all__ = ["AivmInfosRepository"]

AivmInfosCache = TypeAdapter(dict[str, AivmInfo])


class AivmInfosRepository:
    """
    インストール済み音声合成モデルのスキャンとメタデータの取得、キャッシュの管理を行うリポジトリ。

    エンジン起動時はキャッシュがあれば読み込み、バックグラウンドですべてのインストール済み音声合成モデルの情報を構築する。
    """

    # AivisHub API のベース URL
    AIVISHUB_API_BASE_URL: Final[str] = "https://api.aivis-project.com/v1"

    # AivisSpeech でサポートされているマニフェストバージョン
    SUPPORTED_MANIFEST_VERSIONS: Final[list[str]] = ["1.0"]

    # AivisSpeech でサポートされている音声合成モデルのアーキテクチャ
    SUPPORTED_MODEL_ARCHITECTURES: Final[list[ModelArchitecture]] = [
        ModelArchitecture.StyleBertVITS2,
        ModelArchitecture.StyleBertVITS2JPExtra,
    ]

    # エンジン起動の高速化に用いるキャッシュファイルの保存パス
    CACHE_FILE_PATH: Final[Path] = get_save_dir() / "aivm_infos_cache.json"

    def __init__(self, installed_models_dir: Path) -> None:
        """
        AivmInfosRepository のコンストラクタ

        Parameters
        ----------
        installed_models_dir : Path
            AIVMX ファイルのインストール先ディレクトリ
        """

        self.installed_models_dir = installed_models_dir
        self._lock = threading.Lock()

        # pytest から実行されているかどうか
        self._is_pytest = "pytest" in sys.argv[0] or "py.test" in sys.argv[0]

        # すべてのインストール済み音声合成モデルの情報を保持するマップ
        self._installed_aivm_infos: dict[str, AivmInfo] | None = None

        # コンストラクタ初期化時（＝エンジン起動時）、キャッシュがあればそこから即座に読み込む
        ## update_repository() は比較的実行コストが高い（モデル数が増えるほど時間がかかる）ため、
        ## 現在起動時に残したキャッシュを活用し、エンジンの起動を高速化する
        result = self._load_from_cache()
        if result is True:
            # キャッシュ情報が存在する際は、バックグラウンドでスキャンを開始
            def update_repository_in_background() -> None:
                # E2E テスト実行時に毎回スキャンするとあまりに時間がかかりすぎるため無効化
                if self._is_pytest:
                    return
                # BERT モデルのロードと並行させるため、少し待ってから実行
                ## aivmlib.read_aivmx_metadata() はモデルファイルをロードする関係で若干 CPU-bound だが、
                ## Python は GIL の制約により、CPU-bound な処理はマルチスレッドでもほとんど並列化できない
                ## そこで StyleBertVITS2TTSEngine 初期化時の BERT モデルのロードが GIL 外のネイティブコードで行われるのを活用し、
                ## GIL の制約を受けない BERT モデルのロードと並行させ、エンジン起動時間を短縮している
                time.sleep(1)
                try:
                    self.update_repository()
                except Exception as ex:
                    logger.error(
                        "Failed to update repository in background:", exc_info=ex
                    )

            threading.Thread(
                target=update_repository_in_background, daemon=True
            ).start()
        else:
            # キャッシュ情報が存在しない際はサーバー起動前に情報準備が必要なため、同期的にスキャンを行う
            self.update_repository()

        # この時点で確実に self._installed_aivm_infos が None でないことを保証する
        assert self._installed_aivm_infos is not None

    def get_installed_aivm_infos(self) -> dict[str, AivmInfo]:
        """
        すべてのインストール済み音声合成モデルの情報を取得する

        Returns
        -------
        aivm_infos : dict[str, AivmInfo]
            インストール済み音声合成モデルの情報 (キー: 音声合成モデルの UUID, 値: AivmInfo)
        """

        # コンストラクタ初期化時に確認した通り、この時点で self._installed_aivm_infos が None でないことを保証する
        assert self._installed_aivm_infos is not None
        return self._installed_aivm_infos

    def update_model_load_state(self, aivm_uuid: str, is_loaded: bool) -> None:
        """
        音声合成モデルのロード状態を更新する
        このメソッドは StyleBertVITS2TTSEngine 上でロード/アンロードが行われた際に呼び出される

        Parameters
        ----------
        aivm_uuid : str
            AIVM マニフェスト記載の UUID
        is_loaded : bool
            モデルがロードされているかどうか
        """

        if (
            self._installed_aivm_infos is not None
            and aivm_uuid in self._installed_aivm_infos
        ):
            self._installed_aivm_infos[aivm_uuid].is_loaded = is_loaded

    def update_repository(self) -> None:
        """
        すべてのインストール済み音声合成モデルから AIVM メタデータを取得し、内部状態を最新の情報に更新する。
        更新後の情報は次回起動時に利用するキャッシュにも反映される。
        """

        # ファイルシステムをスキャンして最新の音声合成モデルの情報を取得
        new_installed_aivm_infos = self._scan_models(self.installed_models_dir)

        # 情報の更新前に、現在保持されている既存のロード状態を新しい AivmInfo に移行する
        if self._installed_aivm_infos is not None:
            for aivm_uuid, aivm_info in new_installed_aivm_infos.items():
                if aivm_uuid in self._installed_aivm_infos:
                    aivm_info.is_loaded = self._installed_aivm_infos[aivm_uuid].is_loaded  # fmt: skip

        # 内部状態を更新
        self._installed_aivm_infos = new_installed_aivm_infos

        # AivisHub API からインストール済み音声合成モデルのアップデート情報を取得し、内部状態を更新
        try:
            self._installed_aivm_infos = asyncio.run(
                self._update_latest_version_info(self._installed_aivm_infos)
            )
        except Exception as ex:
            # AivisHub API からの情報取得に失敗しても起動に影響を与えないよう、ログ出力のみ行う
            logger.warning(
                "Failed to fetch update information. Continuing with cached model data:",
                exc_info=ex,
            )

        # 現在保持している情報をキャッシュに保存
        self._persist_to_cache()

    def _load_from_cache(self) -> bool:
        """
        キャッシュファイルからすべてのインストール済み音声合成モデルの情報を取得し、
        内部で保持している self._installed_aivm_infos に格納する。

        Returns
        -------
        bool
            キャッシュの読み込みに成功したかどうか
        """

        # キャッシュファイルが存在しない（初回起動時など）
        if not self.CACHE_FILE_PATH.exists():
            logger.info("Cache file not found, will load models directly.")
            return False

        with self._lock:
            try:
                # キャッシュファイルからインストール済みの音声合成モデルの情報を読み込む
                with open(self.CACHE_FILE_PATH, encoding="utf-8") as f:
                    result = AivmInfosCache.validate_json(f.read())
                # すべてのモデルのロード状態を False にする
                for aivm_info in result.values():
                    aivm_info.is_loaded = False
                self._installed_aivm_infos = result
                logger.info(
                    f"Loaded {len(self._installed_aivm_infos)} models from cache."
                )
                return True
            except Exception as ex:
                logger.warning("Failed to load cache file:", exc_info=ex)
                return False

    def _persist_to_cache(self) -> None:
        """
        内部で保持しているすべてのインストール済み音声合成モデルの情報を、キャッシュファイルに保存・反映する。
        """

        # まだインストール済みの音声合成モデルをスキャンし終わっていないため何も実行しない
        if self._installed_aivm_infos is None:
            return

        # 万が一保存先ディレクトリが存在しない場合は作成
        self.CACHE_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)

        with self._lock:
            try:
                # 一時ファイルに書き込んでから名前変更することで、
                # 書き込み中にクラッシュしてもキャッシュファイルが壊れないようにする
                temp_path = self.CACHE_FILE_PATH.with_suffix(".tmp")
                with open(temp_path, mode="w", encoding="utf-8") as f:
                    f.write(
                        AivmInfosCache.dump_json(
                            self._installed_aivm_infos, indent=4
                        ).decode("utf-8")
                    )
                # ファイル名を変更（既存のファイルは上書き）
                temp_path.replace(self.CACHE_FILE_PATH)
            except Exception as ex:
                logger.warning("Failed to save cache file:", exc_info=ex)

    @classmethod
    def _scan_models(cls, installed_models_dir: Path) -> dict[str, AivmInfo]:
        """
        指定されたディレクトリに保存されている *.aivmx ファイルを走査し、すべての音声合成モデルの情報を取得する。

        Parameters
        ----------
        installed_models_dir : Path
            AIVMX ファイルのインストール先ディレクトリ

        Returns
        -------
        dict[str, AivmInfo]
            スキャンで検出された、インストール済みのすべての音声合成モデルの情報
        """

        logger.info("Scanning installed models ...")
        start_time = time.time()

        # AIVMX ファイルのインストール先ディレクトリ内に配置されている .aivmx ファイルのパスを取得
        aivm_file_paths = glob.glob(str(installed_models_dir / "*.aivmx"))

        # 各 AIVMX ファイルごとに
        aivm_infos: dict[str, AivmInfo] = {}
        for aivm_file_path_str in aivm_file_paths:
            # 最低限のパスのバリデーション
            aivm_file_path = Path(aivm_file_path_str)
            if not aivm_file_path.exists():
                logger.warning(f"{aivm_file_path}: File not found. Skipping...")
                continue
            if not aivm_file_path.is_file():
                logger.warning(f"{aivm_file_path}: Not a file. Skipping...")
                continue

            # AIVM メタデータの読み込み
            try:
                with open(aivm_file_path, mode="rb") as f:
                    aivm_metadata = aivmlib.read_aivmx_metadata(f)
                    aivm_manifest = aivm_metadata.manifest
            except aivmlib.AivmValidationError as ex:
                logger.warning(
                    f"{aivm_file_path}: Failed to read AIVM metadata. Skipping...",
                    exc_info=ex,
                )
                continue

            # 音声合成モデルの UUID
            aivm_uuid = str(aivm_manifest.uuid)

            # すでに同一 UUID のファイルがインストール済みかどうかのチェック
            if aivm_uuid in aivm_infos:
                logger.info(
                    f"{aivm_file_path}: AIVM model {aivm_uuid} is already installed. Skipping..."
                )
                continue

            # マニフェストバージョンのバリデーション
            # バージョン文字列をメジャー・マイナーに分割
            manifest_version_parts = aivm_manifest.manifest_version.split(".")
            if len(manifest_version_parts) != 2:
                logger.warning(
                    f"{aivm_file_path}: Invalid AIVM manifest version format: {aivm_manifest.manifest_version} Skipping..."
                )
                continue
            # サポートされているマニフェストバージョンごとにチェック
            manifest_major, _ = map(int, manifest_version_parts)
            for supported_manifest_version in cls.SUPPORTED_MANIFEST_VERSIONS:
                # メジャーバージョンを取得
                supported_major = int(supported_manifest_version.split(".")[0])
                if manifest_major != supported_major:
                    # メジャーバージョンが AIVM マニフェストのものと異なる場合はスキップ
                    logger.warning(
                        f"{aivm_file_path}: AIVM manifest version {aivm_manifest.manifest_version} is not supported (different major version). Skipping..."
                    )
                    continue
                # 同じメジャーバージョンだが、より新しいマイナーバージョンの場合は警告を出して続行
                elif (
                    aivm_manifest.manifest_version
                    not in cls.SUPPORTED_MANIFEST_VERSIONS
                ):
                    logger.warning(
                        f"{aivm_file_path}: AIVM manifest version {aivm_manifest.manifest_version} is newer than supported versions. Trying to load anyway..."
                    )

            # 音声合成モデルのアーキテクチャがサポートされているかどうかのチェック
            if aivm_manifest.model_architecture not in cls.SUPPORTED_MODEL_ARCHITECTURES:  # fmt: skip
                logger.warning(
                    f"{aivm_file_path}: Model architecture {aivm_manifest.model_architecture} is not supported. Skipping..."
                )
                continue

            # 仮の AivmInfo モデルを作成
            aivm_info = AivmInfo(
                is_loaded=False,
                # 初期値として False を設定 (AivisHub から情報を取得できるまではアップデートなし扱い)
                is_update_available=False,
                # 初期値として True を設定 (AivisHub にモデルが公開されているか確認できるまでは Private 扱い)
                is_private_model=True,
                # 初期値として AIVM マニフェスト記載のバージョンを設定
                latest_version=aivm_manifest.version,
                # AIVMX ファイルのインストール先パス
                file_path=aivm_file_path,
                # AIVMX ファイルのインストールサイズ (バイト単位)
                file_size=aivm_file_path.stat().st_size,
                # AIVM マニフェスト
                manifest=aivm_manifest,
                # 話者情報は後で追加するため、空リストを渡す
                speakers=[],
            )

            # 話者情報を LibrarySpeaker に変換し、AivmInfo.speakers に追加
            for speaker_manifest in aivm_manifest.speakers:
                speaker_uuid = str(speaker_manifest.uuid)

                # AivisSpeech Engine は日本語のみをサポートするため、日本語をサポートしない話者は除外
                ## 念のため小文字に変換してから比較
                supported_langs = [
                    lang.lower() for lang in speaker_manifest.supported_languages
                ]
                if not any(lang in supported_langs for lang in ['ja', 'ja-jp']):  # fmt: skip
                    logger.warning(f"{aivm_file_path}: Speaker {speaker_uuid} does not support Japanese. Skipping...")  # fmt: skip
                    continue

                # 話者アイコンを Base64 文字列に変換
                speaker_icon = cls.extract_base64_from_data_url(speaker_manifest.icon)

                # スタイルごとのメタデータを取得
                speaker_styles: list[SpeakerStyle] = []
                style_infos: list[StyleInfo] = []
                for style_manifest in speaker_manifest.styles:
                    # AIVM マニフェスト内の話者スタイル ID を VOICEVOX ENGINE 互換の StyleId に変換
                    style_id_list = cls.local_style_id_to_style_id(style_manifest.local_id, speaker_uuid)  # fmt: skip

                    # SpeakerStyle の作成
                    style_name = style_manifest.name
                    for style_id in style_id_list:
                        styleid_bytes = style_id.to_bytes(4, "big", signed=True) #4byte
                        effect_style_id = styleid_bytes[0]
                        new_style_name = style_name

                        """
                        b"\x00", # effect == "native"
                        b"\x01", #effect == "native_echo"
                        b"\x02", #effect == "native_reverb"
                        b"\x03", #effect == "native_slow"
                        b"\x04", #effect == "native_white_noise"   

                        b"\x05", #effect == "native_dakuten"    
                        b"\x06", #effect == "native_dakuten_echo" 
                        b"\x07", #effect == "native_dakuten_reverb" 
                        b"\x08", #effect == "native_dakuten_slow"    
                        b"\x09", #effect == "native_dakuten_white_noise" 

                        b"\x0a", # effect == "native_babytalk" int 10
                        b"\x0b", #effect == "native_babytalk_echo" int 11
                        b"\x0c", #effect == "native_babytalk_reverb" int 12
                        b"\x0d", #effect == "native_babytalk_slow" int 13
                        b"\x0e", #effect == "native_babytalk_white_noise" int 14

                        b"\x0f", #effect == "kansai" int 15
                        b"\x10", #effect == "native_kansai_echo" int 16
                        b"\x11", #effect == "native_kansai_reverb" int 17
                        b"\x12", #effect == "native_kansai_slow" int 18
                        b"\x13", #effect == "native_kansai_white_noise" int19
                            
                        b"\x14", # effect == "native_kansai_dakuten" int20
                        b"\x15", #effect == "native_kansai_dakuten_echo" int21
                        b"\x16", #effect == "native_kansai_dakuten_reverb" int22
                        b"\x17", #effect == "native_kansai_dakuten_slow" int23
                        b"\x18", #effect == "native_kansai_dakuten_white_noise" int24

                        b"\x19", #effect == "native_kansai_babytalk" int25
                        b"\x1a", #effect == "native_kansai_babytalk_echo" int26
                        b"\x1b", #effect == "native_kansai_babytalk_reverb" int27
                        b"\x1c", #effect == "native_kansai_babytalk_kansai_slow" int28  
                        b"\x1d", #effect == "native_kansai_babytalk_white_noise" int29  

                        b"\x1e", # effect == "robot" int30  
                        b"\x1f", #effect == "robot_echo" int31  
                        b"\x20", #effect == "robot_reverb" int32  
                        b"\x21", #effect == "robot_slow" int33  
                        b"\x22", #effect == "robot_white_noise" int34   

                        b"\x23", #effect == "robot_dakuten" int35    
                        b"\x24", #effect == "robot_dakuten_echo" int36 
                        b"\x25", #effect == "robot_dakuten_reverb" int37
                        b"\x26", #effect == "robot_dakuten_slow" int38   
                        b"\x27", #effect == "robot_dakuten_white_noise" int39 

                        b"\x28", # effect == "robot_babytalk" int 40
                        b"\x29", #effect == "robot_babytalk_echo" int 41
                        b"\x2a", #effect == "robot_babytalk_reverb" int 42
                        b"\x2b", #effect == "robot_babytalk_slow" int 43
                        b"\x2d", #effect == "robot_babytalk_white_noise" int 44

                        b"\x2c", #effect == "robot_kansai" int 45
                        b"\x2e", #effect == "robot_kansai_echo" int 46
                        b"\x2f", #effect == "robot_kansai_reverb" int 47
                        b"\x30", #effect == "robot_kansai_slow" int 48
                        b"\x31", #effect == "robot_kansai_white_noise" int49
                            
                        b"\x32", # effect == "robot_kansai_dakuten" int50
                        b"\x33", #effect == "robot_kansai_dakuten_echo" int51
                        b"\x34", #effect == "robot_kansai_dakuten_reverb" int52
                        b"\x35", #effect == "robot_kansai_dakuten_slow" int53
                        b"\x36", #effect == "robot_kansai_dakuten_white_noise" int54

                        b"\x37", #effect == "robot_kansai_babytalk" int55
                        b"\x38", #effect == "robot_kansai_babytalk_echo" int56
                        b"\x39", #effect == "robot_kansai_babytalk_reverb" int57
                        b"\x3a", #effect == "robot_kansai_babytalk_kansai_slow" int58  
                        b"\x3b", #effect == "robot_kansai_babytalk_white_noise" int59    

                        b"\x3c", # effect == "vcdown" int60  
                        b"\x3d", #effect == "vcdown_echo" int61  
                        b"\x3e", #effect == "vcdown_reverb" int62  
                        b"\x3f", #effect == "vcdown_slow" int63  
                        b"\x40", #effect == "vcdown_white_noise" int64   

                        b"\x41", #effect == "vcdown_dakuten" int65    
                        b"\x42", #effect == "vcdown_dakuten_echo" int66 
                        b"\x43", #effect == "vcdown_dakuten_reverb" int67
                        b"\x44", #effect == "vcdown_dakuten_slow" int68   
                        b"\x45", #effect == "vcdown_dakuten_white_noise" int69 

                        b"\x46", # effect == "vcdown_babytalk" int 70
                        b"\x47", #effect == "vcdown_babytalk_echo" int 71
                        b"\x48", #effect == "vcdown_babytalk_reverb" int 72
                        b"\x49", #effect == "vcdown_babytalk_slow" int 73
                        b"\x4a", #effect == "vcdown_babytalk_white_noise" int 74

                        b"\x4b", #effect == "vcdown_kansai" int 75
                        b"\x4c", #effect == "vcdown_kansai_echo" int 76
                        b"\x4d", #effect == "vcdown_kansai_reverb" int 77
                        b"\x4e", #effect == "vcdown_kansai_slow" int 78
                        b"\x4f", #effect == "vcdown_kansai_white_noise" int79
                            
                        b"\x50", # effect == "vcdown_kansai_dakuten" int80
                        b"\x51", #effect == "vcdown_kansai_dakuten_echo" int81
                        b"\x52", #effect == "vcdown_kansai_dakuten_reverb" int82
                        b"\x53", #effect == "vcdown_kansai_dakuten_slow" int83
                        b"\x54", #effect == "vcdown_kansai_dakuten_white_noise" int84

                        b"\x55", #effect == "vcdown_kansai_babytalk" int85
                        b"\x56", #effect == "vcdown_kansai_babytalk_echo" int86
                        b"\x57", #effect == "vcdown_kansai_babytalk_reverb" int87
                        b"\x58", #effect == "vcdown_kansai_babytalk_kansai_slow" int88  
                        b"\x59", #effect == "vcdown_kansai_babytalk_white_noise" int89  

                        
                        b"\x3c", # effect == "vcdown" int60  
                        b"\x3d", #effect == "vcdown_echo" int61  
                        b"\x3e", #effect == "vcdown_reverb" int62  
                        b"\x3f", #effect == "vcdown_slow" int63  
                        b"\x40", #effect == "vcdown_white_noise" int64   

                        b"\x41", #effect == "vcdown_dakuten" int65    
                        b"\x42", #effect == "vcdown_dakuten_echo" int66 
                        b"\x43", #effect == "vcdown_dakuten_reverb" int67
                        b"\x44", #effect == "vcdown_dakuten_slow" int68   
                        b"\x45", #effect == "vcdown_dakuten_white_noise" int69 

                        b"\x46", # effect == "vcdown_babytalk" int 70
                        b"\x47", #effect == "vcdown_babytalk_echo" int 71
                        b"\x48", #effect == "vcdown_babytalk_reverb" int 72
                        b"\x49", #effect == "vcdown_babytalk_slow" int 73
                        b"\x4a", #effect == "vcdown_babytalk_white_noise" int 74

                        b"\x4b", #effect == "vcdown_kansai" int 75
                        b"\x4c", #effect == "vcdown_kansai_echo" int 76
                        b"\x4d", #effect == "vcdown_kansai_reverb" int 77
                        b"\x4e", #effect == "vcdown_kansai_slow" int 78
                        b"\x4f", #effect == "vcdown_kansai_white_noise" int79
                            
                        b"\x50", # effect == "vcdown_kansai_dakuten" int80
                        b"\x51", #effect == "vcdown_kansai_dakuten_echo" int81
                        b"\x52", #effect == "vcdown_kansai_dakuten_reverb" int82
                        b"\x53", #effect == "vcdown_kansai_dakuten_slow" int83
                        b"\x54", #effect == "vcdown_kansai_dakuten_white_noise" int84

                        b"\x55", #effect == "vcdown_kansai_babytalk" int85
                        b"\x56", #effect == "vcdown_kansai_babytalk_echo" int86
                        b"\x57", #effect == "vcdown_kansai_babytalk_reverb" int87
                        b"\x58", #effect == "vcdown_kansai_babytalk_kansai_slow" int88  
                        b"\x59", #effect == "vcdown_kansai_babytalk_white_noise" int89  

                        b"\x5a", # effect == "vcup" int90  
                        b"\x5b", #effect == "vcup_echo" int91  
                        b"\x5c", #effect == "vcup_reverb" int92  
                        b"\x5d", #effect == "vcup_slow" int93  
                        b"\x5e", #effect == "vcup_white_noise" int94   

                        b"\x5f", #effect == "vcup_dakuten" int95    
                        b"\x60", #effect == "vcup_dakuten_echo" int96 
                        b"\x61", #effect == "vcup_dakuten_reverb" int97
                        b"\x62", #effect == "vcup_dakuten_slow" int98   
                        b"\x63", #effect == "vcup_dakuten_white_noise" int99 

                        b"\x64", # effect == "vcup_babytalk" int 100
                        b"\x65", #effect == "vcup_babytalk_echo" int 101
                        b"\x66", #effect == "vcup_babytalk_reverb" int 102
                        b"\x67", #effect == "vcup_babytalk_slow" int 103
                        b"\x68", #effect == "vcup_babytalk_white_noise" int 104

                        b"\x69", #effect == "vcup_kansai" int 105
                        b"\x6a", #effect == "vcup_kansai_echo" int 106
                        b"\x6b", #effect == "vcup_kansai_reverb" int 107
                        b"\x6c", #effect == "vcup_kansai_slow" int 108
                        b"\x6d", #effect == "vcup_kansai_white_noise" int109
                            
                        b"\x6e", # effect == "vcup_kansai_dakuten" int110
                        b"\x6f", #effect == "vcup_kansai_dakuten_echo" int111
                        b"\x70", #effect == "vcup_kansai_dakuten_reverb" int112
                        b"\x71", #effect == "vcup_kansai_dakuten_slow" int113
                        b"\x72", #effect == "vcup_kansai_dakuten_white_noise" int114

                        b"\x73", #effect == "vcup_kansai_babytalk" int115
                        b"\x74", #effect == "vcup_kansai_babytalk_echo" int116
                        b"\x75", #effect == "vcup_kansai_babytalk_reverb" int117
                        b"\x76", #effect == "vcup_kansai_babytalk_kansai_slow" int118 
                        b"\x77", #effect == "vcup_kansai_babytalk_white_noise" int119  
                        """       
                        
                        if effect_style_id == 0:
                            new_style_name = style_name

                        elif effect_style_id == 1:
                            new_style_name = f"{style_name} (エコー)"

                        elif effect_style_id == 2:
                            new_style_name = f"{style_name} (リバーブ)"

                        elif effect_style_id == 3:
                            new_style_name = f"{style_name} (スロウモーション)"

                        elif effect_style_id == 4:
                            new_style_name = f"{style_name} (ホワイトノイズ)"

                        elif effect_style_id == 5:
                            new_style_name = f"{style_name} (濁音)"

                        elif effect_style_id == 6:
                            new_style_name = f"{style_name} (濁音, エコー)"

                        elif effect_style_id == 7:
                            new_style_name = f"{style_name} (濁音, リバーブ)"

                        elif effect_style_id == 8:
                            new_style_name = f"{style_name} (濁音, スロウモーション)"

                        elif effect_style_id == 9:
                            new_style_name = f"{style_name} (濁音, ホワイトノイズ)"

                        elif effect_style_id == 10:
                            new_style_name = f"{style_name} (赤ちゃん言葉)"

                        elif effect_style_id == 11:
                            new_style_name = f"{style_name} (赤ちゃん言葉, エコー)"

                        elif effect_style_id == 12:
                            new_style_name = f"{style_name} (赤ちゃん言葉, リバーブ)"

                        elif effect_style_id == 13:
                            new_style_name = f"{style_name} (赤ちゃん言葉, スロウモーション)"

                        elif effect_style_id == 14:
                            new_style_name = f"{style_name} (赤ちゃん言葉, ホワイトノイズ)"

                        elif effect_style_id == 15:
                            new_style_name = f"{style_name} (関西弁)"

                        elif effect_style_id == 16:
                            new_style_name = f"{style_name} (関西弁, エコー)"

                        elif effect_style_id == 17:
                            new_style_name = f"{style_name} (関西弁, リバーブ)"

                        elif effect_style_id == 18:
                            new_style_name = f"{style_name} (関西弁, スロウモーション)"

                        elif effect_style_id == 19:
                            new_style_name = f"{style_name} (関西弁, ホワイトノイズ)"

                        elif effect_style_id == 20:
                            new_style_name = f"{style_name} (関西弁, 濁音)"

                        elif effect_style_id == 21:
                            new_style_name = f"{style_name} (関西弁, 濁音, エコー)"

                        elif effect_style_id == 22:
                            new_style_name = f"{style_name} (関西弁, 濁音, リバーブ)"

                        elif effect_style_id == 23:
                            new_style_name = f"{style_name} (関西弁, 濁音, スロウモーション)"

                        elif effect_style_id == 24:
                            new_style_name = f"{style_name} (関西弁, 濁音, ホワイトノイズ)"

                        elif effect_style_id == 25:
                            new_style_name = f"{style_name} (関西弁, 赤ちゃん言葉)"

                        elif effect_style_id == 26:
                            new_style_name = f"{style_name} (関西弁, 赤ちゃん言葉, エコー)"

                        elif effect_style_id == 27:
                            new_style_name = f"{style_name} (関西弁, 赤ちゃん言葉, リバーブ)"

                        elif effect_style_id == 28:
                            new_style_name = f"{style_name} (関西弁, 赤ちゃん言葉, スロウモーション)"

                        elif effect_style_id == 29:
                            new_style_name = f"{style_name} (関西弁, 赤ちゃん言葉, ホワイトノイズ)"

                        elif effect_style_id == 30:
                            new_style_name = f"{style_name} (ロボ声)"

                        elif effect_style_id == 31:
                            new_style_name = f"{style_name} (ロボ声, エコー)"

                        elif effect_style_id == 32:
                            new_style_name = f"{style_name} (ロボ声, リバーブ)"

                        elif effect_style_id == 33:
                            new_style_name = f"{style_name} (ロボ声, スロウモーション)"

                        elif effect_style_id == 34:
                            new_style_name = f"{style_name} (ロボ声, ホワイトノイズ)"

                        elif effect_style_id == 35:
                            new_style_name = f"{style_name} (ロボ声, 濁音)"

                        elif effect_style_id == 36:
                            new_style_name = f"{style_name} (ロボ声, 濁音, エコー)"

                        elif effect_style_id == 37:
                            new_style_name = f"{style_name} (ロボ声, 濁音, リバーブ)"

                        elif effect_style_id == 38:
                            new_style_name = f"{style_name} (ロボ声, 濁音, スロウモーション)"

                        elif effect_style_id == 39:
                            new_style_name = f"{style_name} (ロボ声, 濁音, ホワイトノイズ)"

                        elif effect_style_id == 40:
                            new_style_name = f"{style_name} (ロボ声, 赤ちゃん言葉)"

                        elif effect_style_id == 41:
                            new_style_name = f"{style_name} (ロボ声, 赤ちゃん言葉, エコー)"

                        elif effect_style_id == 42:
                            new_style_name = f"{style_name} (ロボ声, 赤ちゃん言葉, リバーブ)"

                        elif effect_style_id == 43:
                            new_style_name = f"{style_name} (ロボ声, 赤ちゃん言葉, スロウモーション)"

                        elif effect_style_id == 44:
                            new_style_name = f"{style_name} (ロボ声, 赤ちゃん言葉, ホワイトノイズ)"

                        elif effect_style_id == 45:
                            new_style_name = f"{style_name} (ロボ声, 関西弁)"

                        elif effect_style_id == 46:
                            new_style_name = f"{style_name} (ロボ声, 関西弁, エコー)"

                        elif effect_style_id == 47:
                            new_style_name = f"{style_name} (ロボ声, 関西弁, リバーブ)"

                        elif effect_style_id == 48:
                            new_style_name = f"{style_name} (ロボ声, 関西弁, スロウモーション)"

                        elif effect_style_id == 49:
                            new_style_name = f"{style_name} (ロボ声, 関西弁, ホワイトノイズ)"

                        elif effect_style_id == 50:
                            new_style_name = f"{style_name} (ロボ声, 関西弁, 濁音)"

                        elif effect_style_id == 51:
                            new_style_name = f"{style_name} (ロボ声, 関西弁, 濁音, エコー)"

                        elif effect_style_id == 52:
                            new_style_name = f"{style_name} (ロボ声, 関西弁, 濁音, リバーブ)"

                        elif effect_style_id == 53:
                            new_style_name = f"{style_name} (ロボ声, 関西弁, 濁音, スロウモーション)"

                        elif effect_style_id == 54:
                            new_style_name = f"{style_name} (ロボ声, 関西弁, 濁音, ホワイトノイズ)"

                        elif effect_style_id == 55:
                            new_style_name = f"{style_name} (ロボ声, 関西弁, 赤ちゃん言葉)"

                        elif effect_style_id == 56:
                            new_style_name = f"{style_name} (ロボ声, 関西弁, 赤ちゃん言葉, エコー)"

                        elif effect_style_id == 57:
                            new_style_name = f"{style_name} (ロボ声, 関西弁, 赤ちゃん言葉, リバーブ)"

                        elif effect_style_id == 58:
                            new_style_name = f"{style_name} (ロボ声, 関西弁, 赤ちゃん言葉, スロウモーション)"

                        elif effect_style_id == 59:
                            new_style_name = f"{style_name} (ロボ声, 関西弁, 赤ちゃん言葉, ホワイトノイズ)"

                        elif effect_style_id == 60:
                            new_style_name = f"{style_name} (低音ボイチェン)"

                        elif effect_style_id == 61:
                            new_style_name = f"{style_name} (低音ボイチェン, エコー)"

                        elif effect_style_id == 62:
                            new_style_name = f"{style_name} (低音ボイチェン, リバーブ)"

                        elif effect_style_id == 63:
                            new_style_name = f"{style_name} (低音ボイチェン, スロウモーション)"

                        elif effect_style_id == 64:
                            new_style_name = f"{style_name} (低音ボイチェン, ホワイトノイズ)"

                        elif effect_style_id == 65:
                            new_style_name = f"{style_name} (低音ボイチェン, 濁音)"

                        elif effect_style_id == 66:
                            new_style_name = f"{style_name} (低音ボイチェン, 濁音, エコー)"

                        elif effect_style_id == 67:
                            new_style_name = f"{style_name} (低音ボイチェン, 濁音, リバーブ)"

                        elif effect_style_id == 68:
                            new_style_name = f"{style_name} (低音ボイチェン, 濁音, スロウモーション)"

                        elif effect_style_id == 69:
                            new_style_name = f"{style_name} (低音ボイチェン, 濁音, ホワイトノイズ)"

                        elif effect_style_id == 70:
                            new_style_name = f"{style_name} (低音ボイチェン, 赤ちゃん言葉)"

                        elif effect_style_id == 71:
                            new_style_name = f"{style_name} (低音ボイチェン, 赤ちゃん言葉, エコー)"

                        elif effect_style_id == 72:
                            new_style_name = f"{style_name} (低音ボイチェン, 赤ちゃん言葉, リバーブ)"

                        elif effect_style_id == 73:
                            new_style_name = f"{style_name} (低音ボイチェン, 赤ちゃん言葉, スロウモーション)"

                        elif effect_style_id == 74:
                            new_style_name = f"{style_name} (低音ボイチェン, 赤ちゃん言葉, ホワイトノイズ)"

                        elif effect_style_id == 75:
                            new_style_name = f"{style_name} (低音ボイチェン, 関西弁)"

                        elif effect_style_id == 76:
                            new_style_name = f"{style_name} (低音ボイチェン, 関西弁, エコー)"

                        elif effect_style_id == 77:
                            new_style_name = f"{style_name} (低音ボイチェン, 関西弁, リバーブ)"

                        elif effect_style_id == 78:
                            new_style_name = f"{style_name} (低音ボイチェン, 関西弁, スロウモーション)"

                        elif effect_style_id == 79:
                            new_style_name = f"{style_name} (低音ボイチェン, 関西弁, ホワイトノイズ)"

                        elif effect_style_id == 80:
                            new_style_name = f"{style_name} (低音ボイチェン, 関西弁, 濁音)"

                        elif effect_style_id == 81:
                            new_style_name = f"{style_name} (低音ボイチェン, 関西弁, 濁音, エコー)"

                        elif effect_style_id == 82:
                            new_style_name = f"{style_name} (低音ボイチェン, 関西弁, 濁音, リバーブ)"

                        elif effect_style_id == 83:
                            new_style_name = f"{style_name} (低音ボイチェン, 関西弁, 濁音, スロウモーション)"

                        elif effect_style_id == 84:
                            new_style_name = f"{style_name} (低音ボイチェン, 関西弁, 濁音, ホワイトノイズ)"

                        elif effect_style_id == 85:
                            new_style_name = f"{style_name} (低音ボイチェン, 関西弁, 赤ちゃん言葉)"

                        elif effect_style_id == 86:
                            new_style_name = f"{style_name} (低音ボイチェン, 関西弁, 赤ちゃん言葉, エコー)"

                        elif effect_style_id == 87:
                            new_style_name = f"{style_name} (低音ボイチェン, 関西弁, 赤ちゃん言葉, リバーブ)"

                        elif effect_style_id == 88:
                            new_style_name = f"{style_name} (低音ボイチェン, 関西弁, 赤ちゃん言葉, スロウモーション)"

                        elif effect_style_id == 89:
                            new_style_name = f"{style_name} (低音ボイチェン, 関西弁, 赤ちゃん言葉, ホワイトノイズ)"

                        elif effect_style_id == 90:
                            new_style_name = f"{style_name} (高音ボイチェン)"

                        elif effect_style_id == 91:
                            new_style_name = f"{style_name} (高音ボイチェン, エコー)"

                        elif effect_style_id == 92:
                            new_style_name = f"{style_name} (高音ボイチェン, リバーブ)"

                        elif effect_style_id == 93:
                            new_style_name = f"{style_name} (高音ボイチェン, スロウモーション)"

                        elif effect_style_id == 94:
                            new_style_name = f"{style_name} (高音ボイチェン, ホワイトノイズ)"

                        elif effect_style_id == 95:
                            new_style_name = f"{style_name} (高音ボイチェン, 濁音)"

                        elif effect_style_id == 96:
                            new_style_name = f"{style_name} (高音ボイチェン, 濁音, エコー)"

                        elif effect_style_id == 97:
                            new_style_name = f"{style_name} (高音ボイチェン, 濁音, リバーブ)"

                        elif effect_style_id == 98:
                            new_style_name = f"{style_name} (高音ボイチェン, 濁音, スロウモーション)"

                        elif effect_style_id == 99:
                            new_style_name = f"{style_name} (高音ボイチェン, 濁音, ホワイトノイズ)"

                        elif effect_style_id == 100:
                            new_style_name = f"{style_name} (高音ボイチェン, 赤ちゃん言葉)"

                        elif effect_style_id == 101:
                            new_style_name = f"{style_name} (高音ボイチェン, 赤ちゃん言葉, エコー)"

                        elif effect_style_id == 102:
                            new_style_name = f"{style_name} (高音ボイチェン, 赤ちゃん言葉, リバーブ)"

                        elif effect_style_id == 103:
                            new_style_name = f"{style_name} (高音ボイチェン, 赤ちゃん言葉, スロウモーション)"

                        elif effect_style_id == 104:
                            new_style_name = f"{style_name} (高音ボイチェン, 赤ちゃん言葉, ホワイトノイズ)"

                        elif effect_style_id == 105:
                            new_style_name = f"{style_name} (高音ボイチェン, 関西弁)"

                        elif effect_style_id == 106:
                            new_style_name = f"{style_name} (高音ボイチェン, 関西弁, エコー)"

                        elif effect_style_id == 107:
                            new_style_name = f"{style_name} (高音ボイチェン, 関西弁, リバーブ)"

                        elif effect_style_id == 108:
                            new_style_name = f"{style_name} (高音ボイチェン, 関西弁, スロウモーション)"

                        elif effect_style_id == 109:
                            new_style_name = f"{style_name} (高音ボイチェン, 関西弁, ホワイトノイズ)"

                        elif effect_style_id == 110:
                            new_style_name = f"{style_name} (高音ボイチェン, 関西弁, 濁音)"

                        elif effect_style_id == 111:
                            new_style_name = f"{style_name} (高音ボイチェン, 関西弁, 濁音, エコー)"

                        elif effect_style_id == 112:
                            new_style_name = f"{style_name} (高音ボイチェン, 関西弁, 濁音, リバーブ)"

                        elif effect_style_id == 113:
                            new_style_name = f"{style_name} (高音ボイチェン, 関西弁, 濁音, スロウモーション)"

                        elif effect_style_id == 114:
                            new_style_name = f"{style_name} (高音ボイチェン, 関西弁, 濁音, ホワイトノイズ)"

                        elif effect_style_id == 115:
                            new_style_name = f"{style_name} (高音ボイチェン, 関西弁, 赤ちゃん言葉)"

                        elif effect_style_id == 116:
                            new_style_name = f"{style_name} (高音ボイチェン, 関西弁, 赤ちゃん言葉, エコー)"

                        elif effect_style_id == 117:
                            new_style_name = f"{style_name} (高音ボイチェン, 関西弁, 赤ちゃん言葉, リバーブ)"

                        elif effect_style_id == 118:
                            new_style_name = f"{style_name} (高音ボイチェン, 関西弁, 赤ちゃん言葉, スロウモーション)"

                        elif effect_style_id == 119:
                            new_style_name = f"{style_name} (高音ボイチェン, 関西弁, 赤ちゃん言葉, ホワイトノイズ)"

                        speaker_style = SpeakerStyle(
                            # VOICEVOX ENGINE 互換のスタイル ID
                            id=style_id,
                            # スタイル名
                            name=new_style_name,
                            # AivisSpeech は歌唱音声合成に対応しないので talk で固定
                            type="talk",
                        )
                        speaker_styles.append(speaker_style)

                        # StyleInfo の作成
                        style_info = StyleInfo(
                            # VOICEVOX ENGINE 互換のスタイル ID
                            id=style_id,
                            # アイコン画像
                            ## 未指定時は話者のアイコン画像がスタイルのアイコン画像として使われる
                            icon=cls.extract_base64_from_data_url(style_manifest.icon) if style_manifest.icon else speaker_icon,
                            # 立ち絵を省略
                            ## VOICEVOX ENGINE 本家では portrait に立ち絵が入るが、AivisSpeech Engine では敢えてアイコン画像のみを設定する
                            portrait=None,
                            # ボイスサンプル
                            voice_samples=[
                                cls.extract_base64_from_data_url(sample.audio)
                                for sample in style_manifest.voice_samples
                            ],
                            # 書き起こしテキスト
                            voice_sample_transcripts=[
                                sample.transcript
                                for sample in style_manifest.voice_samples
                            ],
                        )  # fmt: skip
                        style_infos.append(style_info)

                # LibrarySpeaker の作成
                ## 事前に取得・生成した SpeakerStyle / StyleInfo をそれぞれ Speaker / SpeakerInfo に設定する
                aivm_info_speaker = LibrarySpeaker(
                    # 話者情報
                    speaker=Speaker(
                        # 話者 UUID
                        speaker_uuid=speaker_uuid,
                        # 話者名
                        name=speaker_manifest.name,
                        # 話者のバージョン
                        ## 音声合成モデルのバージョンを話者のバージョンとして設定する
                        version=aivm_manifest.version,
                        # AivisSpeech Engine では全話者に対し常にモーフィング機能を無効化する
                        ## Style-Bert-VITS2 の仕様上音素長を一定にできず、話者ごとに発話タイミングがずれてまともに合成できないため
                        supported_features=SpeakerSupportedFeatures(
                            permitted_synthesis_morphing="NOTHING",
                        ),
                        # 話者スタイル情報
                        styles=speaker_styles,
                    ),
                    # 追加の話者情報
                    speaker_info=SpeakerInfo(
                        # ライセンス (Markdown またはプレーンテキスト)
                        ## 同一 AIVM / AIVMX ファイル内のすべての話者は同一のライセンスを持つ
                        policy=aivm_manifest.license if aivm_manifest.license else "",
                        # アイコン画像
                        ## VOICEVOX ENGINE 本家では portrait に立ち絵が入るが、AivisSpeech Engine では敢えてアイコン画像を設定する
                        portrait=speaker_icon,
                        # 追加の話者スタイル情報
                        style_infos=style_infos,
                    ),
                )  # fmt: skip
                aivm_info.speakers.append(aivm_info_speaker)

            # 完成した AivmInfo を UUID をキーとして追加
            aivm_infos[aivm_uuid] = aivm_info

        # 音声合成モデル名でソートしてから返す
        sorted_aivm_infos = dict(sorted(aivm_infos.items(), key=lambda x: x[1].manifest.name))  # fmt: skip
        logger.info(
            f"Scanned {len(sorted_aivm_infos)} installed models. ({time.time() - start_time:.2f}s)"
        )

        return sorted_aivm_infos

    @classmethod
    async def _update_latest_version_info(
        cls, aivm_infos: dict[str, AivmInfo]
    ) -> dict[str, AivmInfo]:
        """
        指定された音声合成モデルのアップデート情報を取得し、AivmInfo の latest_version と is_update_available を更新した上で返す。
        音声合成モデルごとに並行して HTTP API を叩くことで高速化を図っている（このため非同期メソッドとして実装している）。

        Parameters
        ----------
        aivm_infos : dict[str, AivmInfo]
            スキャンで検出された、インストール済みのすべての音声合成モデルの情報

        Returns
        -------
        dict[str, AivmInfo]
            AivisHub 上のアップデート情報が反映された、インストール済みのすべての音声合成モデルの情報
        """

        async def fetch_latest_version(aivm_info: AivmInfo) -> None:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{cls.AIVISHUB_API_BASE_URL}/aivm-models/{aivm_info.manifest.uuid}",
                        headers={"User-Agent": generate_user_agent()},
                        timeout=5.0,  # 5秒でタイムアウト
                    )

                    # 404 の場合は AivisHub に公開されていないモデルのためスキップ
                    if response.status_code == 404:
                        return

                    # 200 以外のステータスコードは異常なのでエラーとして処理
                    if response.status_code != 200:
                        logger.warning(
                            f"Failed to fetch model info for {aivm_info.manifest.uuid} from AivisHub (HTTP Error {response.status_code})."
                        )
                        logger.warning(f"Response: {response.text}")
                        return

                    model_info = response.json()

                    # model_files から最新の AIVMX ファイルのバージョンを取得
                    latest_aivmx_version = next(
                        (
                            file
                            for file in model_info["model_files"]
                            if file["model_type"] == "AIVMX"
                        ),
                        None,
                    )

                    if latest_aivmx_version is not None:
                        # latest_version を更新
                        aivm_info.latest_version = latest_aivmx_version["version"]
                        # バージョン比較を行い is_update_available を更新
                        current_version = Version.parse(aivm_info.manifest.version)
                        latest_version = Version.parse(aivm_info.latest_version)
                        aivm_info.is_update_available = latest_version > current_version

                        # AivisHub に情報が存在するため、プライベートモデルではない
                        aivm_info.is_private_model = False

            except httpx.TimeoutException:
                logger.warning(
                    f"Timeout while fetching model info for {aivm_info.manifest.uuid} from AivisHub."
                )
            except Exception as ex:
                # エラーが発生しても起動に影響を与えないよう、ログ出力のみ行う
                # - httpx.RequestError: ネットワークエラーなど
                # - KeyError: レスポンスの JSON に必要なキーが存在しない
                # - StopIteration: model_files に AIVMX が存在しない
                # - ValueError: Version.parse() が失敗
                logger.warning(
                    f"Failed to fetch model info for {aivm_info.manifest.uuid} from AivisHub:",
                    exc_info=ex,
                )

        # 全モデルの更新タスクを作成
        update_tasks = [
            fetch_latest_version(aivm_info) for aivm_info in aivm_infos.values()
        ]

        # 全タスクを同時に実行
        await asyncio.gather(*update_tasks, return_exceptions=True)
        logger.info("Updated latest version information.")

        # 新バージョンの更新がある場合はログに出力
        update_available_models = [
            aivm_info
            for aivm_info in aivm_infos.values()
            if aivm_info.is_update_available
        ]
        if len(update_available_models) > 0:
            logger.info(f"Update available {len(update_available_models)} models:")
            for aivm_info in update_available_models:
                logger.info(
                    f"- {aivm_info.manifest.name} ({aivm_info.manifest.uuid}) v{aivm_info.manifest.version} -> v{aivm_info.latest_version}"
                )

        return aivm_infos

    @staticmethod
    def extract_base64_from_data_url(data_url: str) -> str:
        """
        指定された Data URL から Base64 部分のみを取り出す

        Parameters
        ----------
        data_url : str
            Data URL

        Returns
        -------
        base64 : str
            Base64 部分
        """

        # バリデーション
        if not data_url:
            raise ValueError("Data URL is empty.")
        if not data_url.startswith("data:"):
            raise ValueError("Invalid data URL format.")

        # Data URL のプレフィックスを除去して、カンマの後の Base64 エンコードされた部分を取得
        if "," in data_url:
            base64_part = data_url.split(",", 1)[1]
        else:
            raise ValueError("Invalid data URL format.")
        return base64_part

    @staticmethod
    def local_style_id_to_style_id(local_style_id: int, speaker_uuid: str) -> list[StyleId]:
        """
        AIVM マニフェスト内のローカルなスタイル ID を VOICEVOX ENGINE 互換のグローバルに一意な StyleId に変換する

        Parameters
        ----------
        local_style_id : int
            AIVM マニフェスト内のローカルなスタイル ID
        speaker_uuid : str
            話者の UUID (aivm_manifest.json に記載されているものと同一)

        Returns
        -------
        style_id : StyleId
            VOICEVOX ENGINE 互換のグローバルに一意なスタイル ID
        """

        if not speaker_uuid:
            raise ValueError("speaker_uuid must be a non-empty string")
        if not (0 <= local_style_id <= 15):
            raise ValueError("local_style_id must be an integer between 0 and 31")


        # UUID をハッシュ化する
        uuid_hash = binascii.crc32(speaker_uuid.encode(), 0)
        uuid_bytes = uuid_hash.to_bytes(4, "big", signed=False) #4byte

        
        
        effect_id = [
                        b"\x00", # effect == "native"
                        b"\x01", #effect == "native_echo"
                        b"\x02", #effect == "native_reverb"
                        b"\x03", #effect == "native_slow"
                        b"\x04", #effect == "native_white_noise"   

                        b"\x05", #effect == "native_dakuten"    
                        b"\x06", #effect == "native_dakuten_echo" 
                        b"\x07", #effect == "native_dakuten_reverb" 
                        b"\x08", #effect == "native_dakuten_slow"    
                        b"\x09", #effect == "native_dakuten_white_noise" 

                        b"\x0a", # effect == "native_babytalk" int 10
                        b"\x0b", #effect == "native_babytalk_echo" int 11
                        b"\x0c", #effect == "native_babytalk_reverb" int 12
                        b"\x0d", #effect == "native_babytalk_slow" int 13
                        b"\x0e", #effect == "native_babytalk_white_noise" int 14

                        b"\x0f", #effect == "kansai" int 15
                        b"\x10", #effect == "native_kansai_echo" int 16
                        b"\x11", #effect == "native_kansai_reverb" int 17
                        b"\x12", #effect == "native_kansai_slow" int 18
                        b"\x13", #effect == "native_kansai_white_noise" int19
                            
                        b"\x14", # effect == "native_kansai_dakuten" int20
                        b"\x15", #effect == "native_kansai_dakuten_echo" int21
                        b"\x16", #effect == "native_kansai_dakuten_reverb" int22
                        b"\x17", #effect == "native_kansai_dakuten_slow" int23
                        b"\x18", #effect == "native_kansai_dakuten_white_noise" int24

                        b"\x19", #effect == "native_kansai_babytalk" int25
                        b"\x1a", #effect == "native_kansai_babytalk_echo" int26
                        b"\x1b", #effect == "native_kansai_babytalk_reverb" int27
                        b"\x1c", #effect == "native_kansai_babytalk_slow" int28  
                        b"\x1d", #effect == "native_kansai_babytalk_white_noise" int29  

                        b"\x1e", # effect == "robot" int30  
                        b"\x1f", #effect == "robot_echo" int31  
                        b"\x20", #effect == "robot_reverb" int32  
                        b"\x21", #effect == "robot_slow" int33  
                        b"\x22", #effect == "robot_white_noise" int34   

                        b"\x23", #effect == "robot_dakuten" int35    
                        b"\x24", #effect == "robot_dakuten_echo" int36 
                        b"\x25", #effect == "robot_dakuten_reverb" int37
                        b"\x26", #effect == "robot_dakuten_slow" int38   
                        b"\x27", #effect == "robot_dakuten_white_noise" int39 

                        b"\x28", # effect == "robot_babytalk" int 40
                        b"\x29", #effect == "robot_babytalk_echo" int 41
                        b"\x2a", #effect == "robot_babytalk_reverb" int 42
                        b"\x2b", #effect == "robot_babytalk_slow" int 43
                        b"\x2d", #effect == "robot_babytalk_white_noise" int 44

                        b"\x2c", #effect == "robot_kansai" int 45
                        b"\x2e", #effect == "robot_kansai_echo" int 46
                        b"\x2f", #effect == "robot_kansai_reverb" int 47
                        b"\x30", #effect == "robot_kansai_slow" int 48
                        b"\x31", #effect == "robot_kansai_white_noise" int49
                            
                        b"\x32", # effect == "robot_kansai_dakuten" int50
                        b"\x33", #effect == "robot_kansai_dakuten_echo" int51
                        b"\x34", #effect == "robot_kansai_dakuten_reverb" int52
                        b"\x35", #effect == "robot_kansai_dakuten_slow" int53
                        b"\x36", #effect == "robot_kansai_dakuten_white_noise" int54

                        b"\x37", #effect == "robot_kansai_babytalk" int55
                        b"\x38", #effect == "robot_kansai_babytalk_echo" int56
                        b"\x39", #effect == "robot_kansai_babytalk_reverb" int57
                        b"\x3a", #effect == "robot_kansai_babytalk_kansai_slow" int58  
                        b"\x3b", #effect == "robot_kansai_babytalk_white_noise" int59  

                        b"\x3c", # effect == "vcdown" int60  
                        b"\x3d", #effect == "vcdown_echo" int61  
                        b"\x3e", #effect == "vcdown_reverb" int62  
                        b"\x3f", #effect == "vcdown_slow" int63  
                        b"\x40", #effect == "vcdown_white_noise" int64   

                        b"\x41", #effect == "vcdown_dakuten" int65    
                        b"\x42", #effect == "vcdown_dakuten_echo" int66 
                        b"\x43", #effect == "vcdown_dakuten_reverb" int67
                        b"\x44", #effect == "vcdown_dakuten_slow" int68   
                        b"\x45", #effect == "vcdown_dakuten_white_noise" int69 

                        b"\x46", # effect == "vcdown_babytalk" int 70
                        b"\x47", #effect == "vcdown_babytalk_echo" int 71
                        b"\x48", #effect == "vcdown_babytalk_reverb" int 72
                        b"\x49", #effect == "vcdown_babytalk_slow" int 73
                        b"\x4a", #effect == "vcdown_babytalk_white_noise" int 74

                        b"\x4b", #effect == "vcdown_kansai" int 75
                        b"\x4c", #effect == "vcdown_kansai_echo" int 76
                        b"\x4d", #effect == "vcdown_kansai_reverb" int 77
                        b"\x4e", #effect == "vcdown_kansai_slow" int 78
                        b"\x4f", #effect == "vcdown_kansai_white_noise" int79
                            
                        b"\x50", # effect == "vcdown_kansai_dakuten" int80
                        b"\x51", #effect == "vcdown_kansai_dakuten_echo" int81
                        b"\x52", #effect == "vcdown_kansai_dakuten_reverb" int82
                        b"\x53", #effect == "vcdown_kansai_dakuten_slow" int83
                        b"\x54", #effect == "vcdown_kansai_dakuten_white_noise" int84

                        b"\x55", #effect == "vcdown_kansai_babytalk" int85
                        b"\x56", #effect == "vcdown_kansai_babytalk_echo" int86
                        b"\x57", #effect == "vcdown_kansai_babytalk_reverb" int87
                        b"\x58", #effect == "vcdown_kansai_babytalk_kansai_slow" int88  
                        b"\x59", #effect == "vcdown_kansai_babytalk_white_noise" int89  

                        b"\x5a", # effect == "vcup" int90  
                        b"\x5b", #effect == "vcup_echo" int91  
                        b"\x5c", #effect == "vcup_reverb" int92  
                        b"\x5d", #effect == "vcup_slow" int93  
                        b"\x5e", #effect == "vcup_white_noise" int94   

                        b"\x5f", #effect == "vcup_dakuten" int95    
                        b"\x60", #effect == "vcup_dakuten_echo" int96 
                        b"\x61", #effect == "vcup_dakuten_reverb" int97
                        b"\x62", #effect == "vcup_dakuten_slow" int98   
                        b"\x63", #effect == "vcup_dakuten_white_noise" int99 

                        b"\x64", # effect == "vcup_babytalk" int 100
                        b"\x65", #effect == "vcup_babytalk_echo" int 101
                        b"\x66", #effect == "vcup_babytalk_reverb" int 102
                        b"\x67", #effect == "vcup_babytalk_slow" int 103
                        b"\x68", #effect == "vcup_babytalk_white_noise" int 104

                        b"\x69", #effect == "vcup_kansai" int 105
                        b"\x6a", #effect == "vcup_kansai_echo" int 106
                        b"\x6b", #effect == "vcup_kansai_reverb" int 107
                        b"\x6c", #effect == "vcup_kansai_slow" int 108
                        b"\x6d", #effect == "vcup_kansai_white_noise" int109
                            
                        b"\x6e", # effect == "vcup_kansai_dakuten" int110
                        b"\x6f", #effect == "vcup_kansai_dakuten_echo" int111
                        b"\x70", #effect == "vcup_kansai_dakuten_reverb" int112
                        b"\x71", #effect == "vcup_kansai_dakuten_slow" int113
                        b"\x72", #effect == "vcup_kansai_dakuten_white_noise" int114

                        b"\x73", #effect == "vcup_kansai_babytalk" int115
                        b"\x74", #effect == "vcup_kansai_babytalk_echo" int116
                        b"\x75", #effect == "vcup_kansai_babytalk_reverb" int117
                        b"\x76", #effect == "vcup_kansai_babytalk_kansai_slow" int118 
                        b"\x77", #effect == "vcup_kansai_babytalk_white_noise" int119  
        ]
            

        out = []

        for id in effect_id:
            new_style_id_bytes = local_style_id.to_bytes(1, "big", signed=False) #1byte
            voicevox_styleid_bytes = id + uuid_bytes[:2] + new_style_id_bytes
            styleid = StyleId(int.from_bytes(voicevox_styleid_bytes, "big", signed=True)) #int32符号付きにしないと動かない
            out.append(styleid)

        return out

    @staticmethod
    def style_id_to_local_style_id(style_id: StyleId) -> int:
        """
        VOICEVOX ENGINE 互換のグローバルに一意な StyleId を AIVM マニフェスト内のローカルなスタイル ID に変換する

        Parameters
        ----------
        style_id : StyleId
            VOICEVOX ENGINE 互換のグローバルに一意なスタイル ID

        Returns
        -------
        local_style_id : int
            AIVM マニフェスト内のローカルなスタイル ID
        """

 
        styleid_bytes = style_id.to_bytes(4, "big", signed=True) #8byte
        local_style_id = styleid_bytes[3]

        return local_style_id

