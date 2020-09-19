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
from classes import *
from functions import *
global ok


# serialNameEnvia = "COM3"
serialNameEnvia = "COM4"
inicia = False
serialNameRecebe = "COM3"

#window = tk.Tk()
#e1 = tk.Entry(window)

# e1.pack()
#imageR = e1.get()
imageR = "oiakon.png"
txBuffer = open(imageR, 'rb').read()

# Criando todos os payloads
global dictPayloads
createPayloads(txBuffer)


def createHandshake():
    headHandshake = Head(1, 1, 1, nPayloads, 0, 1, 0, 0, 0, 0)
    return headHandshake


def main():
    global eop
    try:
        com = enlace(serialNameEnvia)
        com.enable()
        print("Comunicacao aberta com sucesso. Comecando timer...")
        t0 = time.time()

        handshake = Pacote(createHandshake(), 0, eop)
        print("Enviando Handshake")
        handshake.sendPacote(com)

        while True:
            com.sendData(handshake)
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
                print(dictPayloads[i])
                head = Head(3, 1, 2, nPayloads, i, i, 0, i-1, 0, 0)
                pacote = head + dictPayloads[i] + eop
                com.sendData(pacote)
                time.sleep(0.1)
                # Confirmação é T4
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


# button = tk.Button(window,
#                   text='OK', command=main)
# button.pack()
# window.mainloop()


# so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
