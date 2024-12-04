import sys
import re

def parse_glud(glud_file):
    """
    Lê a GLUD do arquivo, garantindo o balanceamento de {} e () em várias linhas.
    """
    try:
        with open(glud_file, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Erro: Arquivo '{glud_file}' não encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao abrir o arquivo '{glud_file}': {e}")
        sys.exit(1)

    rules = {}
    start_symbol = None
    variables = set()
    terminals = set()

    # Juntar linhas que fazem parte de uma mesma expressão com parênteses ou chaves
    def join_multiline(lines, open_char, close_char):
        """Reúne linhas enquanto os caracteres abertos não forem fechados."""
        combined_lines = []
        buffer = []
        balance = 0

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):  # Ignorar comentários e linhas vazias
                continue

            balance += line.count(open_char) - line.count(close_char)
            buffer.append(line)

            if balance == 0:
                combined_lines.append(" ".join(buffer))
                buffer = []

        if balance != 0:
            print(f"Erro: {open_char} e {close_char} desbalanceados.")
            sys.exit(1)

        return combined_lines

    # Reunir linhas de definições e produções
    joined_lines = join_multiline(lines, "(", ")")
    joined_lines = join_multiline(joined_lines, "{", "}")

    in_productions = False
    productions_block = []
    for line in joined_lines:
        # Processar cabeçalho: <G>=({A,B,C}, {a,b}, P, A)
        if "=({" in line and "}, {" in line:
            match = re.match(r"(.*?)=\(\{(.+?)\}, \{(.+?)\}, P, (.+?)\)", line)
            if match:
                variables = set(match.group(2).split(","))
                terminals = set(match.group(3).split(","))
                start_symbol = match.group(4).strip()
            else:
                print(f"Erro: Formato inválido no cabeçalho da GLUD: '{line}'")
                sys.exit(1)
            continue

        # Detectar início das produções
        if line == "P = {":
            in_productions = True
            continue

        # Detectar fim das produções
        if line == "}":
            in_productions = False
            continue

        # Processar produções
        if in_productions:
            productions_block.append(line)

    # Processar bloco de produções
    for line in productions_block:
        if "->" not in line:
            print(f"Erro: Produção inválida: '{line}'")
            sys.exit(1)

        left, right = line.split("->", 1)
        left = left.strip()
        right = [x.strip() for x in right.split("|")]

        # Adicionar regras ao dicionário
        if left not in rules:
            rules[left] = []
        rules[left].extend(right)

    # Validar GLUD
    if not start_symbol or not variables or not terminals:
        print("Erro: Definição da GLUD incompleta.")
        sys.exit(1)

    return start_symbol, rules, variables, terminals

def is_word_accepted(word, start_symbol, rules):
    """
    Verifica se uma palavra é aceita pela GLUD.
    """
    stack = [(start_symbol, 0)]  # Pilha para backtracking: (símbolo atual, índice na palavra)

    while stack:
        current_symbol, index = stack.pop()

        # Se o índice da palavra for igual ao tamanho e o símbolo for vazio, a palavra é aceita
        if index == len(word) and current_symbol == "":
            return True

        # Se o índice ultrapassar o tamanho da palavra, ignorar
        if index > len(word):
            continue

        # Aplicar as regras para o símbolo atual
        if current_symbol in rules:
            for production in rules[current_symbol]:
                # Substituir o símbolo atual pela produção e empilhar
                if production == "":
                    stack.append(("", index))
                elif index < len(word) and word[index] == production[0]:
                    stack.append((production[1:], index + 1))
        elif index < len(word) and word[index] == current_symbol:
            # Símbolo terminal: avançar
            stack.append(("", index + 1))

    return False

def test_words(glud_file, words_file):
    """
    Lê a GLUD e testa as palavras do arquivo de palavras.
    """
    # Carregar a GLUD
    start_symbol, rules, variables, terminals = parse_glud(glud_file)

    # Carregar as palavras
    try:
        with open(words_file, 'r') as f:
            words = [word.strip() for word in f.read().split(",")]
    except FileNotFoundError:
        print(f"Erro: Arquivo '{words_file}' não encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro ao abrir o arquivo '{words_file}': {e}")
        sys.exit(1)

    # Testar cada palavra
    results = {}
    for word in words:
        results[word] = is_word_accepted(word, start_symbol, rules)

    return results

if __name__ == "__main__":
    # Verificar se os arquivos de entrada foram fornecidos
    if len(sys.argv) < 3:
        print("Uso: python main.py <arquivo_glud> <arquivo_palavras>")
        sys.exit(1)

    # Arquivos de entrada
    glud_file = sys.argv[1]
    words_file = sys.argv[2]

    # Testar as palavras
    results = test_words(glud_file, words_file)

    # Exibir os resultados
    print("Resultados:")
    for word, accepted in results.items():
        status = "ACEITA" if accepted else "REJEITADA"
        print(f"Palavra '{word}': {status}")
