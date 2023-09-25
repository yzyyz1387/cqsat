# python3
# -*- coding: utf-8 -*-
# @Time    : 2023-09-25 2:21
# @Author  : yzyyz
# @Email   :  youzyyz1384@qq.com
# @File    : media_utils.py
# @Software: PyCharm
from pathlib import Path

import pysilk
import os, pilk
from pydub import AudioSegment
import numpy as np
import librosa
from os import walk
from os.path import join as pjoin
from sys import argv
from subprocess import run as prun
import soundfile as sf
import pilk
import av


# 为什么是24000？
async def to_pcm(in_path: str) -> tuple[str, int]:
    """任意媒体文件转 pcm"""
    out_path = os.path.splitext(in_path)[0] + '.pcm'
    with av.open(in_path) as in_container:
        in_stream = in_container.streams.audio[0]
        sample_rate = in_stream.codec_context.sample_rate
        with av.open(out_path, 'w', 's16le') as out_container:
            out_stream = out_container.add_stream(
                'pcm_s16le',
                # rate=sample_rate,
                rate=24000,

                layout='mono'
            )
            try:
                for frame in in_container.decode(in_stream):
                    frame.pts = None
                    for packet in out_stream.encode(frame):
                        out_container.mux(packet)
            except:
                pass
    return out_path, sample_rate


async def sil_to_wav(silk_path, wav_path, rate: int = 24000):
    """
    silk 文件转 wav
    """
    wav_data = pysilk.decode_file(silk_path, to_wav=True, sample_rate=rate)
    with open(wav_path, "wb") as f:
        f.write(wav_data)
    return wav_path


async def convert_to_silk_wav(media_path: str, out_path: Path) -> str:
    """任意媒体文件转 wav, 返回路径"""
    pcm_path, sample_rate = await to_pcm(media_path)
    silk_path = os.path.splitext(pcm_path)[0] + '.silk'
    pilk.encode(pcm_path, silk_path, pcm_rate=24000, tencent=True)
    os.remove(pcm_path)
    wav_path = (await sil_to_wav(silk_path, str(out_path.resolve()) + '.wav'))
    return wav_path


async def MergeTwoMp3(voice: Path, mdc: Path, prefix: Path = None, snr: int = 0):
    audio, rate = librosa.load(voice, sr=None)
    no = await awgn(audio, snr) if snr else audio
    sf.write(str(voice.resolve()), no, rate)

    input_voice_2 = AudioSegment.from_mp3(voice)
    input_voice_3 = AudioSegment.from_mp3(mdc)
    if prefix:
        input_voice_1 = AudioSegment.from_mp3(prefix)
        output_voice = input_voice_1 + input_voice_2 + input_voice_3
    else:
        output_voice = input_voice_2 + input_voice_3

    output_voice_path = str(voice.resolve()).replace('.wav', '.mp3')
    output_voice.export(output_voice_path, format="mp3")
    Path(voice).unlink()
    return output_voice_path


async def awgn(audio, snr):
    # 在audio y中 添加噪声 噪声强度SNR为int
    audio_power = audio ** 2
    audio_average_power = np.mean(audio_power)
    audio_average_db = 50 * np.log10(audio_average_power)
    noise_average_db = audio_average_db - snr
    noise_average_power = 100 ** (noise_average_db / 10)
    mean_noise = 1
    noise = np.random.normal(mean_noise, np.sqrt(noise_average_power), len(audio))
    return audio + noise


if __name__ == '__main__':
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(convert_to_silk_wav('testimportant.amr'))
