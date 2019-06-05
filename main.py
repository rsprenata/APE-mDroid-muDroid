import os
from time import sleep
from PIL import Image
import subprocess
from image_checker import checkSimilarPictures

STATUS_BAR_CROP_HEIGHT = 80
SCREEN_CPATURE_DELAY = 0.2
SCREENSHOTS_DIRECTORY = '/home/juniorrek/eclipse-workspace/ScreenShooter2000/src/'

def analyze_results(file_name1, file_name2):
    image1 = os.path.join(SCREENSHOTS_DIRECTORY, file_name1)
    image2 = os.path.join(SCREENSHOTS_DIRECTORY, file_name2)
    
    similar, crashed = checkSimilarPictures(image1, image2)
    
    return similar

def captureScreen(pic_name, path):
    image_path = os.path.join(path, pic_name)
    device_path = '/sdcard/%s' % pic_name
    sleep(SCREEN_CPATURE_DELAY)
    command = ['adb', 'shell', "screencap -p", device_path]
    subprocess.call(command)
    command = ['adb', 'pull', device_path, image_path]
    subprocess.call(command)

    while not os.path.isfile(image_path):
        sleep(0.1)

    command = ['adb', 'shell', 'rm', device_path]
    subprocess.call(command)
    img = Image.open(image_path)
    w, h = img.size
    img.crop((0, STATUS_BAR_CROP_HEIGHT, w, h)).save(image_path)
    return image_path

def main():
    raw_input("Pressione ENTER para tirar a primeira foto...")
    captureScreen('pic_name1.png', SCREENSHOTS_DIRECTORY)
    raw_input("Pressione ENTER para tirar a segunda foto...")
    captureScreen('pic_name2.png', SCREENSHOTS_DIRECTORY)
    similar = analyze_results('pic_name1.png', 'pic_name2.png')
    if similar:
        print 'Imagens iguais'
    else:
        print 'Imagens diferentes'

if __name__ == '__main__':
    main()