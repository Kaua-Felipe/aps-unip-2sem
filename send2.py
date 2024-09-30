import pika

def criptografar_texto_to_cesar(msg, chave):
    listNumber = "0123456789"
    soma = 0

    msg_final = ""
    words = list(msg)
    newwords = [None] * len(msg)
    ascChave = [None] * len(chave)

    # Loop para transformar a chave em um número
    for index, item in enumerate(chave):
        if item in listNumber:
            ascChave[index] = int(item)
        else:
            ascChave[index] = ord(item)
        soma += ascChave[index]
    media = int(soma / len(ascChave))

    # Primeiro loop
    for i in range(len(msg)):
        letter = msg[i]
        asc = ord(letter)
        print(asc)
        ready = asc - media
        if ready < 32:
            ready = (asc + 100) - media
        letter = chr(ready)
        words[i] = letter

    # Segundo loop
    for i in range(len(msg) - 1, -1, -1):
        asc2 = ord(words[i])
        ready2 = asc2 - i
        if ready2 < 0:
            ready2 += 127
        words[i] = chr(ready2)
        newwords[i] = words[i]

    # Concatenar o resultado final
    msg_final = ''.join(newwords)

    return msg_final

def descriptografar_texto_from_cesar(msg_criptografada, chave):
    listNumber = "0123456789"
    soma = 0

    words = list(msg_criptografada)
    newwords = [None] * len(msg_criptografada)
    ascChave = [None] * len(chave)

    # Loop para transformar a chave em um número (mesmo procedimento)
    for index, item in enumerate(chave):
        if item in listNumber:
            ascChave[index] = int(item)
        else:
            ascChave[index] = ord(item)
        soma += ascChave[index]
    media = int(soma / len(ascChave))

    # Primeiro passo (inverso do segundo loop)
    for i in range(len(msg_criptografada)):
        asc2 = ord(words[i])
        ready2 = asc2 + i  # Inverte a operação de subtração do índice
        if ready2 >= 127:
            ready2 -= 127  # Ajusta se ultrapassar o valor 127
        words[i] = chr(ready2)
    
    # Segundo passo (inverso do primeiro loop)
    for i in range(len(words)):
        letter = words[i]
        asc = ord(letter)
        ready = asc + media  # Inverte a subtração da média
        if ready >= 132:  # Limite ajustado ao que foi adicionado no criptografar
            ready = (asc - 100) + media
        words[i] = chr(ready)

    # Concatenar o resultado final
    msg_final = ''.join(words)

    return msg_final


connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(queue="fila2")

frase = input("Frase a ser enviada: ")

channel.basic_publish(exchange="", routing_key="fila2", body=criptografar_texto_to_cesar(frase, "a mesma chave"))
print(" [x] Send Message!")

connection.close()
