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
with open(words_file) as f:
    words = f.read().strip().replace("\n", "").split(",")


# Processar o GLUD
variables = parse_variables(glud)

# Cria automato
automato = Automato(variables)

# converte automato
automato.converte_afd()

if automato.determinado:
    print('O autômato gerado teve de ser determinado. Segue o autômato correspondente:',
          automato, sep="\n")
elif automato.removeu_vazios:
    print('Foram removidos movimentos vazios do autômato. Segue o autômato correspondente:', automato, sep="\n")
else:
    print("O autômato convertido da GLC já era AFD. Segue o autômato gerado:",
          automato, sep="\n")

print("Testes para cada palavra: \n")

# Verifica se cada palavra é aceita pelo AFD
for word in words:
    print(f"{word}:", automato.aceita(word))
