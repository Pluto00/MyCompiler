import ply.lex as lex

reserved = {
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'while': 'WHILE',
    'switch': 'SWITCH',
    'case': 'CASE',
    'do': 'DO',
    'for': 'FOR',
    'goto': 'GOTO',
    'continue': 'CONTINUE',
    'break': 'BREAK',
}

# List of token names.   This is always required

numbers = [
    "INTEGER",
    "FLOAT",
    "HEX",
]

tokens = [
             'PLUS',
             'PLUS_EQUAL',
             'MINUS',
             'MINUS_EQUAL',
             'TIMES',
             'TIMES_EQUAL',
             'DIVIDE',
             'DIVIDE_EQUAL',
             'INC',
             'DEC',
             'XOR',
             'COMPARE',
             'AND',
             'OR',
             'STRING',
             'ID',
             'EQUAL',
         ] + list(reserved.values()) + numbers

# Regular expression rules for simple tokens
t_PLUS = r'\+'
t_PLUS_EQUAL = r'\+='
t_MINUS = r'-'
t_MINUS_EQUAL = r'-='
t_TIMES = r'\*'
t_TIMES_EQUAL = r'\*='
t_DIVIDE = r'/'
t_DIVIDE_EQUAL = r'/='
t_XOR = r'\^'
t_INC = r'\+\+'
t_DEC = r'--'
t_EQUAL = r'=|:='
t_STRING = r'".*"'
t_AND = r"&&"
t_OR = r"\|\|"
t_COMPARE = r"<=|>=|==|<|>|!=|<>"
literals = "+-*/;{}()[]"


# A regular expression rule with some action code


def t_FLOAT(t):
    r'\d + (\.\d+)'
    t.value = float(t.value)
    return t


def t_HEX(t):
    r'0[xX][0-9a-fA-F]+'
    t.type = "INTEGER"
    t.value = int(t.value, 16)
    return t


def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_ID(t):
    r'(?i)\b[a-z_]\w*'
    t.type = reserved.get(t.value.lower(), 'ID')
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Define a rule to handle comment
def t_COMMENT(t):
    r'\/\/.*'
    pass


# A string containing ignored characters (spaces and tabs)
t_ignore = ' \t'


# Error handling rule
def t_error(t):
    print("Line %s Error" % t.lexer.lineno, end="")
    t.lexer.next_line()


# Build the lexer
lexer = lex.lex()
