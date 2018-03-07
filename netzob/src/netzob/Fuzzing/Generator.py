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
# |             ANSSI,   https://www.ssi.gouv.fr                              |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | File contributors :                                                       |
# |       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
# |       - Rémy Delion <remy.delion (a) amossys.fr>                          |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Standard library imports                                                  |
# +---------------------------------------------------------------------------+
import abc

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck


class Generator(object, metaclass=abc.ABCMeta):
    """Generates values. Abstract class.
    """

    # Available algorithms for number generation in RandomState module
    NG_mt19937 = 'mt19937'
    NG_mlfg_1279_861 = 'mlfg_1279_861'
    NG_mrg32k3a = 'mrg32k3a'
    NG_pcg32 = 'pcg32'
    NG_pcg64 = 'pcg64'
    NG_xorshift128 = 'xorshift128'
    NG_xoroshiro128plus = 'xoroshiro128plus'
    NG_xorshift1024 = 'xorshift1024'
    NG_dsfmt = 'dsfmt'


    def __init__(self, seed=0):
        self.seed = seed

    @abc.abstractmethod
    def __iter__(self):
        """The iterator interface."""

    @abc.abstractmethod
    def __next__(self):
        """The iterator interface."""

    @property
    def seed(self):
        """The seed used to initialize the generator.

        :type: :class:`int`
        """
        return self._seed

    @seed.setter  # type: ignore
    def seed(self, seed):
        self._seed = seed
