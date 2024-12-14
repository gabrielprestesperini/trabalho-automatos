from typing import Dict, List, Tuple


class Automato:

    # define as tipagens
    estados: List[str]
    alfabeto: List[str]
    transicoes: Dict[Tuple[str, str], list[str]] = {}
    estado_inicial: str
    estados_finais: List[str] = []
    determinado: bool = False
    removeu_vazios: bool = False

    def __init__(self, dict_automato: dict):
        """
        Inicializa um autômato finito.

        Args:
            dict_automato (dict): Dicionário com as propriedades do autômato.
            Exemplo:  {'MinhaG': [['A', 'B', 'C'], ['a', 'b'], 'P', 'A'], 'P': ['A -> aB', 'A -> B', 'B -> bC', 'C -> a']}
        """
        self.name = next(iter(dict_automato.keys()))

        # Atribui definição do automato (cabeçalho)
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

            # Para cada destino daquela transição
            destItems: list[str] = items[1].strip().split("|")
            for dest in destItems:
                dest = dest.strip()
                # só estado destino
                if (dest in self.estados):
                    estado_destino = dest
                    self.__validateEstato(estado_destino)
                    self.__adiciona_transicao(
                        estado_origem, "", estado_destino)
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
                    self.__adiciona_transicao(
                        estado_origem, simbolo, estado_destino)

    def __aux_aceita(self, estado: str, cadeia: str) -> bool:
        """
        Função auxiliar para verificar se uma cadeia é aceita pelo autômato.

        Args:
            estado (str): Estado atual.
            cadeia (str): Cadeia de entrada.

        Returns:
            bool: True se a cadeia for aceita, False caso contrário.
        """

        # Se a palavra for vazia, retorna se o estado inicial é final
        if not cadeia:
            return estado in self.estados_finais or estado == ""

        charTerminal = cadeia[0]
        trans = self.transicoes.get((estado, charTerminal), [])
        transOpt = self.transicoes.get((estado, ""), [])
        if (len(trans) > 0 or len(transOpt) > 0):
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
        return self.__aux_aceita(self.estado_inicial, cadeia.strip())

    def __adiciona_transicao(self, estado_origem, simbolo, estado_destino):
        """
        Adiciona uma transição ao autômato.

        Args:
            estado_origem (str): Estado de origem.
            simbolo (str): Símbolo de transição.
            estado_destino (str): Estado de destino.
        """
        if ((estado_origem, simbolo) in self.transicoes):
            self.transicoes[(estado_origem, simbolo)].append(estado_destino)
        else:
            self.transicoes[(estado_origem, simbolo)] = [estado_destino]

    def converte_afd(self):
        """
        Função que checa se o autômato precisa ser convertido para AFD e chama as funções correspondentes.
        """
        # Checa se precisa remover movimentos vazios
        for trans in self.transicoes:
            if trans[1]=="":
                self.__converte_afn()
                self.removeu_vazios=True
                break
        # Checa se precisa ser determinado (mais de uma transição com o mesmo simbolo e estado)
        for estado in self.estados:
            for letra in self.alfabeto:
                if(len(self.transicoes.get((estado,letra)))>1):
                    self.__converte_afd()
                    self.determinado=True
                    break
            if(self.determinado):
                break

    def __converte_afn(self):
        """
        Converte o automato para AFN (Autônomo Finito Não-Determinístico)
        Muda-se apenas a função de transição e os estados finais
        """

        def fecho_vazio(estado):
            """
            Retorna o fecho vazio (estados alcançáveis apenas com movimentos vazios) de um estado.

            Args:
                estado(str): o estado para calcular o fecho vazio
             Returns:
                list: lista de estados do fecho
            """
            visitados = []
            pilha = [estado]
            while pilha:
                atual = pilha.pop()
                if atual not in visitados:
                    visitados.append(atual)
                    # Adiciona transições vazias se existirem
                    pilha.extend(self.transicoes.get((atual, ""), []))

            return visitados
        # Cria variáveis novas
        estados_finais_afn = []
        transicoes_afn = {}

        # Calcula o fechos-vazios de todos os estados
        fechos = {estado: fecho_vazio(estado) for estado in self.estados}

        #  Determinar os novos estados finais
        for estado, fecho in fechos.items():
            for estado_final in self.estados_finais:
                if estado_final in fecho:
                    estados_finais_afn.append(estado)

        # Recalcula as transições para cada símbolo no alfabeto
        transicoes_afn = {}
        for estado in self.estados:
            # Para cada letra do alfabeto
            for simbolo in self.alfabeto:
                estados_alcancaveis_com_simbolo = set()
                
                # Para cada estado alcançável por palavras vazias a partir do estado atual
                for estado_no_fecho in fechos[estado]:
                    # Se o estado alcanvável tiver transições com o simbolo, atualiza a lista de alcancáveis pelo simbolo
                    if self.transicoes.get((estado_no_fecho, simbolo), {}):
                        for prox_estado in self.transicoes[(estado_no_fecho, simbolo)]:
                            estados_alcancaveis_com_simbolo.update(fechos[prox_estado])
                # Caso tenha encontrado novos estados alcançáveis, atualiza lista original
                if estados_alcancaveis_com_simbolo:
                    transicoes_afn[(estado, simbolo)] = list(estados_alcancaveis_com_simbolo)
        
        # Re-atribui para automato os novos parâmetros
        self.transicoes = transicoes_afn
        self.estados_finais = estados_finais_afn

    def __converte_afd(self):
        """
        Converte o automato para AFD (Autônomo Finito Determinístico)
        """
        novos_estados = []
        novas_transicoes = {}
        novos_estados_finais = []
        
        # O estado inicial no determinístico é o fecho do estado inicial do não determinístico
        estado_inicial_deterministico = frozenset([self.estado_inicial])
        novos_estados.append(estado_inicial_deterministico)
        
        # Conjunto visitado para evitar repetição de estados
        estados_visitados = set()
        estados_visitados.add(estado_inicial_deterministico)

        # Fila de processamento para estados determinísticos
        fila = [estado_inicial_deterministico]

        while fila:
            estado_atual = fila.pop(0)
            
            for simbolo in self.alfabeto:
                # Determinar os estados alcançáveis com o símbolo
                estados_alcancaveis = set()
                for sub_estado in estado_atual:
                    estados_alcancaveis.update(self.transicoes.get((sub_estado, simbolo), []))
                
                if estados_alcancaveis:
                    estado_destino = frozenset(estados_alcancaveis)
                    
                    # Adiciona a transição no autômato determinístico
                    novas_transicoes[(estado_atual, simbolo)] = estado_destino
                    
                    # Adiciona o novo estado caso ainda não tenha sido processado
                    if estado_destino not in estados_visitados:
                        estados_visitados.add(estado_destino)
                        fila.append(estado_destino)
                        novos_estados.append(estado_destino)

        # Determinar os novos estados finais
        for estado in novos_estados:
            if any(sub_estado in self.estados_finais for sub_estado in estado):
                novos_estados_finais.append(estado)
        
        # Converter os estados de volta para strings legíveis
        mapeamento_estados = {estado: f"q{index}" for index, estado in enumerate(novos_estados)}
        estados_legiveis = [mapeamento_estados[estado] for estado in novos_estados]
        transicoes_legiveis = {(mapeamento_estados[origem], simbolo): [mapeamento_estados[destino]]
                               for (origem, simbolo), destino in novas_transicoes.items()}
        estados_finais_legiveis = [mapeamento_estados[estado] for estado in novos_estados_finais]

        # Atualizar o autômato com os novos estados e transições
        self.estados = estados_legiveis
        self.transicoes = transicoes_legiveis
        self.estado_inicial = mapeamento_estados[estado_inicial_deterministico]
        self.estados_finais = estados_finais_legiveis

    def __str__(self):
        """
        Representação do autômato como string.
        """
        return (f"Estados: {self.estados}\n"
                f"Alfabeto: {self.alfabeto}\n"
                f"Transições: {self.transicoes}\n"
                f"Estado Inicial: {self.estado_inicial}\n"
                f"Estados Finais: {self.estados_finais}\n")

