% inputs from the met_net
% species(Species).
% reaction(Reaction,Network).
% reactant(Species,Reaction).
% product(Species,Reaction).
% draft(Network).
% seed(Species).
% target(Species).

% find minimal set of xreactions such that xscope contains targets in pscope

% what is producible by the original network

  samenames(R,N1,N2) :- reaction(R,N1),draft(N1),N1!=N2,reaction(R,N2).
  samereactants(R) :- samenames(R,N1,N2), reactant(M2,R,N1): reactant(M2,R,N2).
  sameproducts(R) :- samenames(R,N1,N2), product(M2,R,N1): product(M2,R,N2).
  same(R):- samenames(R,N1,N2), samereactants(R), sameproducts(R), reversible(R,N1), reversible(R,N2).
  same(R):- samenames(R,N1,N2), samereactants(R), sameproducts(R), not reversible(R,N1), not reversible(R,N2).


  dscope(M) :- seed(M).

  dscope(M) :- product(M,R,N), reaction(R,N), draft(N),
               dscope(M2) : reactant(M2,R,N).

  dscope(M) :- reactant(M,R,N), reaction(R,N), draft(N), reversible(R),
               dscope(M2) : product(M2,R,N).

% what is producible with all reactions

  pscope(M) :- seed(M).

  pscope(M) :- product(M,R,N), reaction(R,N),
               pscope(M2) : reactant(M2,R,N).

  pscope(M) :- reactant(M,R,N), reaction(R,N), reversible(R),
               pscope(M2) : product(M2,R,N).

% what are the interesting reactions

  interesting(M) :- target(M), not dscope(M), pscope(M).

  interesting(M) :- reactant(M,R,N), not dscope(M), iireaction(R,N).

  interesting(M) :- product(M,R,N), not dscope(M), iireaction(R,N), reversible(R).

  iireaction(R,N) :- interesting(M), product(M,R,N), reaction(R,N).
  iireaction(R,N) :- interesting(M), reactant(M,R,N), reaction(R,N), reversible(R).


  binteresting(M) :- dscope(M).

  binteresting(M) :- product(M,R,N),  bireaction(R,N).
  binteresting(M) :- reactant(M,R,N), bireaction(R,N), reversible(R).

  bireaction(R,N) :- binteresting(M), reactant(M,R,N), product(M2,R,N), not dscope(M2), reaction(R,N).
  bireaction(R,N) :- binteresting(M), product(M,R,N), reactant(M2,R,N), not dscope(M2), reaction(R,N), reversible(R).

  % take care of reactions that produce something from nothing
  has_reactant(R) :- reactant(M,R,N).
  has_product(R)  :- product(M,R,N).
  bireaction(R,N) :- product(M,R,N), not has_reactant(R), not dscope(M), reaction(R,N).
  bireaction(R,N) :- reactant(M,R,N), not has_product(R), not dscope(M), reaction(R,N), reversible(R).


 ireaction(R,N) :- iireaction(R,N), bireaction(R,N), not same(R).
%  ireaction(R,N) :- iireaction(R,N), bireaction(R,N), not draft(N).

%  iscope(M) :- seed(M).

%  iscope(M) :- product(M,R,N), reaction(R,N), draft(N),
%               iscope(M2) : reactant(M2,R,N).

%  iscope(M) :- reactant(M,R,N), reaction(R,N), draft(N), reversible(R),
%               iscope(M2) : product(M2,R,N).

%  iscope(M) :- product(M,R,N), ireaction(R,N),
%               iscope(M2) : reactant(M2,R,N).

%  iscope(M) :- reactant(M,R,N), ireaction(R,N), reversible(R),
%               iscope(M2) : product(M2,R,N).

%:- target(X), pscope(X), not iscope(X).

#show ireaction/2.
