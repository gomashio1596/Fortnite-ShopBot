# -*- coding: utf-8 -*-
from PIL import Image, ImageFont
from typing import Union
import traceback
import datetime
import requests
import logging
import locale
import json
import io
import os
import re

log = logging.getLogger(__name__)

class Utility:
    def ReadFile(self, filename: str, directory: str = "") -> (str, None):
        try:
            log.debug(f"Loading file {directory}{filename}")
            with open(f"{directory}{filename}", "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            log.error(self, f"Failed to read {directory}{filename}, {e}")
            return None

    def GET(self, url: str, headers: dict = {}, params: dict = {}, timeout: Union[int, float, tuple] = 0) -> (str, None):
        res = requests.get(url, headers=headers, params=params, timeout=timeout)
        log.debug(f"GET {url} {str(headers)} [{res.status_code}]")

        if res.status_code == 200:
            return res.text
        else:
            log.critical(f"Failed to GET {url} [{res.status_code}]")
            return None

    def Now_ISO(self) -> str:
        nowiso = datetime.datetime.utcnow().isoformat().split('.')[0]
        log.debug(f"nowiso {nowiso}")
        return nowiso

    def ISOtoHuman(self, date: str, dateformat: str = "%A, %B %-d, %Y %H:%M:%S", hour: int = 0, language: str = "en") -> (str, None):
        log.debug(f"Converting time {date} to {language}, +{hour}")
        try:
            locale.setlocale(locale.LC_ALL, language)
        except locale.Error:
            log.warning(f"Unsupported locale configured, using system default")

        try:
            return (datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=hour)).strftime(dateformat.replace("%#d","%-d"))
        except ValueError:
            try:
                return (datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S") + datetime.timedelta(hours=hour)).strftime(dateformat.replace("%-d","%#d"))
            except Exception as e:
                log.error(self, f"Failed to convert to human-readable time, {e}")
                return None

    def Split_Special(self, data: dict) -> (dict, None):
        Result = {"featured": [], "daily": [], "special": []}
        log.debug(f"Spliting Special, featured: {len(data['data']['featured'])} daily: {len(data['data']['daily'])}")
        try:
            if len(data['data']['featured']) > 1:
                for card in data['data']['featured']:
                    if card['isSpecial']:
                        Result['special'].append(card)
                    else:
                        Result['featured'].append(card)
            if len(data['data']['daily']) > 1:
                for card in data['data']['daily']:
                    if card['isSpecial']:
                        Result['special'].append(card)
                    else:
                        Result['daily'].append(card)
            return Result
        except Exception as e:
            log.error(self, f"Failed to split special, {e}")
            return None

    def Sort_Item(self, data: dict) -> (dict, None):
        Result = {"featured": [], "daily": [], "special": []}
        log.debug(f"Sorting item, featured: {len(data['featured'])} daily: {len(data['daily'])} special: {len(data['special'])}")
        try:
            if len(data['featured']) > 1:
                sortPriority=[]
                featured=[]
                for num, card in enumerate(data['featured']):
                    sortPriority.append((card['sortPriority'], num))
                SortedPriority=sorted(sortPriority, key=lambda x:x[0])
                for num, card in enumerate(data['featured']):
                    for sort in SortedPriority:
                        if sort[1] == num:
                            featured.append(card)
                Result['featured']=featured
            if len(data['daily']) > 1:
                sortPriority=[]
                daily=[]
                for num, card in enumerate(data['daily']):
                    sortPriority.append((card['sortPriority'], num))
                SortedPriority=sorted(sortPriority, key=lambda x:x[0])
                for num, card in enumerate(data['daily']):
                    for sort in SortedPriority:
                        if sort[1] == num:
                            daily.append(card)
                Result['daily']=daily
            if len(data['special']) > 1:
                sortPriority=[]
                special=[]
                for num, card in enumerate(data['special']):
                    sortPriority.append((card['sortPriority'], num))
                SortedPriority=sorted(sortPriority, key=lambda x:x[0])
                for num, card in enumerate(data['special']):
                    for sort in SortedPriority:
                        if sort[1] == num:
                            special.append(card)
                Result['special'] = special
            return Result
        except Exception as e:
            log.error(self, f"Failed to sort item, {e}")
            return None

    def Text_Override(self, data: dict, text_override: dict) -> (dict, None):
        Result = data
        log.debug(f"Overriding text, featured: {len(data['featured'])} daily: {len(data['daily'])} special: {len(data['special'])}")
        try:
            if len(Result['featured']) > 1:
                for card in Result['featured']:
                    for item in card['items']:
                        for category, text in text_override.items():
                            if item['type'] == category:
                                item['displayType'] = text
                                log.debug(f"Overided {item['type']} -> {text}")
            if len(Result['daily']) > 1:
                for card in Result['daily']:
                    for item in card['items']:
                        for category, text in text_override.items():
                            if item['type'] == category:
                                item['displayType'] = text
                                log.debug(f"Overided {item['type']} -> {text}")
            if len(Result['special']) > 1:
                for card in Result['special']:
                    for item in card['items']:
                        for category, text in text_override.items():
                            if item['type'] == category:
                                item['displayType'] = text
                                log.debug(f"Overided {item['type']} -> {text}")
            return Result
        except Exception as e:
            log.error(self, f"Failed to override text, {e}")
            return None

    def Extract_ItemShop(self, data: dict) -> (dict, None):
        try:
            log.debug("Extracting data...")
            Extracted = {"featured": [], "daily": [], "special": []}
            if len(data['featured']) > 1:
                for num, card in enumerate(data['featured']):
                    Extracted['featured'].append({"regularPrice": card['regularPrice'], "finalPrice": card['finalPrice'], "banner": card['banner'], "items": []})
                    for item in card['items']:
                        Extracted['featured'][num]['items'].append({"name": item['name'], "type": item['type'], "displayType": item.get('displayType', item['type']), "rarity": item['rarity'], "backendRarity": item['backendRarity'], "images": item['images']})
            if len(data['daily']) > 1:
                for num, card in enumerate(data['daily']):
                    Extracted['daily'].append({"regularPrice": card['regularPrice'], "finalPrice": card['finalPrice'], "banner": card['banner'], "items": []})
                    for item in card['items']:
                        Extracted['daily'][num]['items'].append({"name": item['name'], "type": item['type'], "displayType": item.get('displayType', item['type']), "rarity": item['rarity'], "backendRarity": item['backendRarity'], "images": item['images']})
            if len(data['special']) > 1:
                for num, card in enumerate(data['special']):
                    Extracted['special'].append({"regularPrice": card['regularPrice'], "finalPrice": card['finalPrice'], "banner": card['banner'], "items": []})
                    for item in card['items']:
                        Extracted['special'][num]['items'].append({"name": item['name'], "type": item['type'], "displayType": item.get('displayType', item['type']), "rarity": item['rarity'], "backendRarity": item['backendRarity'], "images": item['images']})
            return Extracted
        except Exception as e:
            log.error(self, f"Failed to GET ItemShop data, {e}")
            return None

class ImageUtil:
    def Open(self, filename: str, directory: str = "assets/images/") -> "Image":
        return Image.open(f"{directory}{filename}")

    def OpenFont(self, size: int, font: str = "LuckiestGuy-Regular.ttf",directory: str = "assets/fonts/",) -> "Font":
        try:
            return ImageFont.truetype(f"{directory}{font}", size)
        except OSError:
            log.warning(f"{directory}{font} not found, change font to LuckiestGuy-Regular.ttf")
            return ImageFont.truetype(f"{directory}LuckiestGuy-Regular.ttf", size)
        except Exception as e:
            log.error(f"Failed to load font, {e}")

    def GET_Image(self, url: str) -> "Image":
        res = requests.get(url, stream=True)
        
        if res.status_code == 200:
            return Image.open(res.raw)
        else:
            print(f"Failed to GET {url} [{res.status_code}]")
            return None

    def RatioResize(self, image: Image.Image, maxWidth: int, maxHeight: int) -> "Image":
        ratio = max(maxWidth / image.width, maxHeight / image.height)

        return image.resize( (int(image.width * ratio), int(image.height * ratio)), Image.ANTIALIAS )

    def RatioResize_NoAA(self, image: Image.Image, maxWidth: int, maxHeight: int) -> "Image":
        ratio = max(maxWidth / image.width, maxHeight / image.height)

        return image.resize( (int(image.width * ratio), int(image.height * ratio)) )

    def CenterX(self, foregroundWidth: int, backgroundWidth: int, distanceTop: int = 0) -> tuple:
        return (int(backgroundWidth / 2) - int(foregroundWidth / 2), distanceTop)

    def FontSize(self, imagewidth: int, maxsize: int, text: str) -> int:
        return min( maxsize, ( (imagewidth - 40) // len(text) ) )

base = "https://www.epicgames.com"
base_public_service = "https://account-public-service-prod03.ol.epicgames.com"
launcher_token = "MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE=" 
fortnite_token = "ZWM2ODRiOGM2ODdmNDc5ZmFkZWEzY2IyYWQ4M2Y1YzY6ZTFmMzFjMjExZjI4NDEzMTg2MjYyZDM3YTEzZmM4NGQ="

class AuthUtil:
    def get_device_auth_details(self) -> dict:
        if os.path.isfile("device_auths.json"):
            with open("device_auths.json", "r") as fp:
                return json.load(fp)
        return {}

    def store_device_auth_details(self, email: str, details: dict) -> None:
        existing = AuthUtil.get_device_auth_details(self)
        existing[email] = details
        with open("device_auths.json", "w") as fp:
            json.dump(existing, fp)

    def email_and_password_auth(self, session: requests.sessions.Session, email: str, password: str) -> requests.models.Response:
        session.get(f"{base}/id/api/csrf")
        res = session.post(
            f"{base}/id/api/login", 
            headers={
                "x-xsrf-token": session.cookies.get("XSRF-TOKEN")
            },
            data={
                "email": email,
                "password": password,
                "rememberMe": False,
                "captcha": ""
            },
            cookies=session.cookies
        )
        return res

    def exchange_code_auth(self, session: requests.sessions.Session, email: str) -> requests.models.Response:
        res = session.post(
            "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token",
            headers={
                "Authorization": f"basic {launcher_token}"
            },
            data={
                "grant_type": "exchange_code",
                "exchange_code": input(f"Enter exchange code for {email}: "),
                "token_type": "eg1"
            }
        )
        return res

    def device_auth(self, session: requests.sessions.Session, deviceId: str, accountId: str, secret: str) -> requests.models.Response:
        res = session.post(
            "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token",
            headers={
                "Authorization": f"basic {launcher_token}"
            },
            data={
                "grant_type": "device_auth",
                "device_id": deviceId,
                "account_id": accountId,
                "secret": secret,
                "token_type": "eg1"
            }
        )
        return res

    def generate_device_auth(self, session: requests.sessions.Session, client_id: str, launcher_access_token: str, user_agent: str) -> requests.models.Response:
        res = session.post(
            f"https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{client_id}/deviceAuth",
            headers={
                "Authorization": f"Bearer {launcher_access_token}",
                "User-Agent": user_agent
            }
        )
        return res

    def authenticate(self, session: requests.sessions.Session, email: str, password: str, user_agent: str) -> str:
        session.get(f"{base}/id/api/csrf")
        device_auth_details=AuthUtil.get_device_auth_details(self).get(email, {})
        if os.path.isfile("device_auths.json") is False or device_auth_details == {}:
            res = AuthUtil.email_and_password_auth(self, session, email, password)
            log.debug(f"\nemail_and_password_auth")
            log.debug(res.status_code)
            log.debug(res.text)

            if res.status_code == 409:
                return AuthUtil.authenticate(self, session, email, password, user_agent)

            if res.status_code == 431:
                session.get(f"{base}/id/api/csrf")
                res = session.post(
                    f"{base}/id/api/login/mfa",
                    headers={
                        "x-xsrf-token": session.cookies.get("XSRF-TOKEN")
                    },
                    data={
                        "code": input("Please enter the 2fa code: "),
                        "method": "authenticator",
                        "rememberDevice": False
                    },
                    cookies=session.cookies
                )

                if res.status_code == 400:
                    raise ValueError("Wrong 2fa code entered.")

            if not res.status_code == 400:
                res = session.get(
                    f"{base}/id/api/exchange", 
                    headers={
                        "x-xsrf-token": session.cookies.get("XSRF-TOKEN")
                    },
                    cookies=session.cookies
                )
                exchange_code_ = res.json()["code"]

                res = session.post(
                    f"{base_public_service}/account/api/oauth/token", 
                    headers={
                        "Authorization": f"basic {launcher_token}"
                    },
                    data={
                        "grant_type": "exchange_code",
                        "exchange_code": exchange_code_,
                        "token_type": "eg1"
                    }
                )
                client_id=res.json()["account_id"]
                launcher_access_token = res.json()["access_token"]
                res = AuthUtil.generate_device_auth(self, session, client_id, launcher_access_token, user_agent)
                if res.status_code == 200:
                    details={"deviceId": res.json().get("deviceId"), "accountId": res.json().get("accountId"), "secret": res.json().get("secret")}
                    AuthUtil.store_device_auth_details(self, email, details)

            if res.status_code == 400:
                res = AuthUtil.exchange_code_auth(self, session, email)
                log.debug(f"\nexchange_code_auth")
                log.debug(res.status_code)
                log.debug(res.text)

                if res.status_code == 400:
                    raise ValueError("Wrong exchange_code entered.")

                if res.status_code == 200:
                    launcher_access_token = res.json()["access_token"]
                    client_id = res.json()["account_id"]
                    res = AuthUtil.generate_device_auth(self, session, client_id, launcher_access_token, user_agent)

                    if res.status_code == 200:
                        details={"deviceId": res.json().get("deviceId"), "accountId": res.json().get("accountId"), "secret": res.json().get("secret")}
                        AuthUtil.store_device_auth_details(self, email, details)
        else:
            res = AuthUtil.device_auth(self, session, **device_auth_details)
            log.debug(f"\ndevice_auth")
            log.debug(res.status_code)
            log.debug(res.text)

            if res.status_code == 400:
                raise ValueError("Wrong device auth detail entered.")

            if res.status_code == 200:
                launcher_access_token = res.json()["access_token"]

        return launcher_access_token

    def get_special_offer(self, session: requests.sessions.Session, email: str, password: str, user_agent: str, language: str) -> (str, None):
        launcher_access_token = AuthUtil.authenticate(self, session, email, password, user_agent)
        data = io.StringIO(
            session.get(
                "https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/cloudstorage/system/a22d837b6a2b46349421259c0a5411bf",
                headers={
                    "Authorization": f"Bearer {launcher_access_token}"
                }
            ).text
        ).readlines()

        for text in data:
            if ('Key="AC1E7A1349AB80D63BFF31A642006C54"' in text) or ('NativeString="Special Featured"' in text):
                text=text
                break
        
        match = re.search(r'LocalizedStrings=.+', text)
        if match is not None:
            match = eval(match.group(0).replace("LocalizedStrings=","",1).replace(")","",1), globals())
            for i in match:
                if i[0] == language:
                    match = i[1]
            log.info(f"Special Offer: {match}")
            return match
        else:
            log.info(f"Special Offer: None")
            return None