% Quicksort written in a relational style.

lower([], _, []).
lower([H|T], V, [H|Rest]) :-
    H < V,
    lower(T, V, Rest).
lower([H|T], V, Rest) :-
    H >= V,
    lower(T, V, Rest).

upper([], _, []).
upper([H|T], V, [H|Rest]) :-
    H > V,
    upper(T, V, Rest).
upper([H|T], V, Rest) :-
    H =< V,
    upper(T, V, Rest).

equal([], _, []).
equal([H|T], V, [H|Rest]) :-
    H =:= V,
    equal(T, V, Rest).
equal([H|T], V, Rest) :-
    H =\= V,
    equal(T, V, Rest).

qsort([], []).
qsort([V|Rest], Sorted) :-
    lower(Rest, V, Lower),
    equal([V|Rest], V, Equal),
    upper(Rest, V, Upper),
    qsort(Lower, SortedLower),
    qsort(Upper, SortedUpper),
    append(SortedLower, Equal, Temp),
    append(Temp, SortedUpper, Sorted).
