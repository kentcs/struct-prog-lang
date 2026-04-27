% A few small list predicates for pattern matching and recursion.

first([H|_], H).

rest([_|T], T).

member2(X, [X|_]).
member2(X, [_|T]) :- member2(X, T).

append2([], L, L).
append2([H|T], L, [H|R]) :- append2(T, L, R).

length2([], 0).
length2([_|T], N) :-
    length2(T, M),
    N is M + 1.
