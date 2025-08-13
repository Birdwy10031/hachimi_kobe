import os
import time
from datetime import timedelta

import alibabacloud_oss_v2 as oss

region = 'cn-chengdu'
bucket = 'hachimi-kobe-bots'
# 从环境变量中加载凭证信息，用于身份验证
credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()

# 加载SDK的默认配置，并设置凭证提供者
cfg = oss.config.load_default()
cfg.credentials_provider = credentials_provider

# 设置配置中的区域信息
cfg.region = region
def main():
    """
    Python SDK V2 客户端初始化配置说明：

    1. 签名版本：Python SDK V2 默认使用 V4 签名，提供更高的安全性
    2. Region配置：初始化 Client 时，必须指定阿里云 Region ID 作为请求地域标识，例如华东1（杭州）Region ID：cn-hangzhou
    3. Endpoint配置：
       - 可通过Endpoint参数自定义服务请求的访问域名
       - 当不指定 Endpoint 时，将根据 Region 自动构造公网访问域名，例如Region为cn-hangzhou时，构造访问域名为：https://oss-cn-hangzhou.aliyuncs.com
    4. 协议配置：
       - SDK 默认使用 HTTPS 协议构造访问域名
       - 如需使用 HTTP 协议，在指定域名时明确指定：http://oss-cn-hangzhou.aliyuncs.com
    """

    # 从环境变量中加载凭证信息，用于身份验证
    credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()

    # 加载SDK的默认配置，并设置凭证提供者
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider

    # 方式一：只填写Region（推荐）
    # 必须指定Region ID，以华东1（杭州）为例，Region填写为cn-hangzhou，SDK会根据Region自动构造HTTPS访问域名
    cfg.region = region

    # # 方式二：同时填写Region和Endpoint
    # # 必须指定Region ID，以华东1（杭州）为例，Region填写为cn-hangzhou
    # cfg.region = 'cn-hangzhou'
    # # 填写Bucket所在地域对应的公网Endpoint。以华东1（杭州）为例，Endpoint填写为'https://oss-cn-hangzhou.aliyuncs.com'
    # cfg.endpoint = 'https://oss-cn-hangzhou.aliyuncs.com'

    # 使用配置好的信息创建OSS客户端
    client = oss.Client(cfg)

    # 定义要上传的字符串内容
    text_string = "Hello, OSS!"
    data = text_string.encode('utf-8')  # 将字符串编码为UTF-8字节串

    # 执行上传对象的请求，指定存储空间名称、对象名称和数据内容
    result = client.put_object(oss.PutObjectRequest(
        bucket=bucket,
        key="first_key",
        body=data,
    ))

    # 输出请求的结果状态码、请求ID、ETag，用于检查请求是否成功
    print(f'status code: {result.status_code}\n'
          f'request id: {result.request_id}\n'
          f'etag: {result.etag}'
    )

def upload(key:str,file_path:str):
    # 使用配置好的信息创建OSS客户端
    client = oss.Client(cfg)

    # 执行上传对象的请求，直接从文件上传
    # 指定存储空间名称、对象名称和本地文件路径
    result = client.put_object_from_file(
        oss.PutObjectRequest(
            bucket=bucket,  # 存储空间名称
            key=key  # 对象名称
        ),
        file_path  # 本地文件路径
    )
    client.presign()
    # 输出请求的结果信息，包括状态码、请求ID、内容MD5、ETag、CRC64校验码、版本ID和服务器响应时间
    print(f'status code: {result.status_code},'
          f' request id: {result.request_id},'
          f' content md5: {result.content_md5},'
          f' etag: {result.etag},'
          f' hash crc64: {result.hash_crc64},'
          f' version id: {result.version_id},'
          f' server time: {result.headers.get("x-oss-server-time")},'
          )

def upload_all_in_folder(folder_path, prefix=''):
    """
    扫描 folder_path 下的所有文件，并调用 upload 上传。
    :param folder_path: 本地文件夹路径
    :param prefix: 上传到 OSS 时对象名称的前缀（可选）
    """
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            # 生成 OSS 的 key
            key = os.path.join(prefix, file_name).replace('\\', '/')
            print(f'Uploading {file_path} -> {key}')
            upload(key, file_path)

def generate_presigned_url(key: str, expire_seconds: int = 3600):
    """
    生成带签名的临时 URL
    :param key: OSS 对象名
    :param expire_seconds: URL 有效期（秒）
    :return: 临时 URL
    """
    # 使用配置好的信息创建OSS客户端
    client = oss.Client(cfg)

    result = client.presign(
        oss.GetObjectRequest(
            bucket=bucket,
            key=key,
        ),
        expires=timedelta(seconds=expire_seconds),
    )
    print(result.url)
    return result.url


if __name__ == "__main__":
    # upload("audio/hachimi/firstKey.silk","./audio/output.silk")
    # upload_all_in_folder('./audio/hachimi/output','audio/hachimi/')
    generate_presigned_url("audio/hachimi/cat1.silk")