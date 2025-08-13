import subprocess
import os

def to_pcm(mp3_path, pcm_path):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", mp3_path,
        "-f", "s16le",     # 输出 16bit 小端 PCM
        "-ar", "24000",    # 采样率 24kHz
        "-ac", "1",        # 单声道
        pcm_path
    ]
    print("Running ffmpeg:", " ".join(cmd))
    subprocess.run(cmd, check=True)

def pcm_to_silk(encoder_path, pcm_path, silk_path):
    cmd = [
        encoder_path,
        pcm_path,
        silk_path,
        "-Fs_API", "24000",        # 采样率 24kHz，默认可省略
        "-packetlength", "20",     # 包大小20ms，默认
        "-rate", "25000",          # 码率 25000 bps，默认
        "-complexity", "2",        # 复杂度最高
        "-tencent"                 # 兼容腾讯微信的编码格式
    ]
    print("Running silk encoder:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("编码器错误输出:", result.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd)
    else:
        print("编码器输出:", result.stdout)

pcm_file = "temp.pcm"             # 临时 PCM 文件
# silk_file = "output.silk"         # 生成的 silk 文件
encoder_exe = "./encoder.exe"     # 编码器可执行文件路径
def encode(audio_path,silk_file):
    try:
        to_pcm(audio_path, pcm_file)
        pcm_to_silk(encoder_exe, pcm_file, silk_file)
        print("转换成功:", silk_file)
        return silk_file
    except subprocess.CalledProcessError as e:
        print("转换失败:", e)
    finally:
        if os.path.exists(pcm_file):
            os.remove(pcm_file)

def encode_all_in_folder(folder_path, prefix=''):
    """
    扫描 folder_path 下的所有文件，并调用 upload 上传。
    :param folder_path: 本地文件夹路径
    :param prefix: 上传到 OSS 时对象名称的前缀（可选）
    """
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            name_without_ext = os.path.splitext(file_name)[0]
            file_path = os.path.join(root, file_name)
            output_path = os.path.join(prefix, name_without_ext+'.silk').replace('\\', '/')
            print(f'Encoding {file_path} -> {output_path}')
            encode(file_path,output_path)
if __name__ == "__main__":
    encode_all_in_folder("./hachimi","./hachimi/output/")
