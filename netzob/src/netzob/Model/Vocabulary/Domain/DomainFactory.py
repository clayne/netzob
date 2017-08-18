# -*- coding: utf-8 -*-

# +---------------------------------------------------------------------------+
# |          01001110 01100101 01110100 01111010 01101111 01100010            |
# |                                                                           |
# |               Netzob : Inferring communication protocols                  |
# +---------------------------------------------------------------------------+
# | Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
# | This program is free software: you can redistribute it and/or modify      |
# | it under the terms of the GNU General Public License as published by      |
# | the Free Software Foundation, either version 3 of the License, or         |
# | (at your option) any later version.                                       |
# |                                                                           |
# | This program is distributed in the hope that it will be useful,           |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of            |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
# | GNU General Public License for more details.                              |
# |                                                                           |
# | You should have received a copy of the GNU General Public License         |
# | along with this program. If not, see <http://www.gnu.org/licenses/>.      |
# +---------------------------------------------------------------------------+
# | @url      : http://www.netzob.org                                         |
# | @contact  : contact@netzob.org                                            |
# | @sponsors : Amossys, http://www.amossys.fr                                |
# |             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt import Alt
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg import Agg
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat import Repeat
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Model.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode


class DomainFactory(object):
    """This factory enables the manipulation of a domain, as for example to normalize it.

    For instance, you can normalize domains provided by users

    >>> from netzob.all import *
    >>> domain = DomainFactory.normalizeDomain([Raw(), 10])
    >>> print(domain.varType)
    Alt
    >>> print(domain.children[0].dataType)
    Raw=None ((0, 524288))
    >>> print(domain.children[1].dataType)
    Integer=10 ((None, None))

    >>> domain = DomainFactory.normalizeDomain(Agg([Alt(["toto", 20]), String("!")]))
    >>> print(domain.varType)
    Agg
    >>> print(domain.children[0].varType)
    Alt
    >>> print(domain.children[0].children[1].dataType)
    Integer=20 ((None, None))
    >>> print(domain.children[1].dataType)
    String=! ((None, None))

    >>> f = Field(domain=Agg([String("hello"), ["john", "kurt"]]))
    >>> print(f.str_structure())
    Field
    |--   Agg
          |--   Data (String=hello ((None, None)))
          |--   Alt
               |--   Data (String=john ((None, None)))
               |--   Data (String=kurt ((None, None)))
    """

    @staticmethod
    def normalizeDomain(domain):
        # If domain starts with an Alternative (or a list)
        if isinstance(domain, (list, Alt)):
            return DomainFactory.__normalizeAlternateDomain(domain)
        # If domain starts with an Aggregate
        elif isinstance(domain, Agg):
            return DomainFactory.__normalizeAggregateDomain(domain)
        elif isinstance(domain, Repeat):
            return DomainFactory.__normalizeRepeatDomain(domain)
        else:
            return DomainFactory.__normalizeLeafDomain(domain)

    @staticmethod
    def __normalizeLeafDomain(domain):
        if isinstance(domain, (Data, AbstractRelationVariableLeaf)):
            return domain
        else:
            return AbstractType.normalize(domain).buildDataRepresentation()

    @staticmethod
    def __normalizeAlternateDomain(domain):
        if isinstance(domain, list):
            if len(domain) == 1:
                return DomainFactory.__normalizeLeafDomain(domain[0])
        if isinstance(domain, Alt):
            result = domain
        else:
            result = Alt()
        if isinstance(domain, (list, Alt)):
            # Eliminate duplicate elements
            tmpResult = []
            if isinstance(domain, list):
                for child in domain:
                    tmpResult.append(DomainFactory.normalizeDomain(child))
            else:
                for child in domain.children:
                    tmpResult.append(DomainFactory.normalizeDomain(child))
            uniqResult = []
            for elt in tmpResult:
                if isinstance(elt, AbstractVariableNode):
                    uniqResult.append(elt)
                else:
                    found = False
                    for uElt in uniqResult:
                        if uElt == elt:
                            found = True
                            break
                    if found is False:
                        uniqResult.append(elt)
            if len(uniqResult) == 1:
                return uniqResult[0]
            else:
                result.children = []
                for elt in uniqResult:
                    result.children.append(elt)
        else:
            raise TypeError(
                "Impossible to normalize the provided domain as an alternate.")
        return result

    @staticmethod
    def __normalizeAggregateDomain(domain):
        if isinstance(domain, Agg):
            normalized_children = []
            for child in domain.children:
                normalized_children.append(DomainFactory.normalizeDomain(child))
            domain.children = normalized_children
        else:
            raise TypeError(
                "Impossible to normalize the provided domain as an aggregate.")
        return domain

    @staticmethod
    def __normalizeRepeatDomain(domain):
        return domain
