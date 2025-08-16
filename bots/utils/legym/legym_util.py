import random
from datetime import timedelta
from http.client import responses
from typing import Optional

import requests
from botpy import logging

from bots.utils.legym import encrypt_util, decrypt_util
from bots.utils.redis.redis_client import RedisClient


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
    GET_LIMIT_URL = f"https://{BASE_URL}/running/app/getRunningLimit"
    GET_VERSION_URL = f"https://{BASE_URL}/authorization/mobileApp/getLastVersion?platform=2"
    UPLOAD_URL = f"https://{BASE_URL}/running//app/v3/upload"
    # 常量
    CALORIE_PER_MILEAGE = 58.3
    # 360 s/km
    PACE = 360.0
    PACE_RANGE = 0.6
    def __init__(self,user_id):
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
        self.semester_id = None
        self.version = ""
        self.daily = None
        self.day = None
        self.end = None
        self.limit = None
        self.scoring = None
        self.start = None
        self.week = None
        self.weekly = None
    def login(self,username, password)-> Optional[User]:
        #加密构造body t+pyd
        body = encrypt_util.encrypt_login_body(username, password)
        try:
            #获取加密的response
            response = requests.post(url=self.LOGIN_URL, json=body,headers=self.headers)
            if response.ok:
                #解密得到data
                kv = response.json()
                pyd =kv["data"]["pyd"]
                t = kv["data"]["t"]
                data = decrypt_util.decrypt_response_body(pyd=pyd, t=t)
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
    def get_version(self):
        try:
            response = requests.get(
                url=self.GET_VERSION_URL,
                headers=self.headers,
            )
            if response.ok:
                data = response.json()
                #setVersion
                self.version = data.get("versionLabel")
                return data
            else:
                raise Exception(response.text)
        except requests.exceptions.RequestException as e:
            _log.error(e)
        except Exception as e:
            _log.warning(e)
    def get_limit(self):
        try:
            response = requests.post(
                url=self.GET_LIMIT_URL,
                headers=self.headers,
                json={
                    "semesterId":self.semester_id
                }

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
    def upload(self,mileage,end_time,geojson_str):
        #更新useragent
        self.headers["User_Agent"] = f"QJGX/{self.version} (com.ledreamer.legym; build:30000868; iOS 16.0.2) Alamofire/5.8.0"
        #不允许超过 当天最大里程 本周最大里程 单次最大里程
        mileage = min(mileage,self.daily-self.day,self.weekly-self.week,self.end)
        if mileage <self.start:
            #小于最小里程
            return False
        #随机扰动
        mileage += random.uniform(-0.02,-0.001)
        #根据配速计算总时长 总耗时 15s扰动
        keep_time = int(mileage*self.PACE + random.randint(-15,15))
        #从end_time 计算 start_time 早8s开始
        start_time = end_time - timedelta(seconds=keep_time + 8)
        #计算卡路里
        calorie = int(self.CALORIE_PER_MILEAGE*mileage)
        #平均配速 ms/km
        ave_pace = int(keep_time/mileage * 1000)
        pace_number = int(mileage*1000/self.PACE_RANGE/2)
        #签名 (hs sha1)
        sign_digital = encrypt_util.hs(f"{mileage}1{start_time.strftime('%Y-%m-%d %H:%M:%S')}{calorie}{ave_pace}{keep_time}{pace_number}{mileage}1")
        try:
            response = requests.post(
                url=self.UPLOAD_URL,
                headers=self.headers,
                json={
                    "semesterId":self.semester_id,
                    "appVersion":self.version,
                    "avePace": ave_pace,
                    "calorie": calorie,
                    "deviceType":"iPhone 13 Pro",
                    "effectiveMileage":mileage,
                    "effectivePart":1,
                    "endTime":end_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "gpsMileage":mileage,
                    "keepTime":keep_time,
                    "limitationsGoalsSexInfoId":self.limit,
                    "paceNumber":pace_number,
                    "paceRange":self.PACE_RANGE,
                    "routineLine":"",
                    "scoringType":self.scoring,
                    "signDigital":sign_digital,
                    "signPoint":[],
                    "startTime":start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "systemVersion":"16.0.2",
                    "totalMileage":mileage,
                    "totalPart":1,
                    "runType":"自由跑"
                }
            )
            if response.ok:
                data = response.json()
                _log.info(data)
                return True
            else:
                raise Exception(response.text)
        except requests.exceptions.RequestException as e:
            _log.error(e)
        except Exception as e:
            _log.warning(e)
    def quickRun(self,username,password,mileage,end_time,geojson_str):
        user = self.login(username=username,password=password)
        self.get_version()
        self.get_limit()
        self.upload(mileage=mileage,end_time=end_time,geojson_str=geojson_str)
        return user
if __name__ == "__main__":
    legym_client = LegymClient()
    user = legym_client.login("18550940934","Dd1810031")
    data = legym_client.get_version()
    _log.info(data)

