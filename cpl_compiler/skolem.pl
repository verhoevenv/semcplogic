%%% -*- Mode: Prolog; -*-

:- module(skolem,[to_sk/2, list_to_sk/2, to_var/2, variablize/2,
	          sk_vars/2, sk_terms/2, sk_ground/1, sk_mgu/3,
		  sk_unify/4,sk_subst/3]).

:- op(667,xfx, '=>').


%========================================================================
%= Skolemize list of atoms
%========================================================================	

to_sk(T1,T2):- !,
	copy_term(T1,T2),
	numbervars(T2,0,_).

%skolemize a whole list of lists....
list_to_sk([],[]).
list_to_sk([L1|Ls1],[L2|Ls2]):-
	to_sk(L1,L2),
	list_to_sk(Ls1,Ls2).


%========================================================================
%= replace '$VAR'(N) with new variable in a list of atoms
%= (Inverse Skolemize)
%========================================================================	

to_var(ST,T) :- !,
	variablize(ST,[],_,T).

variablize([],A,A,[]) :- !.
variablize([ST|STs],Subst,NewSubst,[T|Ts]):-!,
	variablize(ST,Subst,TmpSubst,T),
	variablize(STs,TmpSubst,NewSubst,Ts).
variablize('$VAR'(N),Subst,NewSubst,T) :- !,
	(
	  (memberchk('$VAR'(N)=>C,Subst))
	->
	  (T=C,NewSubst=Subst);
	  (T=_,NewSubst=['$VAR'(N)=>T|Subst])
	).
variablize(ST,Subst,NewSubst,T) :- !,
	ST=..[P|SArgs],!,
	variablize(SArgs,Subst,NewSubst,Args),
	T=..[P|Args],!.	
	
% for rules...	
variablize([],[]).
variablize([Rule|Rules],[VRule|VRules]) :-
	to_var(Rule,VRule),
	variablize(Rules,VRules).	


%========================================================================
%= gather list of 'skolem constants'
%========================================================================

sk_vars(Conj,Vars) :-
	sk_vars(Conj,[],VarsTmp),
	sort(VarsTmp,Vars).

sk_vars([],Vars,Vars) :- !.
sk_vars('$VAR'(N),OldVars,['$VAR'(N)|OldVars]) :- !.
sk_vars([T|Ts],OldVars,Vars):- 
	sk_vars(T,OldVars,TVars),
	sk_vars(Ts,TVars,Vars),!.
sk_vars(T,OldVars,Vars) :- 
	T=..[_|Args],
	sk_vars(Args,OldVars,Vars),!.


%==================================================================
%= sk_terms: compute all constants and Variables
%==================================================================

sk_terms(Cons,Terms) :-
	sk__terms(Cons,[],NewTerms),
	sort(NewTerms,Terms).

sk__terms([],Terms,Terms).
sk__terms([not(L)|Rest],OldTerms,Terms) :- !,
	sk__terms([L|Rest],OldTerms,Terms).
sk__terms([L|Rest],OldTerms,NewTerms) :-
	L=..[_|Terms],
	append(Terms,OldTerms,NewTermsA),
	sk__terms(Rest,NewTermsA,NewTerms).


%==================================================================
%= Are there any 'skolem constants'?
%==================================================================

sk_ground(Conj) :-
	sk_vars(Conj,Vars),!,
	Vars==[].


%==================================================================
%= compute mgu of (unordered) sets A and B of skolemized atoms
%==================================================================

sk_mgu(ConjA,ConjB,SimplifiedSubst) :-
	sk_mgu(ConjA,ConjB,[],Subst),
	call_chr(Subst,SimplifiedSubst).

sk_mgu([],[],Subs,Subs). 
sk_mgu([A|RestConjA],ConjB,SoFarSubs,Subs):- 
	select(B,ConjB,RestConjB),
	sk_unify([A],[B],[],NewSubs),
	sk_subst(RestConjA,NewSubs,SubsRestConjA),
	append(SoFarSubs,NewSubs,SubsTmp),
	sort(SubsTmp,SortedSubsTmp),
	sk_mgu(SubsRestConjA,RestConjB,SortedSubsTmp,Subs).


%===================================================================
%= compute mgu of ordered list of conjunctions A and B
%===================================================================

sk_unify([],[],Subst,Subst) :- !.
sk_unify(['$VAR'(N)|RestA],['$VAR'(N)|RestB],OldSubst,NewSubst) :- !,
	sk_unify(RestA,RestB,OldSubst,NewSubst).
sk_unify(['$VAR'(N)|RestA],[TermB|RestB],OldSubst,NewSubst) :-
	sk_unify(RestA,RestB,[('$VAR'(N) => TermB)|OldSubst],NewSubst).
sk_unify([TermA|RestA],['$VAR'(N)|RestB],OldSubst,NewSubst) :-
	sk_unify(RestA,RestB,[('$VAR'(N) => TermA)|OldSubst],NewSubst).
sk_unify([TermA|RestA],[TermB|RestB],OldSubst,NewSubst) :- !,
	TermA =.. [Functor|ArgsA],
	TermB =.. [Functor|ArgsB],
	sk_unify(ArgsA,ArgsB,OldSubst,Subst),
	sk_unify(RestA,RestB,Subst,NewSubst),!.


%====================================================================
%= apply substitution
%====================================================================

sk_subst([],_,[]) :- !.
sk_subst([ST|STs],Subst,[T|Ts]):-!,
	sk_subst(ST,Subst,T),!,
	sk_subst(STs,Subst,Ts),!.
sk_subst('$VAR'(N),Subst,T) :- !,
	(
	  memberchk('$VAR'(N)=>C,Subst)
	->
	  (T=C);
	  (T='$VAR'(N))
	),!.
sk_subst(ST,Subst,T) :- !,
	ST=..[P|SArgs],
	sk_subst(SArgs,Subst,Args),
	T=..[P|Args].

%====================================================================
%= To avoid the use of libraries
%====================================================================

memberchk(X,[X|_]) :-
	!.
memberchk(X,[_|T]) :-
	memberchk(X,T).

append([], L, L).
append([H|T], L, [H|R]) :-
        append(T, L, R).

%   select(?Element, ?Set, ?Residue)
%   is true when Set is a list, Element occurs in Set, and Residue is
%   everything in Set except Element (things stay in the same order).

select(Element, [Element|Rest], Rest).
select(Element, [Head|Tail], [Head|Rest]) :-
        select(Element, Tail, Rest).
