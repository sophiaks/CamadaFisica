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


def main():
    try:
        com = enlace(serialNameEnvia)
        com.enable()
        print("Comunicacao aberta com sucesso. Comecando timer...")
        t0 = time.time()
        # HANDSHAKE E CONFIRMACAO DO HANDSHAKE
        handshake = 1
        tamanho = 0
        tipoMsg = 0  # DATA
        i = 0
        tamanhoPayloadBytes = tamanho.to_bytes(1, byteorder='big')
        handshakeBytes = handshake.to_bytes(1, byteorder="big")
        tipoMsgBytes = tipoMsg.to_bytes(1, byteorder='big')
        nPayloadBytes = tamanho.to_bytes(1, byteorder="big")
        iBytes = i.to_bytes(1, byteorder='big')
        tamanhoTotalBytes = tamanho.to_bytes(5, byteorder='big')
        ok = None
        handshakeBytes = tipoMsgBytes + handshakeBytes +  nPayloadBytes + tipoMsgBytes + tamanhoPayloadBytes + iBytes + tamanhoTotalBytes

            tipoMsgBytes + handshakeBytes + nPayloadBytes + \
                tamanhoPayloadBytes + iBytes + tamanhoTotalBytes
        eop = 4321
        handshake1 = handshakeBytes + int.to_bytes(eop, byteorder='big')

        while ok == None:
            com.sendData(handshake1.to_bytes(1, byteorder="big"))
            ok, nOk = com.getData(1)
            time.sleep(0.01)
            if ok != None:
                break
            time.sleep(5)
            startOver = input('Servidor inativo. Tentar novamente? S/N')
            if startOver == "N":
                com.disable()

        print('############################')
        print('Verificacao do Handshake ok')
        print('########################### \n')

        print("Dividindo bytes em payloads...")
        imageR = e1.get()
        txBuffer = open(imageR, 'rb').read()
        print('Tamanho total da imagem: {} bytes'.format(os.path.getsize(imageR)))
        tamanhoTotal = len(txBuffer)
        # Quantos payloads tem
        nPayloadFloat = math.ceil(len(txBuffer)/114)
        print("Numero de payloads: {0}".format(nPayloadFloat))
        ultimoPacote = False
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

            # TRANSFORMANDO HEAD EM BYTES
            tamanhoPayloadBytes = tamanhoPayload.to_bytes(1, byteorder='big')
            handshakeBytes = handshake.to_bytes(1, byteorder="big")
            tipoMsgBytes = tipoMsg.to_bytes(1, byteorder='big')
            nPayloadBytes = nPayloadFloat.to_bytes(1, byteorder="big")
            iBytes = i.to_bytes(1, byteorder='big')
            tamanhoTotalBytes = tamanhoTotal.to_bytes(5, byteorder='big')

            print('_____PAYLOAD {0}_____'.format(i))
            print('Handshake: {0} \nNumero de Payloads: {1} \nNumero desse payload: {2} \nTamanho desse Payload: {3}\nTamanho total: {4} bytes'.format(
                handshake, nPayloadFloat, i, tamanhoPayload, tamanhoTotal))
            head = tipoMsgBytes + handshakeBytes + nPayloadBytes + \
                tamanhoPayloadBytes + iBytes + tamanhoTotalBytes
            eopOriginal = 4321
            eop = eopOriginal.to_bytes(4, byteorder='big')
            message = head + payload + eop

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


button = tk.Button(window,
                   text='OK', command=main)
button.pack()
window.mainloop()
# so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
