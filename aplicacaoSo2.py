#####################################################
# Camada Física da Computação
# Carareto
# 11/08/2020
# Aplicação
####################################################


# esta é a camada superior, de aplicação do seu software de comunicação serial UART.
# para acompanhar a execução e identificar erros, construa prints ao longo do código!

from enlace import *
from classes import *
from functions import *
import time
import os
numeroP = 0

serialNameRecebe = "COM3"
errorOrder = False
errorSize = False
global listaPacotes
listaPacotes = []


def getHandshake(com):
    handshake1, nHandshake1 = com.getData(14)
    ok = handshake1[1]
    tipoMsg = handshake1[0]
    print("Handshake recebido")
    time.sleep(0.01)
    print("Mandando confirmacao do handshake")

    if ok == 1:
        com.sendData(handshake1)
        # 1 senddata e 3 getdatas!
    else:
        print("Recepcao do handshake falhou. Tenta novamente.")
        com.disable()


def getHead(com):
    print('Esperando o head')
    head, nHead = com.getData(10)
    head = bytesToHead(head)


def getPayload(com, tamanhoPayload):
    payload, numeroPayload = com.getData(tamanhoPayload)
    if payloadCompleto == None:
        payloadCompleto = payload
    else:
        payloadCompleto += payload


def getEop(com):
    global eop
    global intEop
    eop, nEop = com.getData(4)
    intEop = int.from_bytes(eop, byteorder='big')


def sendConfirmation(com, nPayload):
    if nPayload == numeroP + 1:
        print("Ordem dos pacotes correta")
    else:
        print("\n\nOrdem dos pacotes incorreta.")
        errorOrder = True
        head = Head(6, 0, 0, 0, 0, 0, numeroP+1, listaPacotes[-1], 0, 0)
    if intEop == 4321:
        print("End of package do pacote {0} recebido".format(nPayload))
        confirmation = head + eop
        com.sendData(confirmation)
    else:
        print(
            "Ocorreu algum erro. O tamanho do pacote nao corresponde com o informado no head.\n")
        errorSize = True
        head = Head(6, 0, 0, 0, 0, 0,)
        confirmation = head + eop


def checkAllPackages(com):
    print("i, nPayload: {0}, {1}".format(i, nPayload))
    if i == nPayload:
        print("Todos os pacotes recebidos.")
        print("Tamanho total recebido: {}".format(len(payloadCompleto)))
        # ATE AQUI TA OK
        tipoMsg = 2
        # TIPO MSG - CONFIRMACAO
        yama = len(payloadCompleto)
        print(yama)
        headson = Head(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        payloaderson = yama.to_bytes(5, byteorder='big')
        pacotejohnson = headson + payloaderson + eop
        time.sleep(1)
        com.sendData(pacotejohnson)
        time.sleep(1)
        print("Acabaram os pacotes :)")
        print("TAMANHO ENVIADO PRO CLIENTE")
        global finished
        finished = True
    else:
        print('Não acabaram os pacotes')


def main():

    try:
        global payloadCompleto
        payloadCompleto = None
        errorOrder = False
        errorSize = False
        com2 = enlace(serialNameRecebe)
        com2.enable()
        print("Comunicacao do segundo arduino aberta com sucesso")
        print("Esperando handshake...")

        getHandshake(com2)

        i = 0
        nPayload = 1
        while i < nPayload:
            getHead(com2)
            getPayload(com2, tamanhoPayload)
            getEop(com2)

            checkPackageOrder(nPayload)

            sendConfirmation(com2)

            if i == nPayload:
                break

#___________________________________________________________#
#                                                           #
#                 ENCERRANDO A COMUNICACAO                  #
#___________________________________________________________#

        print("---------------------------------------")
        print("Comunicacao encerrada. Parando timer...")
        print("---------------------------------------")
        if errorOrder:
            print("\nOCORREU UM ERRO COM A ORDEM DOS PACOTES")
            print("TENTE NOVAMENTE\n")
        if errorSize:
            print("\nOCORREU UM ERRO COM O TAMANHO DE UM OU MAIS PACOTES")
            print("TENTE NOVAMENTE\n")

        com2.disable()
    except Exception as ex:
        print(ex)
        com2.disable()


# so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
