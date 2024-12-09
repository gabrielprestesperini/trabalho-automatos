import sys
from typing import Dict, List, Tuple


class Automato:

    # define as tipagens
    estados: List[str]
    alfabeto: List[str]
    transicoes: Dict[Tuple[str, str], list[str]] = {}
    estado_inicial: str
    estados_finais: List[str] = []

    def __init__(self, dict_automato: dict):
        """
        Inicializa um autômato finito.

        Args:
            dict_automato (dict): Dicionário com as propriedades do autômato.
        """
        self.name = next(iter(dict_automato.keys()))
        defAutomato = dict_automato[self.name]

        self.estados = defAutomato[0]
        self.alfabeto = defAutomato[1]
        self.estado_inicial = defAutomato[3]

        p = dict_automato['P']
        self.__proccess_transitions(p)

    def __validateEstato(self, estado: str):
        if not estado in self.estados:
            raise ValueError(f"Estado \"{estado}\" não encontrado\n")

    def __validateSimbolo(self, simbolo: str):
        if not simbolo in self.alfabeto:
            raise ValueError(f"Símbolo \"{simbolo}\" não encontrado\n")

    # cria uma função private
    def __proccess_transitions(self, p: List[str]):
        for trans in p:
            items = trans.split("->")
            estado_origem = items[0].strip()
            self.__validateEstato(estado_origem)
            destItems: list[str] = items[1].strip().split("|")
            for dest in destItems:
                dest = dest.strip()

                # só estado destino
                if (dest in self.estados):
                    estado_destino = dest
                    self.__validateEstato(estado_destino)
                    self.__adiciona_transicao(estado_origem, "", estado_destino)
                # só simbolo
                elif (dest in self.alfabeto or dest == "" or (len(dest) == 3 and dest[1] in self.estados and dest[0] == '"' and dest[2] == '"')):
                    if len(dest) == 3:
                        simbolo = dest[1]
                    else:
                        simbolo = dest

                    # adiciona como estado final
                    if not estado_origem in self.estados_finais:
                        self.estados_finais.append(estado_origem)
                        
                    # adiciona como transição final
                    if simbolo:
                        self.__validateSimbolo(simbolo)
                    self.__adiciona_transicao(estado_origem, simbolo, "")
                else:
                    simbolo = dest[0]
                    dest = dest[1:]
                    if (simbolo == '"'):
                        simbolo = dest[0]
                        dest = dest[2:]
                    estado_destino = dest
                    
                    # adiciona como transição
                    self.__validateSimbolo(simbolo)
                    self.__validateEstato(estado_destino)
                    self.__adiciona_transicao(estado_origem, simbolo, estado_destino)

    def __aux_aceita(self, estado: str, cadeia: str) -> bool:
        """
        Função auxiliar para verificar se uma cadeia é aceita pelo autômato.

        Args:
            estado (str): Estado atual.
            cadeia (str): Cadeia de entrada.

        Returns:
            bool: True se a cadeia for aceita, False caso contrário.
        """
        if not cadeia:
            return estado in self.estados_finais or estado == ""

        char = cadeia[0]
        trans = self.transicoes.get((estado, char), [])
        transOpt = self.transicoes.get((estado, ""), [])
        if(len(trans) > 0 or len(transOpt) > 0):
            result = False
            for t in trans:
                result = result or self.__aux_aceita(t, cadeia[1:])
            for t in transOpt:
                result = result or self.__aux_aceita(t, cadeia)
            return result
        else: 
            return False
        
    def aceita(self, cadeia: str) -> bool:
        """
        Verifica se uma cadeia é aceita pelo autômato.

        Args:
            cadeia (str): Cadeia de entrada.

        Returns:
            bool: True se a cadeia for aceita, False caso contrário.
        """
        return self.__aux_aceita(self.estado_inicial, cadeia)


    def __adiciona_transicao(self, estado_origem, simbolo, estado_destino):
        """
        Adiciona uma transição ao autômato.

        Args:
            estado_origem (str): Estado de origem.
            simbolo (str): Símbolo de transição.
            estado_destino (str): Estado de destino.
        """
        if((estado_origem, simbolo) in self.transicoes):
            self.transicoes[(estado_origem, simbolo)].append(estado_destino)
        else:
            self.transicoes[(estado_origem, simbolo)] = [estado_destino]

    def __str__(self):
        """
        Representação do autômato como string.
        """
        return (f"Estados: {self.estados}\n"
                f"Alfabeto: {self.alfabeto}\n"
                f"Transições: {self.transicoes}\n"
                f"Estado Inicial: {self.estado_inicial}\n"
                f"Estados Finais: {self.estados_finais}\n")
