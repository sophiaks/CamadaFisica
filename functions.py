import math
from classes import *
import aplicacaoSo2


def createPayloads(img):
    global nPayloads
    global tamanhoTotal
    global dictPayloads
    dictPayloads = {}
    nPayloads = math.ceil(len(img)/114)
    tamanhoTotal = len(img)


def bytesToHead(bytes):
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
    headConf = com.getData(10)
    eop = com.getData(4)
    headConf = bytesToHead(headConf)
    if headConf.h6 == 0 and eop is not None and headConf.h0 == 4:
        print("\n\n CONFIRMACAO RECEBIDA E PACOTE ENVIADO COM SUCESSO! \n\n")
        return True
    else:
        return False
