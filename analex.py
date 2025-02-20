from automata.fa.Moore import Moore
import sys, os
import re
import ipdb
from pprint import pprint
from myerror import MyError

error_handler = MyError('LexerErrors')

global check_cm
global check_key

states = []

capital_letter = [ 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z' ]  # Letras maiúsculas

lowercase_letter = [ 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z' ]  # Letras minúsculas

numbers = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' ]  # Dígitos numéricos

symbols = [ '+', '-', '*', '/', '=', '!', '<', '>', '(', ')', '{', '}', '[', ']', ',', ';' ]  # Operadores e símbolos

delimiter_characters = [ ' ', '\n', '/t', ''] # Caracteres utilizados para verificar o fim de uma palavra

letters = []
letters.extend(capital_letter)
letters.extend(lowercase_letter)

alfanumericals = []
alfanumericals.extend(letters)
alfanumericals.extend(numbers)

input_alphabet = []  # Todas as letras e símbolos que a linguagem aceita

input_alphabet.extend(alfanumericals)
input_alphabet.extend(symbols)
input_alphabet.extend(delimiter_characters)

# output_alphabet =   [
#                         'IF', 'ELSE', 'INT', 'FLOAT', 'RETURN', 'VOID', 'WHILE', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LESS', 'LESS_EQUAL',
#                         'GREATER', 'GREATER_EQUAL', 'EQUALS', 'DIFFERENT', 'LPAREN', 'RPAREN' , 'LBRACKETS', 'RBRACKETS',
#                         'LBRACES', 'RBRACES', 'ATTRIBUTION', 'SEMICOLON', 'COMMA', 'NUMBER', 'ID', 'SPACE', 'NOTHING', '\n'
#                     ], # Lista de outputs possíveis

output_alphabet = [] # Eu olhei no código da máquina e só é necessário o alfabeto de output para a conversão de Mealy para Moore
 
initial_state = 'start' # Estado inicial  

reserved_letters = [ 'i', 'e', 'f', 'r', 'v', 'w' ]  # Letras iniciais de palavras reservadas

non_reserved_letters = []
non_reserved_letters.extend(capital_letter)
non_reserved_letters.extend(lowercase_letter)
non_reserved_letters = [letter for letter in non_reserved_letters if letter not in reserved_letters]

difficult_treatment_symbols = ['!', '<', '>', '=', '/']

transition_table = {}

output_table = {}

easy_symbols_table = {
    '(': 'LPAREN',
    ')': 'RPAREN',
    '{': 'LBRACES',
    '}': 'RBRACES',
    '[': 'LBRACKETS',
    ']': 'RBRACKETS',
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'TIMES',
    # '/': 'DIVIDE',
    # '=': 'ATTRIBUTION',
    # '!': 'DIFFERENT',
    # '<': 'LESS',
    # '>': 'GREATER',
    ';': 'SEMICOLON',
    ',': 'COMMA'
}

difficult_symbols_table = {
    # '(': 'LPAREN',
    # ')': 'RPAREN',
    # '{': 'LBRACES',
    # '}': 'RBRACES',
    # '[': 'LBRACKETS',
    # ']': 'RBRACKETS',
    # '+': 'PLUS',
    # '-': 'MINUS',
    # '*': 'TIMES',
    '/': 'DIVIDE',
    '=': 'ATTRIBUTION',
    '!': 'DIFFERENT',
    '<': 'LESS',
    '>': 'GREATER',
    # ';': 'SEMICOLON',
    # ',': 'COMMA'
}

def create_state(name):
    transition_table[name] = {}

def create_output(name, output):
    output_table[name] = output

def join_output(name, first_output, second_output):
    output_table[name] = f'{output_table[first_output]}\n{output_table[second_output]}'

def copy_transition(to_state, from_state='start', exception=None):
    if exception is None:
        exception = []
    for input, output in transition_table[from_state].items():
        if input not in exception:
            transition_table[to_state][input] = output

########################################################################################

# start state
create_state('start')

# start letters
for letter in letters:
    if letter not in reserved_letters: # Se a letra não for uma letra inicial de palavra reservada
        transition_table['start'][letter] = 'id_treatment'
    else:
        transition_table['start'][letter] = f'{letter}_treatment'
#
# start numbers
for number in numbers:
    transition_table['start'][number] = 'number_treatment'
#
# start symbols
for symbol in symbols:
    if symbol not in difficult_treatment_symbols:
        transition_table['start'][symbol] = f'{symbol}_accepted'
    else:
        transition_table['start'][symbol] = f'{symbol}_treatment'
#
# start delimiter_characters
for char in delimiter_characters:
    transition_table['start'][char] = 'start'
#
# start state finished

########################################################################################

# symbols states
for symbol in symbols:
    if symbol not in difficult_treatment_symbols:
        name = f'{symbol}_accepted'
        create_state(name)
        copy_transition(name)
        create_output(name, easy_symbols_table[symbol])
    else:
        if symbol == '/':
            create_state('/_treatment')
            create_state('/_accepted')
            create_state('comment_treatment_1')
            create_state('comment_treatment_2')
            transition_table['start'][symbol] = '/_treatment'
            transition_table['/_treatment']['*'] = 'comment_treatment_1'

            copy_transition('/_accepted')

            output_table['/_accepted'] = difficult_symbols_table[symbol]

            for char in input_alphabet:
                if char in letters:
                    create_state(f'{char}_id_treatment_/_accepted')
                    transition_table['/_treatment'][char] = f'{char}_id_treatment_/_accepted'
                    create_output(f'{char}_id_treatment_/_accepted', 'DIVIDE')

                if char in numbers:
                    create_state(f'{char}_number_treatment_/_accepted')
                    transition_table['/_treatment'][char] = f'{char}_number_treatment_/_accepted'
                    create_output(f'{char}_number_treatment_/_accepted', 'DIVIDE')
                
                if char in symbols:
                    if char not in difficult_treatment_symbols and char != '*':
                        create_state(f'{char}_accepted_/_accepted')
                        transition_table['/_treatment'][char] = f'{char}_accepted_/_accepted'
                        #feitos no fim do tratamento de simbolos
                        # create_output(f'{char}_accepted_/_accepted', 'DIVIDE\n' + output_table[f'{char}_accepted'])
                        # copy_transition(f'{char}_accepted_/_accepted', f'{char}_accepted')
                    if char in difficult_treatment_symbols and char != '*':
                        create_state(f'{char}_treatment_/_accepted')
                        transition_table['/_treatment'][char] = f'{char}_treatment_/_accepted'
                        create_output(f'{char}_treatment_/_accepted', 'DIVIDE')
                        # copy_transition(f'{char}_treatment_/_accepted', f'{char}_treatment') #feito no fim do tratamento de símbolos
                
                if char in delimiter_characters:
                    transition_table['/_treatment'][char] = '/_accepted'
            
            for char in input_alphabet:
                if char != '*':
                    transition_table['comment_treatment_1'][char] = 'comment_treatment_1'
                if char != '/':
                    transition_table['comment_treatment_2'][char] = 'comment_treatment_1'
                if char == '*':
                    transition_table['comment_treatment_1'][char] = 'comment_treatment_2'
                if char == '/':
                    transition_table['comment_treatment_2'][char] = 'comment_treatment_2'
        
            transition_table['comment_treatment_2']['/'] = 'start'
        
        if symbol == '=':
                create_state('=_treatment')
                create_state('==_accepted')
                create_state('=_accepted')
                create_state('==_accepted')

                copy_transition('=_accepted')
                copy_transition('==_accepted')

                transition_table['start'][symbol] = '=_treatment'

                create_output('=_accepted', difficult_symbols_table[symbol])
                create_output('==_accepted', 'EQUALS')

                for char in input_alphabet:
                    if char != '=':
                        transition_table['=_treatment'][char] = '=_accepted'
                    if char == '=':
                        transition_table['=_treatment'][char] = '==_accepted'
            
        if symbol == '!':
                create_state('!_treatment')
                create_state('!_accepted')
                create_state('!=_accepted')

                copy_transition('!_accepted')
                copy_transition('!=_accepted')

                transition_table['start'][symbol] = '!_treatment'

                create_output('!=_accepted', difficult_symbols_table[symbol])
                create_output('!_accepted', 'NOT')

                for char in input_alphabet:
                    if char != '=':
                        transition_table['!_treatment'][char] = '!_accepted'
                    if char == '=':
                        transition_table['!_treatment'][char] = '!=_accepted'
        
        if symbol == '<':
                create_state('<_treatment')
                create_state('<_accepted')
                create_state('<=_accepted')

                copy_transition('<_accepted')
                copy_transition('<=_accepted')

                transition_table['start'][symbol] = '<_treatment'

                create_output('<=_accepted', 'GREATER_EQUAL')
                create_output('<_accepted', difficult_symbols_table[symbol])

                for char in input_alphabet:
                    if char != '=':
                        transition_table['<_treatment'][char] = '<_accepted'
                    if char == '=':
                        transition_table['<_treatment'][char] = '<=_accepted'
            
        if symbol == '>':
                create_state('>_treatment')
                create_state('>_accepted')
                create_state('>=_accepted')

                copy_transition('>_accepted')
                copy_transition('>=_accepted')

                transition_table['start'][symbol] = '>_treatment'

                create_output('>=_accepted', 'GREATER_EQUAL')
                create_output('>_accepted', difficult_symbols_table[symbol])

                for char in input_alphabet:
                    if char != '=':
                        transition_table['>_treatment'][char] = '>_accepted'
                    if char == '=':
                        transition_table['>_treatment'][char] = '>=_accepted'

for char in input_alphabet:
        if char in symbols:
            if char not in difficult_treatment_symbols and char != '*':
                create_output(f'{char}_accepted_/_accepted', 'DIVIDE\n' + output_table[f'{char}_accepted'])
                copy_transition(f'{char}_accepted_/_accepted', f'{char}_accepted', ['/', '*'])
            if char in difficult_treatment_symbols and char != '*':
                copy_transition(f'{char}_treatment_/_accepted', f'{char}_treatment')

# symbols states finished

########################################################################################

# number_treatment state
create_state('number_treatment') # Treatment done below 

create_state('number_accepted')

copy_transition('number_accepted', exception=numbers)

create_state('number_id_treatment')

# ATENÇÃO, É NECESSÁRIO LIDAR COM ID ANTES DE FAZER A CÓPIA DE TRANSIÇÕES DE ID
# copy_transition('number_id_treatment', 'id_treatment')
# ---implementado no id_treatment---

create_output('number_accepted', 'NUMBER')

for letter in letters:
    transition_table['number_treatment'][letter] = 'number_id_treatment'

for number in numbers:
    transition_table['number_treatment'][number] = 'number_treatment'

# number_symbol_treatment is done here
for symbol in symbols:
    if symbol not in difficult_treatment_symbols:
        name = f'number_{symbol}_accepted'
        create_state(name)
        copy_transition(f'{name}', f'{symbol}_accepted')
        transition_table['number_treatment'][symbol] = name
        join_output(name, 'number_accepted', f'{symbol}_accepted')
    else:
        create_state(f'number_{symbol}_treatment')

        # ATENÇÃO 
        copy_transition(f'number_{symbol}_treatment', f'{symbol}_treatment')
        transition_table['number_treatment'][symbol] = f'number_{symbol}_treatment'

for char in delimiter_characters:
    transition_table['number_treatment'][char] = 'number_accepted'
# number_treatment state finished

########################################################################################

# id_treatment state
create_state('id_treatment')
create_state('id_accepted')

copy_transition('id_accepted')

create_output('id_accepted', 'ID')

for letter in letters:
    transition_table['id_treatment'][letter] = 'id_treatment'

for number in numbers:
    transition_table['id_treatment'][number] = 'id_treatment'

for symbol in symbols:
    if symbol not in difficult_treatment_symbols:
        transition_table['id_treatment'][symbol] = 'id_accepted'
    else:
        transition_table['id_treatment'][symbol] = f'{symbol}_treatment'

for symbol in symbols:
    if symbol not in difficult_treatment_symbols:
        name = f'id_{symbol}_accepted'
        create_state(name)
        copy_transition(f'{name}', f'{symbol}_accepted')
        transition_table['id_treatment'][symbol] = name
        join_output(name, 'id_accepted', f'{symbol}_accepted')
    else:
        create_state(f'id_{symbol}_treatment')

        copy_transition(f'id_{symbol}_treatment', f'{symbol}_treatment')
        create_output(f'id_{symbol}_treatment', 'ID') # ATENÇÃO 
        transition_table['id_treatment'][symbol] = f'id_{symbol}_treatment'

for delimiter in delimiter_characters:
    transition_table['id_treatment'][delimiter] = 'id_accepted'

# Copy to number_id_treatment
copy_transition('number_id_treatment', 'id_treatment')

# Copy to {symbol}_id_treatment_/_accepted e {symbol}_number_treatment_/_accepted
for char in input_alphabet:
    if char in letters:
        copy_transition(f'{char}_id_treatment_/_accepted', 'id_treatment')

    if char in numbers:
        copy_transition(f'{char}_number_treatment_/_accepted', 'number_treatment')

# id_treatment state finished

########################################################################################

def process_symbol_group(group, char, branch, copy_exc, token_prefix):
    """
    Cria um estado e configura as transições e output para um determinado grupo.
    
    Parâmetros:
      - group: Nome do grupo (ex.: 'v_treatment', 'void_vo', 'void_voi' ou 'void_void')
      - char: o caractere em questão (por exemplo, ';', '+', etc.)
      - branch: 'accepted' ou 'treatment'
      - copy_exc: lista de exceções para passar para copy_transition (ex.: ['o'], ['i'], ['d'] ou [] se nenhuma)
      - token_prefix: string a ser usada como prefixo no output (ex.: "ID\n" ou "VOID\n")
    """
    # Monta o nome do estado
    state_name = f"{group}_{char}_{branch}"
    create_state(state_name)
    
    # Insere o estado criado na tabela de transições do grupo
    # Se o grupo já não existir em transition_table, inicializamos um dicionário para ele
    if group not in transition_table:
        transition_table[group] = {}
    transition_table[group][char] = state_name

    # Para o branch "accepted", a saída é o prefixo mais o valor já definido em output_table para f'{char}_accepted'
    if branch == "accepted":
        extra = output_table.get(f"{char}_accepted", "")
        out_str = f"{token_prefix}{extra}"
    else:
        out_str = token_prefix

    create_output(state_name, out_str)

    # Define o estado de origem para copiar as transições:
    # para "accepted", usamos f'{char}_accepted'; para "treatment", usamos f'{char}_treatment'
    source_state = f"{char}_accepted" if branch == "accepted" else f"{char}_treatment"
    copy_transition(state_name, source_state, exception=copy_exc)


########################################################################################

# reserved_letters states
for letter in reserved_letters:
    name = f'{letter}_treatment'
    create_state(name)
    copy_transition(name, exception=[letter])

    transition_table['start'][letter] = f'{letter}_treatment'

    if letter == 'i':
        create_state('if_if')
        create_state('if_accepted')
        create_state('if_id_treatment')

        create_state('int_in')
        create_state('int_int')
        create_state('int_accepted')
        create_state('int_id_treatment')
        create_state('int_symbol_treatment')

        copy_transition('if_accepted')
        copy_transition('int_accepted')
        copy_transition('if_id_treatment', 'id_treatment')
        copy_transition('int_id_treatment', 'id_treatment')

        create_output('if_accepted', 'IF')
        create_output('int_accepted', 'INT')

        for char in input_alphabet:
            if char == 'f':
                transition_table[f'{letter}_treatment'][char] = 'if_if'
                for char in input_alphabet:
                    if char in letters or char in numbers:
                        transition_table['if_if'][char] = 'if_id_treatment'
                    if char in symbols:
                        if char not in difficult_treatment_symbols:
                            process_symbol_group("if_if", char, "accepted", [], "IF\n")
                        else:
                            process_symbol_group("if_if", char, "treatment", [], "IF\n")
                    if char in delimiter_characters:
                        transition_table['if_if'][char] = 'if_accepted'

            if char == 'n':
                transition_table[f'{letter}_treatment'][char] = 'int_in'
                for char in input_alphabet:
                    if char in letters or char in numbers:
                        if char != 't':
                            transition_table['int_in'][char] = 'int_id_treatment'
                        if char == 't':
                            transition_table['int_in'][char] = 'int_int'
                            for char in input_alphabet:
                                if char in letters:
                                    transition_table['int_int'][char] = 'int_id_treatment'
                                if char in symbols:
                                    if char not in difficult_treatment_symbols:
                                        create_state(f'int_int_{char}_accepted')
                                        transition_table['int_int'][char] = f'int_int_{char}_accepted'
                                        create_output(f'int_int_{char}_accepted', f'ID\n{output_table[f'{char}_accepted']}')
                                        copy_transition(f'int_int_{char}_accepted', f'{char}_accepted')
                                    else:
                                        create_state(f'int_int_{char}_treatment')
                                        transition_table['int_int'][char] = f'int_int_{char}_treatment'
                                        create_output(f'int_int_{char}_treatment', f'ID\n')
                                        copy_transition(f'int_int_{char}_treatment', f'{char}_treatment')
                                if char in delimiter_characters: 
                                    transition_table['int_int'][char] = 'int_accepted'

                    if char in symbols:
                        if char not in difficult_treatment_symbols:
                            create_state(f'int_in_{char}_accepted')
                            transition_table['int_in'][char] = f'int_in_{char}_accepted'
                            create_output(f'int_in_{char}_accepted', f'ID\n{output_table[f'{char}_accepted']}')
                            copy_transition(f'int_in_{char}_accepted', f'{char}_accepted')
                        else:
                            create_state(f'int_in_{char}_treatment')
                            transition_table['int_in'][char] = f'int_in_{char}_treatment'
                            create_output(f'int_in_{char}_treatment', f'ID\n')
                            copy_transition(f'int_in_{char}_treatment', f'{char}_treatment')
                    if char in delimiter_characters:
                        transition_table['int_in'][char] = 'id_accepted'
    
    if letter == 'v':
        create_state('void_vo')
        create_state('void_voi')
        create_state('void_void')
        create_state('void_accepted')
        create_state('void_id_treatment')

        copy_transition('void_accepted')
        copy_transition('void_id_treatment', 'id_treatment')

        create_output('void_accepted', 'VOID')

        for char in input_alphabet:
            if char in letters or char in numbers:
                if char == 'o':
                    transition_table[f'v_treatment'][char] = 'void_vo'                      
                else: 
                    transition_table[f'v_treatment'][char] = 'void_id_treatment'

                if char == 'i':
                    transition_table['void_vo'][char] = 'void_voi'
                else:
                    transition_table['void_vo'][char] = 'void_id_treatment'

                if char == 'd':
                    transition_table['void_voi'][char] = 'void_void'
                else:
                    transition_table['void_voi'][char] = 'void_id_treatment'

            if char in symbols:
                if char not in difficult_treatment_symbols:
                    process_symbol_group("v_treatment", char, "accepted", ['o'], "ID\n")
                    process_symbol_group("void_vo",   char, "accepted", ['i'], "ID\n")
                    process_symbol_group("void_voi",  char, "accepted", ['d'], "ID\n")
                    process_symbol_group("void_void", char, "accepted", [],     "VOID\n")
                    # create_state(f'v_treatment_{char}_accepted')
                    # transition_table[f'v_treatment'][char] = f'v_treatment_{char}_accepted'
                    # create_output(f'v_treatment_{char}_accepted', f'ID\n{output_table[f'{char}_accepted']}')
                    # copy_transition(f'v_treatment_{char}_accepted', f'{char}_accepted', ['o'])

                    # create_state(f'void_vo_{char}_accepted')
                    # transition_table['void_vo'][char] = f'void_vo_{char}_accepted'
                    # create_output(f'void_vo_{char}_accepted', f'ID\n{output_table[f'{char}_accepted']}')
                    # copy_transition(f'void_vo_{char}_accepted', f'{char}_accepted', ['i'])

                    # create_state(f'void_voi_{char}_accepted')
                    # transition_table[f'void_voi'][char] = f'void_voi_{char}_accepted'
                    # create_output(f'void_voi_{char}_accepted', f'ID\n{output_table[f'{char}_accepted']}')
                    # copy_transition(f'void_voi_{char}_accepted', f'{char}_accepted', ['d'])

                    # create_state(f'void_void_{char}_accepted')
                    # transition_table[f'void_void'][char] = f'void_void_{char}_accepted'
                    # create_output(f'void_void_{char}_accepted', f'VOID\n{output_table[f'{char}_accepted']}')
                    # copy_transition(f'void_void_{char}_accepted', f'{char}_accepted')

                else:
                    process_symbol_group("v_treatment", char, "treatment", ['o'], "ID\n")
                    process_symbol_group("void_vo",   char, "treatment", ['i'], "ID\n")
                    process_symbol_group("void_voi",  char, "treatment", ['d'], "ID\n")
                    process_symbol_group("void_void", char, "treatment", [],     "VOID\n")
                    # create_state(f'v_treatment_{char}_treatment')
                    # transition_table[f'v_treatment'][char] = f'v_treatment_{char}_treatment'
                    # create_output(f'v_treatment_{char}_treatment', f'ID\n')
                    # copy_transition(f'v_treatment_{char}_treatment', f'{char}_treatment', ['o'])

                    # create_state(f'void_vo_{char}_treatment')
                    # transition_table['void_vo'][char] = f'void_vo_{char}_treatment'
                    # create_output(f'void_vo_{char}_treatment', f'ID\n')
                    # copy_transition(f'void_vo_{char}_treatment', f'{char}_treatment', ['i'])

                    # create_state(f'void_voi_{char}_treatment')
                    # transition_table[f'void_voi'][char] = f'void_voi_{char}_treatment'
                    # create_output(f'void_voi_{char}_treatment', f'ID\n')
                    # copy_transition(f'void_voi_{char}_treatment', f'{char}_treatment', ['d'])

                    # create_state(f'void_void_{char}_treatment')
                    # transition_table[f'void_void'][char] = f'void_voi_{char}_treatment'
                    # create_output(f'void_void_{char}_treatment', f'VOID\n')
                    # copy_transition(f'void_void_{char}_treatment', f'{char}_treatment')

            if char in delimiter_characters:
                transition_table[f'v_treatment'][char] = 'id_accepted'
                transition_table['void_vo'][char] = 'id_accepted'
                transition_table['void_voi'][char] = 'id_accepted'
                transition_table['void_void'][char] = 'void_accepted' 
   
    if letter == 'r':
        create_state('return_re')
        create_state('return_ret')
        create_state('return_retu')
        create_state('return_retur')
        create_state('return_return')
        create_state('return_accepted')
        create_state('return_id_treatment')

        copy_transition('return_accepted')
        copy_transition('return_id_treatment', 'id_treatment')

        create_output('return_accepted', 'RETURN')

        for char in input_alphabet:
            if char in letters or char in numbers:
                if char == 'e':
                    transition_table['r_treatment'][char] = 'return_re'
                else:
                    transition_table['r_treatment'][char] = 'return_id_treatment'
                
                if char == 't':
                    transition_table['return_re'][char] = 'return_ret'
                else:
                    transition_table['return_re'][char] = 'return_id_treatment'

                if char == 'u':
                    transition_table['return_ret'][char] = 'return_retu'
                else:
                    transition_table['return_ret'][char] = 'return_id_treatment'

                if char == 'r':
                    transition_table['return_retu'][char] = 'return_retur'
                else:
                    transition_table['return_retu'][char] = 'return_id_treatment'

                if char == 'n':
                    transition_table['return_retur'][char] = 'return_return'
                else:
                    transition_table['return_retur'][char] = 'return_id_treatment'

            if char in symbols:
                if char not in difficult_treatment_symbols:
                    process_symbol_group("r_treatment", char, "accepted", ['e'], "ID\n")
                    process_symbol_group("return_re",   char, "accepted", ['t'], "ID\n")
                    process_symbol_group("return_ret",  char, "accepted", ['u'], "ID\n")
                    process_symbol_group("return_retu", char, "accepted", ['r'], "ID\n")
                    process_symbol_group("return_retur",char, "accepted", ['n'], "ID\n")
                    process_symbol_group("return_return", char, "accepted", [], "RETURN\n")

                else:
                    process_symbol_group("r_treatment", char, "treatment", ['e'], "ID\n")
                    process_symbol_group("return_re",   char, "treatment", ['t'], "ID\n")
                    process_symbol_group("return_ret",  char, "treatment", ['u'], "ID\n")
                    process_symbol_group("return_retu", char, "treatment", ['r'], "ID\n")
                    process_symbol_group("return_retur",char, "treatment", ['n'], "ID\n")
                    process_symbol_group("return_return", char, "treatment", [], "RETURN\n")
            
            if char in delimiter_characters:
                transition_table[f'r_treatment'][char] = 'id_accepted'
                transition_table['return_re'][char] = 'id_accepted'
                transition_table['return_ret'][char] = 'id_accepted'
                transition_table['return_retu'][char] = 'id_accepted'
                transition_table['return_retur'][char] = 'id_accepted'
                transition_table['return_return'][char] = 'return_accepted'

    if letter == 'f':
        create_state('float_fl')
        create_state('float_flo')
        create_state('float_floa')
        create_state('float_float')
        create_state('float_accepted')
        create_state('float_id_treatment')

        copy_transition('float_accepted')
        copy_transition('float_id_treatment', 'id_treatment')

        create_output('float_accepted', 'FLOAT')

        for char in input_alphabet:
            if char in letters or char in numbers:
                if char == 'l':
                    transition_table['f_treatment'][char] = 'float_fl'
                else:
                    transition_table['f_treatment'][char] = 'float_id_treatment'
                
                if char == 'o':
                    transition_table['float_fl'][char] = 'float_flo'
                else:
                    transition_table['float_fl'][char] = 'float_id_treatment'

                if char == 'a':
                    transition_table['float_flo'][char] = 'float_floa'
                else:
                    transition_table['float_flo'][char] = 'float_id_treatment'

                if char == 't':
                    transition_table['float_floa'][char] = 'float_float'
                else:
                    transition_table['float_floa'][char] = 'float_id_treatment'

            if char in symbols:
                if char not in difficult_treatment_symbols:
                    process_symbol_group("f_treatment", char, "accepted", ['l'], "ID\n")
                    process_symbol_group("float_fl",   char, "accepted", ['o'], "ID\n")
                    process_symbol_group("float_flo",  char, "accepted", ['a'], "ID\n")
                    process_symbol_group("float_floa", char, "accepted", ['t'], "ID\n")
                    process_symbol_group("float_accepted", char, "accepted", [], "FLOAT\n")

                else:
                    process_symbol_group("f_treatment", char, "treatment", ['l'], "ID\n")
                    process_symbol_group("float_fl",   char, "treatment", ['o'], "ID\n")
                    process_symbol_group("float_flo",  char, "treatment", ['a'], "ID\n")
                    process_symbol_group("float_floa", char, "treatment", ['t'], "ID\n")
                    process_symbol_group("float_accepted", char, "treatment", [], "FLOAT\n")
            
            if char in delimiter_characters:
                transition_table['f_treatment'][char] = 'id_accepted'
                transition_table['float_fl'][char] = 'id_accepted'
                transition_table['float_flo'][char] = 'id_accepted'
                transition_table['float_floa'][char] = 'id_accepted'
                transition_table['float_float'][char] = 'float_accepted'

    if letter == 'e':
        create_state('else_el')
        create_state('else_els')
        create_state('else_else')
        create_state('else_accepted')
        create_state('else_id_treatment')

        copy_transition('else_accepted')
        copy_transition('else_id_treatment', 'id_treatment')

        create_output('else_accepted', 'ELSE')

        for char in input_alphabet:
            if char in letters or char in numbers:
                if char == 'l':
                    transition_table['e_treatment'][char] = 'else_el'
                else:
                    transition_table['e_treatment'][char] = 'else_id_treatment'
                
                if char == 's':
                    transition_table['else_el'][char] = 'else_els'
                else:
                    transition_table['else_el'][char] = 'else_id_treatment'

                if char == 'e':
                    transition_table['else_els'][char] = 'else_else'
                else:
                    transition_table['else_els'][char] = 'else_id_treatment'

            if char in symbols:
                if char not in difficult_treatment_symbols:
                    process_symbol_group("e_treatment", char, "accepted", ['l'], "ID\n")
                    process_symbol_group("else_el",  char, "accepted", ['s'], "ID\n")
                    process_symbol_group("else_els", char, "accepted", ['e'], "ID\n")
                    process_symbol_group("else_accepted", char, "accepted", [], "ELSE\n")

                else:
                    process_symbol_group("e_treatment", char, "treatment", ['l'], "ID\n")
                    process_symbol_group("else_el",   char, "treatment", ['s'], "ID\n")
                    process_symbol_group("else_els",  char, "treatment", ['e'], "ID\n")
                    process_symbol_group("else_accepted", char, "treatment", [], "ELSE\n")

            if char in delimiter_characters:
                transition_table['e_treatment'][char] = 'id_accepted'
                transition_table['else_el'][char] = 'id_accepted'
                transition_table['else_els'][char] = 'id_accepted'
                transition_table['else_else'][char] = 'else_accepted'

    if letter == 'w':
        create_state('while_wh')
        create_state('while_whi')
        create_state('while_whil')
        create_state('while_while')
        create_state('while_accepted')
        create_state('while_id_treatment')

        copy_transition('while_accepted')
        copy_transition('while_id_treatment', 'id_treatment')

        create_output('while_accepted', 'WHILE')

        for char in input_alphabet:
            if char in letters or char in numbers:
                if char == 'h':
                    transition_table['w_treatment'][char] = 'while_wh'
                else:
                    transition_table['w_treatment'][char] = 'while_id_treatment'
                
                if char == 'i':
                    transition_table['while_wh'][char] = 'while_whi'
                else:
                    transition_table['while_wh'][char] = 'while_id_treatment'

                if char == 'l':
                    transition_table['while_whi'][char] = 'while_whil'
                else:
                    transition_table['while_whi'][char] = 'while_id_treatment'

                if char == 'e':
                    transition_table['while_whil'][char] = 'while_while'
                else:
                    transition_table['while_whil'][char] = 'while_id_treatment'

            if char in symbols:
                if char not in difficult_treatment_symbols:
                    process_symbol_group("w_treatment", char, "accepted", ['h'], "ID\n")
                    process_symbol_group("while_wh",  char, "accepted", ['i'], "ID\n")
                    process_symbol_group("while_whi", char, "accepted", ['l'], "ID\n")
                    process_symbol_group("while_whil",char, "accepted", ['e'], "ID\n")
                    process_symbol_group("while_accepted", char, "accepted", [], "WHILE\n")

                else:
                    process_symbol_group("w_treatment", char, "treatment", ['h'], "ID\n")
                    process_symbol_group("while_wh",   char, "treatment", ['i'], "ID\n")
                    process_symbol_group("while_whi",  char, "treatment", ['l'], "ID\n")
                    process_symbol_group("while_whil", char, "treatment", ['e'], "ID\n")
                    process_symbol_group("while_accepted", char, "treatment", [], "WHILE\n")

            if char in delimiter_characters:
                transition_table['w_treatment'][char] = 'id_accepted'
                transition_table['while_wh'][char] = 'id_accepted'
                transition_table['while_whi'][char] = 'id_accepted'
                transition_table['while_whil'][char] = 'id_accepted'
                transition_table['while_while'][char] = 'while_accepted'
########################################################################################

def main():

    moore = Moore(
                    states,
                    input_alphabet,
                    output_alphabet,
                    transition_table, 
                    initial_state, 
                    output_table 
                )

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
        if re.match (padrao_not_cm, arg):
            check_file = True
            idx_cm = idx + 1

            if re.match (padrao_cm, arg):
                check_cm = True

        if arg == "-k":
            check_key = True
    
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
            pprint(source_file)
            print("Entrada:")
        
        output = (moore.get_output_from_string(source_file))
        output = output.replace("\r\n", "\n")
        print(output)


if __name__ == "__main__":

    try:
        main()
    except Exception as e:
        print(e)
