import os
import json
import requests
import xml.etree.ElementTree as ET
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 1. Configurar Autenticação no Google Sheets
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials_json = os.environ.get("GOOGLE_CREDENTIALS")
spreadsheet_id = os.environ.get("SPREADSHEET_ID")

creds_dict = json.loads(credentials_json)
credentials = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(credentials)

sheet = client.open_by_key(spreadsheet_id).sheet1

# 2. Lista das Estações (Uruguaiana, Quaraí, Alegrete e Manoel Viana)
estacoes = [
    {"cod": "77150000", "nome": "Uruguaiana"},
    {"cod": "76800000", "nome": "Quaraí"},
    {"cod": "76600001", "nome": "Alegrete"},
    {"cod": "76560000", "nome": "Manoel Viana"}
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 3. Coletar dados de cada estação
for e in estacoes:
    try:
        url = f"http://telemetriaws.ana.gov.br/ServiceANA.asmx/DadosHidrometeorologicos?codEsta={e['cod']}&dataInicio=&dataFim="
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            primeiro_dado = root.find('.//DadosHidrometereologicos')
            
            if primeiro_dado is not None:
                data_hora = primeiro_dado.find('DataHora').text if primeiro_dado.find('DataHora') is not None else str(datetime.now())
                nivel_str = primeiro_dado.find('Nivel').text if primeiro_dado.find('Nivel') is not None else "0"
                vazao_str = primeiro_dado.find('Vazao').text if primeiro_dado.find('Vazao') is not None else "0"
                chuva_str = primeiro_dado.find('Chuva').text if primeiro_dado.find('Chuva') is not None else "0"

                nivel = float(nivel_str.replace(',', '.')) if nivel_str else 0.0
                vazao = float(vazao_str.replace(',', '.')) if vazao_str else 0.0
                chuva = float(chuva_str.replace(',', '.')) if chuva_str else 0.0

                # Adiciona linha na planilha do Google Sheets
                if nivel > 0:
                    sheet.append_row([e['cod'], data_hora, nivel, vazao, chuva, str(datetime.now())])
                    print(f"Sucesso: {e['nome']} - Nível: {nivel}")
    except Exception as err:
        print(f"Erro na estação {e['nome']}: {err}")
