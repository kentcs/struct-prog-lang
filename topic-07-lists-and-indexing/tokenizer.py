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
    # These punctuation tokens are what make list literals and indexing work:
    #   [1,2,3]
    #   x[0]
    [r"\[", "["],
    [r"\]", "]"],
    [r"\,", ","],
    [r"\:", ":"],
    [r"\;", ";"],
    [r".", "error"],  # unexpected content
]

for pattern in patterns:
    pattern[0] = re.compile(pattern[0])


# The lex/tokenize function
def tokenize(characters):
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






def clean(tokens):
    for token in tokens.copy():
        for key in ["line", "column"]:
            if key in token:
                del token[key]
    return tokens










def verify_same_tokens(a, b):
    return clean(tokenize(a)) == clean(tokenize(b))





















