import ply.lex as lex

tokens = ["FUNC_TV", "FUNC_TF", "LIST_TV", "LIST_TF", "CAMP", "SEP"]

def t_FUNC_TV(t):
    r'(([^\n,"]+)|"([^\n"]+)")\{(\d+),(\d+)\}::([^\n,]+)'

    listSize = int(lexer.lexmatch.group(6))

    if lexer.lexmatch.group(4):
        t.lexer.campos.append(lexer.lexmatch.group(4))
        t.lexer.listasTV[lexer.lexmatch.group(4)] = (int(lexer.lexmatch.group(5)), int(lexer.lexmatch.group(6)))
        t.lexer.funcoes[lexer.lexmatch.group(4)] = lexer.lexmatch.group(7)
    else: 
        t.lexer.campos.append(lexer.lexmatch.group(3))
        t.lexer.listasTV[lexer.lexmatch.group(3)] = (int(lexer.lexmatch.group(5)), int(lexer.lexmatch.group(6)))
        t.lexer.funcoes[lexer.lexmatch.group(3)] = lexer.lexmatch.group(7)

    while listSize > 1:
        t.lexer.campos.append('')
        listSize -= 1

    return t

def t_FUNC_TF(t):
    r'(([^\n,"]+)|"([^\n"]+)")\{(\d+)\}::([^\n,]+)'

    listSize = int(lexer.lexmatch.group(12))

    if lexer.lexmatch.group(11):
        t.lexer.campos.append(lexer.lexmatch.group(11))
        t.lexer.listasTF[lexer.lexmatch.group(11)] = int(lexer.lexmatch.group(12))
        t.lexer.funcoes[lexer.lexmatch.group(11)] = lexer.lexmatch.group(13)
    else: 
        t.lexer.campos.append(lexer.lexmatch.group(10))
        t.lexer.listasTF[lexer.lexmatch.group(10)] = int(lexer.lexmatch.group(12))
        t.lexer.funcoes[lexer.lexmatch.group(11)] = lexer.lexmatch.group(13)

    while listSize > 1:
        t.lexer.campos.append('')
        listSize -= 1

    return t

def t_LIST_TV(t):
    r'(([^\n,"]+)|"([^\n"]+)")\{(\d+),(\d+)\}'

    listSize = int(lexer.lexmatch.group(19))

    if lexer.lexmatch.group(17):
        t.lexer.campos.append(lexer.lexmatch.group(17))
        t.lexer.listasTV[lexer.lexmatch.group(17)] = (int(lexer.lexmatch.group(18)), int(lexer.lexmatch.group(19)))
    else: 
        t.lexer.campos.append(lexer.lexmatch.group(16))
        t.lexer.listasTV[lexer.lexmatch.group(16)] = (int(lexer.lexmatch.group(18)), int(lexer.lexmatch.group(19)))

    while listSize > 1:
        t.lexer.campos.append('')
        listSize -= 1

    return t

def t_LIST_TF(t):
    r'(([^\n,"]+)|"([^\n"]+)")\{(\d+)\}'

    listSize = int(lexer.lexmatch.group(24))
    
    if lexer.lexmatch.group(23):
        t.lexer.campos.append(lexer.lexmatch.group(23))
        t.lexer.listasTF[lexer.lexmatch.group(23)] = int(lexer.lexmatch.group(24))
    else: 
        t.lexer.campos.append(lexer.lexmatch.group(22))
        t.lexer.listasTF[lexer.lexmatch.group(22)] = int(lexer.lexmatch.group(24))

    while listSize > 1:
        t.lexer.campos.append('')
        listSize -= 1

    return t

def t_CAMP(t):
    r'([^\n,"]+)|"([^\n"]+)"'

    if lexer.lexmatch.group(27):
        t.lexer.campos.append(lexer.lexmatch.group(27))
    else: 
        t.lexer.campos.append(lexer.lexmatch.group(26))

    return t

t_ignore = '\n\t, '

def t_error(t):
    print(f"ERROR: Illegal character '{t.value[0]}' at position ({t.lineno}, {t.lexpos})")
    t.lexer.skip(1)

