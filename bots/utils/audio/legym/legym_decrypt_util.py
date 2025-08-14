import base64
from Crypto.Cipher import AES

from bots.utils.audio.legym import legym_encrypt_util

# DYNAMIC_FIXED 与 Rust 中 uncaesar 解码后的结果一致
DYNAMIC_FIXED = legym_encrypt_util.uncaesar("402881hd7f39f5g5017f39g143d8062e")

def get_dynamic_key(t: int) -> str:
    t_str = str(t)
    if len(t_str) < 8:
        raise ValueError("t too short")
    dest = t_str[2:5]
    nptr = t_str[4:8]
    v2 = int(t_str[-1])

    v1 = int(dest)
    v3 = v1 - int(nptr)
    v4 = abs(v3)
    v5 = v4 << v2

    return f"{v5}{DYNAMIC_FIXED}"

def decrypt_aes_ecb_base64(ciphertext_b64: str, key: str) -> str:
    key_bytes = key.encode('utf-8')
    key_bytes = key_bytes.ljust(16, b'\0')[:16]  # AES-128
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    ciphertext = base64.b64decode(ciphertext_b64)
    plaintext = cipher.decrypt(ciphertext)

    # 去掉 PKCS7 padding
    pad_len = plaintext[-1]
    return plaintext[:-pad_len].decode('utf-8')

def decode_response_body(pyd: str, t: int) -> str:
    key = get_dynamic_key(t)
    return decrypt_aes_ecb_base64(pyd, key)

if __name__ == "__main__":
    # 示例：替换为 login 返回的 pyd 和 t
    pyd = "5Ga0jQFy4qiQMsyOBaVeIOYZXnWPCSe2LsD4TlhPD6CzobhYplHpe+Xs7QpqJNPHyfSWyHuZPQO/hCDg0hhOGgC5EqZ2gnsmZESScShjpOQU1R7AVi5eN7iGMO7/Ji6LWVaGddW3sjvdisLupQ2t8DqKXN/fEWDA3yPW540iBM51a+9Vge6ZDr7AEQKWeVmxP5YOmaAzSw5AKC0ddjlwCSRykYsjFL0heRg/ps0mS12t94GvJfSwkQypk9eSYQVAToSCbOTbYOyEk+nYnppk2dTD0jTqMZJD29RcUBSJsa2qi7zqFjc20UeTjAYP6J3fvMTqiADKHJphJomE1YvGGfSMXGU/7a40pPq97Rnttra2yZuGmZJ6UQ7TsZj//iOFK5yOeHC56b+cJi1oa9saUypLJZ8bfP/V7tsiQ/tAcu0S0PTGinN28yzDZlX1DhXsv8/Ox0VVEtuQP1HRRTZfB0Bkx84FU4+YHPrEzn60g0qSojVZsroRsPFjAEXCr8nokSkITk7GTXcYYKry1kDMT/fwBMtrZYwCgDQpFP0EaZiASU/wsHJZA3UDrGtAuS4Q3YBleGWwrbXwN9ECwk1+waC3dnjSQUF0eXZyH+zWGILlwNPbX48a/552RxWJTDYDSQfw8wId6ev0B2Iscll0JYMekAGlqqh6w0FFVQVgIIi/b5KlbDYmLe02DxdxdwHhKX0Q0AEP3tU7qudMFgAxwk5McVUsUoA9w4dzcJiY4c8vv2Ofz3m1xmfPP/HmVcZ0pQHXr4sJUtRDmeb/HLVCi4Y+Ukf1zAYkEV3rwKCtGewDQoiCgq/FbqeIpjNG+x/5Nso9uP5IDs+GyQi+eOA75v/QHaP+NfZwyCBAXvmrTJPDkRXg8s3HCusRbB2IM3lyKHaqG2ZbfxIIMo+OV9GksCWintWw8V7bi591FPGGF2Ej2dGWv8T31d2TVoxN88PcZPwYTYI82UXb1GWfDs48/Loevo/L0vlkU426kN2/HlLzkYWs7R6vpXwj9MmiMLvTYfAtNNvq/GFcDd7PViVb0QTkAa0ff+2hSjGrgQi2njp9yqmOvamxLybT4CWKe2dAC/aj+YpTCi26C/f3Pgw243Kmu40snKmGgTa15sHEFpHUoD1yPymDx+UyoOwgmaWxTzymXaROOQyTt9exNriz5wr3ERY3gSMKyCzSNeh+yo1Vu9vLdv7rlod0tgr0DcN5pbUmetIEwbmqtV8o5xrrbqhJ5coaGjm+1xRvzdWCV4NkBMc9kBRPE0hZoJ+/yckViwkYyQ+9g2152Ajx4N9K3R/fm210YLJx9pRe4TIO3wXmysVEEi5M42R478imbSFvp1sojXFTMgVpyr76s09QlDBByL7u7ry7O74rV9uC607Stt+SAIGdMjcjYHr0SRfCmrU7aGEOOmwFcTzFReafuOH9s6RQgnyLZiQgGaKjkkFXayujN/yXc647YJEQ3K8LXCeTvnqpUKwHQLhZrNegZ21XwXKrwkzelHVC6U97C3k="
    t = 1755185312441

    decoded_json = decode_response_body(pyd, t)
    print(decoded_json)
