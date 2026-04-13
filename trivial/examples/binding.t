x = 1;

foo = function() {
  return x;
};

bar = function() {
  x = 2;
  return foo();
};

print(bar());

function makeCounter() {
    count = 0;
    return function() {
        extern count = count + 1;
        return count;
    };
};

c1 = makeCounter();
c2 = makeCounter();

print(c1());  // 1
print(c1());  // 2
print(c2());  // 1
print(c1());  // 3