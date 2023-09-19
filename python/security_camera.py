import cv2
import re
import argparse
import time
import os
import logging
# from securitycamera.firebase import Firebase
from securitycamera.slack import Slack
from securitycamera.telegram import TelegramBot
from securitycamera.intruderdetector import IntruderDetector
# from securitycamera.training import Training


def setupLogger():
    # create logger with 'spam_application'
    myLogger = logging.getLogger('security_camera')
    myLogger.setLevel(logging.INFO)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('security_camera.log')
    fh.setLevel(logging.INFO)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    myLogger.addHandler(fh)
    myLogger.addHandler(ch)
    return myLogger


logger = setupLogger()
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()


# ap.add_argument("-d", "--directory", type=str, default ="/data/videos/incoming",
# 	help="path to optional input video directory")
ap.add_argument("-d", "--directory", type=str, default ="./micamshare",
	help="path to optional input video directory")

ap.add_argument("-i", "--input", type=str,
	help="path to optional input video file")

# ap.add_argument("-download", "--download-training", type=str,
# 	help="download training files")

# ap.add_argument("-training", "--training", type=str,
# 	help="start training")

ap.add_argument("-c","--clear-slack-files", action='store_true',
	help="clears files in slack")

ap.add_argument("-slack", "--slack-credentials", type=str, default="config.ini",
	help="path to optional slack configuration")

ap.add_argument("-telegram", "--telegram-credentials", type=str, default="config.ini",
	help="path to optional telegram configuration")

# ap.add_argument("-firebase", "--firebase-credentials", type=str, default="firebase_credentials.json",
# 	help="path to optional slack configuration")

ap.add_argument("-credentials", "--credentials-path", type=str, default="./credentials",
	help="path to optional folder for credentials")

ap.add_argument("-s", "--skip-frames", type=int, default=30,
	help="# of skip frames between detections")
args = vars(ap.parse_args())



def wait_for_video(directory, time_limit=3600, check_interval=60):
    '''Return next video file to process, if not keep checking once every check_interval seconds for time_limit seconds.
    time_limit defaults to 1 hour
    check_interval defaults to 1 minute
    '''

    now = time.time()
    last_time = now + time_limit

    while time.time() <= last_time:
        logger.info("Searching for new camera uploads")
        print("check directory", directory)
        for root, dirs, files in os.walk(directory):
            
            files = [fi for fi in files if fi.endswith(".mp4") and not fi.startswith(".")]
            print("check files detected", files)
            for file in files:
                filePath = os.path.join(root, file)

                if not os.path.isfile(filePath + '.processed') and \
                        os.path.getsize(filePath) > 0 and \
                        isValidVideoFile(filePath):
                    return filePath

        # Wait for check interval seconds, then check again.
        time.sleep(check_interval)

    return None



def isValidVideoFile(file):
    if not os.path.exists(file):
        return False
    cap = cv2.VideoCapture(file)
    totalFrameCount = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()
    return totalFrameCount > 0


def moveVideoToArchive(file):
    open(file + '.processed', 'w').close()

def wait_for_videos(slackCredentialsConfigPath,
                    telegramCredentualsConfigPath, 
                    # firebaseCredentialsPath, 
                    videosFolder):
    intruderDetector = IntruderDetector(slackCredentialsConfigPath,
                                        telegramCredentualsConfigPath 
                                        # firebaseCredentialsPath
                                        )
    while True:
        try:
            file = wait_for_video(videosFolder, 3600 * 354, 1)

            if file is None:
                continue

            result = intruderDetector.processFile(file)

            if result:
                moveVideoToArchive(file)
        except FileNotFoundError as e:
            logger.error(e)



logger.info("OpenCV version :  {0}".format(cv2.__version__))
# if a video path was not supplied, search for files in the given
# folder
credentialsPath = args.get("credentials_path")
slackCredentialsConfigPath = "{}/{}".format(credentialsPath, args.get("slack_credentials") )
telegramCredentialsConfigPath = "{}/{}".format(credentialsPath, args.get("telegram_credentials") )

# firebaseCredentialsPath = "{}/{}".format(credentialsPath, args.get("firebase_credentials") )

if args.get("clear_slack_files",False):
    slack = Slack(args.get(slackCredentialsConfigPath))
    slack.clearFiles()
# elif args.get("training", False):
#     trainingDir = args.get("training")
#     training = Training(trainingDir)
#     print("Get training")
# elif args.get("download_training", False):
#     destDir = args.get("download_training")
    # firebase = Firebase(firebaseCredentialsPath)
    # firebase.downloadImagesForTraining( destDir)
    # print("Download training")
elif not args.get("input", False):
    print("checking for new files")
    logger.info("[INFO] Checking for new incoming files")
    wait_for_videos(slackCredentialsConfigPath,
                    telegramCredentialsConfigPath,
                    # firebaseCredentialsPath, 
                    args.get("directory"))
else:
    file =  args["input"]
    intruderDetector = IntruderDetector(slackCredentialsConfigPath,
                                        telegramCredentialsConfigPath,
                                        # firebaseCredentialsPath, 
                                        debug=True)
    intruderDetector.processFile(file)