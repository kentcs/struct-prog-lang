// Chapter 1: Numbers and Arithmetic - Test Suite

print("Chapter 1: Numbers and Arithmetic");

print "Testing basic numbers...";
x = 1;
assert x == 1;

x = -123.456;
assert x == -123.456;

print "Testing arithmetic operations...";

// addition
assert 1+2 == 3;

// subtraction  
assert 4-1 == 3;

// multiplication
assert 4 * 5 == 20;
assert 0.4 * 5 == 2.0;

// division
assert 6/2 == 3;
assert 5.5 / 0.5 == 11.0;

// operator precedence
assert 2+3*4 == 14;
assert (2+3)*4 == 20;

// negation
assert -5 == 0-5;

print "Chapter 1 tests completed.";

// Chapter 2: Variables and Assignment - Test Suite

print("Chapter 2: Variables and Assignment");

print "Testing variable assignment...";
x = 1;
assert x == 1;
assert not(x == 3);

x = -123.456;
assert x == -123.456;

// reassignment
x = 42;
assert x == 42;

// using variables in expressions
y = 5;
z = x + y;
assert z == 47;

// assignment with arithmetic
x = 10;
x = x + 5;
assert x == 15;

x = x * 2;
assert x == 30;

print "Chapter 2 tests completed.";

// ========== Chapter 3: Strings and Basic I/O ==========

print("Chapter 3: Strings and Basic I/O");

print "Testing strings...";
x = "alpha";
assert x == "alpha";
print x;

// string concatenation
assert "dog" + "cat" == "dogcat";

// string repetition
assert "dog" * 2 == "dogdog";
assert 2 * "dog" == "dogdog";

// string comparison
assert "dog" == "dog";
assert not("dog" == "cat");
assert "dog" != "cat";
assert not("dog" != "dog");

// print statements
print "Testing print statements...";
print("This is a string in parentheses");
print "This is a string without parentheses";

name = "World";
greeting = "Hello, " + name + "!";
print greeting;

print "Chapter 3 tests completed.";

// Chapter 4: Booleans and Comparisons - Test Suite

print("Chapter 4: Booleans and Comparisons");

print "Testing boolean values...";
x = true;
assert x == true;
x = false;
assert x == false;

print "Testing numeric comparisons...";
assert 1==1;
assert not(1==2);
assert 1!=2;
assert not(1!=1);

assert 1 < 2;
assert not(2 < 1);
assert 1 <= 2;
assert 2 <= 2;
assert not(2 <= 1);

assert 3 > 2;
assert not(2 > 3);
assert 3 >= 2;
assert 2 >= 2;
assert not(2 >= 3);

print "Testing string comparisons...";
assert "dog" == "dog";
assert not("dog" == "cat");
assert "dog" != "cat";
assert not("dog" != "dog");

print "Testing boolean operations...";
assert true == not(false);
assert false == not(true);

print "Chapter 4 tests completed.";

// Chapter 5: Logical Operators - Test Suite

print("Chapter 5: Logical Operators");

print "Testing logical NOT...";
assert not(false) == true;
assert not(true) == false;
assert not(1 == 2);
assert not not(1 == 1);

print "Testing logical AND...";
assert true && true;
assert not(true && false);
assert not(false && true);
assert not(false && false);

// short-circuiting
x = 1;
assert (x == 1) && (x < 2);
assert not((x == 2) && (x < 2));

print "Testing logical OR...";
assert true || true;
assert true || false;
assert false || true;
assert not(false || false);

// short-circuiting
assert (x == 1) || (x == 2);
assert not((x == 3) || (x == 4));

print "Testing combined logical expressions...";
assert (true && true) || false;
assert not((false && true) || false);
assert true || (false && true);

print "Chapter 5 tests completed.";

// Chapter 6: Conditional Statements - Test Suite

print("Chapter 6: Conditional Statements");

print "Testing basic if statements...";
x = 2;
if (x < 3) {
    x = x + 4
}
assert x == 6;

print "Testing if-else statements...";
x = 2;
if (x < 3) {
    x = x + 4
} else {
    x = x + 5
}
assert x == 6;

x = 5;
if (x < 3) {
    x = x + 4
} else {
    x = x + 5
}
assert x == 10;

