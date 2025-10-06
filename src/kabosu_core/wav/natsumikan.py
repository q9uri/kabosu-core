# MIT License

# Copyright (c) 2025 WariHima

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pydub import AudioSegment
import librosa
import soundfile as sf
from pathlib import Path
import numpy as np
from scipy import interpolate
from scipy.ndimage import zoom

import pyworld as pw

def voicecanger_robot(
    input_wav_path: Path | str,
    output_wav_path: Path | str
    ):

    raw_wave, samplerate = sf.read(input_wav_path) 
    _f0, t = pw.dio(raw_wave, samplerate)  # 基本周波数の抽出 
    f0 = pw.stonemask(raw_wave, _f0, t, samplerate)  # 基本周波数の修正 
    sp = pw.cheaptrick(raw_wave, f0, t, samplerate)  # スペクトル包絡の抽出 
    ap = pw.d4c(raw_wave, f0, t, samplerate)  # 非周期性指標の抽出
    
    synthesized = pw.synthesize(_f0, sp, ap, samplerate)
    sf.write(file=output_wav_path, data=synthesized, samplerate=samplerate)

def merge_wav(
    base_input_wav_path: Path | str,
    speaker_input_wav_path: Path | str,
    output_wav_path: Path | str
    ):

    raw_wave, samplerate = sf.read(speaker_input_wav_path) 
    _speaker_f0, t = pw.dio(raw_wave, samplerate)  # 基本周波数の抽出 
    speaker_f0 = pw.stonemask(raw_wave, _speaker_f0, t, samplerate)  # 基本周波数の修正 
    speaker_sp = pw.cheaptrick(raw_wave, speaker_f0, t, samplerate)  # スペクトル包絡の抽出 
    speaker_ap = pw.d4c(raw_wave, speaker_f0, t, samplerate)  # 非周期性指標の抽出

    raw_wave, samplerate = sf.read(base_input_wav_path) 
    _base_f0, t = pw.dio(raw_wave, samplerate)  # 基本周波数の抽出 
    base_f0 = pw.stonemask(raw_wave, _base_f0, t, samplerate)  # 基本周波数の修正 
    base_sp = pw.cheaptrick(raw_wave, base_f0, t, samplerate)  # スペクトル包絡の抽出 
    base_ap = pw.d4c(raw_wave, base_f0, t, samplerate)  # 非周期性指標の抽出

    fix_f0_rate = speaker_f0.mean() / base_f0.mean()
    fix_sp_rate = speaker_sp.mean() / base_sp.mean()
    fix_ap_rate = speaker_ap.mean() / base_ap.mean()

    convert_rate = 1.0
    modified_f0 = base_f0 * fix_f0_rate
    modified_sp = base_sp * (fix_sp_rate * convert_rate) 
    modified_ap = base_ap * (fix_ap_rate * convert_rate) 

    synthesized = pw.synthesize(modified_f0, modified_sp, modified_ap, samplerate)
    sf.write(file=output_wav_path, data=synthesized, samplerate=samplerate)


def add_white_noise(
        input_wav_path: Path | str,
        output_wav_path: Path | str,
        noise_level: float = 0.05
    ):
    raw_wave, samplerate = sf.read(input_wav_path) 
    raw_wave = add_white_noise_ndarry(audio_array=raw_wave, noise_level=noise_level)
    sf.write(file=output_wav_path, data=raw_wave, samplerate=samplerate)


def convert_to_echo(
    input_wav_path: Path | str,
    output_wav_path: Path | str,
    delay:int = 500,
    num_echos:int = 3,
    decay:int = 500
    ):
    audio = AudioSegment.from_wav(input_wav_path)
    echo_audio = add_echo(audio, delay=delay, num_echos=num_echos, decay=decay)
    echo_audio.export(output_wav_path, format="wav")

def convert_to_youmu(
    input_wav_path: Path | str,
    output_wav_path: Path | str):

    raw_wave, samplerate = sf.read(input_wav_path)
    raw_wave = librosa.effects.pitch_shift(raw_wave, sr=samplerate, n_steps=3.6)#12 = 200%, 130% pitch
    sf.write(file=output_wav_path, data=raw_wave, samplerate=samplerate)

