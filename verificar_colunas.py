import pandas as pd
import joblib
import os
import glob

# --- CONFIGURAÇÃO ---
SCALER_PATH = 'scaler.pkl'
CSV_ORIGINAL_PATH = 'Portmap (1).csv' # O dataset que você usou para treinar
CSV_NOVO_DIR = 'CICFlowMeter-master/output_csv/'

print("Iniciando a verificação de colunas...")

try:
    # 1. Carregar as colunas que o modelo ESPERA
    scaler = joblib.load(SCALER_PATH)
    colunas_esperadas = set(scaler.get_feature_names_out())
    print(f"O modelo espera {len(colunas_esperadas)} features.")

    # 2. Carregar as colunas do CSV ORIGINAL para referência (opcional, mas bom para comparar)
    df_original = pd.read_csv(CSV_ORIGINAL_PATH, nrows=1) # Lê apenas o cabeçalho
    df_original.columns = df_original.columns.str.strip()
    colunas_originais = set(df_original.drop(columns=['Label'], errors='ignore'))
    
    # 3. Carregar as colunas do NOVO CSV gerado
    list_of_files = glob.glob(os.path.join(CSV_NOVO_DIR, '*.csv'))
    if not list_of_files:
        print(f"ERRO: Nenhum arquivo CSV encontrado em '{CSV_NOVO_DIR}'.")
        exit()
    
    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"Analisando o arquivo gerado: {os.path.basename(latest_file)}")
    df_novo = pd.read_csv(latest_file, nrows=1) # Lê apenas o cabeçalho
    df_novo.columns = df_novo.columns.str.strip()
    colunas_novas = set(df_novo.columns)
    print(f"O novo CSV gerou {len(colunas_novas)} features.")

    # 4. Comparar os conjuntos de colunas
    print("\n--- DIAGNÓSTICO ---")

    colunas_faltando_no_novo = colunas_esperadas - colunas_novas
    if colunas_faltando_no_novo:
        print("\n[PROBLEMA] Colunas que o modelo ESPERA, mas que FALTAM no novo CSV:")
        for col in sorted(list(colunas_faltando_no_novo)):
            print(f"- {col}")
    
    colunas_extras_no_novo = colunas_novas - colunas_esperadas
    if colunas_extras_no_novo:
        print("\n[INFO] Colunas EXTRAS no novo CSV que o modelo não conhece:")
        for col in sorted(list(colunas_extras_no_novo)):
            print(f"- {col}")

    if not colunas_faltando_no_novo and not colunas_extras_no_novo:
         print("\n[SUCESSO] Os conjuntos de colunas são idênticos! O problema pode ser outro.")

except FileNotFoundError as e:
    print(f"\nERRO: Arquivo não encontrado - {e}. Verifique se todos os arquivos estão na pasta correta.")
except Exception as e:
    print(f"\nOcorreu um erro inesperado: {e}")