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


serialNameRecebe = "COM3"
imageW = "eikiRecebido.png"


def main():

    try:
        global payloadCompleto
        payloadCompleto = None
        com2 = enlace(serialNameRecebe)
        com2.enable()
        print("Comunicacao do segundo arduino aberta com sucesso")
        print("Esperando handshake...")
        # Recebendo handshake
        ok, nOk = com2.getData(14)
        ok = ok[3]
        print("Handshake recebido")
        time.sleep(0.01)
        handshake = int.from_bytes(ok, byteorder="big")
        print("Mandando confirmacao do handshake")
        print('Handshake = {} \n'.format(handshake))
        if handshake == 1:
            com2.sendData(ok)
            # 1 senddata e 3 getdatas!
        else:
            print("Recepcao do handshake falhou. Tenta novamente.")
            com2.disable()
        i = 0
        nPayload = 1
        finished = False
        while i < nPayload and not finished:
            print('Esperando o head')
            head, nHead = com2.getData(10)
            # DESMEMBRANDO O HEAD
            tipoMsg = head[0]
            handshake = head[1]
            nPayload = head[2]
            tamanhoPayload = head[3]
            i = head[4]
            tamanhoTotalBytes = head[5:]

            print('\nPacote {0}/{1}'.format(i, nPayload))

            tamanhoTotal = int.from_bytes(tamanhoTotalBytes, byteorder='big')

            print('_____PAYLOAD {0}_____'.format(i))
            print('Handshake: {0} \nNumero de Payloads: {1} \nNumero desse payload: {2} \nTamanho desse Payload: {3} Bytes\nTamanho total: {4} bytes'.format(
                handshake, nPayload, i, tamanhoPayload, tamanhoTotal))

            if tipoMsg == 0:
                tipoMsg = "DADOS"
            print("Tipo da mensagem: {0}".format(tipoMsg))

            payload, nPayload = com2.getData(tamanhoPayload)
            if payloadCompleto == None:
                payloadCompleto = payload
            else:
                payloadCompleto += payload
            print(
                '\n{0}/{1} Bytes recebidos'.format(tamanhoPayload, tamanhoTotal))
            eop, nEop = com2.getData(4)
            intEop = int.from_bytes(eop, byteorder='big')
            print('\nEnd of package: {0}'.format(intEop))
            if intEop == 4321:
                print("End of package do pacote {0} recebido".format(i))
                confirmation = head + eop
                com2.sendData(confirmation)
            # Encerra comunicação
            if len(payloadCompleto) == tamanhoTotal:
                print("Todos os pacotes recebidos.")
                print("Tamanho total recebido: {}".format(len(payloadCompleto)))
                payloadCompletoBytes = int.to_bytes(
                    len(payloadCompleto), byteorder='big')
                head = head[:2] + payloadCompletoBytes + head[4:]
                pacote = head + len(payloadCompletoBytes) + eop
                com2.sendData(pacote)
                break
            else:
                print('faltam pacotes')

        print("-------------------------")
        print("Comunicacao encerrada. Parando timer...")
        print("-------------------------")

        com2.disable()
    except Exception as ex:
        print(ex)
        com2.disable()


# so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
