from CLIENT import dictPayloads


class Head:
    '''
    h0: tipo de mensagem
    h1: id do sensor
    h2: id do servidor
    h3: número total de pacotes do arquivo
    h4: número do pacote a ser enviado
    h5: id do arquivo
    h6: pacote solicitado para recomeço quando há erro no envio
    h7: último pacote recebido com sucesso
    h8-h9: livre
    '''

    def __init__(self, h0, h1, h2, h3, h4, h5, h6, h7, h8, h9):
        self.h0 = h0.to_bytes(1, byteorder="big")
        self.h1 = h1.to_bytes(1, byteorder="big")
        self.h2 = h2.to_bytes(1, byteorder="big")
        self.h3 = h3.to_bytes(1, byteorder="big")
        self.h4 = h4.to_bytes(1, byteorder="big")
        self.h5 = h5.to_bytes(1, byteorder="big")
        self.h6 = h6.to_bytes(1, byteorder="big")
        self.h7 = h7.to_bytes(1, byteorder="big")
        self.h8 = h8.to_bytes(1, byteorder="big")
        self.h9 = h9.to_bytes(1, byteorder="big")

        self.tipoMsg = h0
        self.idSensor = h1
        self.idServer = h2
        self.totalPacotes = h3
        self.nPacote = h4
        self.idFile = h5
        self.nErro = h6
        self.ultimoPacoteOk = h7
        self.tamanhoPayload = h8
        self.parabens = h9

    def printInfoPacote(self):
        print("\n\n_____PACOTE {0}_____\n\n".format(self.nPacote))
        if self.h0 == 1:
            msg = 'Mensagem de handshake'
        if self.h0 == 2:
            msg = 'Servidor ocioso, pronto para receber mensagens'
        if self.h0 == 3:
            msg = 'Mensagem de dados'
        if self.h0 == 4:
            msg = 'Pacote recebido pelo servidor'
        if self.h0 == 5:
            msg = 'Timeout'
        if self.h0 == 6:
            msg = 'Ocorreu algum erro'
        else:
            msg = 'OK'
        print(msg)
        print('Tipo de mensagem: {}\n'.format(self.h0))
        print('Id do Sensor: {}'.format(self.h1))
        print('Id do Servidor: {}'.format(self.h2))
        print('Total de pacotes: {}'.format(self.h3))
        print('Numero deste pacote: {}'.format(self.nPacote))
        print('Id do arquivo: {}'.format(self.idFile))
        print('Erro no pacote: {}'.format(self.nErro))
        if (self.ultimoPacoteOk == 0):
            print('Ultimo pacote enviado com sucesso: Handshake')
        print('Ultimo pacote enviado com sucesso: {}\n'.format(self.ultimoPacoteOk))

    def headToBytes(self):
        h0 = self.h0
        h1 = self.h1
        h2 = self.h2
        h3 = self.h3
        h4 = self.h4
        h5 = self.h5
        h6 = self.h6
        h7 = self.h7
        h8 = self.h8
        h9 = self.h9
        bytes = h0 + h1 + h2 + h3 + h4 + h5 + h6 + h7 + h8 + h9
        return bytes


class Payload():
    '''
    Variável entre 0 e 114 bytes
    '''

    def __init__(self, data):
        self.data = data
        self.tamanho = len(data)
        self.i = None
        for num, payload in dictPayloads:
            if payload == data:
                self.i == num


class Pacote:
    def __init__(self, head, i, eop):
        self.eop = eop
        self.head = head
        if i != 0:
            self.pacote = head + dictPayloads[i] + self.eop
        else:
            self.pacote = head + self.eop
            print(self.pacote)

    # def pacoteToBytes():

    def sendPacote(self, com):
        print("Enviando pacote")
        com.sendData(self.pacote)
        print("Pacote Enviado")

    def getPacote(self, com):
        com.getData(self.head.tamanhoPayload)
