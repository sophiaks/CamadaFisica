from classes import Head
import math

def createPayloads(img):
    global nPayloads
    global tamanhoTotal
    global dictPayloads
    dictPayloads = {}
    nPayloads = math.ceil(len(img)/114)
    tamanhoTotal = len(img)


def bytesToHead(bytes):
    print("Transformando bytes recebidos em Head")
    h0 = bytes[0]
    h1 = bytes[1]
    h2 = bytes[2]
    h3 = bytes[3]
    h4 = bytes[4]
    h5 = bytes[5]
    h6 = bytes[6]
    h7 = bytes[7]
    h8 = bytes[8]
    h9 = bytes[9]
    head = Head(h0, h1, h2, h3, h4, h5, h6, h7, h8, h9)
    return head


def getPackageConfirmation(com):
    headConf, nHeadConf = com.getData(10)
    eop = com.getData(4)
    headConf = bytesToHead(headConf)
    print(headConf.nErro, headConf.tipoMsg)
    if headConf.nErro == 0 and eop is not None and headConf.tipoMsg == 1:
        print("\n\n CONFIRMACAO RECEBIDA E PACOTE ENVIADO COM SUCESSO! \n\n")
        return True
    else:
        return False
