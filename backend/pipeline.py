import xmltodict
import json
import os
import glob
from lxml import etree

def process_archive_pipeline():
    print("Iniciando o Pipeline de Dados Jamstack...\n")

    # ==========================================
    # 1. Configuração de Caminhos (Paths)
    # ==========================================
    # Assumimos que este script está dentro da pasta /backend
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    XML_DIR = os.path.join(BASE_DIR, 'xml_raw')
    DTD_PATH = os.path.join(BASE_DIR, 'schema.dtd')
    
    # O Output vai navegar "para cima e para o lado" até à pasta pública do Frontend
    FRONTEND_DATA_DIR = os.path.join(BASE_DIR, '..', 'frontend', 'public', 'data')
    JSON_OUTPUT_PATH = os.path.join(FRONTEND_DATA_DIR, 'manuscritos.json')

    # Garantir que as pastas existem
    os.makedirs(XML_DIR, exist_ok=True)
    os.makedirs(FRONTEND_DATA_DIR, exist_ok=True)

    # Carregar as regras de validação (DTD)
    try:
        with open(DTD_PATH, 'r', encoding='utf-8') as dtd_file:
            dtd = etree.DTD(dtd_file)
    except Exception as e:
        print(f"❌ Erro ao carregar o ficheiro schema.dtd: {e}")
        print("Certifica-te que o ficheiro existe na pasta /backend.")
        return

    # Lista para guardar todos os manuscritos válidos
    all_manuscripts = []

    # ==========================================
    # 2. Validação e Transformação (Em Lote)
    # ==========================================
    # Procurar todos os ficheiros XML na pasta xml_raw
    xml_files = glob.glob(os.path.join(XML_DIR, '*.xml'))
    
    if not xml_files:
        print(f"⚠️ Nenhum ficheiro XML encontrado na pasta: {XML_DIR}")
        return

    for xml_path in xml_files:
        filename = os.path.basename(xml_path)
        print(f"A processar: {filename}...")

        try:
            # Validar o XML
            with open(xml_path, 'r', encoding='utf-8') as xml_file:
                xml_doc = etree.parse(xml_file)

            if not dtd.validate(xml_doc):
                print(f"  ❌ Validação Falhou para {filename}! Erros:")
                for error in dtd.error_log:
                    print(f"    - Linha {error.line}: {error.message}")
                continue # Ignora este ficheiro e passa ao próximo

            # Se for válido, transformar em Dicionário Python
            with open(xml_path, 'r', encoding='utf-8') as raw_file:
                xml_content = raw_file.read()

            data_dict = xmltodict.parse(xml_content, attr_prefix='@_')
            all_manuscripts.append(data_dict)
            print(f"  ✅ Transformação com sucesso.")

        except etree.XMLSyntaxError as e:
            print(f"  ❌ Erro de Sintaxe XML em {filename}: {e}")
        except Exception as e:
            print(f"  ❌ Erro inesperado em {filename}: {e}")

    # ==========================================
    # 3. Exportação para JSON Estático (Frontend)
    # ==========================================
    if all_manuscripts:
        try:
            with open(JSON_OUTPUT_PATH, 'w', encoding='utf-8') as json_file:
                json.dump(all_manuscripts, json_file, indent=None, ensure_ascii=False)
            print(f"\n✅ Pipeline Concluído! {len(all_manuscripts)} registos guardados em: {JSON_OUTPUT_PATH}")
        except Exception as e:
            print(f"❌ Erro ao guardar o JSON final: {e}")
    else:
        print("\n⚠️ Nenhum registo válido para exportar.")

# Executar o Pipeline
if __name__ == "__main__":
    process_archive_pipeline()
