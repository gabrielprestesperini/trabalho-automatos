import sys
from typing import TextIO, List
from parse_variables import parse_variables
from automato import Automato


def open_file(file_path: str) -> TextIO:
    """
    Abre um arquivo para leitura.

    Args:
        file_path (str): O caminho do arquivo a ser aberto.

    Returns:
        TextIO: Um objeto de arquivo aberto.
    """
    try:
        return open(file_path, 'r', encoding='utf-8')
    except FileNotFoundError:
        print(f"Erro: Arquivo '{file_path}' não encontrado.")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        

# ==================================================================================================

# Verificar se os arquivos de entrada foram fornecidos
if len(sys.argv) < 3:
    print("Uso: python script.py <arquivo_glud> <arquivo_words>")
    sys.exit(1)

# Arquivo de entrada
glud_file = sys.argv[1]
words_file = sys.argv[2]

# Abrir o arquivo
glud = open_file(glud_file)
words: List[str] = open_file(words_file).read().strip().split(",")

# Processar o GLUD
variables = parse_variables(glud)

# Cria automato
automato = Automato(variables)
print('automato.__str__(): ', automato.__str__())

# verifica se as palavras são aceitas pelo automato
for word in words:
    print(f"{word}:", automato.aceita(word))
