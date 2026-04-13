import re

patterns = [
    [r"//[^\n]*", "comment"],  # Comment
    [r"\s+", "whitespace"],  # Whitespace
    [r"\d*\.\d+|\d+\.\d*|\d+", "number"],  # numeric literals
    [r'"([^"]|"")*"', "string"],  # string literals
    [r"true|false", "boolean"],  # boolean literals
    [r"null", "null"],  # the null literal
    [r"function", "function"],  # function keyword
    [r"return", "return"],  # return keyword
    [r"extern", "extern"],  # extern keyword
    [r"if", "if"],  # if keyword
    [r"else", "else"],  # else keyword
    [r"while", "while"],  # while keyword
    [r"for", "for"],  # for keyword
    [r"break", "break"],  # break keyword
    [r"continue", "continue"],  # continue keyword
    [r"print", "print"],  # print keyword
    [r"import", "import"],  # import keyword
    [r"exit", "exit"],  # exit keyword
    [r"and", "&&"],  # alternate for &&
    [r"or", "||"],  # alternate for ||
    [r"not", "!"],  # alternate for !
    [r"assert", "assert"],
    [r"[a-zA-Z_][a-zA-Z0-9_]*", "identifier"],  # identifiers
    [r"\+", "+"],
    [r"\-", "-"],
    [r"\*", "*"],
    [r"\/", "/"],
    [r"\%", "%"],
    [r"\(", "("],
    [r"\)", ")"],
    [r"\{", "{"],
    [r"\}", "}"],
    [r"==", "=="],
    [r"!=", "!="],
    [r"<=", "<="],
    [r">=", ">="],
    [r"<", "<"],
    [r">", ">"],
    [r"\&\&", "&&"],
    [r"\|\|", "||"],
    [r"\!", "!"],
    [r"\=", "="],
    [r"\.", "."],
    [r"\[", "["],
    [r"\]", "]"],
    [r"\,", ","],
    [r"\:", ":"],
    [r"\;", ";"],
    [r".", "error"],  # unexpected content
]

for pattern in patterns:
    pattern[0] = re.compile(pattern[0])

test_generated_tags = set()


# The lex/tokenize function
def tokenize(characters, generated_tags=test_generated_tags):
    current_line = 1
    current_column = 1
    tokens = []
    position = 0
    while position < len(characters):
        # find the first token pattern that matches
        for pattern, tag in patterns:
            match = pattern.match(characters, position)
            if match:
                break

        # this should never fail, since the last pattern matches everything.
        assert match

        # note that the tag was generated
        generated_tags.add(tag)

        # complain about errors and throw exception
        if tag == "error":
            raise Exception(f"Syntax error: illegal character : {[match.group(0)]}")

        # package the token
        token = {"tag": tag}
        value = match.group(0)
        if token["tag"] == "identifier":
            token["value"] = value
        if token["tag"] == "string":
            token["value"] = value[1:-1].replace('""', '"')
        if token["tag"] == "number":
            if "." in value:
                token["value"] = float(value)
            else:
                token["value"] = int(value)
        if token["tag"] == "boolean":
            token["value"] = True if value == "true" else False

        # save the current column and line
        token["column"] = current_column
        token["line"] = current_line

        # process line and column advancement
        if tag == "whitespace":
            for c in value:
                assert c in " \t\n"
                if c == "\n":
                    current_line += 1
                    current_column = 1
                if c == "\t":
                    while current_column % 4 != 1:
                        current_column += 1
                if c == " ":
                    current_column += 1
        else:
            current_column += len(value)

        # append token to stream, skipping whitespace and comments
        if tag not in ["comment", "whitespace"]:
            tokens.append(token)

        # update position for next match
        position = match.end()

    tokens.append(
        {
            "tag": None,
            "line": current_line,
            "column": current_column,
        }
    )
    return tokens


