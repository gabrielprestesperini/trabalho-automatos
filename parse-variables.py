import re
import argparse
import json
from typing import List, TextIO

def is_balanced(s: str) -> bool:
    """
    Verifica se a string possui parênteses () e chaves {} balanceados e em ordem,
    ignorando todos os outros caracteres.

    Args:
        s (str): A string a ser verificada.

    Returns:
        bool: True se a string estiver balanceada, False caso contrário.
    """
    stack = []  # Pilha para rastrear os caracteres de abertura
    
    # Mapeamento de fechamento para abertura
    matching_pairs = {')': '(', '}': '{'}
    
    # Filtra apenas os caracteres relevantes
    filtered_s = ''.join(char for char in s if char in "(){}")
    
    for char in filtered_s:
        if char in "({":  # Se for um caractere de abertura, adiciona à pilha
            stack.append(char)
        elif char in ")}":  # Se for um caractere de fechamento
            if not stack or stack[-1] != matching_pairs[char]:
                return False  # Não há abertura correspondente ou está fora de ordem
            stack.pop()  # Remove o caractere de abertura correspondente da pilha
    
    return len(stack) == 0  # Deve terminar com a pilha vazia para estar balanceado

def extract_children(array_text: str) -> list:
    """
    Extrai os elementos filhos de uma string representando um array, suportando 
    arrays e sub-arrays delimitados por {} ou (), mesmo com aninhamentos complexos.

    Args:
        array_text (str): A string no formato de array, como "{...}" ou "(...)".

    Returns:
        list: Uma lista de strings representando os elementos do array.
    """
    result = []
    copy_array_text = array_text[1:-1].strip()
    newText = ""
    
    # print("copy_array_text: ", copy_array_text)

    while len(copy_array_text) > 0: 
        
        while(copy_array_text[0] in [',', ' ']):
            copy_array_text = copy_array_text[1:]    
        
        if(copy_array_text.startswith("{") or copy_array_text.startswith("(")):
            
            newText = copy_array_text[0:1]
            copy_array_text = copy_array_text[1:]
            
            while not is_balanced(newText):
                newText += copy_array_text[0:1]
                copy_array_text = copy_array_text[1:]
            
            # print("append",newText)
            result.append(
                newText
            )

        else:
            array_splited = copy_array_text.split(",")
            # print("append",array_splited[0].strip())
            result.append(
                array_splited[0].strip()
            )
            copy_array_text = ",".join(array_splited[1:])  
    
    # print("result extract: ", result)
    return result

def remove_after_hash_outside_quotes(input_string: str) -> str:
    """
    Remove tudo após o caractere '#' que não está entre aspas duplas.
    """
    in_quotes = False
    for index, char in enumerate(input_string):
        if char == '"':  # Alterna o estado de dentro das aspas
            in_quotes = not in_quotes
        elif char == '#' and not in_quotes:  # Encontra o '#' fora das aspas
            return input_string[:index].strip()  # Retorna a string até o índice do '#'
    return input_string.strip()  # Retorna a string inteira se nenhum '#' válido for encontrado

def parse_variables(file: TextIO):
    """
    Lê um arquivo e identifica variáveis na forma <nome_da_variavel> = <valor>.
    
    Args:
        file (TextIO): Um objeto de arquivo aberto.
    
    Returns:
        dict: Um dicionário com os pares nome/valor das variáveis.
    """
    # Regex para identificar variáveis na forma <nome_da_variavel> = <valor>
    variable_pattern = r'^(?P<name>\w+)\s*=\s*(?P<value>.+)$'
    variables = {}

    for line in file:
        # Remove comentários fora de aspas
        line = remove_after_hash_outside_quotes(line.strip())
        if not line:  # Ignorar linhas vazias
            continue

        # Verifica se a linha corresponde ao padrão de variável
        match = re.match(variable_pattern, line)
        if match:
            name = match.group("name")
            value = match.group("value")

            variables[name] = validate_value(value, file)  # Adiciona ao dicionário

    return variables

def validate_value(value: str, file: TextIO):
    if(value.startswith("{") or value.startswith("(")):
        finalValue = []
        while not is_balanced(value): 
            value = value + remove_after_hash_outside_quotes(file.readline().strip())
        
        for inside in extract_children(value):
            # print("inside: ",inside)
            finalValue.append(
                validate_value(inside.strip(), file)
            )
        
        return finalValue
    else:
        value.strip()
        if(value.startswith("\"") and value.endswith("\"")):    # caso entre ""
            return value[1:-1]
        if value.isdigit():                                     # caso numero inteiro
            return int(value)
        return value                                            # string sem ""

def main():
    # Configurando o parser de argumentos
    parser = argparse.ArgumentParser(description="Compilador para identificar variáveis.")
    parser.add_argument("file", help="Caminho do arquivo a ser processado.")
    
    args = parser.parse_args()

    try:
        # Lendo o arquivo
        file_content = open(args.file, 'r', encoding='utf-8') 
        
        # Processando o conteúdo do arquivo
        variables = parse_variables(file_content)
        print("Variáveis identificadas:")
        for name, value in variables.items():
            print(f"{name} = {json.dumps(value,indent=4)}")
    except FileNotFoundError:
        print(f"Erro: Arquivo '{args.file}' não encontrado.")
    except Exception as e:
        print(f"Erro inesperado: {e}")

if __name__ == "__main__":
    main()
