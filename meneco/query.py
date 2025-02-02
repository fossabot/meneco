# Copyright (c) 2014, Sven Thiele <sthiele78@gmail.com>
#
# This file is part of meneco.
#
# meneco is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# meneco is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with meneco.  If not, see <http://www.gnu.org/licenses/>.
# -*- coding: utf-8 -*-
import os
import clyngor
from clyngor import as_pyasp
from clyngor.as_pyasp import TermSet, Atom
from meneco import utils


root                      = __file__.rsplit('/', 1)[0]
unproducible_prg          = root + '/encodings/unproducible_targets.lp'
ireaction_prg             = root + '/encodings/ireactions.lp'
minimal_completion_prg    = root + '/encodings/card_min_completions_all_targets.lp'
heuristic_prg             = root + '/encodings/heuristic.lp'
minimal_completion_wb_prg = root + '/encodings/card_min_completions_all_targets_with_bounds.lp'
completion_prg            = root + '/encodings/completions_all_targets.lp'


# def get_mapping_ireaction(termset):
#     dict    = {}
#     revdict = {}
#     for a in termset:
#       if a.pred() == "ireaction" :
#         if not a.arg(0) in dict:
#           id             = len(dict)
#           dict[a.arg(0)] = id
#           revdict[id]    = a.arg(0)
#     return dict, revdict


# def map_reaction_ids(termset, dict):
#     mapped = TermSet()
#     for a in termset:
#       if a.pred() == "reaction" :
#         if a.arg(0) in dict:
#           mapped.add(Term('reaction', [str(dict[a.arg(0)]), a.arg(1)]))
#         else : mapped.add(a)

#       elif a.pred() == "xreaction" :
#         if a.arg(0) in dict:
#           mapped.add(Term('xreaction', [str(dict[a.arg(0)]), a.arg(1)]))
#         else : mapped.add(a)

#       elif a.pred() == "ireaction" :
#         if a.arg(0) in dict:
#           mapped.add(Term('ireaction', [str(dict[a.arg(0)]), a.arg(1)]))
#         else : print("Error: unknown ireaction, query.py line 64")

#       elif a.pred() == "value" :
#         if a.arg(0) in dict:
#           mapped.add(Term('value', [str(dict[a.arg(0)]), a.arg(1)]))
#         else : mapped.add(a)

#       elif a.pred() == "product" :
#         if a.arg(1) in dict:
#           mapped.add(Term('product', [a.arg(0), str(dict[a.arg(1)]),a.arg(2)]))
#         else : mapped.add(a)

#       elif a.pred() == "reactant" :
#         if a.arg(1) in dict:
#           mapped.add(Term('reactant', [a.arg(0), str(dict[a.arg(1)]),a.arg(2)]))
#         else : mapped.add(a)

#       elif a.pred() == "reversible" :
#         if a.arg(0) in dict:
#           mapped.add(Term('reversible', [str(dict[a.arg(0)])]))
#         else : mapped.add(a)
#       else :
#         mapped.add(a)

#     return mapped


# def unmap_reaction_ids(termset, revdict):
#     unmapped = TermSet()
#     for a in termset:
#       if a.pred() == "xreaction" :
#         unmapped.add(Term('xreaction', [str(revdict[int(a.arg(0))]), a.arg(1)]))

#     return unmapped


def get_unproducible(draft, seeds, targets):
    draft_f  = utils.to_file(draft)
    seed_f   =  utils.to_file(seeds)
    target_f = utils.to_file(targets)
    prg      = [unproducible_prg, draft_f, seed_f, target_f ]
    options = ''
    best_model = None
    models = clyngor.solve(prg, options=options)
    for model in models.discard_quotes.by_arity:
        best_model = model
    os.unlink(draft_f)
    os.unlink(seed_f)
    os.unlink(target_f)
    return best_model


def compute_ireactions(instance):
    instance_f = utils.to_file(instance)
    prg        = [ ireaction_prg, instance_f]
    best_model = None

    models = clyngor.solve(prg)
    for model in models.discard_quotes.by_arity:
        best_model = model
    os.unlink(instance_f)

    output = TermSet()
    for pred in best_model :
        if pred == 'ireaction' :
            for a in best_model[pred] : 
                output.add(Atom('ireaction(\"' + a[0] +'\",\"' + a[1] + '\")'))

    return output


def get_minimal_completion_size(draft, repairnet, seeds, targets):

    instance   = TermSet(draft.union(repairnet).union(targets).union(seeds))
    ireactions = compute_ireactions(instance)
    instance   = TermSet(instance.union(ireactions))
    instance_f = utils.to_file(instance)

    prg        = [minimal_completion_prg, instance_f]

    co         = "--configuration=jumpy --opt-strategy=usc,5"

    optimum = None
    models = clyngor.solve(prg, options=co)
    for model in models.discard_quotes.by_arity:
        optimum = model
  
    os.unlink(instance_f)
    return optimum


def get_intersection_of_optimal_completions(draft, repairnet, seeds, targets, optimum):

    instance   = TermSet(draft.union(repairnet).union(targets).union(seeds))
    ireactions = compute_ireactions(instance)
    instance   = TermSet(instance.union(ireactions))
    instance_f = utils.to_file(instance)

    prg        = [minimal_completion_prg, instance_f]

    options = '--configuration=jumpy --opt-strategy=usc,5 --enum-mode=cautious --opt-mode=optN,' + str(optimum)
    best_model = None
    models = clyngor.solve(prg, options=options)
    for model in models.discard_quotes.by_arity:
        best_model = model

    os.unlink(instance_f)
    return best_model


def get_union_of_optimal_completions(draft, repairnet, seeds, targets, optimum):

    instance   = TermSet(draft.union(repairnet).union(targets).union(seeds))
    ireactions = compute_ireactions(instance)
    instance   = TermSet(instance.union(ireactions))
    instance_f = utils.to_file(instance)
    prg        = [minimal_completion_prg, instance_f]

    options = '--configuration jumpy --opt-strategy=usc,5 --enum-mode=brave --opt-mode=optN,' + str(optimum)

    models = clyngor.solve(prg, options=options)
    for model in models.discard_quotes.by_arity:
        best_model = model

    os.unlink(instance_f)
    return best_model



def get_optimal_completions(draft, repairnet, seeds, targets, optimum, nmodels=0):

    instance   = TermSet(draft.union(repairnet).union(targets).union(seeds))
    ireactions = compute_ireactions(instance)
    instance   = TermSet(instance.union(ireactions))
    instance_f = utils.to_file(instance)

    prg        = [minimal_completion_prg, instance_f]

    options = '--configuration=handy --opt-strategy=usc,0 --opt-mode=optN,' + str(optimum)

    models = clyngor.solve(prg, options=options, nb_model=nmodels).by_arity.discard_quotes
    opt_models = clyngor.opt_models_from_clyngor_answers(models)

    return opt_models


def get_intersection_of_completions(draft, repairnet, seeds, targets):

    instance   = TermSet(draft.union(repairnet).union(targets).union(seeds))
    ireactions = compute_ireactions(instance)
    instance   = TermSet(instance.union(ireactions))
    instance_f = utils.to_file(instance)

    prg        = [completion_prg, instance_f]
    options    = '--enum-mode=cautious --opt-mode=ignore '

    
    best_model = None
    models = clyngor.solve(prg, options=options)
    for model in models.discard_quotes.by_arity:
        best_model = model

    os.unlink(instance_f)
    return best_model