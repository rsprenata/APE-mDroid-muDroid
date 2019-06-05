import re

def main():
    logPath = '/home/juniorrek/MDroidPlusMutants/org.jtb.alogcat-mutants.log';
    mutante = '91';
    mutante = 'Mutant ' + mutante;
    
    #Encontra linha
    with open(logPath, 'r') as f:
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
        print operador.group();
    print linha;

if __name__ == '__main__':
    main()