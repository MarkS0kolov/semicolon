import re # matching special samples
import bullshit

SINGLE_TOKENS: list[tuple[str,str]] = [ # single tokens. used pretty rare
    
    # main :)
    (r'\.', 'DOT'), # just dot
    (r',', 'CMA'), # just comma
    
    # comments
    (r'.', None), # any other symbol is a comment
]

TWO_DIGIT_TOKENS: list[tuple[str,str]] = [ # two digit tokens. section markers and splitter markers. essential
                                        # for any program
    # sections markers (2 total)
    (r'\.\.', 'DSC'), # data section marker
    (r'\.,', 'ISC'), # instruction section marker
    # splitter markers (2 total)
    (r',\.', 'DSP'), # marker that splits two data sections (like ',' in arrays)
    (r',,', 'ISP'), # marker that splits two instructions (analog of ';' in langs like C++)
    
    # comments
    (r'.', None), # any other symbol is a comment
    (r'', None),
]

TREE_DIGIT_TOKENS: list[tuple[str,str]] = [ # three digit tokens. only type markers. used almost always
    # type markers (8 total)
    (r'\.\.\.', 'VAR'), # variable
    (r'\.\.,', 'MGC'), # magic variables, classes and e.t.c.
    (r'\.,\.', 'ARR'), # array
    (r',\.\.', 'NUM'), # number (int and float)
    (r'\.,,', 'CLS'), # class (future)
    (r',,\.', 'BUL'), # bool
    (r',\.,', 'STR'), # string
    (r',,,', 'NOT'), # nothing (analog of None or null)
    
    # comments
    (r'.', None), # any other symbol is a comment
    (r'', None),
]

NUM_REPR: list[tuple[str,str]] = [(r'\.+,+', 'DEFAULT')] # representation of num in program (differ from common one) :)
BUL_REPR: list[tuple[str,str]] = [(r'(\.|,)', 'DEFAULT')] # bool representation where '.' - True and ',' - False
NOT_REPR: list[tuple[str,str]] = [(r'()', 'DEFAULT')] # nothing representation

SIX_DIGIT_TOKENS: list[tuple[str,str]] = [ # six digit tokens. only instructions. used always I suppose
    # instruction markers (64 total (30 used))
        # fundamental instructions
    (r'\.\.\.\.\.\.', 'MOV'), # analog of let
    (r'\.\.,,,,', 'DEL'), # delete object
    (r'\.,,\.\.,', 'TYP'), # returns object's type
        # type transformations instructions
    (r',\.,\.\.,', 'TVR'), # to var
    (r'\.\.\.,\.,', 'TAR'), # to array
    (r'\.\.\.\.,,', 'TNM'), # to num
    (r'\.,,,\.\.', 'TBL'), # to bool
    (r',\.\.\.,,', 'TSR'), # to str
        # console instructions
    (r',,,,,,', 'LOG'), # analog of print
    (r',,,\.\.\.', 'INP'), # analog of input
    (r'\.,,,,,', 'ERR'), # analog of raise 
        # math instructions
    (r',,\.,,\.', 'ADD'), # +
    (r'\.\.,\.\.,', 'SUB'), # -
    (r',\.,\.,\.', 'MUL'), # *
    (r'\.,\.,\.,', 'DIV'), # /
        # bool instructions
    (r'\.,,,,\.', 'IFT'), # if ('if then')
    (r',\.\.\.\.,', 'ELS'), # else
    (r'\.\.\.,,,', 'GRT'), # greater than (>)
    (r',,,\.\.\.', 'LST'), # less than (<)
    (r',\.\.\.,\.', 'EQT'), # equal to (==)
    (r'\.,,\.,,', 'ORC'), # or (|)
    (r'\.,,\.\.\.', 'AND'), # and (&)
    (r'\.\.\.,\.\.', 'INA'), # in (.contains)
        # array instructions
    (r'\.,\.\.\.\.', 'IND'), # a possibility to search an element by its index ([i])
    (r'\.,\.,\.\.', 'ITR'), # for ... in ...
    (r',,\.\.,,', 'LEN'), # returns length of an array (or string, because, frankly speaking, it is also an array)
        # loop instructions
    (r',\.,\.,,\.', 'LUP'), # loop (while)
    (r'\.,\.,,,', 'BRK'), # break
    (r',\.,\.\.\.', 'CNT'), # continue
        # functions instructions
    (r'\.\.\.\.\.,', 'RTN'), # return 
        # exception handling
    (r'\.,\.\.,,', 'TRY'),
    (r',\.,,\.\.', 'FAL'),
    (r'\.,\.\.\.,', 'FNL'),

    # comments
    (r'.', None), # any other symbol is a comment
    (r'', None),
]

INSTRUCTIONS = [token[1] for token in SIX_DIGIT_TOKENS][:len(SIX_DIGIT_TOKENS) - 2]

current_position = 0

def lexer(code: str, TOKENS_LIST: list[tuple[str,str]], length: int = None) -> tuple | None | bullshit.Bullshit:
    '''
    Matching and splitting code to tokens
    '''
    global current_position
    length = len(code) if not length else length
    current_position = 0
    res_token = None
    for pattern, token_type in TOKENS_LIST: # Matching tokens with the code
        match = re.match(pattern, code[:length])
        if match: # if there is a match
            if token_type: # if it's type s not none
                res_token = (token_type, match.group()) # append it in tokens list
            code = code[len(match.group()):]
            current_position += len(match.group())                     
            break
    else:
        return bullshit.SyntaxFailure(f"unknown symbol '{code}'")
    return res_token # return tokens list

