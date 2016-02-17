# -*- coding: utf-8 -*-
from __future__ import division

from numpy import (maximum as max_,  logical_not as not_,  absolute as abs_,  minimum as min_,  select)

from openfisca_france.model.base import *  # noqa analysis:ignore


# Paris logement familles monoparentales

class paris_logement_plfm(Variable):
    column = FloatCol
    label = u"Famille monoparentale qui est eligible à Paris logement familles monoparentales"
    entity_class = Familles

    def function(self, simulation, period):
        period = period.this_month
        last_month = period.last_month

        premier_plafond_plfm = simulation.legislation_at(period.start).paris.plfm.premier_plafond_plfm
        deuxieme_plafond_plfm = simulation.legislation_at(period.start).paris.plfm.deuxieme_plafond_plfm
        aide_1er_plafond_plfm = simulation.legislation_at(period.start).paris.plfm.aide_1er_plafond_plfm
        aide_2eme_plafond_plfm = simulation.legislation_at(period.start).paris.plfm.aide_2eme_plafond_plfm

        parent_solo = simulation.calculate('isol', period)
        nb_enfants = simulation.calculate('paris_nb_enfants', period)
        parisien = simulation.calculate('parisien', period)
        statut_occupation = simulation.calculate('statut_occupation_famille', period)
        statut_occupation_plfm = (
            (statut_occupation == 1) +
            (statut_occupation == 2) +
            (statut_occupation == 3) +
            (statut_occupation == 4) +
            (statut_occupation == 5) +
            (statut_occupation == 7))

        loyer = simulation.calculate('loyer', period)
        charges_locatives = simulation.calculate('charges_locatives', period)
        paris_base_ressources_commun = simulation.calculate('paris_base_ressources_commun', last_month)
        aide_logement = simulation.calculate('aide_logement', last_month)

        ressources_mensuelles_famille = paris_base_ressources_commun + aide_logement

        condition_plfm = select([(ressources_mensuelles_famille <= premier_plafond_plfm),
            (ressources_mensuelles_famille <= deuxieme_plafond_plfm)], [aide_1er_plafond_plfm, aide_2eme_plafond_plfm])

        result = condition_plfm * parent_solo * (nb_enfants >= 1) * parisien * statut_occupation_plfm * ((loyer > 0) + (charges_locatives > 0))

        return period, result