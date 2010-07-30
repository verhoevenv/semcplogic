%#!/home/jan/apps/bin/yap -L --

:- ensure_loaded('converter').
:- ensure_loaded('skolem').
:- ensure_loaded(library(lists)).

:- style_check(all).
:- yap_flag(unknown,error).
:- op( 550, yfx, :: ).

do_convert :-
	unix(argv(AllArgs)),
	write(cplogic2problog(AllArgs)), nl,
	AllArgs = [File], !,
	atom_concat([File, '.cpl'], InFile),
	atom_concat([File, '-problog-1.pl'], OutFile1),
	atom_concat([File, '-problog-2.pl'], OutFile2),
	convert_cplogic_file(InFile, OutFile1),
	mtf(OutFile1, OutFile2).

do_convert(File) :-
	atom_concat([File, '.cpl'], InFile),
	atom_concat([File, '-problog-1.pl'], OutFile1),
	atom_concat([File, '-problog-2.pl'], OutFile2),
	convert_cplogic_file(InFile, OutFile1),
	mtf(OutFile1, OutFile2).

% converts input file in cplogic syntax to problog with full negation
% a0:0.5 ; a4:0.5 :- \+ a1, \+ a2,  a3.
convert_cplogic_file(In,Out) :-
	see(In),
	tell(Out),
	format(':- use_module(\'problog_neg\').~2n',[]),
	load_info,
	seen,
	told.

% process input
load_info :-
	read(X),
	(X = end_of_file -> true;
	    process_read(X),
	    load_info).

process_read(Atom:P) :- !,
	format('~w::~q.~n',[P,Atom]).
process_read( ( Head :- Body ) ) :-
	has_choice(Head), !,
	head_to_list(Head,List),
	append(List,[0-null_null_null],List2),
	prepare_neg(Body,Body2),
	Rule = (mvs(List2) :- Body2),
	to_sk(Rule,Rule_SK),
	compile_mvs(Rule_SK).
process_read( Head ) :-
	% added case for empty body
	has_choice(Head), !,
	process_read( (Head :- true) ).
process_read( Logic ) :-
	format('~q.~n',[Logic]).

% disjunction in the head is indicated with ";" in CP-logic
head_to_list(Atom:P,[P-Atom]):-
	!.
head_to_list((Atom:P; T),[P-Atom|T2]) :-
	head_to_list(T,T2).

prepare_neg((\+ Atom),neg(Atom)).
prepare_neg(Atom,Atom) :-
	Atom \= (_,_).
prepare_neg((\+ A, B), (neg(A), C) ) :-
	!,
	prepare_neg(B,C).
prepare_neg((A,B),(A,C)) :-
	prepare_neg(B,C).

% disjunction in the head is indicated with ";" in CP-logic
has_choice((_:_)).
has_choice(((_:_);_)).


% moves the msv encoding to the front of the clause body
% input: output file of convert_cplogic_file/2
% note that this results in unexecutable code if switches get ground only in the body!
mtf(In,Out) :-
	see(In),
	tell(Out),
	process,
	seen,
	told.

process :-
	repeat,
	read(X),
	p(X),
	X==end_of_file.

p((:-use_module(X))) :-
	write(':-'), writeq(use_module(X)), write('.'), nl.
p(end_of_file).
p((P::F)) :-
	format('~w::~q.~n',[P,F]).
p((H:-Body)) :-
	move(Body,New),
	format('~q :- ~q.~n',[H,New]).

move(Old, Res) :-
	goals_to_list(Old, G1),
	collect_mvs(G1, MVS, Others),
	append(MVS, Others, New),
	list_to_goals(New, Res).

collect_mvs([], [], []).
collect_mvs([Goal|R1], L2, L3) :-
	(is_mvs(Goal) ->
		L2 = [Goal|R2],
		collect_mvs(R1, R2, L3)
	;
		L3 = [Goal|R3],
		collect_mvs(R1, L2, R3)
	).

is_mvs(neg(_)) :-
	!,
	fail.
is_mvs(problog_not(X)) :- !,
	is_mvs(X).
is_mvs(X) :-
	atom_concat('mvs_', _, X).

goals_to_list(G, L) :-
	goals_to_list(G, [], L).

goals_to_list((G1, G2), Acc, Res) :-  !,
	goals_to_list(G2, Acc, NAcc),
	goals_to_list(G1, NAcc, Res).
goals_to_list(G, Acc, [G|Acc]).

list_to_goals([], true)	:- !.
list_to_goals(L, G) :-
	list_to_goals2(L, G).

list_to_goals2([G], G) :- !.
list_to_goals2([G|GS], (G,NGS)) :-
	list_to_goals2(GS, NGS).

%:- do_convert.
