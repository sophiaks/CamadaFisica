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
import os
numeroP = 0

serialNameRecebe = "COM3"
imageW = "eikiRecebido.png"
errorOrder = False
errorSize = False


def readHead(head):
    tipoMsg = head[0]
    handshake = head[1]
    nPayload = head[2]
    tamanhoPayload = head[3]
    i = head[4]
    tamanhoTotal = head[5:]
    tamanhoTotal = int.from_bytes(tamanhoTotal, byteorder='big')
    print("\n\n_____PACOTE {0}_____\n\n".format(i))
    print('\n TipoMsg: {0} \nHandshake: {1} \nNumero de Payloads: {2} \nNumero desse payload: {3} \nTamanho desse Payload: {4}\nTamanho total: {5} bytes'.format(
        tipoMsg, handshake, nPayload, i, tamanhoPayload, tamanhoTotal))
    if tipoMsg == 0:
        tipoMsg = "DADOS"
        print("Tipo da mensagem: {0}".format(tipoMsg))
        if tipoMsg == 1:
            tipoMsg = "HANDSHAKE"
    return tipoMsg, handshake, nPayload, tamanhoPayload, i, tamanhoTotal


def makeHead(tipoMsg, handshake, nPayloadFloat, tamanhoPayload, i, tamanhoTotal):
    '''
    Cria o head na ordem: TIPO MENSAGEM, HANDSHAKE, NUMERO DE PAYLOADS, TAMANHO DO PAYLOAD, NUMERO DO PAYLOAD, TAMANHO TOTAL DA MSG
    '''
    tamanhoPayloadBytes = tamanhoPayload.to_bytes(1, byteorder='big')
    handshakeBytes = handshake.to_bytes(1, byteorder="big")
    tipoMsgBytes = tipoMsg.to_bytes(1, byteorder='big')
    nPayloadBytes = nPayloadFloat.to_bytes(1, byteorder="big")
    iBytes = i.to_bytes(1, byteorder='big')
    tamanhoTotalBytes = tamanhoTotal.to_bytes(5, byteorder='big')

    head = tipoMsgBytes + handshakeBytes + nPayloadBytes + \
        tamanhoPayloadBytes + iBytes + tamanhoTotalBytes
    return head


def printPayloadInfo(tipoMsg, handshake, nPayload, tamanhoPayload, i, tamanhoTotal):
    print('\n\nPacote {0}/{1}\n\n'.format(i, nPayload))
    print('\n\n_____PAYLOAD {0}_____\n\n'.format(i))
    print('Handshake: {0} \nNumero de Payloads: {1} \nNumero desse payload: {2} \nTamanho desse Payload: {3} Bytes\nTamanho total: {4} bytes'.format(
        handshake, nPayload, i, tamanhoPayload, tamanhoTotal))
    print(
        '\n{0}/{1} Bytes recebidos'.format(tamanhoPayload, tamanhoTotal))


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
#___________________________________________________________#
#                                                           #
#                    RECEBENDO O HANDSHAKE                  #
#___________________________________________________________#

        handshake1, nHandshake1 = com2.getData(14)
        ok = handshake1[1]
        tipoMsg = handshake1[0]
        print("Handshake recebido")
        time.sleep(0.01)
        print("Mandando confirmacao do handshake")
#___________________________________________________________#
#                                                           #
#                    ENVIANDO O HANDSHAKE                   #
#___________________________________________________________#

        if ok == 1:
            com2.sendData(handshake1)
            # 1 senddata e 3 getdatas!
        else:
            print("Recepcao do handshake falhou. Tenta novamente.")
            com2.disable()
        i = 0
        nPayload = 1
        finished = False
        while i < nPayload and not finished:
            print('Esperando o head')
#___________________________________________________________#
#                                                           #
#                    RECEBENDO O HEAD                       #
#___________________________________________________________#

            head, nHead = com2.getData(10)
            tipoMsg, handshake, nPayload, tamanhoPayload, i, tamanhoTotal = readHead(
                head)
            if nPayload == numeroP + 1:
                print("Ordem dos pacotes correta")
            else:
                print("\n\nOrdem dos pacotes incorreta.")
                errorOrder = True

#___________________________________________________________#
#                                                           #
#                    RECEBENDO O PAYLOAD                    #
#___________________________________________________________#

            payload, numeroPayload = com2.getData(tamanhoPayload)
            if payloadCompleto == None:
                payloadCompleto = payload
            else:
                payloadCompleto += payload
#___________________________________________________________#
#                                                           #
#                    RECEBENDO O EOP                        #
#___________________________________________________________#

            eop, nEop = com2.getData(4)
            intEop = int.from_bytes(eop, byteorder='big')

#___________________________________________________________#
#                                                           #
#             MANDANDO CONFIRMACAO DO RECEBIMENTO           #
#___________________________________________________________#

            if intEop == 4321:
                print("End of package do pacote {0} recebido".format(i))
                confirmation = head + eop
                com2.sendData(confirmation)
            else:
                print(
                    "Ocorreu algum erro. O tamanho do pacote nao corresponde com o informado no head.\n")
                errorSize = True
                confirmation = head + eop
                com2.sendData(confirmation)

#___________________________________________________________#
#                                                           #
#                 ENCERRANDO A COMUNICACAO                  #
#___________________________________________________________#

            print("i, nPayload: {0}, {1}".format(i, nPayload))
            if i == nPayload:
                print("Todos os pacotes recebidos.")
                print("Tamanho total recebido: {}".format(len(payloadCompleto)))
                # ATE AQUI TA OK
                tipoMsg = 2
                # TIPO MSG - CONFIRMACAO
                yama = len(payloadCompleto)
                print(yama)
                headson = makeHead(2, 1, 1, 1, 1, yama)
                payloaderson = yama.to_bytes(5, byteorder='big')
                pacotejohnson = headson + payloaderson + eop

#___________________________________________________________#
#                                                           #
#                 ENCERRANDO A COMUNICACAO                  #
#___________________________________________________________#

                # pacote: 19 bytes
                time.sleep(1)
                com2.sendData(pacotejohnson)
                time.sleep(1)
                print("Acabaram os pacotes :)")
                print("TAMANHO ENVIADO PRO CLIENTE")
                break
            else:
                print('Não acabaram os pacotes >= Acabaram os pacotes :)')

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
