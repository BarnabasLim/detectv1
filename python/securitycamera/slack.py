import configparser
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
# import firebase_admin
# from firebase_admin import credentials


from slackclient import SlackClient
import io
import cv2

class Slack(object):

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

    def __init__(self, slackConfigFilePath, logger):
        self.config = configparser.ConfigParser()
        self.config.read(slackConfigFilePath)
        self.slack_token = self.ConfigSectionMap("Slack")['secrettoken']
        self.channel_id = self.ConfigSectionMap("Slack")['channelid']
        self.logger=logger

        self.sc = SlackClient(self.slack_token)
        self.sc.api_call(
            "chat.postMessage",
            channel=self.channel_id,
            text="Hello, I've been activated at {}".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

        )

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

    def clearFiles(self):
        result = self.sc.api_call("files.list",
                        channel=self.channel_id,
                        types="videos",
                        count=1000
                        )
        print("deleting {}".format(len(result["files"])))
        for file in result["files"]:
                print("Deleting file {}".format(file["id"]))
                deleteFileResult = self.sc.api_call("files.delete",
                             file=file["id"])
                print("result = {} Succeeded = {} ".format(deleteFileResult, deleteFileResult["ok"]))
                if not deleteFileResult["ok"]:
                    break

    def notifySlack(self, file, image_np, image_no_background):
        imageRgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        cv2.imshow("OpenCV/Numpy normal", image_np)
        plt.imshow(imageRgb)
        plt.imsave("./tmp/image_with_background.png", imageRgb)
        print("Movement detected at door for file={}".format(file) , imageRgb)
        plt.imsave("./tmp/image_no_background.png", image_no_background)
        print("Movement detected at door for file={}".format(file) , imageRgb)
        print("Movement detected at door for file={}".format(file) , imageRgb)
        try:
            self.sc.api_call(
                "chat.postMessage",
                channel=self.channel_id,
                text="Movement detected at door for file={}".format(file)

            )
        except Exception as e:
            self.logger.error(e)
        try:
            with open('./tmp/image_with_background.png', 'rb') as f:
                self.sc.api_call(
                    "files.upload",
                    channels=self.channel_id,
                    filename='snapshot1.png',
                    title='Detected Movement in restrited area',
                    initial_comment='Detected person by webcam. Is it anyone you know?',
                    file=io.BytesIO(f.read())
                )
        except Exception as e:
            self.logger.error(e)
        try:
            with open('./tmp/image_no_background.png', 'rb') as f:
                self.sc.api_call(
                    "files.upload",
                    channels=self.channel_id,
                    filename='snapshot2.png',
                    title='Detected Movement in restricted area',
                    initial_comment='Detected person by webcam. Is it anyone you know?',
                    file=io.BytesIO(f.read())
                )
        except Exception as e:
                self.logger.error(e)
        try:
            with open(file, 'rb') as f:
                self.sc.api_call(
                    "files.upload",
                    channels=self.channel_id,
                    filename=file,
                    title='Video with detected movement in restricted area',
                    initial_comment='Video with detected movement',
                    file=io.BytesIO(f.read())
                )
        except Exception as e:
                self.logger.error(e)