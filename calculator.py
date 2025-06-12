import re

def isnum(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def s_exponentiate(a, b): # **
    if isnum(a) and isnum(b): # two numbers
        return float(a) ** float(b)

    raise TypeError("Can't exponentiate strings")

def s_multiply(a, b): # *
    if isnum(a) and isnum(b): # two numbers
        return float(a) * float(b)
    
    if not isnum(a) and not isnum(b): # two strings
        raise TypeError("Can't multiply two strings.")

    if isnum(a): # number and a string
        return str(b) * int(a)
    else: # string and a number
        return str(a) * int(b)

def s_divide(a, b): # /
    if isnum(a) and isnum(b): # two numbers
        return float(a) / float(b)
    
    raise TypeError("Can't divide strings") # a or b is a string

def s_floor_divide(a, b): # //
    if isnum(a) and isnum(b): # two numbers
        return float(a) // float(b)
    
    raise TypeError("Can't floor divide strings") # a or b is a string

def s_module(a, b): # %
    if isnum(a) and isnum(b): # two numbers
        return float(a) % float(b)
    
    raise TypeError("Can't module strings") # a or b is a string

def s_sum(a, b): # +
    if isnum(a) and isnum(b): # two numbers
        return float(a) + float(b)

    if not isnum(a) and not isnum(b): # two strings
        return str(a) + str(b)

    raise TypeError("Can't add string and number.") # string and number

def s_minus(a, b): # -
    if isnum(a) and isnum(b): # two numbers
        return float(a) - float(b)
    
    raise TypeError("Can't subtract strings") # a or b is a string

##########################--lexer--##########################
def lexer(oper):
    oper_tokens = [
    (r'\".*?\"|\'.*?\'', 'string'),  # string token: "text" or 'text'
    (r'\d+(\.\d+)?', 'number'),
    (r'\*\*|//|[%*/+-]', 'operation'),  # all operations grouped
    (r'\(', 'lparen'),
    (r'\)', 'rparen'),
    (r'\s+', None),  # whitespace to skip
    ]
    tokens = []
    string = oper
    while string:
        for token, token_type in oper_tokens: # Matching tokens with the string
            match = re.match(token, string)
            if match: # if there is a match
                if token_type: # if it's type isn't none
                    if token_type == 'string': # if it's a string delete first and last quotes
                        tokens.append([token_type, match.group()[1:-1]]) # append it in tokens list
                    else:
                        tokens.append([token_type, match.group()]) # append it in tokens list
                string = string[len(match.group()):]
                break
        else:
            raise SyntaxError(f"Unknown symbol: {string[0]}")
    tokens.insert(0, ['lparen', '('])
    tokens.append(['rparen', ')'])
    return tokens # return tokens list

##########################--parentheses--##########################

def match_parens(tokenized_oper): # match parens to each other
    lparens = []
    counter = 0 # parenthesis counter
    for i in range(len(tokenized_oper)):
        if tokenized_oper[i][0] == 'lparen': 
            tokenized_oper[i][0] = f'lparen{counter}' # change the token type to lparen + counter
            lparens.append(counter) 
            counter += 1
        elif tokenized_oper[i][0] == 'rparen':
            if not lparens:
                raise SyntaxError("Unmatched closing parenthesis") # raise an error if rparen unmatched
            tokenized_oper[i][0] = f'rparen{lparens.pop()}'
    if lparens:
        raise SyntaxError("Unmatched opening parenthesis") # raise an error if lparen unmatched
    return tokenized_oper


def split_by_parens(tokenized_oper): # split the operation into a dictionary of keys being paren numbers and values being operations inside them
    opers_by_paren = {}
    not_closed_parens = []
    
    for i in range(len(tokenized_oper)):
        token_type, token_value = tokenized_oper[i]
        
        lmatch = re.match(r'lparen(\d+)', token_type)
        rmatch = re.match(r'rparen(\d+)', token_type)
        
        if lmatch:
            paren_id = int(lmatch.group(1))
            not_closed_parens.insert(0, paren_id)
            opers_by_paren[f'paren{paren_id}'] = []  # init new paren scope
        elif rmatch:
            closed_id = int(rmatch.group(1))
            del not_closed_parens[0]  # remove the just-closed one
            if not_closed_parens:
                # insert this closed sub-paren into the outer one
                outer_id = not_closed_parens[0]
                opers_by_paren[f'paren{outer_id}'].append(f'paren{closed_id}')
        else:
            if not_closed_parens:
                current = not_closed_parens[0]
                opers_by_paren[f'paren{current}'].append(token_value)
    
    return opers_by_paren

##########################--calculate--##########################

def calculate(expression): # calculate an expression with no parentheses
    # handle **
    i = len(expression) - 1
    while i >= 0: # go through list from right to left
        if expression[i] == '**':
            a, op, b = expression[i - 1], expression[i], expression[i + 1]
            result = s_exponentiate(a, b)
            expression[i - 1:i + 2] = [result]
            i = len(expression)  # restart from end after changing the length of list
        i -= 1 # go one step back

    # handle *, /, %, //
    i = 0
    while i < len(expression): # go thriugh list from left to right
        if expression[i] in ('*', '/', '%', '//'):
            a, op, b = expression[i - 1], expression[i], expression[i + 1]
            match op:
                case '*': result = s_multiply(a, b)
                case '/': result = s_divide(a, b)
                case '%': result = s_module(a, b)
                case '//': result = s_floor_divide(a, b)
            expression[i - 1:i + 2] = [result]
            i = 0  # restart from beginning
        else:
            i += 1 # go one step forward

    # handle +, -
    i = 0
    while i < len(expression):
        if expression[i] in ('+', '-'):
            a, op, b = expression[i - 1], expression[i], expression[i + 1]
            match op:
                case '+': result = s_sum(a, b)
                case '-': result = s_minus(a, b)
            expression[i - 1:i + 2] = [result]
            i = 0  # restart from beginning
        else:
            i += 1 # go one step forward

    return expression
def oper(expression):

    tokenized = lexer(expression)

    tokenized = match_parens(tokenized)
    opers_by_paren = split_by_parens(tokenized)

    while True:
        changed = False # flag to check if anything changed

        for paren_id, expr in opers_by_paren.items(): # find expressions that don't contain any references to parentheses
            if isinstance(expr, list) and all(not str(e).startswith('paren') for e in expr):
                opers_by_paren[paren_id] = calculate(expr)[0] # calculate expression in paren
                changed = True # changed something

        for paren_id, result in opers_by_paren.items(): # replace all references to the paren in other parentheses
            for key in opers_by_paren:
                expr = opers_by_paren[key]
                if isinstance(expr, list):
                    for i in range(len(expr)):
                        if expr[i] == paren_id: # found a reference to a paren
                            expr[i] = result # replace with its calculated value
                            changed = True

        if not changed: # if nothing changed, all expressions are fully resolved
            break

    return list(opers_by_paren.values())[0]
