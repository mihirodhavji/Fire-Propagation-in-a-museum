import probability
from operator import itemgetter

class Problem:

    def __init__(self, fh):
        # Place here your code to load problem from opened file object fh
        # and use probability.BayesNet() to create the Bayesian network
        
        #  Inicializar variaveis, o history guarda as entradas da linha M, o counter conta tantos instantes
        # é que o problema tem.
        self.rooms, self.history = ({} for i in range(2)) 
        self.propagation_prob = 0.0
        self.counter = 0
        # Iteração das linhas do ficheiro.
        for line in fh:
            # Tira os espaços.
            line_list = line.split()
            # Se for uma linha vazia, line_list vai ser uma lista vazia.
            if(len(line_list) == 0):
                continue
                #  Se a linha for R, cria um dicionário dentro do dicionário rooms,
                # cuja chave é o nome do quarto, correspondente a essa chave # é um dicionário 
                # com chave sensor para guardar os sensores, se o quarto tiver algum, 
                # dentro da chave vizinhos guarda-se a lista de vizinhos, se o quartot tiver vizinhos.
            elif(line_list[0] == 'R'):
                for i in range(1, len(line_list), 1):
                    self.rooms[line_list[i]] = {}
                    self.rooms[line_list[i]]['vizinhos'] = []
                    self.rooms[line_list[i]]['sensor'] = {}
            #  Se a linha for C, significa que é a lista de todos os pares de vizinhos existentes espaçados por um ' '.
            #  Assim para cada par adiciona-se na lista de vizinhos do primeiro elemento o nome do segundo,
            # e na lista de viznhos do segundo elemento adiciona-se o nome do primeiro.
            elif(line_list[0] == 'C'):
                for i in range(1, len(line_list), 1):
                    pair = line_list[i].split(",")
                    self.rooms[pair[0]]['vizinhos'].append(pair[1])
                    self.rooms[pair[1]]['vizinhos'].append(pair[0])
            #  Se a linha for S, significa é a informação de todos os sensores do museu espaçados por um ' '. 
            #  Para cada sensor é dado o código dele, o quarto onde se encontra e as probabilidades TPR e FPR.
            #  Assim cria um dicionário dentro do [quarto_nome]['sensor'] onde usa como chave o código do sensor,
            # dentro deste novo dicionário criado, são criados outros dois, onde guardamos as probabilidades TPR e FPR.
            elif(line_list[0] == 'S'):
                for i in range(1, len(line_list), 1):
                    sensor_info = line_list[i].split(":")
                    self.rooms[sensor_info[1]]['sensor'][sensor_info[0]] = {}
                    self.rooms[sensor_info[1]]['sensor'][sensor_info[0]]['TPR'] = float(sensor_info[2])
                    self.rooms[sensor_info[1]]['sensor'][sensor_info[0]]['FPR'] = float(sensor_info[3])
            #  Se a linha for M, siginifica que é a informação relativa ao sensores ao longo dos vários instantes de tempo.
            #  Cada linha representa um instante. As linhas estão na ordem cronológica.
            #  Usa-se um dicionário para guardar os vários valores dos sensores ao longo do tempo. Como chave usa-se o código 
            # do sensor concatenado com o instante em que foi lido o seu valor(True,False).
            elif(line_list[0] == 'M'):
                for i in range(1, len(line_list), 1):
                    sensor = line_list[i].split(":")
                    if (sensor[1] == 'T'):
                        self.history[sensor[0]+str(self.counter)] = True
                    else:
                        self.history[sensor[0]+str(self.counter)] = False
                self.counter += 1
            #  Se a linha for P, significa que é a informação correspondente à probabilidade do fogo propagar-se 
            # de um quarto vizinho para outro.
            elif(line_list[0] == 'P'):
                self.propagation_prob = float(line_list[1])
        #  Criação do dicionário de probabilidades, se tiver n vizinhos, existem 2^n possibilidades,
        # caso contrário é só True ou False dependendo se estava a arder no caso anterior ou não.
        for key in self.rooms:
            size_l = len(self.rooms[key]['vizinhos']) + 1
            if (self.rooms[key]['vizinhos']):
                self.rooms[key]['dici'] = make_dici(size_l,self.propagation_prob)
            else:
                self.rooms[key]['dici'] = {True: 1, False : 0.0}
        # Criação da lista que entra como argumento no probability.BayesNet.
        lista = []
        for i in range(self.counter):
            for key in self.rooms:
                if (i == 0):
                    # Criação dos nodes pais, no início a probabilidade de haver fogo num quarto é 0.5.
                    tup1 = (key+str(i),'',0.5)
                    lista.append(tup1)
                else:
                    # Um quarto depende sempre do seu estado no instante anterior.
                    str_v = key + str(i-1)
                    # Se tiver vizinhos, o estado neste instante também depende do estados dos vizinhos no instante anterior.
                    if (self.rooms[key]['vizinhos']): 
                        for v in self.rooms[key]['vizinhos']:
                            str_v += " " + v + str(i-1)
                    tup1 = (key+str(i),str_v, self.rooms[key]['dici'])
                    lista.append(tup1)
                # O estado do sensor depende sempre do estado do quarto onde se encontra, naquele mesmo instante.
                for code in self.rooms[key]['sensor']:
                    tup1 = (code+str(i),key+str(i),{True:self.rooms[key]['sensor'][code]['TPR'],False:self.rooms[key]['sensor'][code]['FPR']})
                    lista.append(tup1)
        # Crição da BayesNet.
        self.museu = probability.BayesNet(lista)
        return
                
    def solve(self):
        # Place here your code to determine the maximum likelihood solution
        # returning the solution room name and likelihood
        # use probability.elimination_ask() to perform probabilistic inference
        resultados = []
        # Calcular a probabilidade para todos os quartos, e colocar numa lista.
        for key in self.rooms:
            a = probability.elimination_ask(key+str(self.counter-1), dict(self.history), self.museu)
            resultados.append((key, a[True]))
        # Devolver o tuple com maior probabilidade. Este tuple é constituído pelo nome do quarto e probabilidade.
        return max(resultados,key=itemgetter(1))
    
