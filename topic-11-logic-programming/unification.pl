% Small examples for showing unification clearly.

% same/2 is the simplest possible unification rule.
same(X, X).

% These facts are useful for showing backtracking after unification.
likes(greg, pizza).
likes(greg, coffee).
likes(susan, tea).
likes(kim, pizza).

% Small helper predicates for matching structured terms.
point_x(point(X, _), X).
point_y(point(_, Y), Y).

pair_left(pair(X, _), X).
pair_right(pair(_, Y), Y).

triple_parts(triple(A, B, C), A, B, C).

list_head([H|_], H).
list_tail([_|T], T).
