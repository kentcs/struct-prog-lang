function upper(t,n) {
    if (t == []) { return [] }
    if (head(t) > n) {
        return [head(t)] + upper(tail(t),n)
    } else {
        return upper(tail(t),n)
    }
}

function equal(t,n) {
    if (t == []) { return [] }
    if (head(t) == n) {
        return [head(t)] + equal(tail(t),n)
    } else {
        return equal(tail(t),n)
    }
}

function lower(t,n) {
    if (t == []) { return [] }
    if (head(t) < n) {
        return [head(t)] + lower(tail(t),n)
    } else {
        return lower(tail(t),n)
    }
}

assert upper([1,5,3,7], 4) == [5,7];
assert equal([1,5,3,7], 3) == [3];
assert lower([1,5,3,7], 4) == [1,3];

function sort(s) {
    if (s == []) {
        return s
    }
    n = head(s);
    return sort(lower(s,n)) + equal(s,n) + sort(upper(s,n))
}

unsorted = [1,5,3,7,2,0];
sorted = sort([1,5,3,7,2,0]);
print(sorted);
assert sorted == [0,1,2,3,5,7]; 
print("Done.")