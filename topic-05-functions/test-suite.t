print 3 + 4 * 5;
print (2 + 3) * 4;

x = 10;
y = 20;
print x + y;

print 3 == 3;
print 3 != 5;
print 10 < 20;
print 5 <= 5;
print 15 > 10;
print 10 >= 10;

print true;
print false;
print true and true;
print true and false;
print false or true;
print false or false;
print not true;
print not false;

x = 2;
if (x < 3) {
    print x
} else {
    print 0
};

x = 3;
while (x > 0) {
    print x;
    x = x - 1
};

f = function(x) {
    print x
};
print f(2);

function double(x) {
    print x + x
};
print double(4);
y = 3;
f = function() {
    print y
};
y = 7;
g = function() {
    y = 5;
    _ = f()
};
_ = f();
_ = g(); 
