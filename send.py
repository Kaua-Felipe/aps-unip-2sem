import pika
import random

def criptografar_texto_to_cesar(msg):
    msg_final = ""
    words = list(msg)
    newwords = [None] * len(msg)

    # Primeiro loop
    for i in range(len(msg)):
        letter = msg[i]
        asc = ord(letter)
        if asc == 32:
            ready = 127 - random.randint(1, 10)
        else:
            ready = asc - random.randint(1, 10)
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
channel.queue_declare(queue="hello")

channel.basic_publish(exchange="", routing_key="hello", body=criptografar_texto_to_cesar("Meu nome é Kauã Felipe Alves, e a senha pro e-mail é kkk123Joao!"))
print(" [x] Send Message!")

connection.close()



criptografado = criptografar_texto_to_cesar("kaua Felipe Alves")
descriptografado = descriptografar_cesar_to_texto(criptografado)
print(descriptografado)
