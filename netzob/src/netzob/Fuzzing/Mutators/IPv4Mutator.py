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

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Fuzzing.Mutators.DomainMutator import MutatorInterval
from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator
from netzob.Model.Vocabulary.Types.IPv4 import IPv4
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Types.AbstractType import Sign
from randomstate import RandomState


class IPv4Mutator(IntegerMutator):
    r"""The IPv4 mutator, using pseudo-random generator.

    The IPv4Mutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param mode: If set to :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`, :meth:`generate` will be
        used to produce the value.
        If set to :attr:`MutatorMode.MUTATE <netzob.Fuzzing.DomainMutator.MutatorMode.MUTATE>`, :meth:`mutate` will be used to
        produce the value (not used yet).
        Default value is :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`.
    :param generator: The name of the generator to use, among those
        available in :mod:`randomstate.prng`.
        Default value is :attr:`PRNG_mt19937`.
    :param seed: The seed used in pseudo-random Mutator.
        Default value is :attr:`SEED_DEFAULT <netzob.Fuzzing.Mutator.Mutator.SEED_DEFAULT>`.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type generator: :class:`str`, optional
    :type seed: :class:`int`, optional

    **Internal generator functions**

    The following example shows how to generate an IPv4 value,
    with an arbitrary seed of 4321:

    >>> from netzob.all import *
    >>> fieldIPv4 = Field(IPv4())
    >>> mutator = IPv4Mutator(fieldIPv4.domain, seed=4321)
    >>> mutator.generate()
    b'\x12 #$'
    """

    DATA_TYPE = IPv4

    def __init__(self,
                 domain,
                 generator='mt19937',
                 **kwargs):

        # Call parent init
        super().__init__(domain,
                         interval=MutatorInterval.FULL_INTERVAL,
                         **kwargs)

    def generate(self):
        """This is the mutation method of the IPv4 type.
        It uses a PRNG to produce the value corresponding to the domain.

        :return: the generated content represented with bytes
        :rtype: :class:`bytes`
        """

        if self._currentCounter >= self.getCounterMax():
            raise Exception("Max mutation counter reached")
        self._currentCounter += 1

        # Generate and return a random value in the interval
        self._currentCounter += 1
        dom_type = self.getDomain().dataType
        ipv4Value = self.generateInt()

        return Integer.decode(ipv4Value,
                              unitSize=dom_type.unitSize,
                              endianness=dom_type.endianness,
                              sign=Sign.UNSIGNED)
