% Simple family facts and derived relations.

person(greg).
person(susan).
person(david).
person(jack).
person(kim).
person(steph).

son(greg, david).
son(david, jack).

daughter(kim, david).
daughter(steph, david).

child(X, Y) :- son(X, Y).
child(X, Y) :- daughter(X, Y).

parent(X, Y) :- child(Y, X).

grandchild(X, Y) :- child(X, Z), child(Z, Y).
grandparent(X, Y) :- grandchild(Y, X).

male(X) :- son(X, _).
female(X) :- daughter(X, _).

grandson(X, Y) :- grandchild(X, Y), male(X).
granddaughter(X, Y) :- grandchild(X, Y), female(X).

sibling(X, Y) :- child(X, P), child(Y, P), X \= Y.
