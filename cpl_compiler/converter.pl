
:- use_module(library(lists)).
:- style_check(all).
:- op( 550, yfx, :: ).

get_next_unique_id(ID) :-
	(
	    bb_get(mvs_unique_id,ID)
	->
	    true;
	    ID=1
	),
	ID2 is ID+1,
	bb_put(mvs_unique_id,ID2).

process_all_mvs(mvs(Fact),mvs(Fact2)) :-
	!,
	process_all_mvs(f(mvs(Fact)),f(mvs(Fact2))).
process_all_mvs(Fact,Fact2) :-
	Fact=..[F|Args],
	findall(A2,
	          (
		      member(A,Args),
		      (
			  A=mvs(X)
		      ->
		          (
			      check_mvs(X,X_Checked),
			      A2=mvs(X_Checked)
			  ); A2=A
		      )
		  ),Args_Cleaned),
	Fact2=..[F|Args_Cleaned].

compile_mvs(_Prob :: (_Head :- _Body)) :-
	!,
	format( user_error, ' % Not supported.',[]),
	fail.

compile_mvs(Prob :: Fact) :-
	(contains_mvs(Fact,_,_,_,_);Fact=mvs(_)),
	!,
	get_next_unique_id(ID),
	NewFact=mvs_probabilistic_fact(ID),
	format('~f::~q.~n',[Prob,NewFact]),
	compile_mvs((Fact :- NewFact)).

compile_mvs(Prob :: Fact) :-
	!,
	format('~f::~q.~n',[Prob,Fact]).

compile_mvs((Head :- Body)) :-
	(contains_mvs(Head,_,_,_,_);Head=mvs(_)),
	!,
	

	% count the mvs in the head
	(
	    Head=mvs(_)
	-> 
	    Count=1;
	    (
		findall(1,clean_mvs_but_one(Head,_),List),
		length(List,Count)
	    )
	),

	% check probability for every mvs in the InputFact
	process_all_mvs(Head,InputFact_Cleaned),


	% if there are more than 1 MVS in Fact we have to wrap it
	(
	    Count>1
	->
	    (
		InputFact_Cleaned=..[F|Args],
		Fact=..[mvs_wrapper,F|Args]
	    ) ; Fact=InputFact_Cleaned
	),

	
	get_next_unique_id(Extra_ID),

	( % go over all MVS in Fact
	    clean_mvs_but_one_and_unfold(Fact,Fact_Unfolded),
	    convert_a(Fact_Unfolded,1.0,Extra_ID),

	    fail; % go to next mvs
	    true
	),

	( % go over all MVS in Fact
	    clean_mvs_but_one_and_unfold(Fact,Fact_Unfolded),
	    convert_b(Fact_Unfolded,Body,Extra_ID),
	    fail; % go to next mvs
	    true
	),
	(
	    Count>1
	->
	    (
		mvs_make_collector(Fact,Head2,Body2),
		Head2=..[mvs_wrapper,F2|HeadArgs],
		NewHead=..[F2|HeadArgs],
		format('~q :- ~q.~n',[NewHead,Body2])
	    ); true
	).
compile_mvs((Head :- Body)) :-
	!,
	format('~q :- ~q.~n',[Head,Body]).
compile_mvs(Atom) :-
	(contains_mvs(Atom,_,_,_,_); Atom=mvs(_)),
	!,
	compile_mvs( (Atom :- true) ).
compile_mvs(Atom) :-
	format('~q.~n',[Atom]).

%========================================================================
%= 
%= 
%=
%========================================================================



mvs_make_collector(Fact,FactHead,Body) :-
	findall( (Fact3,X),
	  (
	      clean_mvs_but_one(Fact,Fact2),
	      contains_mvs(Fact2,F,P0,_,P1),
	      append(P0,[X|P1],TmpArg),
	      Fact3 =..[F|TmpArg])
	  ,SubParts),

	  Fact =.. [F|Arguments],
	  mvs_make_collector(Arguments,SubParts,NewArguments,Body),

	  FactHead =.. [F|NewArguments].

mvs_make_collector([],[],[],true).
mvs_make_collector([mvs(_)|T],[ (Fact,Variable) | T2], [Variable|T3],(Fact,T4)) :-
	!,
	mvs_make_collector(T,T2,T3,T4).
mvs_make_collector([X|T],List, [X|T3],List2) :-
	mvs_make_collector(T,List,T3,List2).
	



%========================================================================
%= 
%= 
%=
%========================================================================


check_mvs(MVS,MVS2) :-
	just_list(MVS),
	!,
	length(MVS,L),
	L>0,
	P is 1/L,
	findall( (P-X), member(X,MVS),MVS2).
check_mvs(MVS,MVS2) :-
	probability_list(MVS,0.0,MVS2).

just_list([]).
just_list([H|T]) :-
	\+ H= _-_,
	just_list(T).

