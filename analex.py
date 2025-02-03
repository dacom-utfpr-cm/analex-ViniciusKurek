from automata.fa.Moore import Moore
import sys, os
import re
from pprint import pprint

from myerror import MyError

error_handler = MyError('LexerErrors')

global check_cm
global check_key
    
states = [], # Lista de todos estados do autômato

capital_letter = [ 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z' ]  # Letras maiúsculas

lowercase_letter = [ 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z' ]  # Letras minúsculas

numbers = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' ]  # Dígitos numéricos

simbols = [ '+', '-', '*', '/', '=', '!', '<', '>', '(', ')', '{', '}', '[', ']', ',', ';' ]  # Operadores e símbolos

letters = []
letters.extend(capital_letter)
letters.extend(lowercase_letter)

alfanumericals = []
alfanumericals.extend(letters)
alfanumericals.extend(numbers)

input_alphabet = [
    ' ', '\n', '\t',  # Espaços, quebras de linha, tabulações
]  # Todas as letras e símbolos que a linguagem aceita

input_alphabet.extend(alfanumericals)
input_alphabet.extend(simbols)

output_alphabet =   [
                        'IF', 'ELSE', 'INT', 'FLOAT', 'RETURN', 'VOID', 'WHILE', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LESS', 'LESS_EQUAL',
                        'GREATER', 'GREATER_EQUAL', 'EQUALS', 'DIFFERENT', 'LPAREN', 'RPAREN' , 'LBRACKETS', 'RBRACKETS',
                        'LBRACES', 'RBRACES', 'ATTRIBUTION', 'SEMICOLON', 'COMMA'
                    ], # Lista de outputs possíveis

initial_state = 'start' # Estado inicial  

delimiter_characters = [ ' ', '/n', '/t'] # Caracteres utilizados para verificar o fim de uma palavra

reserved_letters = [ 'i', 'e', 'f', 'r', 'v', 'w' ]  # Letras iniciais de palavras reservadas

non_reserved_letters = []
non_reserved_letters.extend(capital_letter)
non_reserved_letters.extend(lowercase_letter)

transition_table = {
    'start': {},
    'i_reserved': {
        'f': 'if_if',
        'n': 'int_in',
    },
    'if_if': {},
}

#start

#tratamento de letras

for letter in non_reserved_letters:
    transition_table['start'][letter] = 'id_treatment'

for letter in reserved_letters:
    transition_table['start'][letter] = f'{letter}_reserved'

#

#tratamento de números
transition_table['number_treatment'] = {}

for number in numbers:
    transition_table['start'][number] = 'number_treatment'
    transition_table['number_treatment'][number] = 'number_treatment'

for letter in letters:
    transition_table['number_treatment'][letter] = 'id_treatment'

for simbol in simbols: 
    transition_table['number_treatment'][simbol] = f'{simbol}_accepted'

#copia transição e estados de simbolos e muda a saída deles 

#

#tratamento dos símbolos
for simbol in simbols:

    if simbol not in ['!', '<', '>', '=']:  # Excluindo '!', '<', '>', '=' HARDCODED CUIDADO !!!!!!!
        transition_table['start'][simbol] = f'{simbol}_accepted'

    if simbol == '!':
        transition_table['different_treatment'] = {}
        transition_table['start'][simbol] = 'different_treatment'
        transition_table['different_treatment']['='] = 'different_accepted'

    if simbol == '<':
        transition_table['less_treatment'] = {}
        transition_table['start'][simbol] = 'less_treatment'
        transition_table['less_treatment']['='] = 'less_equal_accepted'
        for char in delimiter_characters:
            transition_table['less_treatment'][char] = 'less_accepted'

    if simbol == '>':
        transition_table['greater_treatment'] = {}
        transition_table['start'][simbol] = 'greater_treatment'
        transition_table['greater_treatment']['='] = 'greater_equal_accepted'
        for char in delimiter_characters:
            transition_table['greater_treatment'][char] = 'greater_accepted'

    if simbol == '=':
        transition_table['equal_treatment'] = {}
        transition_table['start'][simbol] = 'equal_treatment'
        transition_table['equal_treatment']['='] = 'equals_accepted'
        for char in delimiter_characters:
            transition_table['equal_treatment'][char] = 'attribution_accepted'

#


teste  = []
# tratamento de id

for char in input_alphabet:
    if char not in delimiter_characters:
        if char not in alfanumericals:
            teste.append(char)
#   

for char in delimiter_characters:
    transition_table['if_if'][char] = 'if_accepted'

for char in set(input_alphabet) - set(delimiter_characters):
    transition_table['if_if'][char] = 'intermediary_id'

for char in alfanumericals:
    if char not in ['n', 'f']:  # Excluindo 'n' e 'f' HARDCODED CUIDADO !!!!!!!
        transition_table['i_reserved'][char] = 'intermediary_id'

output_table = {}

def update_output_table_with_states(transition_table, output_table):
    unique_states = set()
    for state in transition_table:
        unique_states.add(state)
        for next_state in transition_table[state].values():
            unique_states.add(next_state)
    
    for state in unique_states:
        if state not in output_table:
            output_table[state] = ''

update_output_table_with_states(transition_table, output_table)

output_table = {
    '(_accepted': 'LPAREN',
    ')_accepted': 'RPAREN',
    '{_accepted': 'LBRACES',
    '}_accepted': 'RBRACES',
    '[_accepted': 'LBRACKETS',
    ']_accepted': 'RBRACKETS',
    '+_accepted': 'PLUS',
    '-_accepted': 'MINUS',
    '*_accepted': 'TIMES',
    # '/_accepted': 'DIVIDE',
    # '=_accepted': 'EQUALS',
    # '!_accepted': 'DIFFERENT',
    # '<_accepted': 'LESS',
    # '>_accepted': 'GREATER',
    ';_accepted': 'SEMICOLON',
    ',_accepted': 'COMMA',
}

symbol_to_word = {
    '(': 'LPAREN',
    ')': 'RPAREN',
    '{': 'LBRACES',
    '}': 'RBRACES',
    '[': 'LBRACKETS',
    ']': 'RBRACKETS',
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'TIMES',
    '/': 'DIVIDE',
    '=': 'EQUALS',
    '!': 'DIFFERENT',
    '<': 'LESS',
    '>': 'GREATER',
    ';': 'SEMICOLON',
    ',': 'COMMA'
}


def populate_output_table(transition_table):
    # Adicionar todos os estados na output_table com valor de string vazia
    for state in transition_table.keys():
        output_table[state] = ''
    
    for state, transitions in transition_table.items():
        for input_char, next_state in transitions.items():
            if next_state.endswith('_accepted'):
                output_key = next_state
                symbol = next_state.split('_')[0]
                output_value = symbol_to_word.get(symbol, symbol.upper())
                output_table[output_key] = output_value

populate_output_table(transition_table)

def populate_states(transition_table):
    global states
    states = set()
    for state in transition_table:
        states.add(state)
        for next_state in transition_table[state].values():
            states.add(next_state)
    states = list(states)

populate_states(transition_table)

def copy_transitions_states(group, root_state, leaf_state):
    for char in group:
        if char in transition_table[root_state]:
            transition_table[leaf_state][char] = transition_table[root_state][char]
            # print(f"Key: {char}, Value: {transition_table[initial_state][char]}")

copy_transitions_states(simbols, 'start', 'number_treatment')

moore = Moore(
                states,
                input_alphabet,
                output_alphabet,
                transition_table, #lista de transições
                initial_state, #estado inicial
                output_table #tabela de saída
              )

def main():
    DEBUG = 1

    if DEBUG == 1:
        # for state, transitions in transition_table.items():
        #     print(f"State: {state}")
        #     for input_char, next_state in transitions.items():
        #         print(f"  On input '{input_char}' -> {next_state}")
        pprint(transition_table['number_treatment'])

    if DEBUG == 0:
        global check_cm
        global check_key
        global check_file 

        check_cm = False
        check_key = False
        check_file = False

        idx_cm = 0

        padrao_cm = r"[\w\W]*.cm$" #arquivo com fim cm
        padrao_not_cm = r"[\w\W]*\.[\w]+$" #arquivo not cm != arquivo com fim not cm
        
        for idx, arg in enumerate(sys.argv[1:]):
            # print("Argument #{} is {}".format(idx, arg))
            # aux = arg.split('.')
            # if aux[-1] == 'cm':
            #     check_cm = True
            #     idx_cm = idx

            # if(arg == "-k"):
            #     check_key = True
            if re.match (padrao_not_cm, arg):
                check_file = True
                idx_cm = idx + 1

                if re.match (padrao_cm, arg):
                    check_cm = True

            if arg == "-k":
                check_key = True
        
        #print ("No. of arguments passed is ", len(sys.argv))
        # print('check_file', check_file)
        # print('check_cm', check_cm)
        if not check_file:
            raise TypeError(error_handler.newError(check_key, 'ERR-LEX-USE'))
        if not check_cm:
            raise IOError(error_handler.newError(check_key, 'ERR-LEX-NOT-CM'))
        elif not os.path.exists(sys.argv[idx_cm]):
            raise IOError(error_handler.newError(check_key, 'ERR-LEX-FILE-NOT-EXISTS'))
        else:
            data = open(sys.argv[idx_cm])

            source_file = data.read()

            if not check_key:
                print("Definição da Máquina")
                print(moore)
                print("Entrada:")
                print(source_file)
                print("Lista de Tokens:")
            
            print(moore.get_output_from_string(source_file))


if __name__ == "__main__":

    try:
        main()
    except Exception as e:
        print(e)
    except (ValueError, TypeError):
        print(e)