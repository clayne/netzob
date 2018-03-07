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
from netzob.Fuzzing.Mutator import Mutator, MutatorMode
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator
from netzob.Model.Vocabulary.Types.HexaString import HexaString
from netzob.Fuzzing.Generator import Generator
from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
from netzob.Fuzzing.Generators.DeterministGenerator import DeterministGenerator
from netzob.Model.Vocabulary.Types.AbstractType import UnitSize


class HexaStringMutator(DomainMutator):
    """The HexaString mutator, using pseudo-random generator.
    The generated sequence shall not be longer than 2^32 bits.

    The HexaStringMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param mode: If set to :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`,
        :meth:`generate` will be used to produce the value.
        If set to :attr:`MutatorMode.MUTATE <netzob.Fuzzing.DomainMutator.MutatorMode.MUTATE>`,
        :meth:`mutate` will be used to produce the value (not used yet).
        Default value is :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`.
    :param lengthBitSize: The size in bits of the memory on which the generated
        length will be encoded.
        Default value is UnitSize.SIZE_8.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type mode: :class:`int`, optional
    :type lengthBitSize: :class:`int`, optional

    The following example shows how to generate a binary sequence with a length
    in [0, 30] interval:

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.HexaStringMutator import HexaStringMutator
    >>> fieldHexa = Field(HexaString(nbBytes=2))
    >>> mutator = HexaStringMutator(fieldHexa.domain, lengthBitSize=UnitSize.SIZE_4)
    >>> mutator.generate()
    'c574054fa236bfb'

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.HexaStringMutator import HexaStringMutator
    >>> fieldHexa = Field(HexaString(nbBytes=2))
    >>> mutator = HexaStringMutator(fieldHexa.domain, seed=19, lengthBitSize=UnitSize.SIZE_4)
    >>> mutator.generate()
    '18f7c2e03f37235'

    """

    DEFAULT_MIN_LENGTH = 4
    DEFAULT_MAX_LENGTH = 80
    DATA_TYPE = HexaString

    def __init__(self,
                 domain,
                 mode=MutatorMode.GENERATE,
                 generator=Generator.NG_mt19937,
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=Mutator.COUNTER_MAX_DEFAULT,
                 lengthBitSize=UnitSize.SIZE_8):

        # Call parent init
        super().__init__(domain,
                         mode=mode,
                         generator=generator,
                         seed=seed,
                         counterMax=counterMax)

        # Initialize generator
        self.initializeGenerator(lengthBitSize)

    def initializeGenerator(self, lengthBitSize):

        minLength = None
        maxLength = None

        # Check min, max interval
        size = self.domain.dataType.size
        if (isinstance(size, tuple) and len(size) == 2 and
                all(isinstance(_, int) for _ in size)):
            # Handle desired interval according to the storage space of the
            # domain dataType
            minLength = int(self.domain.dataType.size[0] / 8)  # nb bits to nb bytes
            maxLength = int(self.domain.dataType.size[1] / 8)  # nb bits to nb bytes
        if minLength is None or maxLength is None:
            minLength = self.DEFAULT_MIN_LENGTH
            maxLength = self.DEFAULT_MAX_LENGTH

        # Check lengthBitSize
        if isinstance(lengthBitSize, UnitSize):
            lengthBitSize = lengthBitSize.value

        # Build the length generator
        self.lengthGenerator = GeneratorFactory.buildGenerator(DeterministGenerator.NG_determinist,
                                                               seed = self.seed,
                                                               minValue = minLength,
                                                               maxValue = maxLength,
                                                               bitsize = lengthBitSize,
                                                               signed = False)

        # Build the data generator
        self.generator = GeneratorFactory.buildGenerator(self.generator, seed=self.seed)

    def generate(self):
        """This is the fuzz generation method of the raw field.
        It uses lengthMutator to get a sequence length, then a PRNG to produce
        the value.

        :return: A generated content represented with bytes.
        :rtype: :class:`bytes`
        """
        # Call parent generate() method
        super().generate()

        length = next(self.lengthGenerator)

        valueBytes = bytes()
        if length == 0:
            return valueBytes.hex()
        while True:
            spanBytes = 2  # generate a 2-bytes value
            valueInt = int(next(self.generator) * (2 ** (8 * spanBytes) - 1))
            valueBytes += valueInt.to_bytes(spanBytes, byteorder='big')
            if len(valueBytes) >= length:
                break
        return valueBytes.hex()[:length]
