# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from qcloud_cos.cos_exception import CosClientError, CosServiceError
import sys
import os
import logging

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 1. 设置用户属性, 包括 secret_id, secret_key, region 等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
secret_id = os.environ['COS_SECRET_ID']     # 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
secret_key = os.environ['COS_SECRET_KEY']   # 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
region = 'ap-chengdu'      # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
                           # COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
token = None               # 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
scheme = 'https'           # 指定使用 http/https 协议来访问 COS，默认为 https，可不填

config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
client = CosS3Client(config)
bucket = 'hachimi-kobe-bots-1367983852'
def generate_presigned_url(key: str, expire_seconds: int = 3600):
    """
    生成带签名的临时 URL
    :param key: OSS 对象名
    :param expire_seconds: URL 有效期（秒）
    :return: 临时 URL
    """
    # 使用配置好的信息创建OSS客户端
    url = client.get_presigned_url(
        Method='GET',
        Bucket=bucket,
        Key=key,
        Expired=expire_seconds  # 120秒后过期，过期时间请根据自身场景定义
    )
    print(url)
    return url
def upload(key:str,file_path:str):
    # 使用高级接口上传一次，不重试，此时没有使用断点续传的功能
    response = client.upload_file(
        Bucket=bucket,
        Key=key,
        LocalFilePath=file_path,
        EnableMD5=False,
        progress_callback=None
    )