import pika, sys, os
import threading
from colorama import Fore, Style, Back, init
from time import sleep

def descriptografar(key, msg):
    def broke_message(msg):
        arrBlocks = []

        for i in range(0, len(msg), 64):
            arrBlocks.append(msg[i:i+64])
        for i in range(0, len(arrBlocks)):
            tam = len(arrBlocks[i])
            if tam < 64:
                for _ in range(0, 64 - tam + 1):
                    arrBlocks[i].append(0)

        return arrBlocks
    def descriptografar_texto_to_cesar(msg):
        msg_final = ""
        words = list(msg)

        for i in range(len(msg)):
            letter = msg[i]
            asc = ord(letter)

            if not (asc >= 33 and asc <= 126):
                asc = ord(words[i - 1]) + 1
            ready = asc + 3

            letter = chr(ready)
            words[i] = letter
        msg_final = ''.join(words)

        return msg_final
    def aes_to_state(aes):
        state = [[0]*4 for _ in range(4)]

        p1 = aes[:16]
        p2 = aes[16:32]
        p3 = aes[32:48]
        p4 = aes[48:]

        parts = [p1, p2, p3, p4]

        for i in range(4):
            p1 = int(parts[i][:4], 16)
            p2 = int(parts[i][4:8], 16)
            p3 = int(parts[i][8:12], 16)
            p4 = int(parts[i][12:], 16)

            state[i] = [p1, p2, p3, p4]

        return state
    def key_to_round_key(key):
        if isinstance(key, str):
            byte_key = key.encode('utf-8')
        else:
            byte_key = key

        round_key = [[0]*4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                index = i * 4 + j
                if index < len(byte_key):
                    round_key[j][i] = byte_key[index]
                else:
                    round_key[j][i] = 0
        return round_key
    def add_round_key(state, round_key):
        for i in range(4):
            for j in range(4):
                state[i][j] ^= round_key[i][j]  # Inverso de XOR é o próprio XOR
        return state
    def inv_shift_rows(state):
        for i in range(1, 4):
            state[i] = state[i][-i:] + state[i][:-i]  # Desfazer o deslocamento
        return state
    def inv_sub_bytes(state, INV_S_BOX):
        for i in range(4):
            for j in range(4):
                state[i][j] = INV_S_BOX[state[i][j]]
        return state
    def state_to_message(state):
        # Inicializa uma lista para armazenar os bytes
        byte_message = []
        
        # Percorre o estado e extrai os bytes
        for i in range(len(state)):
            for j in range(4):
                for k in range(4):
                    byte_message.append(state[i][j][k])
        
        # Remove os zeros adicionados como padding (se houver)
        while byte_message and byte_message[-1] == 0:
            byte_message.pop()
        
        # print(byte_message)

        try:
            # Converte a lista de bytes de volta para uma string
            message = bytes(byte_message).decode('utf-8')
        except UnicodeDecodeError:
            # Caso a decodificação falhe, retorne a versão hexadecimal
            message = ''.join(f'{chr(byte % 127 + 33 if byte % 127 < 33 else byte % 127)}' for byte in byte_message)
            # message = ''.join(f'{byte:02x}' for byte in byte_message)

        return message
    S_BOX = [
        0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
        0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
        0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
        0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
        0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
        0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
        0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
        0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
        0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
        0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
        0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
        0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
        0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
        0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
        0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
        0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16
    ]

    blockMessage = broke_message(msg)

    message_blocks = []
    final_message = ""
    inv_S_BOX = [0] * 256

    for i in range(256):
        inv_S_BOX[S_BOX[i]] = i

    for i, _ in enumerate(blockMessage):
        text = descriptografar_texto_to_cesar(blockMessage[i])
        state_aes_msg = aes_to_state(text)
        key_round_key = key_to_round_key(key)
        state_round_key = add_round_key(state_aes_msg, key_round_key)
        state_inv_shiftrows = inv_shift_rows(state_round_key)
        state_inv_subbytes = inv_sub_bytes(state_inv_shiftrows, inv_S_BOX)

        message_blocks.append(state_inv_subbytes)

    final_message = state_to_message(message_blocks)

    return final_message
def animacao_envio():
    os.system("cls")

    mensagem_base = Fore.CYAN + "Esperando por mensagens"
    pontos = ""
    while len(msg) == 0:  # Continua enquanto não houver mensagem
        print(f"\r{mensagem_base}{pontos}", end="")
        pontos += "."
        
        if len(pontos) > 3:
            sleep(0.7)
            pontos = ""
            os.system("cls")
            print(f"\r{mensagem_base}{pontos}", end="")
        else:
            sleep(0.7)

    os.system("cls")
def start_consuming():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="48.211.222.206", credentials=pika.PlainCredentials('aps2semestre', 'RabbitMQ1234')))
    channel = connection.channel()

    channel.queue_declare(queue='fila')

    def callback(ch, method, properties, body):
        global msg

        # print( "Mensagem recebida...")
        msg = body.decode("utf-8")

        ch.basic_ack(delivery_tag=method.delivery_tag)
        ch.stop_consuming()

    channel.basic_consume(queue='fila', on_message_callback=callback, auto_ack=False)
    channel.start_consuming()
    connection.close()
def main():
    global msg

    # Cria a thread para o consumo de mensagens
    consume_thread = threading.Thread(target=start_consuming)
    consume_thread.start()

    # Executa a animação enquanto espera por uma mensagem
    animacao_envio()

    # Aguarda a thread de consumo terminar
    consume_thread.join()
    
    print(Fore.GREEN + "\rMensagem recebida!")

    sleep(2)
    os.system("cls")

msg = ""

if __name__ == "__main__":
    try:
        while True:
            main()

            print(Back.BLUE + r'''
*******************************************************************************************************
*    ____ ____  ___ ____ _____ ___   ____ ____      _    _____ ___    _            _    _____ ____    *
*   / ___|  _ \|_ _|  _ \_   _/ _ \ / ___|  _ \    / \  |  ___|_ _|  / \          / \  | ____/ ___|   *
*  | |   | |_) || || |_) || || | | | |  _| |_) |  / _ \ | |_   | |  / _ \        / _ \ |  _| \___ \   *
*  | |___|  _ < | ||  __/ | || |_| | |_| |  _ <  / ___ \|  _|  | | / ___ \      / ___ \| |___ ___) |  *
*   \____|_| \_\___|_|    |_| \___/ \____|_| \_\/_/   \_\_|   |___/_/   \_\    /_/   \_\_____|____/   *
*                                                                                                     *
*******************************************************************************************************''' + Style.RESET_ALL)

            key = input(Back.LIGHTBLACK_EX + "Informe a chave a ser utilizada:" + Style.RESET_ALL + " ")

            os.system("cls")

            msgDescriptografada = descriptografar(key, msg)
            print(f"A mensagem recebida é: {msgDescriptografada}\n")

            receberMsg = int(input("Esperar por mais mensagens? [1] Sim [0] Não: "))
            if not receberMsg:
                break

            msg = ""

            os.system("clear")
    except KeyboardInterrupt:
        print('Sistema Interrompido!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