def convert_to_reverb(
    input_wav_path: Path | str,
    output_wav_path: Path | str,
    reverberance:int =60,
    damping:int =40,
    room_scale:int =80):

    raw_wave, samplerate = sf.read(input_wav_path)
    raw_wave = add_reverb(raw_wave, reverberance=reverberance, damping=damping, room_scale=room_scale)
    sf.write(file=output_wav_path, data=raw_wave, samplerate=samplerate)


def wav_pitch_change(
    input_wav_path: Path | str,
    output_wav_path: Path | str,
    n_steps: int
    ):

    raw_wave, samplerate = sf.read(input_wav_path)
    raw_wave, samplerate = sf.read(input_wav_path)
    raw_wave = librosa.effects.pitch_shift(raw_wave, sr=samplerate, n_steps=n_steps)
    sf.write(file=output_wav_path, data=raw_wave, samplerate=samplerate)

#----------------------------------------------------------------------------------------------
# 以下のコードはこちらからお借りした。
# #https://qiita.com/Tadataka_Takahashi/items/1c1681bc2e931b92bca9
#--------------------------------------------------------------------------------------------------------
def add_echo(sound: AudioSegment, delay:int, num_echos:int, decay:int):
    echo = sound.fade_out(duration=decay)
    for i in range(num_echos):
        echo_delay = delay * (i + 1)
        echo_decay = decay * (num_echos - i)
        delayed_echo = AudioSegment.silent(duration=echo_delay) + echo.fade_out(duration=echo_decay)
        sound = sound.overlay(delayed_echo)
    return sound

def add_reverb(samples, reverberance:int =50, damping=50, room_scale=75):

    # パラメータを正規化
    reverberance = max(0, min(100, reverberance)) / 100
    damping = max(0, min(100, damping)) / 100
    room_scale = max(0, min(100, room_scale)) / 100

    delay_samples = int(8000 * room_scale * 0.1)
    decay = 1 - damping
    # リバーブを適用
    reverb_samples = np.zeros_like(samples)
    for i in range(len(samples)):
        if i < delay_samples:
            reverb_samples[i] = samples[i]
        else:
            reverb_samples[i] = samples[i] + reverberance * decay * reverb_samples[i - delay_samples]
    
    return reverb_samples


#----------------------------------------------------------------------------------------------
# 以下のコードはこちらからお借りした。
# https://toolbox.aaa-plaza.net/archives/3619
#--------------------------------------------------------------------------------------------------------
def cahnge_speed(
    input_wav_path: Path | str,
    output_wav_path: Path | str,
    speed:int = 0.5):
# 再生速度を通常の何倍にするか


    # 元音声の読み込み（16ビットモノラル限定）
    raw_wave, samplerate = sf.read(input_wav_path)

    # 変換後のデータを格納する配列を用意
    count = int((len(raw_wave)-1)/speed)
    dst = np.empty(count, dtype="float64")

    # 補間関数を求める
    f = interpolate.interp1d(range(len(raw_wave)), raw_wave, kind="cubic")     

    # 再生速度変換
    for i in range(0,count):
        dst[i] = f(i*speed)


    sf.write(file=output_wav_path, data=dst, samplerate=samplerate)

#----------------------------------------------------------------------------------------------
# 以下のコードはgeminiに考えてもらった。
#--------------------------------------------------------------------------------------------------------
def add_white_noise_ndarry(audio_array, noise_level=0.05):
    """
    オーディオデータにホワイトノイズを追加して聞き取りづらくする関数

    Args:
        audio_array (np.ndarray): 入力オーディオデータ
        noise_level (float): ノイズの強度（0〜1.0）。値が大きいほどノイズが強くなる

    Returns:
        np.ndarray: ノイズが追加されたオーディオデータ
    """
    # オーディオデータと同じ形状のランダムなノイズを生成
    #noise = np.random.randn(len(audio_array))
    noise = np.random.randn(len(audio_array))
    
    # ノイズの強度を調整
    # np.max(np.abs(audio_array))を使って、元の音声の最大振幅に対する相対的なノイズレベルを設定
    adjusted_noise = noise * (noise_level * np.max(np.abs(audio_array)))
    
    # 元のオーディオにノイズを加算
    noisy_audio = audio_array + adjusted_noise
    
    # オーバーフローを避けるために値をクリッピング
    noisy_audio = np.clip(noisy_audio, -1.0, 1.0)
    
    return noisy_audio