def test_simple_tokens():
    print("testing simple tokens...")
    examples = ".,[,],+,-,*,/,(,),{,},;,:,!,&&,||,<,>,<=,>=,==,!=,=,%".split(",")
    examples.append(",")
    for example in examples:
        t = tokenize(example)[0]
        print(t)
        assert t["tag"] == example
        assert t["line"] == 1
        assert t["column"] == 1
        assert "value" not in t
    example = "(*/ +-[]{})  //comment"
    t = tokenize(example)
    example = example.replace(" ", "").replace("//comment", "")
    n = len(example)
    assert len(t) == n + 1
    for i in range(0, n):
        assert t[i]["tag"] == example[i]
    t1 = tokenize("and or not")
    t2 = tokenize("&& || !")
    assert [t["tag"] for t in t1] == [t["tag"] for t in t2]


def test_number_tokens():
    print("testing number tokens...")
    for s in ["1", "22", "12.1", "0", "12.", "123145", ".1234"]:
        t = tokenize(s)
        assert len(t) == 2, f"got tokens = {t}"
        assert t[0]["tag"] == "number"
        assert t[0]["value"] == float(s)


def clean(tokens):
    for token in tokens.copy():
        for key in ["line", "column"]:
            if key in token:
                del token[key]
    return tokens


def test_string_tokens():
    print("testing string tokens...")
    for s in ['"example"', '"this is a longer example"', '"an embedded "" quote"']:
        t = tokenize(s)
        t = clean(t)
        assert len(t) == 2
        assert t[0]["tag"] == "string"
        # adjust for the embedded quote behaviour
        assert t[0]["value"] == s[1:-1].replace('""', '"')


def test_boolean_tokens():
    print("testing boolean tokens...")
    for s in ["true", "false"]:
        t = tokenize(s)
        t = clean(t)
        assert len(t) == 2
        assert t[0]["tag"] == "boolean"
        assert t[0]["value"] == (
            s == "true"
        ), f"got {[t[0]['value']]} expected {[(s == 'true')]}"
    t = tokenize("null")
    assert len(t) == 2
    assert t[0]["tag"] == "null"


def test_identifier_tokens():
    print("testing identifier tokens...")
    for s in ["x", "y", "z", "alpha", "beta", "gamma", "input"]:
        t = tokenize(s)
        t = clean(t)
        assert len(t) == 2
        assert t[0]["tag"] == "identifier"
        assert "value" in t[0], f"Token for '{s}' should have a 'value' field."
        assert t[0]["value"] == s


def test_whitespace():
    print("testing whitespace...")
    for s in ["1", "1  ", "  1", "  1  "]:
        t = tokenize(s)
        t = clean(t)
        assert len(t) == 2
        assert t[0]["tag"] == "number"
        assert t[0]["value"] == 1


def verify_same_tokens(a, b):
    return clean(tokenize(a)) == clean(tokenize(b))


def test_multiple_tokens():
    print("testing multiple tokens...")
    assert clean(tokenize("1+2")) == [
        {"tag": "number", "value": 1},
        {"tag": "+"},
        {"tag": "number", "value": 2},
        {"tag": None},
    ]
    assert clean(tokenize("1+2-3")) == [
        {"tag": "number", "value": 1},
        {"tag": "+"},
        {"tag": "number", "value": 2},
        {"tag": "-"},
        {"tag": "number", "value": 3},
        {"tag": None},
    ]

    assert clean(tokenize("3+4*(5-2)")) == [
        {"tag": "number", "value": 3},
        {"tag": "+"},
        {"tag": "number", "value": 4},
        {"tag": "*"},
        {"tag": "("},
        {"tag": "number", "value": 5},
        {"tag": "-"},
        {"tag": "number", "value": 2},
        {"tag": ")"},
        {"tag": None},
    ]

    assert verify_same_tokens("3+4*(5-2)", "3 + 4 * (5 - 2)")
    assert verify_same_tokens("3+4*(5-2)", " 3 + 4 * (5 - 2) ")
    assert verify_same_tokens("3+4*(5-2)", "  3  +  4 * (5 - 2)  ")