probability_list([],_,[]).
probability_list([N-S|T],Sum,[N2-S|T2]) :-
	(
	    T=[]
	->
	    N2 is 1-Sum;
	    (
		( number(N) -> N2=N; true),
		( N=A/B -> N2 is A/B; true),
		( var(N2) -> throw(unknown_probability_expression(N)); true),
		( N2<0 -> throw(error('Only probabilities > 0 are allowed',N)); true),
		( N2>1 -> throw(error('Only values <= 1 are allowed',N));true),
		NewSum is Sum+N2
	    )
	),
	probability_list(T,NewSum,T2).
		
%========================================================================
%= store the facts with the learned probabilities to a file
%= if F is a variable, a filename based on the current iteration is used
%=
%========================================================================
convert_a([],_,_).
convert_a([P-Atom|T],OldAcc,Extra_ID) :-
	(
	    T=[]
	->
	    true;  % no output for last list element
	    (

		Atom =.. [Functor|AllArguments],
		length(AllArguments,Arity),

		atomic_concat([mvs_fact_,Functor,'_',Arity,'_',Extra_ID],NewAtom),

		ProbFact =.. [NewAtom|AllArguments],
		( P=:=0 -> P1 is 0.0 ; P1 is  P/OldAcc),
		clean_mvs(ProbFact,ProbFactClean),
		format('~f::~q.~n',[P1,ProbFactClean]),
		Acc is OldAcc*(1-P1),
		convert_a(T,Acc,Extra_ID)
	    )
	).

convert_b([],_,_).
convert_b([_-Atom|T],Body,Extra_ID) :-
	Atom =.. [Functor|AllArguments],
	(
	    T=[]
	->
	    (
		NewBody=Body,
		NextBody=Body
	    );
	    (

		length(AllArguments,Arity),
		atomic_concat([mvs_fact_,Functor,'_',Arity,'_',Extra_ID],NewFunctor),

		ProbFact =.. [NewFunctor|AllArguments],
		tuple_append(Body,ProbFact,NewBody),
		tuple_append(Body,problog_not(ProbFact),NextBody)
	    )
	),

	(
	    Atom=null_null_null
	->
	    true;
	    format('~q :- ~q.~n',[Atom,NewBody])
	),
	convert_b(T,NextBody,Extra_ID).

tuple_append(true,X,X).
tuple_append(X,true,X) :-
	X \= true.
tuple_append((A,B),X,(A,B2)) :-
	X \= true,
	tuple_append(B,X,B2).
tuple_append(X,Y,(X,Y)) :-
	X \= true,
	Y \= true,
	X \= (_,_).



unfold_mvs(Fact,Fact_Unfolded) :-
	(
	    Fact=mvs(L)
	->
	    Fact_Unfolded=L;
	    (
		contains_mvs(Fact,F,P0,mvs(L),P1),
		
		findall(P-Fact2, (
		member(P-C,L),
		(
		    C=null_null_null
		-> Fact2=null_null_null;
		(
		append(P0,[C|P1],Args),
		Fact2 =.. [F|Args]))), Fact_Unfolded)
	    )
	).

contains_mvs(Fact,Functor,Part0,mvs(Values),Part1) :-
	Fact =.. [Functor|Tail],
	once(append(Part0,[mvs(Values)|Part1],Tail)).

clean_mvs(Fact,Fact_Without_MVS) :-
	Fact =..[F|Arguments],
	findall(A,(member(A0,Arguments), (A0=mvs(_) -> A=mvs; A=A0)),NewArguments),
	Fact_Without_MVS =..[F|NewArguments].

clean_mvs_but_one_and_unfold(mvs(List),List) :-
	!.
clean_mvs_but_one_and_unfold(Fact,List) :-
	clean_mvs_but_one(Fact,Fact_Without_Mvs),
	unfold_mvs(Fact_Without_Mvs,List).


clean_mvs_but_one(Fact,Fact_Without_MVS) :-
	Fact =..[F|Arguments],
	clean_mvs_but_one_intern1(Arguments,ArgumentsC),
	Fact_Without_MVS =.. [F|ArgumentsC].

clean_mvs_but_one_intern1([X|T],[X2|T2]) :-
	(
	    X=mvs(L)
	->
	    (
		(
		    X2=mvs(L),
		    clean_mvs_but_one_intern2(T,T2)
		); (
		    X2=mvs,
		    clean_mvs_but_one_intern1(T,T2)
		)
	    ); (
	       X2=X,
	       clean_mvs_but_one_intern1(T,T2)
	   )
	).
clean_mvs_but_one_intern2([X|T],[X2|T2]) :-
	(
	    X=mvs(_)
	-> 
	    X2=mvs;X2=X
	),
	clean_mvs_but_one_intern2(T,T2).
clean_mvs_but_one_intern2([],[]).
