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
    try:
        output_table[name] = f'{output_table[first_output]}\n{output_table[second_output]}'
    except:
        print('join_output ERROR')
        print('name:', name)
        print('first_output:', first_output)
        print('second_output:', second_output)

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

                output_table['/_accepted'] = difficult_symbols_table[symbol]

                for char in input_alphabet:
                    if char != '*':
                        transition_table['/_treatment'][char] = '/_accepted'
                        transition_table['comment_treatment_1'][char] = 'comment_treatment_1'
                    if char == '*':
                        transition_table['comment_treatment_1'][char] = 'comment_treatment_2'
                    if char != '/':
                        transition_table['comment_treatment_2'][char] = 'comment_treatment_1'
                    if char == '/':
                        transition_table['comment_treatment_2'][char] = 'start'
        
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

        # ATENÇÃO ainda não implementado
        # copy_transition(f'id_{symbol}_treatment', f'{symbol}_treatment')
        transition_table['id_treatment'][symbol] = f'id_{symbol}_treatment'

for delimiter in delimiter_characters:
    transition_table['id_treatment'][delimiter] = 'id_accepted'

# Copy to number_id_treatment
copy_transition('number_id_treatment', 'id_treatment')
# id_treatment state finished

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
                    else: # char in symbols or char in delimiter_characters
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
                    create_state(f'v_treatment_{char}_accepted')
                    transition_table[f'v_treatment'][char] = f'v_treatment_{char}_accepted'
                    create_output(f'v_treatment_{char}_accepted', f'ID\n{output_table[f'{char}_accepted']}')
                    copy_transition(f'v_treatment_{char}_accepted', f'{char}_accepted', ['o'])

                    create_state(f'void_vo_{char}_accepted')
                    transition_table['void_vo'][char] = f'void_vo_{char}_accepted'
                    create_output(f'void_vo_{char}_accepted', f'ID\n{output_table[f'{char}_accepted']}')
                    copy_transition(f'void_vo_{char}_accepted', f'{char}_accepted', ['i'])

                    create_state(f'void_voi_{char}_accepted')
                    transition_table[f'void_voi'][char] = f'void_voi_{char}_accepted'
                    create_output(f'void_voi_{char}_accepted', f'ID\n{output_table[f'{char}_accepted']}')
                    copy_transition(f'void_voi_{char}_accepted', f'{char}_accepted', ['d'])

                    create_state(f'void_void_{char}_accepted')
                    transition_table[f'void_void'][char] = f'void_void_{char}_accepted'
                    create_output(f'void_void_{char}_accepted', f'VOID\n{output_table[f'{char}_accepted']}')
                    copy_transition(f'void_void_{char}_accepted', f'{char}_accepted')

                else:
                    create_state(f'v_treatment_{char}_treatment')
                    transition_table[f'v_treatment'][char] = f'v_treatment_{char}_treatment'
                    create_output(f'v_treatment_{char}_treatment', f'ID\n')
                    copy_transition(f'v_treatment_{char}_treatment', f'{char}_treatment', ['o'])

                    create_state(f'void_vo_{char}_treatment')
                    transition_table['void_vo'][char] = f'void_vo_{char}_treatment'
                    create_output(f'void_vo_{char}_treatment', f'ID\n')
                    copy_transition(f'void_vo_{char}_treatment', f'{char}_treatment', ['i'])

                    create_state(f'void_voi_{char}_treatment')
                    transition_table[f'void_voi'][char] = f'void_voi_{char}_treatment'
                    create_output(f'void_voi_{char}_treatment', f'ID\n')
                    copy_transition(f'void_voi_{char}_treatment', f'{char}_treatment', ['d'])

                    create_state(f'void_void_{char}_treatment')
                    transition_table[f'void_void'][char] = f'void_voi_{char}_treatment'
                    create_output(f'void_void_{char}_treatment', f'VOID\n')
                    copy_transition(f'void_void_{char}_treatment', f'{char}_treatment')

            if char in delimiter_characters:
                transition_table[f'v_treatment'][char] = 'id_accepted'
                transition_table['void_vo'][char] = 'id_accepted'
                transition_table['void_voi'][char] = 'id_accepted'
                transition_table['void_void'][char] = 'void_accepted' 
   
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

    DEBUG = False
    if DEBUG == True:
        pprint(transition_table['void_accepted'])

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
            
            output = (moore.get_output_from_string(source_file))
            output.replace('\r', '')
            print(output)


if __name__ == "__main__":

    try:
        main()
    except Exception as e:
        print(e)