def test_keywords():
    print("testing keywords...")
    for keyword in [
        "function",
        "return",
        "if",
        "else",
        "while",
        "for",
        "break",
        "continue",
        "assert",
        "extern",  # (reserved for future use)
        "import",  # (reserved for future use)
        "print",
        "exit",
    ]:
        t = clean(tokenize(keyword))
        assert len(t) == 2
        assert t[0]["tag"] == keyword, f"expected {keyword}, got {t[0]}"
        assert "value" not in t


def test_comments():
    print("testing comments...")
    assert verify_same_tokens("//comment", "\n")
    assert verify_same_tokens("//comment\n", "\n")
    assert verify_same_tokens("//alpha//comment\n", "//alpha\n")
    assert verify_same_tokens("1+5  //comment\n", "1+5  \n")
    assert verify_same_tokens('"beta"//comment\n', '"beta"\n')


def test_error():
    print("testing token errors...")
    try:
        t = clean(tokenize("$banana"))
        assert False, "Should have a token exception for '$$'."
    except Exception as e:
        error_string = str(e)
        assert "Syntax error" in error_string
        assert "illegal character" in error_string


def test_tag_coverage():
    print("testing tag coverage...")
    for pattern, tag in patterns:
        assert tag in test_generated_tags, f"Tag [ {tag} ] was not tested."


# Test for keyword followed by identifiers
def test_if_identifier_sequence():
    print("testing keyword followed by identifiers...")
    t = clean(tokenize("if alpha beta"))
    tags = [tok["tag"] for tok in t[:-1]]
    assert tags == ["if", "identifier", "identifier"], f"got {tags}"


def test_line_and_column_tracking():
    print("testing line and column tracking...")

    # Single line, single token
    tokens = tokenize("42")
    assert tokens[0]["line"] == 1
    assert tokens[0]["column"] == 1

    # Single line, multiple tokens
    tokens = tokenize("1 + 2")
    assert tokens[0]["line"] == 1 and tokens[0]["column"] == 1  # "1"
    assert tokens[1]["line"] == 1 and tokens[1]["column"] == 3  # "+"
    assert tokens[2]["line"] == 1 and tokens[2]["column"] == 5  # "2"

    # Multiple lines
    tokens = tokenize("x\ny")
    assert tokens[0]["line"] == 1 and tokens[0]["column"] == 1  # "x"
    assert tokens[1]["line"] == 2 and tokens[1]["column"] == 1  # "y"

    # Multiple lines with operators
    tokens = tokenize("1 +\n2")
    assert tokens[0]["line"] == 1 and tokens[0]["column"] == 1  # "1"
    assert tokens[1]["line"] == 1 and tokens[1]["column"] == 3  # "+"
    assert tokens[2]["line"] == 2 and tokens[2]["column"] == 1  # "2"

    # Multiple newlines
    tokens = tokenize("a\n\nb")
    assert tokens[0]["line"] == 1 and tokens[0]["column"] == 1  # "a"
    assert tokens[1]["line"] == 3 and tokens[1]["column"] == 1  # "b"

    # Tab characters (tabs align to multiples of 4)
    tokens = tokenize("x\ty")
    assert tokens[0]["line"] == 1 and tokens[0]["column"] == 1  # "x"
    assert tokens[1]["line"] == 1 and tokens[1]["column"] == 5  # "y"


def test_multiline_code():
    print("testing multiline code...")

    code = """x = 1
y = 2
z = 3"""
    tokens = tokenize(code)

    assert tokens[0]["tag"] == "identifier" and tokens[0]["value"] == "x"
    assert tokens[0]["line"] == 1 and tokens[0]["column"] == 1

    assert tokens[1]["tag"] == "="
    assert tokens[1]["line"] == 1 and tokens[1]["column"] == 3

    assert tokens[2]["tag"] == "number" and tokens[2]["value"] == 1
    assert tokens[2]["line"] == 1 and tokens[2]["column"] == 5

    assert tokens[3]["tag"] == "identifier" and tokens[3]["value"] == "y"
    assert tokens[3]["line"] == 2 and tokens[3]["column"] == 1

    assert tokens[4]["tag"] == "="
    assert tokens[4]["line"] == 2 and tokens[4]["column"] == 3

    assert tokens[5]["tag"] == "number" and tokens[5]["value"] == 2
    assert tokens[5]["line"] == 2 and tokens[5]["column"] == 5

    assert tokens[6]["tag"] == "identifier" and tokens[6]["value"] == "z"
    assert tokens[6]["line"] == 3 and tokens[6]["column"] == 1


