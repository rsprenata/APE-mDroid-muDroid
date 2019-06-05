import os
from time import sleep
from PIL import Image
import subprocess
from image_checker import checkSimilarPictures
import argparse
import logging
from datetime import datetime
import re

#Argumentos default
_D_PATHAPKS = '/home/juniorrek/benchmark/TippyTipperMutantsAPKs/'
_D_ORIGINAL = 'TippyTipper-debug0.apk'
_D_PACKAGE = 'net.mandaria.tippytipper'
_D_CNAME = 'TippyTipper'
_D_LOGPATH = '/home/juniorrek/benchmark/net.mandaria.tippytipper-mutants.log'

#Preparar os argumentos
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--pathapks", default=_D_PATHAPKS, help="Pasta com os apks, mutantes e original")
ap.add_argument("-o", "--original", default=_D_ORIGINAL, help="Nome do apk original")
ap.add_argument("-pk", "--package", default=_D_PACKAGE, help="Package do androidmanifest")
ap.add_argument("-cn", "--cname", default=_D_CNAME, help="Nome em comum dos apks mutantes")
ap.add_argument("-lp", "--logpath", default=_D_LOGPATH, help="Path do log dos operadores dos mutantes gerado pelo MDroidPlus")
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

def operadorMutante(logpath, nmutante):
    mutante = 'Mutant ' + nmutante;
    
    #Encontra linha
    with open(logpath, 'r') as f:
        while True:
            linha = f.readline();
            if not linha:
                linha = 'Nao encontrado';
                break;
            elif mutante in linha:
                linha = linha;
                break;
            
    #Encontra o operador
    if linha != 'Nao encontrado':
        operador = re.search("(?<=; ).*(?= in)", linha)
        return operador.group();
    
    return linha;

def main():
    #le os apks da pasta
    basepath = args["pathapks"]
    original = args["original"]
    package = args["package"]
    cname = args["cname"]
    logpath = args["logpath"]
    
    #configura log
    logging.basicConfig(filename=basepath+'log_analise.log', level=logging.INFO)
    logging.info('ANALISE INICIADA '+datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    logging.info('Original: ' + original)
    
    #cria pasta screenshots
    if not os.path.exists(basepath + 'Screenshots/'):
        os.makedirs(basepath + 'Screenshots/')
    
    #instala aplicativo no emulador,
    #passar endereco onde esta o apk (original ou mutante):
    os.system('adb uninstall ' + package)
    os.system('adb install  ' + basepath + original)

    #executa monkey, ele cria caso de teste com a semente e executa no emulador, 
    #eh necessario passar o package que esta localizado no arquivo Androidmanifest.xml:
    os.system('timeout 1h adb shell monkey --throttle 200 -p '+package+' -s 1000 -v 250 --ignore-crashes --ignore-timeouts --ignore-security-exceptions > monkey.log')
    sleep(1)
    captureScreen(original + '.png', basepath + 'Screenshots/')
    
    #variavel que guarda a quantidade de mortos e vivos por operador
    grupo = {}

    total = 0
    mortos = 0
    for mutante in os.listdir(basepath):
        if mutante.startswith( cname ) and mutante != original:
            os.system('adb uninstall ' + package)
            os.system('adb install ' + basepath + mutante)
            os.system('timeout 1h adb shell monkey --throttle 200 -p '+package+' -s 1000 -v 250 --ignore-crashes --ignore-timeouts --ignore-security-exceptions > monkey.log')
            sleep(1)
            captureScreen(mutante + '.png', basepath + 'Screenshots/')
            similar = analyze_results(basepath + 'Screenshots/', original + '.png', mutante + '.png')
            nmutante = re.search("\d+(?=\.apk)", mutante)
            operador = operadorMutante(logpath, nmutante.group())
            
            #se ainda nao comecou a contar operador
            if operador not in grupo:
                grupo[operador] = {}
                grupo[operador]['vivo'] = 0
                grupo[operador]['morto'] = 0
            
            if similar:
                logging.info('Mutante: ' + mutante + ";Situacao: VIVO" + ";Operador: " + operador)
                print 'Imagens iguais'
                grupo[operador]['vivo'] += 1
            else:
                logging.info('Mutante: ' + mutante + ";Situacao: MORTO" + ";Operador: " + operador)
                print 'Imagens diferentes' 
                grupo[operador]['morto'] += 1
                mortos += 1

            total += 1
        
    # log dos operadores vivos e mortos
    for k in grupo:
        t = grupo[k]['vivo']+grupo[k]['morto']
        logging.info('Operador: ' + k + ";VIVOS: " + str(grupo[k]['vivo']) + ";MORTOS: " + str(grupo[k]['morto']) + ";Total: " + str(t) + ";Score: " + str((float(grupo[k]['morto'])/t)*100) + "%")
    logging.info("TOTAL MUTANTES: " + str(total))
    logging.info("SCORE: " + str((float(mortos)/total)*100) + "%")

if __name__ == '__main__':
    main()
