<<<<<<< HEAD
#parser.py

#EBNF

# expression = term { ("+" | "-") term }

# term = factor { ("*" | "/ ") factor}

# factor = number

def parse_factor(tokens):
    token = token.pop[0]
    if token ["tag"] == "number":
        node = {"tag":"number", "value":token["value"]}
        return node, tokens[1:]
    assert False, f"Expected number, got {token}"

    def test_parse_factor(): 
        print("test parse factor")
        tokens = tokenize("3")
        ast, tokens = parse_factor(tokens)
        assert ast == {'tag': 'number', 'value': 3}
        assert tokens == [{'tag':None, 'line':1, 'value':3}]
        tokens = tokenize("3*3")
        ast, tokens = parse_term(tokens)
        print(tokens)
        
        exit()

        def parse_term(tokens): 
            left, tokens = parse_factor(tokens)
            while tokens[0]["tag"] in ["*", "/"]:
                op = tokens[0]["tag"]
                
                right, tokens = parse_factor(tokens)
                tree = {"tag": op, "left": left, "right": right}


    if __name__ == "__main__": 
        test_parse_factor()
        print("done")