def test_column_tracking_with_multi_char_tokens():
    print("testing column tracking with multi-character tokens...")

    # Multi-character operators
    tokens = tokenize("x == y")
    assert tokens[0]["line"] == 1 and tokens[0]["column"] == 1  # "x"
    assert tokens[1]["line"] == 1 and tokens[1]["column"] == 3  # "=="
    assert tokens[2]["line"] == 1 and tokens[2]["column"] == 6  # "y"

    # Keywords
    tokens = tokenize("if true")
    assert tokens[0]["line"] == 1 and tokens[0]["column"] == 1  # "if"
    assert tokens[1]["line"] == 1 and tokens[1]["column"] == 4  # "true"

    # Long identifiers
    tokens = tokenize("variable1 + variable2")
    assert tokens[0]["line"] == 1 and tokens[0]["column"] == 1  # "variable1"
    assert tokens[1]["line"] == 1 and tokens[1]["column"] == 11  # "+"
    assert tokens[2]["line"] == 1 and tokens[2]["column"] == 13  # "variable2"


def test_strings_with_line_column():
    print("testing strings with line and column tracking...")

    # Simple string
    tokens = tokenize('"hello"')
    assert tokens[0]["line"] == 1 and tokens[0]["column"] == 1

    # String with spaces
    tokens = tokenize('x = "hello world"')
    assert tokens[0]["line"] == 1 and tokens[0]["column"] == 1  # "x"
    assert tokens[1]["line"] == 1 and tokens[1]["column"] == 3  # "="
    assert tokens[2]["line"] == 1 and tokens[2]["column"] == 5  # string starts here


def test_comments_with_line_tracking():
    print("testing comments with line tracking...")

    # Comment at end of line
    tokens = tokenize("x = 1 // comment\ny = 2")
    assert tokens[0]["line"] == 1  # "x"
    assert tokens[1]["line"] == 1  # "="
    assert tokens[2]["line"] == 1  # "1"
    assert tokens[3]["line"] == 2  # "y"
    assert tokens[4]["line"] == 2  # "="
    assert tokens[5]["line"] == 2  # "2"


def test_complex_multiline_code():
    print("testing complex multiline code...")

    code = """function add(x, y) {
    return x + y
}"""
    tokens = tokenize(code)

    # Line 1
    assert (
        tokens[0]["tag"] == "function"
        and tokens[0]["line"] == 1
        and tokens[0]["column"] == 1
    )
    assert (
        tokens[1]["tag"] == "identifier"
        and tokens[1]["value"] == "add"
        and tokens[1]["line"] == 1
    )
    assert tokens[2]["tag"] == "(" and tokens[2]["line"] == 1

    # Line 2 (indented with spaces)
    assert (
        tokens[8]["tag"] == "return"
        and tokens[8]["line"] == 2
        and tokens[8]["column"] == 5
    )
    assert tokens[9]["tag"] == "identifier" and tokens[9]["line"] == 2

    # Line 3
    assert (
        tokens[12]["tag"] == "}"
        and tokens[12]["line"] == 3
        and tokens[12]["column"] == 1
    )


if __name__ == "__main__":
    print("testing tokenizer.")
    test_simple_tokens()
    test_number_tokens()
    test_string_tokens()
    test_boolean_tokens()
    test_identifier_tokens()
    test_whitespace()
    test_multiple_tokens()
    test_keywords()
    test_comments()
    test_error()
    test_if_identifier_sequence()
    test_tag_coverage()
    test_line_and_column_tracking()
    test_multiline_code()
    test_column_tracking_with_multi_char_tokens()
    test_strings_with_line_column()
    test_comments_with_line_tracking()
    test_complex_multiline_code()
    print("done.")
