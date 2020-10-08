#####################################################
# Camada Física da Computação
# Carareto
# 11/08/2020
# Aplicação
####################################################


# esta é a camada superior, de aplicação do seu software de comunicação serial UART.
# para acompanhar a execução e identificar erros, construa prints ao longo do código!


from enlace import *

import time
import math
import os
import subprocess
import logging

logging.basicConfig(filename='CLIENT.log', filemode='w', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


# serialNameEnvia = "COM3"
serialNameEnvia = "COM4"

global t0
counter = 0

serialNameRecebe = "COM3"

def createPayloads():
    global dict
    global nPayloads
    dict = {}
    print("Dividindo bytes em payloads...")
    imageR = "oiakon.png"
    txBuffer = open(imageR, 'rb').read()
    print('Tamanho total da imagem: {} bytes'.format(os.path.getsize(imageR)))
    tamanhoTotal = len(txBuffer)
    nPayloads = math.ceil(len(txBuffer)/114)
    print("Numero de payloads: {0}".format(nPayloads))
    ultimoPacote = False

    for i in range(1, nPayloads+1):
        if i < nPayloads:
            payload = txBuffer[114*(i-1):114*i]
            dict[i] = payload
        else:
            print("ULTIMO PACOTE")
            ultimoPacote = True
            payload = txBuffer[114*(i-1):]
            dict[i] = payload

def createDataHead(idServer, i, errorPackage):
    msgType = b'\x03'
    idClient = b'\x01'
    if errorPackage == None:
        errorPackage = 0
    crc = b'\x00\x00'
    head = msgType + idClient + idServer + nPayloads + i + len(dict[i]) + errorPackage + crc 
    return head

def main():
    try:
        com = enlace(serialNameEnvia)
        com.enable()
        print("Comunicacao aberta com sucesso. Comecando timer...")
        # HANDSHAKE E CONFIRMACAO DO HANDSHAKE
        i = 0
        tipoMsgHandshake = b'\x01'
        idSensor = b'\x01'
        idServer = b'\x02'
        nPayloadBytes = b'\x00'
        inicia = False

        handshakeBytes = tipoMsgHandshake + idSensor +  idServer + nPayloadBytes + nPayloadBytes + b'\x00' + b'\x00'
        eop = b'\0xFF\0xAA\0xFF\0xAA'
        handshake = handshakeBytes + eop

        while inicia == False and counter < 4:
            com.sendData(handshake)
            logging.info("ENVIO_HANDSHAKE")
            print("Envio do Handshake feito")
            inicia, nInicia = com.getData(14)
            print("Confirmacao do Handshake recebida")
            
            time.sleep(0.01)
            if inicia[2] == 2:
                break
            else:
                print(inicia[2])
            time.sleep(5)
            startOver = input('Servidor inativo. Tentar novamente? S/N')
            if startOver == "N":
                com.disable()

        print('############################')
        print('Verificacao do Handshake ok')
        print('########################### \n')
        i = 1
        createPayloads()
        while i <= nPayloads:
            headData = createDataHead(idServer, i, 0)
            
            print('_____PAYLOAD {0}_____'.format(i))
    
            eop = b'\0xFF\0xAA\0xFF\0xAA'
            message = headData + dict[i] + eop

            # EVIANDO PACOTE
            print('\nENVIADO PACOTE...\n')
            com.sendData(message)
            headConf = com.getData(10)
            eop = com.getData(4)
            if headConf == 1 and eop is not None:
                print("Pacote enviado com sucesso!")
            i += 1

            if ultimoPacote:
                print("ULTIMO PACOTE. RECEBENDO TAMANHO DO SERVER...")
                payloadTamanhoHead, nPayloadTamanhoHead = com.getData(10)
                payloadTamanho = payloadTamanhoHead[3]
                com.getData(payloadTamanho)
                com.getData(4)
                break

        print("TAMANHO RECEBIDO: {0} \nTAMANHO ESPERADO: {1}".format(
            payloadTamanho, tamanhoTotal))
        if payloadTamanho == tamanhoTotal:
            print("OPERACAO FEITA COM SUCESSO. TODOS OS BYTES FORAM RECEBIDOS")

    except Exception as ex:
        print(ex)

        com.disable()

    


# so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
