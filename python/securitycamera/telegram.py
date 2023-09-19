import configparser
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime


import telegram
from telegram import InputMediaPhoto, InputMediaVideo

import io
import cv2

class TelegramBot(object):

    def ConfigSectionMap(self,section):
        dict1 = {}
        options = self.config.options(section)
        print(options)
        for option in options:
            try:
                dict1[option] = self.config.get(section, option)
                if dict1[option] == -1:
                    print("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1

    def __init__(self, telegramConfigFilePath, 
                 logger=None):
        self.config = configparser.ConfigParser()
        self.config.read(telegramConfigFilePath)
        self.token = self.ConfigSectionMap("Telegram")['secrettoken']
        self.channel_id = self.ConfigSectionMap("Telegram")['channelid']
        print("check token {} check channel {}".format(self.token,self.channel_id))
        self.bot = telegram.Bot(token = self.token)
        self.bot.send_message(
            chat_id=self.channel_id, 
            text="Hello, I've been activated at {}".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        )
        self.logger=logger

    def ConfigSectionMap(self,section):
        dict1 = {}
        options = self.config.options(section)
        print(options)
        for option in options:
            try:
                dict1[option] = self.config.get(section, option)
                if dict1[option] == -1:
                    print("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1

    # def clearFiles(self):
    #     result = self.bot.api_call("files.list",
    #                     channel=self.channel_id,
    #                     types="videos",
    #                     count=1000
    #                     )
    #     print("deleting {}".format(len(result["files"])))
    #     for file in result["files"]:
    #             print("Deleting file {}".format(file["id"]))
    #             deleteFileResult = self.bot.api_call("files.delete",
    #                          file=file["id"])
    #             print("result = {} Succeeded = {} ".format(deleteFileResult, deleteFileResult["ok"]))
    #             if not deleteFileResult["ok"]:
    #                 break

    def notifyTelegram(self, file, image_np, image_no_background):
        # imageRgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        imageRgb=image_np
        plt.imsave("./tmp/image_with_background.png", imageRgb)
        plt.imsave("./tmp/image_no_background.png", image_no_background)
        try:
            self.bot.send_message(
                chat_id=self.channel_id,
                text="Movement detected at door for file={}".format(file)
            )
        except Exception as e:
            self.logger.error(e)
        try:
            imgList = []
            imgList.append(InputMediaPhoto(open('./tmp/image_with_background.png', 'rb'), caption = 'Detected person by webcam. Is it anyone you know?'))
            imgList.append(InputMediaPhoto(open('./tmp/image_no_background.png', 'rb'), caption = 'Detected person by webcam. Is it anyone you know?'))
            self.bot.send_media_group(
                chat_id=self.channel_id,
                media=imgList
            )
        except Exception as e:
            self.logger.error(e)
        try:
            vid_media=[]
            with open(file, 'rb') as f:
                data = f.read()
                media = InputMediaVideo(data)
                vid_media.append(media)
            vid_media[len(vid_media)-1].caption='Detected person by webcam. Is it anyone you know?'
            self.bot.send_media_group(
                chat_id=self.channel_id,
                media=vid_media
            )
        except Exception as e:
            self.logger.error(e)