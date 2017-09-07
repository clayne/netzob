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
from netzob.Common.Utils.Decorators import typeCheck
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable


class AbstractVariableNode(AbstractVariable):
    """Represents a node in the variable definition of a field.

    A node is a variable which accepts children, such as Alternate (:class:`Alt <netzob.Model.Vocabulary.Variables.Nodes.Alt.Alt>`)
    and Aggregate (:class:`Agg <netzob.Model.Vocabulary.Variables.Nodes.Agg.Agg>`).
    Thus, both of them inherits from this class.

    """

    def __init__(self, varType, children=None, svas=None):
        # First, normalize the children
        self._children = []
        if children is not None:
            self.children = children

        # Then, call the parent init
        super(AbstractVariableNode, self).__init__(varType, svas=svas)

    def isnode(self):
        return True

    @property
    def children(self):
        """Sorted typed list of children attached to the variable node.
        .. warning:: Setting this value with a list copies its members and not the list itself.

        :type: a list of :class:`Variable <netzob.Model.Vocabulary.Variables.Variable>`

        """
        return self._children

    @children.setter
    def children(self, children):
        from netzob.Model.Vocabulary.Domain.DomainFactory import DomainFactory
        from netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg import SELF
        self._children = []
        for idx, child in enumerate(children):
            if type(child) == type and child == SELF:

                # We only support recursivity on the last element (i.e. right recursivity)
                if idx + 1 != len(children):
                    raise ValueError("SELF can only be set at the last position of an Agg")

                normalizedChild = child
            else:
                normalizedChild = DomainFactory.normalizeDomain(child)
            self._children.append(normalizedChild)

    def str_structure(self, deepness=0):
        """Returns a string which denotes the current variable definition
        using a tree display

        """

        tab = ["     " for x in range(deepness - 1)]
        tab.append("|--   ")
        tab.append("{0}".format(self))
        lines = [''.join(tab)]
        for f in self.children:
            lines.append(" " + f.str_structure(deepness + 1))
        return '\n'.join(lines)

    @property
    def field(self):
        return self.__field

    @field.setter
    def field(self, field):
        self.__field = field
        for child in self.children:
            try:
                child.field = field
            except RecursionError as e:
                pass