lexer = lex.lex()

lexer.campos = []
lexer.listasTF = {}
lexer.listasTV = {}
lexer.funcoes = {}

import sys
import re

def functionHandler(function, parameter):
    
    aux = 0
    if isinstance(parameter[0], int):
        for p in parameter:
            aux += p
    
    if function == 'sum':
        return aux
    elif function == 'media':
        return aux / len(parameter)
    elif function == 'sort':
        return sorted(parameter)

def csv2json(csv_filename):
    csvf = open(csv_filename)

    cabecalho = csvf.readline()
    lexer.input(cabecalho)
    while True:
        tok = lexer.token()

        if not tok:
            break

    jsonToWrite = []

    aspasD = r'"[^"]+'
    aspasDM = re.compile(aspasD)
    aspasE = r'[^"]+"'
    aspasEM = re.compile(aspasE)

    for linha in csvf:
        camposO = linha.split(',')
        campos = []

        i = 0
        while i < len(camposO):
            if aspasDM.match(camposO[i]):
                c = camposO[i]

                j = i + 1

                while j < len(camposO):
                    if aspasEM.match(camposO[j]):
                        c = c + ',' + camposO[j]
                        break
                    else:
                        c = c + camposO[j]
                        j += 1
                
                if c[-1] == '"':
                    c = c[:-1]
                    c = c[1:]
                    campos.append(c)
                    i = j + 1
                else:
                    campos.append(camposO[i][1:])
            else:
                campos.append(camposO[i])
            
            i += 1

        if '\n' in campos[-1]:
            campos[-1] = campos[-1][:-1]

        entry = {}

        listFlag = False
        funcFlag = False
        listSize = 0
        currParam = ''

        for c,e in zip(lexer.campos,campos):
            if not listFlag:
                if c in lexer.listasTF or c in lexer.listasTV:
                    currParam = c
                    listFlag = True
                    if c in lexer.listasTF:
                        listSize = lexer.listasTF[c] - 1
                    elif c in lexer.listasTV:
                        listSize = lexer.listasTV[c][1] - 1
                    if c in lexer.funcoes:
                        funcFlag = True
                        entry[c] = []
                        if e != '':
                            if e.isdigit():
                                entry[c].append(int(e))
                            else:
                                entry[c].append(e)
                    else:
                        entry[c] = []
                        if e != '':
                            if e.isdigit():
                                entry[c].append(int(e))
                            else:
                                entry[c].append(e)
                else:
                    if e != '':
                        if e.isdigit():
                            entry[c] = (int(e))
                        else:
                            entry[c] = e
            elif listFlag:
                listSize -= 1
                if e != '':
                    if e.isdigit():
                        entry[currParam].append(int(e))
                    else:
                        entry[currParam].append(e)

                if listSize == 0:
                    if funcFlag:
                        funcFlag = False
                        entry[currParam] = functionHandler(lexer.funcoes[currParam], entry[currParam])
                    listFlag = False

        jsonToWrite.append(entry)

    json_filename = csv_filename.split('.')[0] + ".json"
    
    with open(json_filename, 'w') as jsonf:
        jsonf.write("[\n")

        i = 0

        while i < len(jsonToWrite) - 1:
            jsonf.write("   {\n")

            for key, value in jsonToWrite[i].items():
                jsonf.write('       \"%s\": \"%s\",\n' % (key, value))

            jsonf.seek(jsonf.tell() - 2, 0)
            jsonf.write("\n   },\n")
            i += 1

        jsonf.write("   {\n")

        for key, value in jsonToWrite[i].items():
            jsonf.write('       \"%s\": \"%s\",\n' % (key, value))

        jsonf.seek(jsonf.tell() - 2, 0)
        jsonf.write("\n   }\n]")

def main():
    args = sys.argv[1:]
    print("A converter ", args[0], " em formato .json...")
    csv2json(args[0])
    print("Conversão completa. Ficheiro " + args[0].split('.')[0] + ".json gerado.")

if __name__ == '__main__':
    main()