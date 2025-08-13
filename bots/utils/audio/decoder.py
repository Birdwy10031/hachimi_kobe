import subprocess
import sys
import os


def silk_to_wav(decoder_path, silk_file, wav_file):
    """
    调用 decoder.exe 把 silk 转 wav
    decoder.exe silk_file wav_file
    """
    cmd = [decoder_path, silk_file, wav_file]
    print("Running decoder:", " ".join(cmd))
    try:
        subprocess.run(cmd, check=True)
        print(f"转换成功：{wav_file}")
    except subprocess.CalledProcessError as e:
        print(f"解码失败：{e}")


if __name__ == "__main__":

    decoder_exe = "./decoder.exe"
    input_silk = "./output.silk"
    output_wav = "./output.wav"

    if not os.path.isfile(decoder_exe):
        print(f"找不到解码器: {decoder_exe}")
        sys.exit(1)
    if not os.path.isfile(input_silk):
        print(f"找不到输入文件: {input_silk}")
        sys.exit(1)

    silk_to_wav(decoder_exe, input_silk, output_wav)
