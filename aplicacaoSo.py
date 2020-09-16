#####################################################
# Camada Física da Computação
# Carareto
# 11/08/2020
# Aplicação
####################################################


# esta é a camada superior, de aplicação do seu software de comunicação serial UART.
# para acompanhar a execução e identificar erros, construa prints ao longo do código!

from enlace import *
import PySimpleGUI as sg
import tkinter as tk
import time
import math
import os
import subprocess


# serialNameEnvia = "COM3"
serialNameEnvia = "COM4"

global t0

serialNameRecebe = "COM3"
imageW = "eikiRecebido.png"
window = tk.Tk()
e1 = tk.Entry(window)

e1.pack()


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

#___________________________________________________________#
#                                                           #
#                     PACOTES DE TESTE                      #
#___________________________________________________________#

# TESTE 1 tem número de bytes incorreto (head != payload)
# TESTE 2 tem ordem dos pacotes invertida


eop = 4321
eopBytes = eop.to_bytes(4, byteorder='big')
mensagemTeste = 16352
mensagemTesteBytes = mensagemTeste.to_bytes(4, byteorder='big')
tamanhoTeste = len(mensagemTesteBytes)
tamanhoTesteErrado = tamanhoTeste - 1

# TESTE1
headPacote1 = makeHead(0, 1, 1, tamanhoTesteErrado, 1, tamanhoTesteErrado)
pacote1Teste = headPacote1 + mensagemTesteBytes + eopBytes

# TESTE 2
headPacote20 = makeHead(0, 2, 2, tamanhoTeste, 2, tamanhoTeste*2)
headPacote21 = makeHead(0, 2, 2, tamanhoTeste, 1, tamanhoTeste*2)
pacote20Teste = headPacote20 + mensagemTesteBytes + eopBytes


def main():
    try:
        com = enlace(serialNameEnvia)
        com.enable()
        print("Comunicacao aberta com sucesso. Comecando timer...")
        t0 = time.time()
#___________________________________________________________#
#                                                           #
#                    MANDANDO HANDSHAKE                     #
#___________________________________________________________#
        handshake = 1
        tamanho = 0
        tipoMsg = 0  # DATA
        tamanhoTotal = 0
        i = 0
        ok = None
        handshakeBytes = makeHead(tipoMsg, handshake, 0, 0, 0, 0)
        # 2 é tipo handshake
        # 1 é handshake OK tá tudo vivo

        handshake1 = handshakeBytes + eopBytes

#___________________________________________________________#
#                                                           #
#                   EESPERANDO RESPOSTA                     #
#___________________________________________________________#

        while ok == None:
            com.sendData(handshake1)
            handshakeConf, nHandshakeConf = com.getData(14)
            if handshakeConf != None and handshakeConf != 0:
                print("Confirmacao do Handshake Recebida")
                ok = handshakeConf[3]
                time.sleep(0.01)
                if ok != None:
                    break
            else:
                startOver = input('Servidor inativo. Tentar novamente? S/N\n')
                if startOver == "N":
                    com.disable()

        print('############################')
        print('Verificacao do Handshake ok')
        print('########################### \n')

        print("Dividindo bytes em payloads...")

#___________________________________________________________#
#                                                           #
#                     PREPARANDO IMAGEM                     #
#___________________________________________________________#

        imageR = e1.get()
        txBuffer = open(imageR, 'rb').read()
        tamanhoTotal = len(txBuffer)
        # Quantos payloads tem
        nPayloadFloat = math.ceil(len(txBuffer)/114)
        ultimoPacote = False

#___________________________________________________________#
#                                                           #
#                     PACOTES DE TESTE                      #
#___________________________________________________________#

        print('\n______ENVIANDO PACOTE DE TESTE PRDEM DO PAYLOAD ERRADO______\n')
        teste = True
        com.sendData(pacote20Teste)
        time.sleep(1)
        print('ESPERANDO A CONFIRMACAO DOS PACOTES')
        com.rx.getIsEmpty()
        headConf = com.getData(10)
        eop = com.getData(4)
        com.disable()

        if teste == False:

            #___________________________________________________________#
            #                                                           #
            #                     CRIANDO O PAYLOAD                     #
            #___________________________________________________________#

            for i in range(1, nPayloadFloat+1):
                # Primeiro byte: tamanho do payload, tipo de msg,
                # Tamanho, tipo da mensagem, numero do pacote, numero de pacotes
                if i < nPayloadFloat:
                    payload = txBuffer[114*(i-1):114*i]
                else:
                    print("ULTIMO PACOTE")
                    ultimoPacote = True
                    payload = txBuffer[114*(i-1):]

                tamanhoPayload = len(payload)

                print('_____PAYLOAD {0}_____'.format(i))
                print('Handshake: {0} \nNumero de Payloads: {1} \nNumero desse payload: {2} \nTamanho desse Payload: {3}\nTamanho total: {4} bytes'.format(
                    handshake, nPayloadFloat, i, tamanhoPayload, tamanhoTotal))
                head = makeHead(tipoMsg, handshake, nPayloadFloat,
                                tamanhoPayload, i, tamanhoTotal)
                eopOriginal = 4321
                eop = eopOriginal.to_bytes(4, byteorder='big')
                message = head + payload + eop

                # EVIANDO PACOTE
                print('\n\n-- ENVIADO PACOTE {0}...--\n\n'.format(i))

                com.sendData(message)
                headConf = com.getData(10)
                eop = com.getData(4)
                if headConf == 1 and eop is not None:
                    print("\n\nCONFIRMACAO RECEBIDA E PACOTE ENVIADO COM SUCESSO!\n\n")
                i += 1

#___________________________________________________________#
#                                                           #
#                 ENVIANDO O ÚLTIMO PACOTE                  #
#___________________________________________________________#

                if ultimoPacote:
                    print("ULTIMO PACOTE. RECEBENDO TAMANHO DO SERVER...")
                    time.sleep(2)
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

            print("TAMANHO RECEBIDO: {0} \nTAMANHO ESPERADO: {1}".format(
                int.from_bytes(payloadTamanho, byteorder='big'), tamanhoTotal))
            if int.from_bytes(payloadTamanho, byteorder='big') == tamanhoTotal:
                print("OPERACAO FEITA COM SUCESSO. TODOS OS BYTES FORAM RECEBIDOS")
                com.disable()

        else:
            print("Pacotes de teste enviados.")
            print("Confirmacao recebida!!")

    except Exception as ex:
        print(ex)
        com.disable()


button = tk.Button(window,
                   text='OK', command=main)
button.pack()
window.mainloop()


# so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
