import re
import sys

listaTD = r'^([^\{]+){(\d+)}$'
listaTV = r'^([^\{]+){(\d+)$'
funcao = r'^(([^\{]+){\d+}|\d+})::(\w+)$'

listaCTD = re.compile(listaTD)
listaCTV = re.compile(listaTV)
funcaoC = re.compile(funcao)

def funcOp(list, op, isdigit):
    if isdigit:
        aux = 0
        for num in list:
            aux += num
        if op == 'sum':
            return aux
        elif op == 'media':
            return aux / len(list)
    
    return sorted(list)


def csv2json(csv_filename):

    csvf = open(csv_filename)
    linha = csvf.readline()

    campos = linha.split(',')
    campos[len(campos) - 1] = campos[len(campos) - 1][:-1]

    campos_filter = []

    listasTD = {}

    listasTV = {}
    ltvFlag = False
    ltvLast = ""

    listas_size = 0

    funcoes = {}

    for l in campos:
        ltd = listaCTD.match(l)
        ltv = listaCTV.match(l)
        func = funcaoC.match(l)

        if listas_size == 0:
            if ltd:
                listas_size = int(ltd.group(2))
                listasTD[ltd.group(1)] = int(ltd.group(2))
                campos_filter.append(ltd.group(1))
            elif ltv:
                ltvLast = ltv.group(1)
                listasTV[ltv.group(1)] = (int(ltv.group(2)), 0)

                campos_filter.append(ltv.group(1))

                ltvFlag = True
            elif func:
                if ltvFlag:
                    funcoes[ltvLast] = func.group(3)

                    listas_size = int(l[0])
                    listasTV[ltvLast] = (listasTV[ltvLast][0], int(l[0]))

                    if listasTV[ltvLast][0] > listasTV[ltvLast][1]:
                        print("Error.")

                    ltvFlag = False
                else:
                    funcoes[func.group(2)] = func.group(3)
            elif ltvFlag:
                listas_size = int(l[0])
                listasTV[ltvLast] = (listasTV[ltvLast][0], int(l[0]))

                if listasTV[ltvLast][0] > listasTV[ltvLast][1]:
                    print("Error.")

                ltvFlag = False
            elif l != '':
                campos_filter.append(l)
            else:
                print("Invalid camps.")
        else:
            if l != '':
                print("Error not enough reserved space.")
            else:
                campos_filter.append(l)
                listas_size -= 1

    # Escrever json

    json_filename = csv_filename.split('.')[0] + ".json"
    jsonf = open(json_filename, "w")

    jsonf.write('[\n')

    for linha in csvf:
        campos = linha.split(',')
        campos[len(campos) - 1] = campos[len(campos) - 1][:-1]

        string = '{\n'

        size = 0
        lengthMin = 0
        lengthMax = 0
        list = []
        
        funcFlag = False
        operacao = ''
        funcList = []

        for c, l in zip(campos_filter, campos):
            if size == 0:
                string = string + '\"' + c + '\"' + ': '
            
            if c in funcoes or funcFlag:
                if not funcFlag:
                    operacao = funcoes[c]
                    if c in listasTD:
                        size = listasTD[c]
                    elif c in listasTV:
                        size = listasTV[c][1]
                    if l != '':
                        if l.isdigit():
                            funcList.append(int(l))
                        else:
                            funcList.append(l)
                    funcFlag = True
                else:
                    if l != '':
                        if l.isdigit():
                            funcList.append(int(l))
                        else:
                            funcList.append(l)
                    
                    size -= 1
                    
                    if size == 1:
                        toWrite = funcOp(funcList, operacao, isinstance(funcList[0], int))
                        size -= 1
                        funcList = []
                        funcFlag = False
                        string = string + '\"' + str(toWrite) + '\",\n'
            elif c in listasTD:
                string = string + '\"['
                size = lengthMin = lengthMax = listasTD[c]

                if l != '':
                    list.append(l)
                    string = string + l + ','
            elif c in listasTV:                
                string = string + '\"' + '['
                size = lengthMax = listasTV[c][1]
                lengthMin = listasTV[c][0]

                if l != '':
                    list.append(l)
                    string = string + l + ','
            elif size > 0:
                if c == '' and l != '':
                    list.append(l)
                    string = string + l + ','
                size -= 1
                if size == 1:
                    string = string[:-1]
                    if len(list) < lengthMin or len(list) > lengthMax:
                        print("Error list out of bounds.")
                    list = []
                    string = string + ']\",\n'
            else:
                string = string + '\"' + l + '\",\n'
        
        string = string[:-2] + '\n},\n'

        jsonf.write(string)

    jsonf.seek(jsonf.tell() - 2, 0)
    jsonf.write('\n]\n')

def main():
    args = sys.argv[1:]
    print("A converter ", args[0], " em formato .json...")
    csv2json(args[0])
    print("Conversão completa. Ficheiro " + args[0].split('.')[0] + ".json gerado.")

if __name__ == '__main__':
    main()
