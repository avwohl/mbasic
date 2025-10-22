from lexer import tokenize

tokens = tokenize("123")
for token in tokens:
    print(token)
