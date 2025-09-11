import json
import random
from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Optional

import requests
from botpy import logging

from bots.utils.legym import encrypt_util, decrypt_util, routine
from datetime import datetime, timedelta
import json
import re

@dataclass
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
    school_id: str

    def __init__(self, organization_id, organization_name, identity, school_name,organization_user_number,real_name, gender, birthday, height, weight, year,mobile, access_token, token_type, refresh_token, semester_id, face_image,school_id,user_id):
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
        self.school_id= school_id
        self.id = user_id





_log = logging.get_logger()


class LegymClient:
    BASE_URL = "cpes.legym.cn"
    LOGIN_URL = f"https://{BASE_URL}/authorization/user/v2/manage/login"
    GET_CURRENT_URL = f"https://{BASE_URL}/education/semester/getCurrent"
    GET_LIMIT_URL = f"https://{BASE_URL}/running/app/getRunningLimit"
    GET_VERSION_URL = f"https://{BASE_URL}/authorization/mobileApp/getLastVersion?platform=2"
    UPLOAD_URL = f"https://{BASE_URL}/running/app/v3/upload"
    RN_FIXED = encrypt_util.uncaesar("3h0783g6891d4d3h9521gfe6ee341560")
    # 常量
    CALORIE_PER_MILEAGE = 58.3
    # 360 s/km
    PACE = 360.0
    PACE_RANGE = 0.6
    def __init__(self):
        self.headers = {
            "Content-Type": "application/json",
            "Connection":"keep-alive",
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
        self.user = None
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
                    user_id = data.get("id"),
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
                    face_image = data.get("faceImage",""),
                    school_id = data.get("schoolId","")
                )
                #Header
                self.headers["Organization"] = user.organization_id
                self.headers["Authorization"] = f"Bearer " + user.access_token

                self.user = user
                return user
        except Exception as e:
            raise e
        return None
    def get_current(self):
        try:
            response = requests.get(
                url=self.GET_CURRENT_URL,
                headers=self.headers
            )
            if response.ok:
                data = response.json()
                self.semester_id=data["data"]["id"]
                return data
        except Exception as e:
            raise e
    def get_version(self):
        try:
            response = requests.get(
                url=self.GET_VERSION_URL,
                headers=self.headers,
            )
            if response.ok:
                data = response.json()
                #setVersion
                self.version = data["data"]["versionLabel"]
                return data

        except Exception as e:
            raise e
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
                res = response.json()
                print(res)
                data = res["data"]
                #获取限制
                #day限制
                self.daily = data["dailyMileage"]
                #day已跑
                self.day = float(data["totalDayMileage"])
                #每次区间
                self.start = data["effectiveMileageStart"]
                self.end = data["effectiveMileageEnd"]
                self.limit = data["limitationsGoalsSexInfoId"]
                self.scoring = data["scoringType"]
                #周已跑
                self.week = float(data["totalWeekMileage"])
                #周上限
                self.weekly = data["weeklyMileage"]
                print(self.daily,self.day,self.end,self.limit,self.scoring,self.start,self.week,self.weekly)
                return data
        except Exception as e:
            raise e
    def upload(self,mileage,end_time,geojson_str):
        #更新useragent
        headers = {
            "Content-Type": "application/json",
            "Connection": "keep-alive",
            "Accept": "*/*",
            "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
            "Accept-Language": "zh-Hans-HK;q=1.0, zh-Hant-HK;q=0.9, yue-Hant-HK;q=0.8",
            "Host": "cpes.legym.cn",
            "User-Agent": "QJGX/3.10.0 (com.ledreamer.legym; build:30000868; iOS 16.0.2) Alamofire/5.8.0",
            "Authorization": f"Bearer {self.user.access_token}"
        }
        #不允许超过 当天最大里程 本周最大里程 单次最大里程

        mileage = min(mileage,self.daily-self.day,self.weekly-self.week,self.end)
        if mileage < self.start:
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
        raw_data = {
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
                    "routineLine":[lg_point.__dict__ for lg_point in routine.get_routine(mileage,geojson_str)],
                    "scoringType":self.scoring,
                    "signDigital":sign_digital,
                    "signPoint":[],
                    "startTime":start_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "systemVersion":"16.0.2",
                    "totalMileage":mileage,
                    "totalPart":1,
                    "type":"自由跑",
                }

        #签名后上传
        self.sign_run_data(data=raw_data,a1=self.user.id,a2=self.user.school_id)
        _log.info(json.dumps(raw_data, indent=2, ensure_ascii=False))
        _log.info(json.dumps(headers))
        try:
            response = requests.post(
                url=self.UPLOAD_URL,
                headers=headers,
                json= raw_data
            )
            if response.ok:
                data = response.json()
                _log.info(data)
                return True
        except Exception as e:
            raise e
    def quick_run(self,username,password,mileage,end_time):
        try:
            client = LegymClient()
            user = client.login(username, password)
            _log.info(user.__str__())
            data = client.get_version()
            _log.info(data)
            data = client.get_current()
            _log.info(data)
            data = client.get_limit()
            _log.info(data)
            with open("./utils/legym/map.geojson", "r", encoding="utf-8") as f:
                content = f.read()
                data = client.upload(mileage=mileage, end_time=end_time, geojson_str=content)
                _log.info(data)
        except Exception as e:
            raise e



    def sign_run_data(self,data: dict, a1: str, a2: str) -> None:
        """
        data: dict, 包含上传跑步记录字段
        a1 semesterId, a2 schoolId: 用于生成加密 key
        """
        # 1️⃣ 构造 oct 对象（JSON 数据）
        oct_dict = {
            "tp": int(data["totalPart"]),
            "ep": int(data["effectivePart"]),
            "kt": int(data["keepTime"]),
            "em": float(data["effectiveMileage"]),
            "rt": str(data["type"]),
            "uer": str(data.get("uneffectiveReason", "")),
            "xq": str(data["semesterId"]),
            "dt": str(data["deviceType"]),
            "bf": float(data["paceRange"]),
            "bs": int(data["paceNumber"]),
            "zlc": float(data["totalMileage"]),
            "jf": int(data["scoringType"]),
            "et": str(data["endTime"]),
            "lid": str(data["limitationsGoalsSexInfoId"]),
            "kll": int(data["calorie"]),
            "app": str(data["appVersion"]),
            "ap": int(data["avePace"]),
            "lcs": float(data["gpsMileage"]),
            "st": str(data["startTime"]),
            "sv": str(data["systemVersion"]),
        }

        #JSON
        json_str = json.dumps(oct_dict, indent=2, ensure_ascii=False)
        formatted_json = re.sub(r": ", " : ", json_str)
        _log.info(formatted_json)
        #生成 dy_key
        dy_key = self.get_rn_key(a1, a2)

        #使用endTime和keepTime生成 sign_time
        end_dt = datetime.strptime(data["endTime"], "%Y-%m-%d %H:%M:%S")
        sign_timestamp = int(end_dt.timestamp()) + data["keepTime"] % 11
        sign_dt = datetime.fromtimestamp(sign_timestamp)
        data["signTime"] = sign_dt.strftime("%Y-%m-%d %H:%M:%S")
        #对 JSON 加密
        data["oct"] = encrypt_util.encrypt_aes_ecb_pkcs7(formatted_json, dy_key)

    def get_rn_key(self,a1: str, a2: str) -> str:
        dest = a1[3:6]
        v14 = a2[4:7]
        v13 = a1[9:12]
        return f"{dest}{v14}{v13}{self.RN_FIXED}"
