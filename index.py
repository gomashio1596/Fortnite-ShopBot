# -*- coding: utf-8 -*-
from util import Utility, ImageUtil, AuthUtil
from PIL import Image, ImageDraw
from math import ceil
import coloredlogs
import traceback
import datetime
import requests
import logging
import time
import json
import re

log = logging.getLogger(__name__)
coloredlogs.install(level="INFO", fmt="[%(asctime)s] %(message)s", datefmt="%I:%M:%S")

class ShopBot:
    def main(self):
        initialized = ShopBot.LoadConfig(ShopBot)
        if initialized:
            log.info("Fortnite-ShopBot")
            log.info("製作者: gomashio")
            log.info("参考: Athena")
            log.info("Getting ItemShop data...")
            data = json.loads(ShopBot.GET_ItemShop(self, api_key=self.api_key, language=self.language))
            date = Utility.ISOtoHuman(self, date=Utility.Now_ISO(self), dateformat=self.text_override['date'], hour=self.text_override['hour'], language=self.language)
            specialoffer = None
            if self.text_override['auto-specialoffer-convert']['enabled']:
                with requests.Session() as session:
                    specialoffer = AuthUtil.get_special_offer(self, session=session, email=self.text_override['auto-specialoffer-convert']['email'], password=self.text_override['auto-specialoffer-convert']['password'], user_agent=self.user_agent, language=self.language)
            if specialoffer is None:
                    specialoffer = self.text_override['auto-specialoffer-convert']['default']
            if data is not None and date is not None:
                log.info("Generating shop image...")
                Image = ShopBot.GenerateImage(self, data=data, date=date, text_override=self.text_override, specialoffer=specialoffer, namefont=self.namefont, categoryfont=self.categoryfont)
            else:
                log.error("Failed to get shop data")
            if Image:
                log.info("Success")
                if self.monitor_change_enabled:
                    ShopBot.MonitorChange(self)
                else:
                    exit()

    def LoadConfig(self) -> bool:
        log.debug("Loading config")
        config = json.loads(Utility.ReadFile(self, "config.json"))
        try:
            self.text_override = config['text-override']
            self.user_agent = self.text_override['auto-specialoffer-convert']['user-agent']
            self.monitor_change_enabled = config['monitor-change']
            self.language = config['text-override']['language']
            self.namefont = config['namefont']
            self.categoryfont = config['categoryfont']
            self.api_key = config['api-key']

            log.info("Loading configuration successful")
            return True
        except Exception as e:
            log.error(self, f"Failed to load config, {e}")
            return False

    def MonitorChange(self) -> bool:
        prevdata = json.loads(ShopBot.GET_ItemShop(self, api_key=self.api_key, language=self.language))
        prevdata_ = Utility.Split_Special(self, data=prevdata)
        prevdata_ = Utility.Extract_ItemShop(self, data=prevdata_)
        time.sleep(600)
        
        while True:
            data = json.loads(ShopBot.GET_ItemShop(self, api_key=self.api_key, language=self.language))
            data_ = Utility.Split_Special(self, data=data)
            data_ = Utility.Extract_ItemShop(self, data=data_)
            log.info("Checking ItemShop change...")
            if prevdata_ == data_:
                log.info("ItemShop changed")
                date = Utility.ISOtoHuman(self, date=Utility.Now_ISO(self), dateformat=self.text_override['date'], hour=self.text_override['hour'], language=self.language)
                specialoffer = None
                if self.text_override['auto-specialoffer-convert']['enabled']:
                    with requests.Session() as session:
                        specialoffer = AuthUtil.get_special_offer(self, session=session, email=self.text_override['auto-specialoffer-convert']['email'], password=self.text_override['auto-specialoffer-convert']['password'], user_agent=self.user_agent, language=self.language) 
                if specialoffer is None:
                    specialoffer = self.text_override['auto-specialoffer-convert']['default']
                if data is not None and date is not None:
                    log.info("Generating shop image...")
                    Image = ShopBot.GenerateImage(self, data=data, date=date, text_override=self.text_override, specialoffer=specialoffer, namefont=self.namefont, categoryfont=self.categoryfont)
                else:
                    log.error("Failed to get shop data")
                if Image:
                    log.info("Success")
            else:
                log.info("ItemShop nothing changed")
            time.sleep(600)

    def GET_ItemShop(self, api_key: str, language: str = "en") -> str:
        return Utility.GET(self, url="https://fortnite-api.com/shop/br", headers={"x-api-key": api_key}, params={"language": language}, timeout=(6.0, 15.0))

    def GenerateImage(self, data: dict, date: str, text_override: dict = {}, specialoffer: str = "Special Offers", namefont: str = "", categoryfont: str = "") -> bool:
        try:
            Splited = Utility.Split_Special(self, data=data)
            Sorted = Utility.Sort_Item(self, data=Splited)
            Overrided = Utility.Text_Override(self, data=Sorted, text_override=text_override['categories'])
            Extracted = Utility.Extract_ItemShop(self, Overrided)
            if len(Extracted['featured']) > 1 or len(Extracted['daily']) > 1 or len(Extracted['special']) > 1:
                if len(Extracted['special']) > 1:
                    rows = max( ceil(len(Extracted['featured']) / 4), ceil(len(Extracted['daily']) / 4), ceil(len(Extracted['special']) / 4) )
                    ShopImage = Image.new("RGBA", (3800, ((545 * rows) + 365)))
                else:
                    rows = max( ceil(len(Extracted['featured']) / 4), ceil(len(Extracted['daily']) / 4) )
                    ShopImage = Image.new("RGBA", (2550, ((545 * rows) + 365)))

                try:
                    background = ImageUtil.Open(self, "background.png")
                    background = ImageUtil.RatioResize(
                        self, background, ShopImage.width, ShopImage.height
                    )
                    ShopImage.paste(
                        background, ImageUtil.CenterX(self, background.width, ShopImage.width)
                    )
                except FileNotFoundError:
                    log.warning("Failed to open background.png")

                for num, unity in enumerate(Extracted.items()):
                    if len(unity[1]) > 1:
                        Unity = ShopBot.GenerateUnity(self, unity[1], namefont, categoryfont)
                        if Unity is not None:
                            canvas = ImageDraw.Draw(ShopImage)
                            font = ImageUtil.OpenFont(self, 48, namefont)
                            ShopImage.paste(
                                Unity,
                                ( (num * 1200) + ( (num + 1) * 50), 315 ),
                                Unity
                            )
                            if unity[0] != "special":
                                canvas.text(
                                    ( 50 + (num * 1250), 260 ),
                                    text_override.get(unity[0], unity[0].capitalize()),
                                    font=font
                                )
                            else:
                                canvas.text(
                                    ( 50 + (num * 1250), 260 ),
                                    specialoffer,
                                    font=font
                                )
                    else:
                        log.debug(f"{unity[0]} is None")
            else:
                ShopImage = Image.new("RGBA", (2550, 365))
                try:
                    background = ImageUtil.Open(self, "background.png")
                    background = ImageUtil.RatioResize(
                        self, background, ShopImage.width, ShopImage.height
                    )
                    ShopImage.paste(
                        background, ImageUtil.CenterX(self, background.width, ShopImage.width)
                    )
                except FileNotFoundError:
                    log.warning("Failed to open background.png")

                canvas = ImageDraw.Draw(ShopImage)
                font = ImageUtil.OpenFont(self, 48, namefont)
                canvas.text(
                    (50, 260),
                    text_override.get("featured", "Featured"),
                    font=font
                )
                canvas.text(
                    (1300, 260),
                    text_override.get("daily", "Daily"),
                    font=font
                )
                log.info("Shop is None")

            try:
                logo = ImageUtil.Open(self, "logo.png").convert("RGBA")
                logo = ImageUtil.RatioResize(self, logo, 0, 210)
                ShopImage.paste(
                    logo, ImageUtil.CenterX(self, logo.width, ShopImage.width), logo
                )
            except FileNotFoundError:
                log.warning("Failed to open logo.png")

            font = ImageUtil.OpenFont(self, 40, namefont)
            canvas.text(
                (5, 5),
                date,
                font=font
            )

            ShopImage.save("itemshop.png")
            return True
        except Exception as e:
            log.error(self, f"Failed to generate image, {e}")
            return False

    def GenerateUnity(self, unities: dict, namefont: str, categoryfont: str) -> ("PIL Image", None):
        Unity=Image.new("RGBA", (1200, -(-len(unities) // 4) * 545))
        if Unity is not None:
            num=1
            line=1
            for card in unities:
                Card = ShopBot.GenerateCard(self, card, namefont, categoryfont).convert("RGBA")
                Unity.paste(
                    Card,
                    ((num - 1) * 300, (line - 1) * 545),
                    Card
                )
                if num % 4 == 0:
                    num=1
                    line+=1
                else:
                    num+=1
            return Unity
        else:
            log.error("Failed to generate unity")
            return None
        
    def GenerateCard(self, card: dict, namefont: str, categoryfont: str) -> ("PIL Image", None):
        Card=Image.new("RGB", (300, 545))

        name = card["items"][0]["name"]
        category = card["items"][0]["type"]
        displaycategory = card["items"][0]["displayType"]
        rarity = card["items"][0]["rarity"]
        backend_rarity = card["items"][0]["backendRarity"].replace("EFortRarity::","",1).lower()
        regularprice = card["regularPrice"]
        finalprice = card["finalPrice"]
        regularprice = str(f"{regularprice:,}")
        finalprice = str(f"{finalprice:,}")
        banner = card["banner"]

        if category == "outfit" or category == "wrap" or category == "banner":
            if card["items"][0]["images"]["featured"] is not None:
                icon = card["items"][0]["images"]["featured"]["url"]
            else:
                log.debug("featured image not found, changing to icon")
                icon = card["items"][0]["images"]["icon"]["url"]
        else:
            icon = card["items"][0]["images"]["icon"]["url"]

        icon = ImageUtil.GET_Image(self, icon).convert("RGBA")
        if category == "backpack" or category == "pickaxe" or category == "glider" or category == "wrap" or category == "music":
            icon = ImageUtil.RatioResize(self, icon, Card.width // 1.6, Card.height // 1.6)
        else:
            icon = ImageUtil.RatioResize(self, icon, Card.width, Card.height)
        try:
            try:
                image = ImageUtil.Open(
                    self,
                    f"color_{rarity}.png").convert("RGBA").resize((Card.width, Card.height)
                ).convert("RGBA")
            except FileNotFoundError as e:
                log.warning(f"Rarity {rarity} not found, defaulted to backend {backend_rarity}")
                image = ImageUtil.Open(self,
                    f"color_{backend_rarity}.png").convert("RGBA").resize((Card.width, Card.height)
                ).convert("RGBA")
            Card.paste(image, (0, 0), image)
            if category == "backpack" or category == "pickaxe" or category == "glider" or category == "wrap" or category == "music":
                Card.paste( icon, ImageUtil.CenterX(self, icon.width, Card.width, icon.width // 6), icon )
            else:
                Card.paste( icon, ImageUtil.CenterX(self, icon.width, Card.width), icon )
            image = ImageUtil.Open(self, f"card_plate_{rarity}.png").convert("RGBA")
            Card.paste(image, (0, 0), image)
            image = ImageUtil.Open(self, f"card_mask_{rarity}.png").convert("RGBA")
            Card.paste(image, (0, 0), image)

            canvas = ImageDraw.Draw(Card)
            font = ImageUtil.OpenFont(
                self,
                ImageUtil.FontSize(self, Card.width, 28, name),
                namefont
            )
            textwidth, _ = font.getsize(f"{name}")
            canvas.text(
                ImageUtil.CenterX(self, textwidth, Card.width, 430),
                f"{name}",
                font=font
            )
            font = ImageUtil.OpenFont(
                self,
                ImageUtil.FontSize(self, Card.width, 20, category),
                categoryfont
            )
            textwidth, _ = font.getsize(f"{displaycategory}")
            canvas.text(
                ImageUtil.CenterX(self, textwidth, Card.width, 458),
                f"{displaycategory}",
                (160, 160, 160),
                font=font
            )

            vbucks = ImageUtil.Open(self, "vbucks.png")
            vbucks = ImageUtil.RatioResize(self, vbucks, 35, 35)
            if regularprice == finalprice:
                regularfont = ImageUtil.OpenFont(
                    self,
                    28,
                    categoryfont
                )
                textWidth, _ = font.getsize(regularprice)
                canvas.text(
                    ImageUtil.CenterX(self, ((textWidth - 5) - vbucks.width), Card.width, 494),
                    regularprice,
                    font=regularfont
                )

                Card.paste(
                    vbucks,
                    ImageUtil.CenterX(self, (vbucks.width + (textWidth + 5)), Card.width, 499),
                    vbucks
                )
            else:
                finalfont = ImageUtil.OpenFont(
                    self,
                    28,
                    categoryfont
                )
                regularfont = ImageUtil.OpenFont(
                    self,
                    22,
                    categoryfont
                )
                regularWidth, regularHeight = regularfont.getsize(regularprice)
                Width, Height = regularfont.getsize(regularprice.replace(","," "))
                finalWidth, finalHeight = finalfont.getsize(finalprice)
                discount = ImageUtil.Open(self, "discount.png")
                discount = discount.resize(( Width, Height - 5))
                canvas.text(
                    ImageUtil.CenterX(self, ((finalWidth + regularWidth - 5) - vbucks.width), Card.width, 494),
                    finalprice,
                    font=finalfont
                )
                Card.paste(
                    vbucks,
                    ImageUtil.CenterX(self, (vbucks.width + (finalWidth + regularWidth + 5)), Card.width, 499),
                    vbucks
                )

                pos = ImageUtil.CenterX(self, (finalWidth + regularWidth - 5) - vbucks.width, Card.width, 499)
                canvas.text(
                    (pos[0] + 60, pos[1]),
                    regularprice,
                    (160, 160, 160),
                    font=regularfont
                )
                pos2 = ImageUtil.CenterX(self, (finalWidth + regularWidth - 5) - vbucks.width, Card.width, 497 + (discount.height // 2))
                Card.paste(
                    discount,
                    (pos2[0] + 60, pos2[1]),
                    discount
                )

            if banner is not None:
                font = ImageUtil.OpenFont(
                    self,
                    20,
                    namefont
                )
                bannerWidth, bannerHeight = font.getsize(banner)
                banner_middle = ImageUtil.Open(self, "banner_middle.png").convert("RGBA")
                banner_middle = banner_middle.resize((bannerWidth + 45, 35))
                banner_rear = ImageUtil.Open(self, "banner_rear.png").convert("RGBA")
                banner_rear = ImageUtil.RatioResize_NoAA(self, banner_rear, 0, 35)
                banner_front = ImageUtil.Open(self, "banner_front.png").convert("RGBA")
                banner_front = banner_front.resize((bannerWidth + 45, 35))
                Card.paste(
                    banner_middle,
                    (0, 0),
                    banner_middle
                )
                Card.paste(
                    banner_rear,
                    (0, 0),
                    banner_rear
                )
                Card.paste(
                    banner_front,
                    (0 , 0),
                    banner_front
                )
                canvas.text(
                    (8, 8),
                    banner,
                    font=font
                )

            return Card
        except Exception as e:
            log.error(self, f"Failed to generate card, {e}")
            return None

if __name__ == "__main__":
    ShopBot.main(ShopBot)
