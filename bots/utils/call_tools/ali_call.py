import os
import time
import dashscope
from dashscope.audio.tts_v2 import VoiceEnrollmentService, SpeechSynthesizer
from botpy.ext.cog_yaml import read
# 1. 环境准备
# 推荐通过环境变量配置API Key

config = read(
    os.path.normpath(
        os.path.join(os.path.dirname(__file__), "../../config.yaml")
    )
)
dashscope.api_key=config["DASHSCOPE_API_KEY"]
if not dashscope.api_key:
    raise ValueError("DASHSCOPE_API_KEY environment variable not set.")

# 2. 定义复刻参数
TARGET_MODEL = "cosyvoice-v3-plus"
# 为音色起一个有意义的前缀
VOICE_PREFIX = "kobevoice"  # 仅允许数字和小写字母，小于十个字符
# 公网可访问音频URL
AUDIO_URL = "http://119.29.219.247/files/8686b45a-7aab-41d2-9e82-eaf9cdc5197e/file-preview?timestamp=1766899477&nonce=aa26887cdaae4855e0d63805e3055f31&sign=U8WfRRxM-tj_2fxbLA_6BwVJe98tnFAAuR9s6lQtA8c="  # 示例URL，请替换为自己的
def generate_voice(text,voice_path):
    # 3. 创建音色 (异步任务)
    # print("--- Step 1: Creating voice enrollment ---")
    # service = VoiceEnrollmentService()
    # try:
    #     voice_id = service.create_voice(
    #         target_model=TARGET_MODEL,
    #         prefix=VOICE_PREFIX,
    #         url=AUDIO_URL
    #     )
    #     print(f"Voice enrollment submitted successfully. Request ID: {service.get_last_request_id()}")
    #     print(f"Generated Voice ID: {voice_id}")
    # except Exception as e:
    #     print(f"Error during voice creation: {e}")
    #     raise e
    # # 4. 轮询查询音色状态
    # print("\n--- Step 2: Polling for voice status ---")
    # max_attempts = 30
    # poll_interval = 10  # 秒
    # for attempt in range(max_attempts):
    #     try:
    #         voice_info = service.query_voice(voice_id=voice_id)
    #         status = voice_info.get("status")
    #         print(f"Attempt {attempt + 1}/{max_attempts}: Voice status is '{status}'")
    #
    #         if status == "OK":
    #             print("Voice is ready for synthesis.")
    #             break
    #         elif status == "UNDEPLOYED":
    #             print(f"Voice processing failed with status: {status}. Please check audio quality or contact support.")
    #             raise RuntimeError(f"Voice processing failed with status: {status}")
    #         # 对于 "DEPLOYING" 等中间状态，继续等待
    #         time.sleep(poll_interval)
    #     except Exception as e:
    #         print(f"Error during status polling: {e}")
    #         time.sleep(poll_interval)
    # else:
    #     print("Polling timed out. The voice is not ready after several attempts.")
    #     raise RuntimeError("Polling timed out. The voice is not ready after several attempts.")

    # 5. 使用复刻音色进行语音合成
    print("\n--- Step 3: Synthesizing speech with the new voice ---")
    try:
        synthesizer = SpeechSynthesizer(model=TARGET_MODEL, voice="cosyvoice-v3-plus-kobevoice-841a92e0f32a42eebc1cd6730a21cd1d")

        # call()方法返回二进制音频数据
        audio_data = synthesizer.call(text)
        print(f"Speech synthesis successful. Request ID: {synthesizer.get_last_request_id()}")

        # 6. 保存音频文件
        with open(voice_path, "wb") as f:
            f.write(audio_data)
        print(f"Audio saved to {voice_path}")

    except Exception as e:
        print(f"Error during speech synthesis: {e}")