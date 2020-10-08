
# @author Sophia Kerber Shigueoka
# @email sophia.shigueoka@gmail.com
# @create date 2020-10-05 00:06:18
# @modify date 2020-10-05 00:08:52

from functions import *
from classes import *
import time
from enlace import *
eop = b'\xff\xaa\xff\xaa'
import math
# esta é a camada superior, de aplicação do seu software de comunicação serial UART.
# para acompanhar a execução e identificar erros, construa prints ao longo do código!

global ok
global dictPayloads

dictPayloads = {}
# serialNameEnvia = "COM3"
serialNameEnvia = "COM4"
inicia = False
serialNameRecebe = "COM3"

imageR = "oiakon.png"
txBuffer = open(imageR, 'rb').read()

# Criando todos os payloads
def createPayloads(img):
    global nPayloads
    global tamanhoTotal
    global dictPayloads
    dictPayloads = {}
    nPayloads = math.ceil(len(img)/114)
    tamanhoTotal = len(img)
    # Primeiro pacote tem índice 1
    for i in range(1,nPayloads):
        if i == nPayloads:
            dictPayloads[i] = img[114*i:]
        else:
            dictPayloads[i] = img[114*i:114*(i+1)]
    print(nPayloads)
    print(dictPayloads)

createPayloads(txBuffer)
print("Payloads Criados\n")


def createHandshake():
    print("Criando Handshake\n")
    headHandshake = Head(1, 1, 1, nPayloads, 0, 1, 0, 0, 0, 0)
    return headHandshake


def main():
    global eop
    try:
        com = enlace(serialNameEnvia)
        com.enable()
        print("Comunicacao aberta com sucesso. Comecando timer...")
        t0 = time.time()
        handshake = Pacote(createHandshake().headToBytes(), 0, eop)
        print("HANDSHAKE")
        while True:
            handshake.sendPacote(com)
            conf = getPackageConfirmation(com)
            if conf == True:
                break
            else:
                startOver = input('Servidor inativo. Tentar novamente? S/N\n')
                if startOver == "N":
                    com.disable()

        print('############################')
        print('Verificacao do Handshake ok')
        print('########################### \n')

        #___________________________________________________________#
        #                                                           #
        #                     CRIANDO O PAYLOAD                     #
        #___________________________________________________________#

        for i in range(1, len(dictPayloads)+1):
            if i <= nPayloads:
                print("i: {0}".format(i))
                print("Dicionário: {0}".format(dictPayloads))
                head = Head(3, 1, 2, nPayloads, i, i, 0, i-1, 0, 0)
                pacote = Pacote(head.headToBytes(), i, eop)
                pacote.sendPacote(com)
                time.sleep(0.1)
                getPackageConfirmation(com)

            if i == nPayloads:
                print("ULTIMO PACOTE. RECEBENDO TAMANHO DO SERVER...")
                time.sleep(0.1)
                com.rx.getIsEmpty()
                payloadTamanhoHead, nPayloadTamanhoHead = com.getData(10)
                print(payloadTamanhoHead)

                if payloadTamanhoHead[0] == 2:
                    print("Recebida a confirmacao")
                    payloadTamanho = payloadTamanhoHead[5:]
                    print(payloadTamanho)
                    com.getData(len(payloadTamanho))
                    com.getData(4)
                    break
                elif payloadTamanhoHead[0] == 0 or payloadTamanhoHead == 1:
                    payloadTamanho = 0

            print("TAMANHO RECEBIDO: {0} \nTAMANHO ESPERADO: {1}".format(
                int.from_bytes(payloadTamanho, byteorder='big'), tamanhoTotal))
            
            if int.from_bytes(payloadTamanho, byteorder='big') == tamanhoTotal:
                print("OPERACAO FEITA COM SUCESSO. TODOS OS BYTES FORAM RECEBIDOS")
                com.disable()

    except Exception as ex:
        print(ex)
        com.disable()


# so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
