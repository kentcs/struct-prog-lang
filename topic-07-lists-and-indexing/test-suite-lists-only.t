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
