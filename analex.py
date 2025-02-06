from automata.fa.Moore import Moore
import sys, os
import re
from pprint import pprint

from myerror import MyError

error_handler = MyError('LexerErrors')

global check_cm
global check_key

states = []

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

# output_alphabet =   [
#                         'IF', 'ELSE', 'INT', 'FLOAT', 'RETURN', 'VOID', 'WHILE', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LESS', 'LESS_EQUAL',
#                         'GREATER', 'GREATER_EQUAL', 'EQUALS', 'DIFFERENT', 'LPAREN', 'RPAREN' , 'LBRACKETS', 'RBRACKETS',
#                         'LBRACES', 'RBRACES', 'ATTRIBUTION', 'SEMICOLON', 'COMMA', 'NUMBER', 'ID', 'SPACE', 'NOTHING', '\n'
#                     ], # Lista de outputs possíveis

output_alphabet = [] # Eu olhei no código da máquina e só é necessário o alfabeto de output para a conversão de Mealy para Moore
 
initial_state = 'start' # Estado inicial  

delimiter_characters = [ ' ', '\n', '/t', ''] # Caracteres utilizados para verificar o fim de uma palavra

reserved_letters = [ 'i', 'e', 'f', 'r', 'v', 'w' ]  # Letras iniciais de palavras reservadas

non_reserved_letters = []
non_reserved_letters.extend(capital_letter)
non_reserved_letters.extend(lowercase_letter)

transition_table = {
    'start': {},
}

#start
def start_treatment():
    try:
        delimiter_characters_treatment()
        letter_treatment()
        number_treatment()
        simbols_treatment()
    except Exception as e:
        print(f"Erro em start_treatment: {e}")

#tratamento de letras

def letter_treatment():
    reserved_letter_treatment()
    non_reserved_letter_treatment()

def non_reserved_letter_treatment():
    for letter in non_reserved_letters:
        transition_table['start'][letter] = 'id_treatment'
        if 'id_treatment' not in transition_table:
            transition_table['id_treatment'] = {}

def reserved_letter_treatment():
    for letter in reserved_letters:
        transition_table['start'][letter] = f'{letter}_reserved'
        if f'{letter}_reserved' not in transition_table:
            transition_table[f'{letter}_reserved'] = {}
    if_treatment()
    int_treatment()
    else_treatment()
    return_treatment()
    void_treatment()
    while_treatment()

def if_treatment():
    return

def int_treatment():
    return

def else_treatment():
    return

def return_treatment():
    return

def void_treatment():
    return

def while_treatment():
    return

#

#tratamento de números
def number_treatment():
    transition_table['number_treatment'] = {}
    transition_table['number_accepted'] = {}

    output_table['number_accepted'] = {}
    output_table['number_accepted'] = 'NUMBER' 

    # Loop para tratamento de números
    for number in numbers:
        transition_table['start'][number] = 'number_treatment'
        transition_table['number_treatment'][number] = 'number_treatment'

    # Tratamento de letras após um número
    for letter in letters:
        transition_table['number_treatment'][letter] = 'id_treatment'

    # Tratamento de símbolos após um número
    for simbol in simbols:
        transition_table['number_treatment'][simbol] = f'number_{simbol}_accepted'
        if f'number_{simbol}_accepted' not in transition_table:
            transition_table[f'number_{simbol}_accepted'] = {}
        if f'number_{simbol}_accepted' not in output_table:
            output_table[f'number_{simbol}_accepted'] = {}
            output_table[f'number_{simbol}_accepted'] = 'NUMBER'

    # Número aceito
    for char in delimiter_characters:
        transition_table['number_treatment'][char] = 'number_accepted'

    copy_transitions('start', 'number_accepted')
#

#tratamento dos símbolos
def simbols_treatment():
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

def delimiter_characters_treatment():
    for char in delimiter_characters:
        transition_table['start'][char] = 'start'


# tratamento de id
def id_treatment():
    return
#   

def i_treatment():
    for char in alfanumericals:
        if char not in ['n', 'f']:  # Excluindo 'n' e 'f' HARDCODED !!!
            transition_table['i_reserved'][char] = 'intermediary_id'

        # int_treatment
        if char == 'n':
            transition_table['i_reserved'][char] = 'int_in'
            if 'int_in' not in transition_table:
                transition_table['int_in'] = {}

        # if_treatment
        if char == 'f':
            transition_table['i_reserved'][char] = 'if_if'
            if 'if_if' not in transition_table:
                transition_table['if_if'] = {}

output_table = {}

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
    for state in transition_table.keys():
        output_table[state] = ''
    
    output_table['number_accepted'] = 'NUMBER' 


def populate_states(transition_table):
    for state in transition_table.keys():
        states.append(state)

def copy_transitions(from_state, to_state):
    for entrada, saida in transition_table[from_state].items():
        transition_table[to_state][entrada] = saida

# def copy_transitions_and_states(group, root_state, leaf_state, new_state_prefix):
#     for char in group:
#         if char in transition_table[root_state]:
#             original_state = transition_table[root_state][char]
#             new_state = f'{new_state_prefix}_{original_state}'
            
#             # Cria o novo estado na transition_table se não existir
#             if new_state not in transition_table:
#                 transition_table[new_state] = {}
                
#                 # Copia as transições do estado original para o novo estado
#                 if original_state in transition_table:
#                     for input_char, next_state in transition_table[original_state].items():
#                         transition_table[new_state][input_char] = next_state
            
#             # Adiciona o novo estado na output_table se não existir
#             # if new_state not in output_table:
#             #     output_table[new_state] = 'teste'
            
#             # Adiciona a transição do leaf_state para o next_state
#             transition_table.setdefault(leaf_state, {})
#             transition_table[leaf_state][char] = new_state

#number_treatment simbol copy
#as que não são _accepted, ainda há de serem tratadas

# copy_transitions_and_states(simbols, 'start', 'number_treatment', 'number')




def main():

    start_treatment()
    populate_states(transition_table)
    populate_output_table(transition_table)

    # pprint(output_table['number_accepted'])

    moore = Moore(
                    states,
                    input_alphabet,
                    output_alphabet,
                    transition_table, #lista de transições
                    initial_state, #estado inicial
                    output_table #tabela de saída
                )

    DEBUG = False

    if DEBUG == True:
        # for state, transitions in transition_table.items():
        #     print(f"State: {state}")
        #     for input_char, next_state in transitions.items():
        #         print(f"  On input '{input_char}' -> {next_state}")   
        return

    if DEBUG == False:
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
                #print("Definição da Máquina")
                # print(moore)
                # print("Entrada:")
                # print(source_file)
                print("Entrada:")
            
            print(moore.get_output_from_string(source_file))


if __name__ == "__main__":

    try:
        main()
    except Exception as e:
        print(e)
