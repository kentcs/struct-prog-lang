# Topic 10: Functional Programming

`sort.t` is a good example of solving a problem by breaking it into smaller problems.

---

## What This Topic Shows

- Recursive helper functions
- Base cases
- Progress toward the base case
- Returning transformed lists
- Building results from smaller results

---

## The Recursive Pattern

A recursive solution needs three things:

1. A base case
2. A way to describe the large problem in terms of the same problem
3. A smaller subproblem that moves toward the base case

That is the whole pattern.

---

## Recursive Helpers

The file defines three filters:

```text
function upper(t,n) { ... }
function equal(t,n) { ... }
function lower(t,n) { ... }
```

Each one:

- checks for the empty-list base case
- looks at `head(t)`
- recurses on `tail(t)`

---

## Base Case

In each helper:

```text
if (t == []) { return [] }
```

This is where the recursion stops.

Without it, the recursion would never stop.

---

## Progress

Each recursive call uses `tail(t)`:

```text
return upper(tail(t),n)
return equal(tail(t),n)
return lower(tail(t),n)
```

That is the progress step:

- the input gets smaller
- the recursion gets closer to the base case

---

## Same Problem, Smaller Input

The helper logic is always the same:

```text
if (head(t) > n) {
    return [head(t)] + upper(tail(t),n)
} else {
    return upper(tail(t),n)
}
```

This is the recursive idea in one sentence:

- solve the same problem on a smaller list

---

## Building Results

`sort()` combines the recursive results:

```text
return sort(lower(s,n)) + equal(s,n) + sort(upper(s,n))
```

That shows a classic functional style:

- no in-place mutation
- return new lists
- compose smaller results into a larger one

---

## Functional Style

This example is useful because it shows:

- decomposition into helper functions
- transformation instead of mutation
- recursion over list structure
- combining returned values

It is not trying to cover all of functional programming. The point is to show the recursive mechanism clearly.
