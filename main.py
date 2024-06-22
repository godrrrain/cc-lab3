from grammar_parser import tokenize, parse
modes = ["parse_expression", "parse_program"]


# code = "1 * 2 ^ 1 <= (2.5 + 1.1) / 2"

code = '''
begin
    a := 2 ^ 1 * 1 <= (2.5 + 1.1) / 2;
    b := 3 - 1 > 10 % 2;
    c := a >= b;
end
'''

if __name__ == '__main__':
    tokens = tokenize(code)
    print(tokens)
    parse(modes[1], tokens)
