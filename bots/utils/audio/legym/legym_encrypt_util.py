# ---------------------
# Python 完整 hs + AES 登录构造
# ---------------------
import hashlib, time, base64, json
from Crypto.Cipher import AES

# 原始 uncaesar 常量
RAW_SALT = "lwdxYiqhaKlUljC6"  # Rust 测试里 SALT
DYNAMIC_RAW = "402881hd7f39f5g5017f39g143d8062e"

def uncaesar(text: str, shift: int = 3) -> str:
    result = []
    for c in text:
        if 'a' <= c <= 'z':
            result.append(chr((ord(c) - ord('a') - shift) % 26 + ord('a')))
        elif 'A' <= c <= 'Z':
            result.append(chr((ord(c) - ord('A') - shift) % 26 + ord('A')))
        else:
            result.append(c)
    return ''.join(result)

salt = uncaesar(RAW_SALT)
DYNAMIC_FIXED = uncaesar(DYNAMIC_RAW)

def hs(text: str) -> str:
    sha1 = hashlib.sha1()
    sha1.update((text + salt).encode('utf-8'))
    return sha1.hexdigest()

def format_json(obj: dict) -> str:
    s = json.dumps(obj, ensure_ascii=False, indent=2)
    return s.replace(": ", " : ")

def pad(data: bytes) -> bytes:
    padding_len = 16 - len(data) % 16
    return data + bytes([padding_len] * padding_len)

def encrypt_aes_ecb_pkcs7(data: str, key: str) -> str:
    key_bytes = key.encode('utf-8').ljust(16, b'\0')[:16]
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(pad(data.encode('utf-8')))).decode('utf-8')

def get_dynamic_key(t: int) -> str:
    t_str = str(t)
    dest = int(t_str[2:5])
    nptr = int(t_str[4:8])
    last_digit = int(t_str[-1])
    v5 = abs(dest - nptr) << last_digit
    return f"{v5}{DYNAMIC_FIXED}"

def encode_login_body(username: str, password: str) -> dict:
    login_json = {
        "entrance": "1",
        "userName": username,
        "password": password,
        "signDigital": hs(f"{username}{password}1")
    }
    json_str = format_json(login_json)
    t = int(time.time() * 1000)
    key = get_dynamic_key(t)
    pyd = encrypt_aes_ecb_pkcs7(json_str, key)
    return {"t": t, "pyd": pyd}


# ---------------------
# 测试
# ---------------------
if __name__ == "__main__":
    username = "18550940934"
    password = "Dd1810031"
    body = encode_login_body(username, password)
    print(body)
