import pandas as pd
import numpy as np
import joblib
import os
import glob

# --- 1. CONFIGURAÇÃO (CARREGANDO OS MODELOS RANDOM FOREST) ---
MODEL_PATH = 'RandomForestddos_model_v2.pkl'  # <-- Carrega o modelo Random Forest
SCALER_PATH = 'RandomForestscaler_v2.pkl'     # <-- Carrega o scaler do Random Forest
CSV_DIR = 'C:/Projeto/TCC/CICFlowMeter-master/output_csv/'
LIMIAR_ALERTA = 70.0  # Limiar de 70% para disparar o alerta

print(f"Carregando modelo {MODEL_PATH} e scaler {SCALER_PATH}...")
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    # Pega o nome da classe de ataque (ex: 'UDP_Flood') que o modelo aprendeu
    classe_ataque_nome = model.classes_[1] 
    print(f"Modelo e scaler carregados com sucesso. Modelo treinado para detectar: {classe_ataque_nome}")
except FileNotFoundError:
    print(f"Erro: Arquivos do modelo ('{MODEL_PATH}' ou '{SCALER_PATH}') não encontrados.")
    print("Certifique-se de que o script 'treinar_modelo_v2.py' (versão RF) foi executado.")
    exit()
except Exception as e:
    print(f"Ocorreu um erro ao carregar os arquivos: {e}")
    exit()

# --- 2. ENCONTRAR E CARREGAR O CSV DE TESTE MAIS RECENTE ---
print(f"Procurando por novos arquivos CSV em {CSV_DIR}...")
list_of_files = glob.glob(os.path.join(CSV_DIR, '*.csv'))

# Excluir os arquivos que usamos para o TREINAMENTO
list_of_files = [f for f in list_of_files if 'benigno_moderno_internet_Flow.csv' not in f]
list_of_files = [f for f in list_of_files if 'ataque_udp_flood_Flow.csv' not in f]
list_of_files = [f for f in list_of_files if 'ataque_nmap_wifi_Flow.csv' not in f] # Caso tenha usado o Nmap

if not list_of_files:
    print(f"Erro: Nenhum *novo* arquivo CSV de teste foi encontrado em '{CSV_DIR}'.")
    print("Gere uma nova captura .pcap e processe-a com o CICFlowMeter.")
    exit()

# Pegar o arquivo mais recente
latest_file = max(list_of_files, key=os.path.getctime)
print(f"Analisando o arquivo: {os.path.basename(latest_file)}")
df_new = pd.read_csv(latest_file)

# --- 3. PRÉ-PROCESSAMENTO (VERSÃO SIMPLIFICADA) ---
df_new.columns = df_new.columns.str.strip()

# !! NÃO HÁ CAMADA DE TRADUÇÃO !!
# O modelo v2 já foi treinado com os nomes de colunas modernos.

model_features = scaler.get_feature_names_out()

# Verificar se todas as colunas necessárias estão presentes
if not all(feature in df_new.columns for feature in model_features):
    missing = set(model_features) - set(df_new.columns)
    print(f"Erro: O CSV gerado não contém todas as features esperadas: {missing}")
    exit()

# Adiciona .copy() para evitar o SettingWithCopyWarning
df_features = df_new[model_features].copy() 
df_features.replace([np.inf, -np.inf], np.nan, inplace=True)
df_features.fillna(0, inplace=True)

# Padronizar os dados com o scaler JÁ TREINADO
X_scaled = scaler.transform(df_features)

# --- 4. PREVISÃO E ANÁLISE DO RESULTADO ---
predictions = model.predict(X_scaled)

# As classes são 0 ('BENIGN') e 1 ('UDP_Flood')
n_benign = np.sum(predictions == 0) 
n_ataque = np.sum(predictions == 1) 
total = len(predictions)

print("\n--- Resultado da Análise (Modelo Random Forest v2) ---")
if total > 0:
    percentual_benigno = (n_benign / total) * 100
    percentual_ataque = (n_ataque / total) * 100
    
    print(f"Total de fluxos de rede analisados: {total}")
    print(f"Fluxos Benignos: {n_benign} ({percentual_benigno:.2f}%)")
    print(f"Fluxos de Ataque ({classe_ataque_nome}): {n_ataque} ({percentual_ataque:.2f}%)")

    # Lógica de alerta com o limiar de 70%
    if percentual_ataque > LIMIAR_ALERTA:
        print(f"\nALERTA: A proporção de tráfego de ataque ({percentual_ataque:.2f}%) ultrapassou o limiar de {LIMIAR_ALERTA}%.")
    else:
        print(f"\nNenhuma ameaça significativa detectada. A proporção de tráfego de ataque ({percentual_ataque:.2f}%) está abaixo do limiar.")
else:
    print("Nenhum fluxo de rede foi capturado para análise.")