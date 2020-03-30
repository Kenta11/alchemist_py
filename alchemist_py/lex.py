import ply.lex as lex

tokens = (
    'STRUCT',
    'RESERVED',
    'TYPE_PRIMITIVE_INT',
    'TYPE_PRIMITIVE_FLOAT',
    'TYPE_CSTDINT',
    'TYPE_UNSIGNED',
    'TYPE_BOOL',
    'TYPE_STRING',
    'VAR_NAME',
    'INTEGER',
    'L_BRACE',
    'R_BRACE',
    'L_BRACKET',
    'R_BRACKET',
    'SEMICOLON',
)

reserved = {
    'struct'   : 'STRUCT',
    'char'     : 'TYPE_PRIMITIVE_INT',
    'short'    : 'TYPE_PRIMITIVE_INT',
    'int'      : 'TYPE_PRIMITIVE_INT',
    'long'     : 'TYPE_PRIMITIVE_INT',
    'float'    : 'TYPE_PRIMITIVE_FLOAT',
    'double'   : 'TYPE_PRIMITIVE_FLOAT',
    'uint8_t'  : 'TYPE_CSTDINT',
    'uint16_t' : 'TYPE_CSTDINT',
    'uint32_t' : 'TYPE_CSTDINT',
    'uint64_t' : 'TYPE_CSTDINT',
    'int8_t'   : 'TYPE_CSTDINT',
    'int16_t'  : 'TYPE_CSTDINT',
    'int32_t'  : 'TYPE_CSTDINT',
    'int64_t'  : 'TYPE_CSTDINT',
    'unsigned' : 'TYPE_UNSIGNED',
    'bool'     : 'TYPE_BOOL',
    'string'   : 'TYPE_STRING'
}

t_L_BRACE              = r'{'
t_R_BRACE              = r'}'
t_L_BRACKET            = r'\['
t_R_BRACKET            = r'\]'
t_SEMICOLON            = r';'
t_INTEGER              = r'([1-9][0-9]*)'

t_ignore    = ' \t\n\r'

def t_RESERVED(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.type = reserved.get(t.value, 'VAR_NAME')
    return t

def t_error(t):
    print("Unknown character", t.value[0])
    t.lexer.skip(1)

lexer = lex.lex(debug=0)

if __name__ == '__main__':
    import sys
    text = open(sys.argv[1]).read()
    lexer.input(text)
    while True:
        tok = lexer.token()
        if not tok:
            break
        else:
            print(tok)
