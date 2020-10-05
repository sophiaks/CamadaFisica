#####################################################
# Camada Física da Computação
# Carareto
# 11/08/2020
# Aplicação
####################################################
import time
import logging
from functions import *
from enlace import *
global listaPacotes
global i
global nPayloads
global payloadCompleto
payloadCompleto = None
listaPacotes = []


serialNameRecebe = "COM3"
errorOrder = False
errorSize = False
numeroP = 0
fmtstr = " Name: SERVER_SOPHIA : %(asctime)s: (%(filename)s): %(levelname)s: %(funcName)s Line: %(lineno)d - %(message)s"
datestr = "%m/%d/%Y %I:%M:%S %p "
# basic logging config
logging.basicConfig(
    filename="custom_log_output.log",
    level=logging.DEBUG,
    filemode="w",
    format=fmtstr,
    datefmt=datestr,
)


def getHandshake(com):
    handshake1, nHandshake1 = com.getData(14)
    print("Get data feito com sucesso")
    ok = handshake1[1]
    tipoMsg = handshake1[0]
    logging.info("RECEPCAO: Handshake")
    print("Handshake recebido")
    time.sleep(0.01)
    logging.info("ENVIO: Confirmação do Handshake")
    print("ENVIO: Confirmação do Handshake")

    if ok == 1:
        com.sendData(handshake1)
        # 1 senddata e 3 getdatas!
    else:
        print("Recepcao do handshake falhou. Tenta novamente.")
        com.disable()



def getHead(com):
    print('Esperando o head')
    head, nHead = com.getData(10)
    print("Head recebido")
    head = bytesToHead(head)
    return head

def getPayload(com, tamanhoPayload, payloadCompleto):
    print("Recebendo {0} bytes".format(tamanhoPayload))
    logging.info("RECEPCAO: Payload com {0} bytes".format(tamanhoPayload))
    payload, numeroPayload = com.getData(tamanhoPayload)
    if payloadCompleto == None:
        payloadCompleto = payload
    else:
        payloadCompleto += payload

def getEop(com):
    global eop
    print("Recebendo eop")
    logging.info("RECEPCAO: eop")
    eop, nEop = com.getData(4)
    return eop


def sendConfirmation(com, nPayload, eopP):
    print("Verificando pacotes")
    if nPayload == numeroP + 1:
        print("Ordem dos pacotes correta")
    else:
        print("\n\nOrdem dos pacotes incorreta.")
        head = Head(6, 0, 0, 0, 0, 0, numeroP+1, listaPacotes[-1], 0, 0)
        erro = True

    if eopP == eop:
        print("End of package do pacote {0} recebido".format(nPayload))
        head = Head(4, 0, 0, 0, 0, 0, nPayload, listaPacotes[-1], 0, 0)

    else:
        print(
            "Ocorreu algum erro. O tamanho do pacote nao corresponde com o informado no head.\n")
        erro = True
        head = Head(6, 0, 0, 0, 0, 0, nPayload, nPayload-1, 0, 0)
    if erro == False:
        listaPacotes.append(nPayload)
        print("Payload {0} adicionado à lista!".format(nPayload))
    confirmation = head + eop
    com.sendData(confirmation)


def checkAllPackages(com, nTotal):
    if thisPayload == nTotal:
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
        global nTotal
        global thisPayload
        thisPayload = 1
        errorOrder = False
        errorSize = False
        com2 = enlace(serialNameRecebe)
        com2.enable()
        print("Comunicacao do segundo arduino aberta com sucesso")
        print("Esperando handshake...")
        getHandshake(com2)

    #    (_____________HANDSHAKE OK_______________)     #

        thisPayload = 1
        nTotal = 2
        while thisPayload < nTotal:
            head = getHead(com2)
            head.printInfoPacote()
            # Redefinindo o números
            nTotal = head.totalPacotes
            thisPayload = head.nPacote
            getPayload(com2, head.tamanhoPayload, payloadCompleto)
            eop = getEop(com2)
            sendConfirmation(com2, thisPayload, eop)
            

            if thisPayload == nTotal:
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
