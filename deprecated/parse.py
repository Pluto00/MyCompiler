from .lexer import lexer, numbers, reserved

ids = {}
# Test it out
with open('code.mc', encoding='utf-8') as f:
    for data in f:
        # Give the lexer some input
        lexer.input(data)
        # Tokenize
        while True:
            tok = lexer.token()
            if not tok:
                break  # No more input
            if tok.type in numbers + ['ID', 'STRING', 'COMPARE']:
                print(f'<{tok.type}, {tok.value}>', end=" ")
            else:
                print(f'<{tok.type}>', end=" ")
            if tok.type == 'ID':
                ids[tok.value.lower()] = True
        print()

print("\n\n\n符号表:")
symbol_table = list(reserved.keys()) + list(ids.keys())
for i in range(len(symbol_table)):
    print(i, symbol_table[i])
