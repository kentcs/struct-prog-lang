import sys

from tokenizer import tokenize
from parser import parse
from evaluator import evaluate

if __name__ == "__main__":  
    if len(sys.argv) != 2:
        print("Usage: python runner.py <expression>")
        sys.exit(1)
    expression = sys.argv[1]
    if expression.endswith(".t"):
        with open(expression, "r") as f:
            expression = f.read().strip()
    tokens = tokenize(expression)
    ast = parse(tokens)
    result = evaluate(ast)
    print(result)