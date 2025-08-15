from http.client import responses
from typing import Optional

import requests
from botpy import logging

from bots.utils.legym import legym_encrypt_util, legym_decrypt_util


class User:
    # 类变量
    organization_id: str
    organization_name: str
    identity: str
    school_name: str
    organization_user_number: str
    real_name: str
    gender: int
    birthday: str
    height: int
    weight: int
    year: int
    mobile: str
    access_token: str
    token_type: str
    refresh_token: str
    semester_id: str
    face_image: str

    def __init__(self, organization_id, organization_name, identity, school_name,organization_user_number,real_name, gender, birthday, height, weight, year,mobile, access_token, token_type, refresh_token, semester_id, face_image):
        self.organization_id = organization_id
        self.organization_name = organization_name
        self.identity = identity
        self.school_name = school_name
        self.organization_user_number = organization_user_number
        self.real_name = real_name
        self.gender = gender
        self.birthday = birthday
        self.height = height
        self.weight = weight
        self.year = year
        self.mobile = mobile
        self.access_token = access_token
        self.token_type = token_type
        self.refresh_token = refresh_token
        self.semester_id = semester_id
        self.face_image = face_image





_log = logging.get_logger()
class LegymClient:
    BASE_URL = "cpes.legym.cn"
    LOGIN_URL = f"https://{BASE_URL}/authorization/user/v2/manage/login"
    GET_CURRENT_URL = f"https://{BASE_URL}/education/semester/getCurrent"
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Connection":"keep-alive",
            "Connection_Type":"application/json",
            "Accept":"*/*",
            "Accept-Encoding":"gzip, deflate, br",
            "Accept-Language":"zh-CN, zh-Hans;q=0.9",
            "Host": self.BASE_URL,
            "User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 15_4_1 like Mac OSX) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Html15Plus/1.0 (Immersed/47) uni-app"
        }
    def login(self,username, password)-> Optional[User]:
        #加密构造body t+pyd
        body = legym_encrypt_util.encrypt_login_body(username, password)
        try:
            #获取加密的response
            response = requests.post(url=self.LOGIN_URL, json=body,headers=self.headers)
            if response.ok:
                #解密得到data
                kv = response.json()
                pyd =kv["data"]["pyd"]
                t = kv["data"]["t"]
                data = legym_decrypt_util.decrypt_response_body(pyd=pyd, t=t)
                _log.info(data)
                user = User(
                    organization_id = data.get("organizationId",""),
                    organization_name = data.get("organizationName",""),
                    identity = data.get("identity",""),
                    school_name = data.get("schoolName",""),
                    organization_user_number = data.get("organizationUserNumber",""),
                    real_name = data.get("realName",""),
                    gender = data.get("gender"),
                    birthday = data.get("birthday",""),
                    height = data.get("height"),
                    weight = data.get("weight"),
                    year = data.get("year",),
                    mobile =data.get("mobile",""),
                    access_token = data.get("accessToken",""),
                    token_type = data.get("tokenType",""),
                    refresh_token = data.get("refreshToken",""),
                    semester_id = data.get("semesterId",""),
                    face_image = data.get("faceImage","")
                )
                #Header
                self.headers["Organization"] = user.organization_id
                self.headers["Authorization"] = f"{user.token_type} " + user.access_token

                return user
            else:
                raise Exception(response.text)
        except requests.exceptions.RequestException as e:
            _log.error(e)
        except Exception as e:
            _log.warning(e)
        return None
    def get_current(self):
        _log.info(self.headers)
        try:
            response = requests.get(
                url=self.GET_CURRENT_URL,
                headers=self.headers
            )
            if response.ok:
                data = response.json()
                return data
            else:
                raise Exception(response.text)
        except requests.exceptions.RequestException as e:
            _log.error(e)
        except Exception as e:
            _log.warning(e)
if __name__ == "__main__":
    legym_client = LegymClient()
    user = legym_client.login("18550940934","Dd1810031")
    data = legym_client.get_current()
    _log.info(data)

