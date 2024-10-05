#!/usr/bin/env python
import pika, sys, os, time
from colorama import Fore, Style, Back, init

msg = ""
def main():
    credentials = pika.PlainCredentials("user", "PzLSXy7zxxx:")

    connection = pika.BlockingConnection(pika.ConnectionParameters(host="20.206.161.10", credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='fila')

    def callback(ch, method, properties, body):
        print("Mensagem recebida...")
        global msg
        msg = body
        ch.basic_ack(delivery_tag=method.delivery_tag)
        ch.stop_consuming()
        time.sleep(2)
        os.system("cls")

    channel.basic_consume(queue='fila', on_message_callback=callback, auto_ack=False)

    print('Esperando por mensagens...')
    channel.start_consuming()

    connection.close()
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

if __name__ == '__main__':
    try:
        while True:
            main()

            newMessage = msg.decode('utf-8')

            print(Back.GREEN + "....................................................." + Style.RESET_ALL)
            print(Back.GREEN + "." + Style.RESET_ALL + "                                                   " + Style.RESET_ALL)

            key = str(input(Back.GREEN + "." + Style.RESET_ALL + " Informe a chave para ver a mensagem recebida: "))
            msgDescriptografada = descriptografar_texto_from_cesar(newMessage, key)

            print(Back.GREEN + "." + Style.RESET_ALL + f" A mensagem é: '{msgDescriptografada}'")

            # Inicializa o colorama
            # init(autoreset=True)

            print(Back.GREEN + "." + Style.RESET_ALL + "                                                   " + Style.RESET_ALL)
            print(Back.GREEN + Fore.WHITE + "....................................................." + Style.RESET_ALL)

            receberMsg = int(input("Esperar por mais mensagens? [1] Sim [0] Não: "))
            if not receberMsg:
                break
            os.system("clear")
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