def solver(input_file):
        return Problem(input_file).solve()

#  Fazer um dicionário com todas as possibilidades de True e False, nb é o numero de pais de um node,
# assim o dicionário terá 2^n chaves. P é a probabilidade de propagação do fogo.
def make_dici(nb,P):
    dici = {}
    zero = []
    for i in range(nb):
        zero.append(False)
    # Caso em que todos são Falsos, a probabilidade é 0.
    dici[tuple(zero)] = 0.0
    n = 1
    for i in range(1,nb+1): 
        n=2*n 
    for i in range(1,n,1):
        key = decToBinary(i,nb)
        # O primeiro bit representa o próprio quarto no instante anterior, por isso se este for True continuará True.
        if (key[0] == True):
            value = 1
        #  Se qualquer outro dos bits for True,ou seja, se qualquer um dos vizinhos estiver a arder,
        # o fogo pode propagar-se com probabilidade P.
        else: 
            value = P
        dici[key]=value
    
    return dici
# Funcao que converte de decimal para binário, n é o número em decimal, e nb é o número de bits.
# Em vez de guardar 0 guarda False, e em vez de guardar 1 guarda True.
def decToBinary(n,nb): 
    binaryNum = [] 
    while (n > 0):  
        if (n % 2 == 0):
            binaryNum.append(False)
        else:
            binaryNum.append(True)
        n = int(n / 2)
    # Adiciona zeros(neste caso False) à esquerda para fazer o número de bits.
    while(len(binaryNum) != nb):
        binaryNum.append(False)
    # Troca a ordem porque os Bits mais Significativos estam no fim da lista.
    binaryNum.reverse()
    # Converte para tuple e envia.
    return tuple(binaryNum)