print "Testing nested conditionals...";
x = 1;
y = 2;
if (x < 2) {
    if (y > 1) {
        x = x + y
    } else {
        x = x - y
    }
} else {
    x = 0
}
assert x == 3;

print "Testing block statement lists...";
if (true) {
    if (1) {x=1}
    if (1) {x=1; x=2}
    if (1) {x=1; x=2};
    if (1) {x=1;;; x=2;}
    x=4
}
assert x == 4;

print "Chapter 6 tests completed.";

// Chapter 10: Functions - Test Suite

print("Chapter 10: Functions");

print "Testing basic function definition and calling...";
function add(a, b) {
    return a + b
}
result = add(3, 5);
assert result == 8;

print "Testing function with multiple parameters...";
function multiply(x, y, z) {
    return x * y * z
}
assert multiply(2, 3, 4) == 24;

print "Testing function with no parameters...";
function get_constant() {
    return 42
}
assert get_constant() == 42;

print "Testing function with local variables...";
function calculate_square(n) {
    temp = n * n;
    return temp
}
assert calculate_square(7) == 49;

print "Testing recursive functions...";
function factorial(n) {
    if (n <= 1) {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}
assert factorial(5) == 120;

print "Testing functions with conditional logic...";
function absolute_value(x) {
    if (x < 0) {
        return -x
    } else {
        return x
    }
}
assert absolute_value(-5) == 5;
assert absolute_value(3) == 3;

print "Testing function calls within expressions...";
function double(x) {
    return x * 2
}
function triple(x) {
    return x * 3
}
assert double(5) + triple(4) == 22;  // 10 + 12

print "Testing function that returns boolean...";
function is_even(n) {
    return (n % 2) == 0
}
assert is_even(4) == true;
assert is_even(7) == false;

print "Chapter 10 tests completed.";

// Chapter 8: Loops - Test Suite

print("Chapter 8: Loops");

print "Testing basic while loops...";
x = 0; 
y = 1;
while (y < 64) {
    y = y * 2;
    x = x + 1
}
assert x == 6;
assert y == 64;

print "Testing loop with conditions...";
sum = 0;
i = 1;
while (i <= 5) {
    sum = sum + i;
    i = i + 1
}
assert sum == 15;  // 1+2+3+4+5

print "Testing nested loops...";
total = 0;
i = 1;
while (i <= 3) {
    j = 1;
    while (j <= 2) {
        total = total + (i * j);
        j = j + 1
    }
    i = i + 1
}
assert total == 18;  // (1*1+1*2) + (2*1+2*2) + (3*1+3*2) = 3+6+9

print "Testing loop with break...";
count = 0;
while (true) {
    count = count + 1;
    if (count >= 5) {
        break
    }
}
assert count == 5;

print "Testing loop with continue...";
sum = 0;
i = 0;
while (i < 10) {
    i = i + 1;
    if (i % 2 == 0) {
        continue
    }
    sum = sum + i
}
assert sum == 25;  // 1+3+5+7+9

print "Chapter 8 tests completed.";

// Chapter 7: Lists and Indexing - Test Suite

print("Chapter 7: Lists and Indexing");

print "Testing list creation...";
x = [1,2,3];
print(x);
assert x == [1,2,3];
assert not (x == [1,2,4]);

print "Testing list indexing...";
assert x[0] == 1;
assert x[1] == 2;
assert x[2] == 3;

print "Testing list assignment...";
x[1] = 27;
assert x[1] == 27;
assert x == [1,27,3];

print "Testing list concatenation...";
a = [1,2];
b = [3,4];
c = a + b;
assert c == [1,2,3,4];

print "Testing list comparison...";
assert [1,2,3] == [1,2,3];
assert not([1,2,3] == [1,2,4]);
assert [1,2,3] != [1,2,4];
assert not([1,2,3] != [1,2,3]);

print "Testing empty lists...";
empty = [];
assert empty == [];
assert not(empty == [1]);

print "Testing nested lists...";
nested = [[1,2], [3,4]];
assert nested[0] == [1,2];
assert nested[1][0] == 3;

print "Chapter 7 tests completed.";
