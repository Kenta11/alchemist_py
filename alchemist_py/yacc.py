import ply.yacc as yacc
import sys

from alchemist.lex import tokens

def p_MESSAGE(p):
    'MESSAGE : PARAMS'
    p[0] = p[1]

def p_PARAMS(p):
    """
    PARAMS : PARAM
           | PARAMS PARAM
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_PARAM(p):
    """
    PARAM : TYPE VAR_NAME SEMICOLON
          | TYPE VAR_NAME ARRAY SEMICOLON
    """
    p[0] = { "type": p[1], "name": p[2] }
    if len(p) == 4:
        p[0]["attribute"] = "unit"
        p[0]["size"] = []
    else:
        p[0]["attribute"] = "array"
        p[0]["size"] = p[3]

def p_TYPE(p):
    """
    TYPE : TYPE_PRIMITIVE_INT
         | TYPE_PRIMITIVE_FLOAT
         | TYPE_CSTDINT
         | TYPE_BOOL
         | TYPE_STRING
         | TYPE_UNSIGNED TYPE_PRIMITIVE_INT
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[1]+' '+p[2]

def typeConversion(t:str)->str:
    typeConversionTable = {
        "int"           : "long",
        "long"          : "long long",
        "unsigned char" : "octet",
        "unsigned int"  : "unsigned long",
        "unsigned long" : "unsigned long long",
        "int8_t"        : "char",
        "int16_t"       : "short",
        "int32_t"       : "long",
        "int64_t"       : "long long",
        "uint8_t"       : "octet",
        "uint16_t"      : "unsigned short",
        "uint32_t"      : "unsigned long",
        "uint64_t"      : "unsigned long long",
        "bool"          : "boolean"
    }
    return typeConversionTable.get(t, t)

def p_ARRAY(p):
    """
    ARRAY : L_BRACKET INTEGER R_BRACKET
          | ARRAY L_BRACKET INTEGER R_BRACKET
    """
    if len(p) == 4:
        p[0] = [int(p[2])]
    else:
        p[0] = p[1] + [int(p[3])]

# syntax error
def p_error(p):
    print('Syntax error in input', p, file=sys.stderr)

parser = yacc.yacc()

# Debug
def parse(data, debug=0):
    return yacc.parse(data, debug=debug)

if __name__ == '__main__':
    text = open(sys.argv[1]).read()
    result = parser.parse(text)
    print(result)
