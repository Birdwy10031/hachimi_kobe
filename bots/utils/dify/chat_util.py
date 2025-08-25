import mimetypes
import os
import tempfile
import time

import requests
from botpy import logging

_log = logging.get_logger()

def get_reply(conversation_id, user_id, text, file_ids, url, api_key):
    files = [{"type":"image","transfer_method":"local_file","upload_file_id":id} for id in file_ids]
    try:
        response = requests.post(url=url, headers={
        "Authorization": f"Bearer {api_key}"},
                  json={
                      "response_mode": "blocking",
                      "user": user_id,
                      "inputs": {
                          "img":files
                      },
                      "query": text,
                      "conversation_id": conversation_id,
                  }
                )
        _log.info(response.text)
        if response.ok:
            return response.json()
        else:
            raise Exception(response.text)
    except Exception as e:
        raise e
def upload(user_id,file_path,url,api_key):
    # 指定路径
    temp_dir = "./temp"

    # 确保指定路径存在
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # 发送请求下载内容
        response = requests.get(file_path)
        if response.status_code == 200:
            # 从响应头中获取文件的 MIME 类型
            content_type = response.headers.get('content-type')

            # 猜测文件后缀
            extension = mimetypes.guess_extension(content_type)
            if not extension:
                extension = ".png"
            _log.info(extension)

            # 创建临时文件
            with tempfile.NamedTemporaryFile(dir=temp_dir, suffix=extension, delete=False) as temp_file:
                temp_file_path = temp_file.name

                try:
                    # 将内容写入临时文件
                    temp_file.write(response.content)
                    print(f"文件已成功下载并保存为 {temp_file_path}")

                    # 读取临时文件内容
                    with open(temp_file_path, 'rb') as file:
                        content = file.read()
                        file_name = os.path.basename(temp_file_path)

                        # 上传文件
                        response = requests.post(url=url, headers={
                            "Authorization": f"Bearer {api_key}"
                        }, files={
                            "file": (file_name, content,f"image/{extension[1:]}"),
                        }, data={
                            "user": user_id  # 使用 data 参数传递表单字段
                        })

                        _log.info(response.text)
                        if response.ok:
                            return response.json()
                        else:
                            raise Exception(response.text)
                finally:
                    # 关闭文件句柄
                    file.close()
                    # 删除临时文件
                    if os.path.exists(temp_file_path):
                        # 多次尝试删除文件以确保它被释放
                        os.remove(temp_file_path)
                        print(f"临时文件 {temp_file_path} 已删除")
        else:
            print(f"下载失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == '__main__':
    # data = get_reply(None,"test","你看看",["https://ts2.tc.mm.bing.net/th/id/OIP-C.PHgMwKINH3zNyGGEIZO20gHaKh?rs=1&pid=ImgDetMain&o=7&rm=3"],"http://119.29.219.247/v1/chat-messages","app-eji81DemxMjijUSEsiDLfjC3")
    # data = upload("test","https://multimedia.nt.qq.com.cn/download?appid=1407&fileid=EhRonUxqRpDg54_XzjDQnQiS7J8-TRjS2gMg_woossPKyu6kjwMyBHByb2RQgL2jAVoQPwvFhuUwWxefTWGc6pFwcnoCULo&rkey=CAMSOLgthq-6lGU_3neQKsshStA4hU0IPDSWQ2Mn1Qqbj97W3j1nMygRuCCUcDKJSccs6cEZv4Aux_d5&spec=0","http://119.29.219.247/v1/files/upload","app-QI3pxspdO6CvPhIyVOoIvPe2")
    # print(data)
    # lst = []
    # lst.append(data["id"])
    # lst.append(data["id"])
    data = get_reply(None,"test","扔出",["99ff5066-47f2-4a34-a6a9-29be43553b14"],"http://119.29.219.247/v1/chat-messages","app-QI3pxspdO6CvPhIyVOoIvPe2")
    print(data)