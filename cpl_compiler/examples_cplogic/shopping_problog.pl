:- use_module('../../problog/problog').

0.200000::mvs_fact_shops_1_1(john).
shops(john) :- mvs_fact_shops_1_1(john).
0.900000::mvs_fact_shops_1_2(mary).
shops(mary) :- mvs_fact_shops_1_2(mary).
0.500000::mvs_fact_spaghetti_0_3.
1.000000::mvs_fact_steak_0_3.
spaghetti :- shops(john),mvs_fact_spaghetti_0_3.
steak :- shops(john),problog_not(mvs_fact_spaghetti_0_3),mvs_fact_steak_0_3.
0.500000::mvs_fact_spaghetti_0_4.
1.000000::mvs_fact_fish_0_4.
spaghetti :- shops(mary),mvs_fact_spaghetti_0_4.
fish :- shops(mary),problog_not(mvs_fact_spaghetti_0_4),mvs_fact_fish_0_4.
