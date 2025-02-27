import os
import re
import cv2
import pytesseract
import numpy as np
import pandas as pd
import warnings
import logging
from flask import current_app

# Configuração de logging para debug
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class OCRProcessor:
    CUSTOM_CONFIG = r'--oem 3 --psm 6 -l por'

    def __init__(self, tesseract_path=None):
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        elif os.environ.get('TESSERACT_PATH'):
            pytesseract.pytesseract.tesseract_cmd = os.environ['TESSERACT_PATH']
        else:
            raise RuntimeError("Caminho do Tesseract não definido.")

    def process_inventory_table(self, image_path):
        try:
            img = self._preprocess_image(image_path)
            text = pytesseract.image_to_string(img, config=self.CUSTOM_CONFIG)

            # Verifica se a saída do OCR é válida
            if not isinstance(text, str) or text.strip() == "":
                raise ValueError("Erro: OCR não retornou texto válido.")

            logging.debug(f"Texto cru do OCR para processamento:\n{text}")

            texto_limpo = self._limpar_texto_ocr(text)
            df = self._parse_inventory_text(texto_limpo)

            # Verifica se a extração do OCR foi bem-sucedida
            if df is None or df.empty:
                raise ValueError("Erro: Nenhum dado extraído da imagem.")

            return df

        except Exception as e:
            raise RuntimeError(f"Erro ao processar a tabela do inventário: {str(e)}")

    def _preprocess_image(self, image_path):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                raise RuntimeError(f"Erro ao carregar a imagem '{image_path}'")

        # Aumentar contraste e nitidez
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        img = cv2.fastNlMeansDenoising(img, None, 30, 7, 21)  # Remover ruídos

        return img

    def _limpar_texto_ocr(self, texto_cru):
        """
        Função para limpar e normalizar o texto extraído pelo OCR.
        Remove caracteres inválidos e tenta restaurar palavras fragmentadas.
        """
        logging.debug("Texto cru do OCR para limpeza:\n%s", texto_cru)

        # Remover caracteres especiais indesejados
        texto_limpo = re.sub(r'[^a-zA-Z0-9À-ÿ\s.,:/-]', '', texto_cru)

        # Substituir múltiplos espaços por um único espaço
        texto_limpo = re.sub(r'\s+', ' ', texto_limpo).strip()

        logging.debug("Texto limpo:\n%s", texto_limpo)

        return texto_limpo

    def _parse_inventory_text(self, text):
        """
        Extrai itens de um texto de OCR, assumindo um formato de tabela de inventário.

        **Exemplo de entrada esperada:**
        ```
        10007 ARROZ BRANCO KG — 10KG
        10026 COBERTURA MORANGO KG — 1KG
        110011 AZEITONA SEM CAROCO KG — 3KG
        140033 FARINHA DE ROSCA KG — 2KG
        ```
        """

        if not isinstance(text, str):
            raise TypeError(f"Erro: esperado string, mas recebido {type(text)}")

        lines = text.split('\n')
        lines = [re.sub(r'[^A-Za-z0-9À-ú\s|,.-]', '', line).strip() for line in lines]
        lines = [line for line in lines if len(line) > 3]  # Filtra linhas muito curtas

        data = []
        pattern = re.compile(
            r'(\d{3,6})\s+'                        # Código do item (3 a 6 dígitos)
            r'([A-Za-zÀ-ú\s\/-]+?)\s+'             # Nome do item
            r'(\d+[\.,]?\d*)\s*([A-Za-z]{1,4})?'   # Quantidade mínima e unidade (opcional)
            r'\s*(\d+[\.,]?\d*)\s*([A-Za-z]{1,4})?'# Quantidade atual e unidade (opcional)
        )

        for line in lines:
            logging.debug(f"Processando linha: {line}")
            match = pattern.search(line)
            if match:
                codigo, nome, minimo, unid_min, estoque, unid_est = match.groups()
                if nome and minimo and estoque:
                    data.append({
                        "codigo": codigo,
                        "nome": nome.strip(),
                        "quantidade_minima": float(minimo.replace(',', '.')),
                        "quantidade_atual": float(estoque.replace(',', '.')),
                        "unidade": unid_est or unid_min
                    })

        if not data:
            logging.warning("Nenhum dado foi extraído do OCR.")
        else:
            logging.info(f"Dados parseados: {len(data)} itens extraídos.")

        return pd.DataFrame(data)

# ---------------------- EXEMPLO DE USO ----------------------

if __name__ == "__main__":
    ocr_processor = OCRProcessor(tesseract_path="C:\\Program Files\\Tesseract-OCR\\tesseract.exe")  # Ajuste conforme necessário

    # Simulação de entrada do OCR (em vez de uma imagem real)
    texto_cru = """
    10007 ARROZ BRANCO KG — 10KG
    10026 COBERTURA MORANGO KG — 1KG
    110011 AZEITONA SEM CAROCO KG — 3KG
    140033 FARINHA DE ROSCA KG — 2KG
    """

    texto_limpo = ocr_processor._limpar_texto_ocr(texto_cru)
    df = ocr_processor._parse_inventory_text(texto_limpo)

    print(df)