def starter_lexer(code: str) -> list[tuple[str, str]] | str | bullshit.Bullshit:
    '''
    Lexing first part of code to tokens (using lexer())
    '''
    tokens_res = []
    first_token = lexer(code, TWO_DIGIT_TOKENS, 2)
    code = code[2:]
    if first_token:
        match first_token[0]:
            case 'ISP':
                tokens_res.append(first_token)
                first_section = lexer(code, TWO_DIGIT_TOKENS, 2)
                code = code[2:]
                if first_section:
                    match first_section[0]:
                        case 'ISC':
                            tokens_res.append(first_section)
                            instruction_name = lexer(code, SIX_DIGIT_TOKENS, 6)
                            if instruction_name:
                                code = code[6:]
                                tokens_res.append(instruction_name)
                                additional_section = lexer(code, TWO_DIGIT_TOKENS, 2)
                                if additional_section:
                                    code = code[2:]
                                    match additional_section[0]:
                                        case 'DSC' | 'ISP':
                                            tokens_res.append(additional_section)
                            else:
                                return bullshit.SyntaxFailure("expected an instruction's name")
                        case 'DSC':
                            tokens_res.append(first_section)
                return (tokens_res, code)
            case _:
                return bullshit.SyntaxFailure(
            "any instruction should start and end with a instruction splitter (',,'). Maybe you forgot one?")
    return bullshit.SyntaxFailure(
            "any instruction should start and end with a instruction splitter (',,'). Maybe you forgot one?")

def data_lexer(code: str) -> list[tuple[str, str]] | str | bullshit.Bullshit:
    '''
    Lexing main content (data) of code depending on its type (using lexer())
    '''
    tokens_res = []
    datatype = lexer(code, TREE_DIGIT_TOKENS, 3)
    if datatype:
        code = code[3:]
        tokens_res.append(datatype)
        match datatype[0]:
            case "NUM":
                num_token = lexer(code, NUM_REPR)
                if num_token:
                    number_length = len(num_token[1])
                    code = code[number_length-1:]
                    tokens_res.append((num_token[0], num_token[1][:-1]))
                    data_end = lexer(code, TWO_DIGIT_TOKENS, 2)
                    if data_end:
                        code = code[2:]
                        tokens_res.append(data_end)
                    else:
                        return bullshit.SyntaxFailure("expected end of data in NUM declaration")
            case "BUL":
                bool_token = lexer(code, BUL_REPR, 1)
                if bool_token:
                    code = code[1:]
                    tokens_res.append(bool_token)
                    data_end = lexer(code, TWO_DIGIT_TOKENS, 2)
                    if data_end:
                        code = code[2:]
                        tokens_res.append(data_end)
                    else:
                        return bullshit.SyntaxFailure("expected end of data in BUL declaration")
            case 'NOT':
                tokens_res.append(('DEFAULT', ''))
                data_end = lexer(code, TWO_DIGIT_TOKENS, 2)
                if data_end:
                    code = code[2:]
                    tokens_res.append(data_end)
                else:
                    return bullshit.SyntaxFailure("expected end of data in NOT declaration")
            case 'ARR' | 'STR' | 'VAR':
                while True:
                    first_section = lexer(code, TWO_DIGIT_TOKENS, 2)
                    code = code[2:]
                    if first_section:
                        match first_section[0]:
                            case 'DSC':
                                tokens_res.append(first_section)
                            case 'DSP':
                                tokens_res.append(first_section)
                                break
                    recursion_res = data_lexer(code)
                    if isinstance(recursion_res, bullshit.Bullshit):
                        return recursion_res
                    tokens_res += recursion_res[0]
                    code = recursion_res[1]
                    elementEnd = lexer(code, TWO_DIGIT_TOKENS, 2)
                    if elementEnd:
                        match elementEnd[0]:
                            case 'DSP':
                                code = code[2:]
                                tokens_res.append(elementEnd)
                                break
                            case 'DSC':
                                pass
                            case _:
                                return bullshit.SyntaxFailure("expected a data splitter at the end of array")
    return (tokens_res, code)

def main_lexer(code: str, stop_token = None) -> list[tuple[str, str]] | str | bullshit.Bullshit:
    '''
    Assembly off all lexers into one. Main lexer
                                                Using:
                                                    data_lexer(),
                                                    starter_lexer() and
                                                    lexer()
    '''
    tokens_res = []
    while code:
        stop = lexer(code, TWO_DIGIT_TOKENS, 2)
        if stop and stop[0] == stop_token:
            break
        starter_result = starter_lexer(code)
        if isinstance(starter_result, bullshit.Bullshit):
            return starter_result
        code = starter_result[1]
        tokens_res += starter_result[0]
        data_tokens = data_lexer(code)
        if isinstance(data_tokens, bullshit.Bullshit):
            return data_tokens
        code = data_tokens[1]
        tokens_res += data_tokens[0]
    return (tokens_res, code)

if __name__ == "__main__": #? Logs
    code = input()
    result = main_lexer(code)
    if isinstance(result, bullshit.Bullshit):
        print(result)
    else:
        print(main_lexer(code)[0])