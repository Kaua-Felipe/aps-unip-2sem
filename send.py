import pika
import random

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

def descriptografar_cesar_to_texto(msg):
    words = list(msg)
    newwords = [None] * len(msg)
    converted = [None] * len(msg)

    # Primeiro loop
    for i in range(len(msg)):
        letter = msg[i]
        asc = ord(letter)
        ready = asc + i
        if ready > 128:
            ready -= 127
        words[i] = chr(ready)

    # Segundo loop (inversão)
    for i in range(len(msg) - 1, -1, -1):
        newwords[i] = words[i]

    # Terceiro loop
    for i in range(len(msg)):
        letter = newwords[i]
        asc = ord(letter)
        ready = asc + random.randint(1, 10)
        letter = chr(ready)
        converted[i] = letter
        newwords[i] = converted[i]

    return ''.join(newwords)


connection = pika .BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(queue="fila")

frase = input("Frase a ser enviada: ")

channel.basic_publish(exchange="", routing_key="fila", body=criptografar_texto_to_cesar(frase, "Agora, qualquer chave que eu colocar aqui, irá criptografar facilmente!"))
print(" [x] Send Message!")

connection.close()
