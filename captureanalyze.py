import os
from time import sleep
from PIL import Image
import subprocess
from image_checker import checkSimilarPictures
import argparse
import logging
from datetime import datetime

#Argumentos default
_D_PATHAPKS = '/home/juniorrek/benchmark/TippyTipperMutantsAPKs/'
_D_ORIGINAL = 'TippyTipper-debug0.apk'
_D_PACKAGE = 'net.mandaria.tippytipper'
_D_CNAME = 'TippyTipper'

#Preparar os argumentos
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--pathapks", default=_D_PATHAPKS, help="Pasta com os apks, mutantes e original")
ap.add_argument("-o", "--original", default=_D_ORIGINAL, help="Nome do apk original")
ap.add_argument("-pk", "--package", default=_D_PACKAGE, help="Package do androidmanifest")
ap.add_argument("-cn", "--cname", default=_D_CNAME, help="Nome em comum dos apks mutantes")
args = vars(ap.parse_args())

#Parametros screenshot
STATUS_BAR_CROP_HEIGHT = 80
SCREEN_CPATURE_DELAY = 0.2

def analyze_results(basepath, file_name1, file_name2):
    image1 = os.path.join(basepath, file_name1)
    image2 = os.path.join(basepath, file_name2)
    
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
    #le os apks da pasta
    basepath = args["pathapks"]
    original = args["original"]
    package = args["package"]
    cname = args["cname"]
    
    #configura log
    logging.basicConfig(filename=basepath+'log_analise.log', level=logging.INFO)
    logging.info('ANALISE INICIADA '+datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    logging.info('Mutante original ' + original)
    
    #cria pasta screenshots
    if not os.path.exists(basepath + 'Screenshots/'):
        os.makedirs(basepath + 'Screenshots/')
    
    #instala aplicativo no emulador,
    #passar endereco onde esta o apk (original ou mutante):
    os.system('adb install -r ' + basepath + original)

    #executa monkey, ele cria caso de teste com a semente e executa no emulador, 
    #eh necessario passar o package que esta localizado no arquivo Androidmanifest.xml:
    os.system('timeout 1h adb shell monkey --throttle 200 -p '+package+' -s 1000 -v 250 --ignore-crashes --ignore-timeouts --ignore-security-exceptions > monkey.log')
    captureScreen(original + '.png', basepath + 'Screenshots/')

    for mutante in os.listdir(basepath):
        if mutante.startswith( cname ) and mutante != original:
            os.system('adb install -r ' + basepath + mutante)
            os.system('timeout 1h adb shell monkey --throttle 200 -p '+package+' -s 1000 -v 250 --ignore-crashes --ignore-timeouts --ignore-security-exceptions > monkey.log')
            captureScreen(mutante + '.png', basepath + 'Screenshots/')
            similar = analyze_results(basepath + 'Screenshots/', original + '.png', mutante + '.png')
            if similar:
                logging.info('Mutante: ' + mutante + ";Situacao: VIVO")
                print 'Imagens iguais'
            else:
                logging.info('Mutante: ' + mutante + ";Situacao: MORTO")
                print 'Imagens diferentes' 
            break;

if __name__ == '__main__':
    main()