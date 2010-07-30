%%% -*- Mode: Prolog; -*-
:- ensure_loaded(converter).
:- ensure_loaded(skolem).
:- ensure_loaded(library(lists)).

:- style_check(all).
:- yap_flag(unknown,error).
:- op( 1199, yfx, <-- ).


convert_cplogic_file(In,Out) :-
	see(In),
	tell(Out),
	format(':- use_module(problog).~2n',[]),
	load_info,
	seen,
	told.

% process input
load_info :-
	read(X),
	(X = end_of_file -> true;
	    process_read(X),
	    load_info).


process_read( ( Head <-- Body )) :-
	!,
	head_to_list(Head,List),
	append(List,[0-null_null_null],List2),
	Rule = (mvs(List2) :- Body),
	to_sk(Rule,Rule_SK),
	compile_mvs(Rule_SK).
process_read( Atom ) :-
	write(Atom),nl.

head_to_list(P:Atom,[P-Atom]):-
	!.
head_to_list((P:Atom,T),[P-Atom|T2]) :-
	head_to_list(T,T2).


:- current_prolog_flag(argv,[From,To]),convert_cplogic_file(From,To).
