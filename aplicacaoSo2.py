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
import logging
serialNameRecebe = "COM3"

logging.basicConfig(filename='SERVER.log', filemode='w', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.info("COMECO DO LOG")

def getHandshake(com):
    global idServerRec
    time1 = time.time()
    handshake, nHandshake = com.getNData_Timed(14, time1)
    idServerRec = handshake[2]
    logging.info("ENVIO : HANDSHAKE")
    print("Handshake recebido")
    time.sleep(5)
    return handshake

    

def main():
    idServer = b'\x02'
    try:
        global payloadCompleto
        payloadCompleto = None
        com2 = enlace(serialNameRecebe)
        com2.enable()
        print("Comunicacao do segundo arduino aberta com sucesso")
        print("Esperando handshake...")
        # Recebendo handshake
        handshake = getHandshake(com2)

        if idServerRec == int.from_bytes(idServer, byteorder="big"):
            print("Mandando confirmacao do handshake")
            tipoMsg = b'\x02'
            idClient = b'\x01'
            idServer = b'\x02'
            eop =  b'\0xFF\0xAA\0xFF\0xAA'
            handshakeAns = tipoMsg + idClient + idServer + handshake[3].to_bytes(1, byteorder="big") + handshake[4].to_bytes(1, byteorder="big") + handshake[5].to_bytes(1, byteorder="big") + handshake[6].to_bytes(1, byteorder="big") + handshake[7].to_bytes(1, byteorder="big") + handshake[8].to_bytes(1, byteorder="big") + handshake[9].to_bytes(1, byteorder="big")  + eop
            com2.sendData(handshakeAns)
        else:
            print(idServerRec, idServer)
            print("Recepcao do handshake falhou. Tenta novamente.")
            com2.disable()

        i = 0
        nPayload = 1
        finished = False

        while i < nPayload and not finished:
            t1 = time.time()
            print('Esperando o head')
            head, nHead = com2.getData(10)
            tipoMsg = head[0]
            totalPackages = head[3]
            i = head[4]
            sizePayload = head[5]
            errorIn = head[6]
            lastPackage = head[7]
            crc = head[8:9]

            print('\nPacote {0}/{1}'.format(i, nPayload))
            print('_____PAYLOAD {0}_____'.format(i))

            payload, nPayload = com2.getData(sizePayload)

            if payloadCompleto == None:
                payloadCompleto = payload
            else:
                payloadCompleto += payload

            print(
                '\n{0} Bytes recebidos'.format(sizePayload))
            eop, nEop = com2.getData(4)

            if eop == b'\0xff\0xAA\0xFF\0xAA':
                print("End of package do pacote {0} recebido".format(i))
                
            tamanhoTotal = 0
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
