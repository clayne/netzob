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
from netzob.Fuzzing.Mutator import Mutator, MutatorMode, center
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator, MutatorInterval
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Fuzzing.Generator import Generator
from netzob.Fuzzing.Generators.GeneratorFactory import GeneratorFactory
from netzob.Fuzzing.Generators.DeterministGenerator import DeterministGenerator
from netzob.Model.Vocabulary.Types.AbstractType import Sign


@NetzobLogger
class IntegerMutator(DomainMutator):
    r"""The integer mutator, using pseudo-random or determinist generator

    The IntegerMutator constructor expects some parameters:

    :param domain: The domain of the field to mutate.
    :param interval: The scope of values to generate.
        If set to :attr:`MutatorInterval.DEFAULT_INTERVAL <netzob.Fuzzing.DomainMutator.MutatorInterval.DEFAULT_INTERVAL>`, the values will be generated
        between the min and max values of the domain.
        If set to :attr:`MutatorInterval.FULL_INTERVAL <netzob.Fuzzing.DomainMutator.MutatorInterval.FULL_INTERVAL>`, the values will be generated in
        [0, 2^N-1], where N is the bitsize (storage) of the field.
        If it is a tuple of integers (min, max), the values will be generate
        between min and max.
        Default value is :attr:`MutatorInterval.DEFAULT_INTERVAL <netzob.Fuzzing.DomainMutator.MutatorInterval.DEFAULT_INTERVAL>`.
    :param lengthBitSize: The storage size in bits of the integer.
        Default value is `None`, which indicates to use the unit size set in the field domain.
    :param mode: If set to :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`, :meth:`generate` will be
        used to produce the value.
        If set to :attr:`MutatorMode.MUTATE <netzob.Fuzzing.DomainMutator.MutatorMode.MUTATE>`, :meth:`mutate` will be used to
        produce the value (not used yet).
        Default value is :attr:`MutatorMode.GENERATE <netzob.Fuzzing.DomainMutator.MutatorMode.GENERATE>`.
    :param generator: The name of the generator to use. Set 'determinist' for the determinist generator, else among those
        available in :mod:`randomstate.prng` for a pseudo-random generator.
        Default value is :attr:`NG_mt19937`.
    :param seed: The seed used in pseudo-random Mutator.
        Default value is :attr:`SEED_DEFAULT <netzob.Fuzzing.Mutator.Mutator.SEED_DEFAULT>`.
    :type domain: :class:`AbstractVariable
        <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, required
    :type interval: :class:`int` or :class:`tuple`, optional
    :type mode: :class:`int`, optional
    :type lengthBitSize: :class:`int`, optional
    :type generator: :class:`str`, optional
    :type seed: :class:`int`, optional


    **Internal generator functions**

    The following example shows how to generate an 8 bits unsigned
    integer with a default seed and by using the default pseudo-random
    generator:

    >>> from netzob.all import *
    >>> fieldInt = Field(uint8())
    >>> mutator = IntegerMutator(fieldInt.domain)
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big') <= 255
    True

    The following example shows how to generate an 8 bits unsigned
    integer in [10, 20] interval with a default seed and by using the
    default pseudo-random generator:

    >>> from netzob.all import *
    >>> fieldInt = Field(uint8())
    >>> mutator = IntegerMutator(fieldInt.domain, interval=(10, 20))
    >>> d = mutator.generate()
    >>> 10 <= int.from_bytes(d, byteorder='big') <= 20
    True

    The following example shows how to generate an 8 bits integer in [10, 20]
    interval, with an arbitrary seed of 4321 and by using the default
    pseudo-random generator:

    >>> from netzob.all import *
    >>> fieldInt = Field(uint8())
    >>> mutator = IntegerMutator(fieldInt.domain, generator=GeneratorFactory.buildGenerator(seed=4321), interval=(10, 20))
    >>> d = mutator.generate()
    >>> 10 <= int.from_bytes(d, byteorder='big') <= 20
    True

    The following example shows how to generate an 8 bits integer in [-128, +127]
    interval, with an arbitrary seed of 52 and by using the determinist
    generator:

    >>> from netzob.all import *
    >>> fieldInt1 = Field(Integer())
    >>> mutator = IntegerMutator(fieldInt1.domain, generator=DeterministGenerator.NG_determinist, seed=52)
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    127

    The following example shows how to generate an 8 bits integer in [10, 20]
    interval, with an arbitrary seed of 1234 and by using the determinist
    generator:

    >>> from netzob.all import *
    >>> fieldInt1 = Field(uint8())
    >>> mutator = IntegerMutator(fieldInt1.domain, generator=DeterministGenerator.NG_determinist, seed=1234, interval=(10, 20))
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    255

    The following example shows how to generate an 8 bits integer in [-10, +5]
    interval, with an arbitrary seed of 1234 and by using the determinist
    generator:

    >>> from netzob.all import *
    >>> fieldInt1 = Field(Integer(interval=(-10, 5)))
    >>> mutator = IntegerMutator(fieldInt1.domain, generator=DeterministGenerator.NG_determinist, seed=1234)
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    33

    The following example shows how to generate an 16 bits integer in
    [-32768, +32767] interval, with an arbitrary seed of 1234 and by using the
    determinist generator:

    >>> from netzob.all import *
    >>> fieldInt1 = Field(Integer(unitSize=UnitSize.SIZE_16))
    >>> mutator = IntegerMutator(fieldInt1.domain, generator=DeterministGenerator.NG_determinist, seed=430)
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    32767


    **Custom generators**

    It is also possible to provide a custom :attr:`generator`.

    .. warning::
       Make sure that each value of the generator is a float between 0.0 and 1.0
       (like :func:`random.random`).

    .. note::
       The value returned by the :meth:`generate` method is *not* the float value
       extracted from the internal state, but a 8-bit binary view in :class:`bytes`.

    This example wraps the :func:`random.random` Python generator (providing
    values in the expected set) into a valid generator mechanism:

    >>> from netzob.all import *
    >>> import random
    >>> from itertools import repeat, starmap
    >>> def repeatfunc(func, times=None, *args):
    ...     if times is None:
    ...         return starmap(func, repeat(args))
    ...     return starmap(func, repeat(args, times))
    >>> random.seed(4321)
    >>> mutator = IntegerMutator(fieldInt.domain, generator=repeatfunc(random.random))
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    65

    This example uses an iterator object with a finite number of values (3),
    resulting in an error as soon as the limit is reached:

    >>> from netzob.all import *
    >>> mutator = IntegerMutator(fieldInt.domain, generator=(0., 0.5, 1.))
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    0
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    128
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    255
    >>> d = mutator.generate()
    Traceback (most recent call last):
    StopIteration

    Note that it is simple to make an infinite number generator from a finite
    number of values by using the function :func:`itertools.cycle` of Python:

    >>> from netzob.all import *
    >>> from itertools import cycle
    >>> mutator = IntegerMutator(fieldInt.domain, generator=cycle(range(2)))
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    0
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    255
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    0

    Constant definitions:
    """

    DATA_TYPE = Integer

    def __init__(self,
                 domain,
                 mode=MutatorMode.GENERATE,
                 generator=Generator.NG_mt19937,
                 seed=Mutator.SEED_DEFAULT,
                 counterMax=Mutator.COUNTER_MAX_DEFAULT,
                 interval=None,
                 lengthBitSize=None):

        # Call parent init
        super().__init__(domain,
                         mode=mode,
                         generator=generator,
                         seed=seed,
                         counterMax=counterMax,
                         lengthBitSize=lengthBitSize)

        # Handle default interval depending on type of generator
        if generator == DeterministGenerator.name or isinstance(generator, DeterministGenerator):
            if interval is None:
                interval = MutatorInterval.DEFAULT_INTERVAL
        else:
            if interval is None:
                interval = MutatorInterval.FULL_INTERVAL

        # Initialize generator
        self.initializeGenerator(interval)

    def initializeGenerator(self, interval):

        # Find min and max potential values for the datatype interval
        self._minLength = 0
        self._maxLength = 0
        if isinstance(interval, tuple) and len(interval) == 2 and all(isinstance(_, int) for _ in interval):
            # Handle desired interval according to the storage space of the domain dataType
            self._minLength = max(interval[0], self.domain.dataType.getMinStorageValue())
            self._maxLength = min(interval[1], self.domain.dataType.getMaxStorageValue())
        elif interval == MutatorInterval.DEFAULT_INTERVAL:
            self._minLength = self.domain.dataType.getMinValue()
            self._maxLength = self.domain.dataType.getMaxValue()
        elif interval == MutatorInterval.FULL_INTERVAL:
            self._minLength = self.domain.dataType.getMinStorageValue()
            self._maxLength = self.domain.dataType.getMaxStorageValue()
        else:
            raise Exception("Not enough information to generate the mutated data.")

        # Initialize either the determinist number generator
        if self.generator == DeterministGenerator.name or isinstance(self.generator, DeterministGenerator):

            # Check bitsize
            if self.lengthBitSize is not None:
                if not isinstance(self.lengthBitSize, int) or self.lengthBitSize <= 0:
                    raise ValueError("{} is not a valid bitsize value".format(self.lengthBitSize))
            if self.lengthBitSize is None:
                self.lengthBitSize = self.domain.dataType.unitSize

            # Check minValue and maxValue consistency according to the bitsize value
            if self._minLength >= 0:
                if self._maxLength > 2**self.lengthBitSize.value - 1:
                    raise ValueError("The upper bound {} is too large and cannot be encoded on {} bits".format(self._maxLength, self.lengthBitSize))
            else:
                if self._maxLength > 2**(self.lengthBitSize.value - 1) - 1:
                    raise ValueError("The upper bound {} is too large and cannot be encoded on {} bits".format(self._maxLength, self.lengthBitSize))
                if self._minLength < -2**(self.lengthBitSize.value - 1):
                    raise ValueError("The lower bound {} is too small and cannot be encoded on {} bits".format(self._minLength, self.lengthBitSize.value))

            # Build the generator
            self.generator = GeneratorFactory.buildGenerator(DeterministGenerator.NG_determinist,
                                                             seed = self.seed,
                                                             minValue = self._minLength,
                                                             maxValue = self._maxLength,
                                                             bitsize = self.lengthBitSize.value,
                                                             signed = self.domain.dataType.sign == Sign.SIGNED)

        # Else instanciate the other kind of generator
        else:
            self.generator = GeneratorFactory.buildGenerator(self.generator, seed=self.seed)
                
    def generate(self):
        """This is the mutation method of the integer type.
        It uses a PRNG to produce the value between minValue and maxValue.

        :return: the generated content represented with bytes
        :rtype: :class:`bytes`
        """
        # Call parent :meth:`generate` method
        super().generate()

        # Generate and return a random value in the interval
        dom_type = self.domain.dataType
        value = self.generateInt()

        # Handle redefined bitsize
        if self.lengthBitSize is not None:
            dst_bitsize = self.lengthBitSize
        else:
            dst_bitsize = dom_type.unitSize

        value = Integer.decode(value,
                               unitSize=dst_bitsize,
                               endianness=dom_type.endianness,
                               sign=dom_type.sign)
        return value

    def generateInt(self):
        """This is the mutation method of the integer type.
        It uses a random generator to produce the value in interval.

        :return: the generated int value
        :rtype: :class:`int`
        """
        v = next(self.generator)

        if not isinstance(self.generator, DeterministGenerator):        
            v = center(v, self._minLength, self._maxLength)

        return v


def _test_endianness():
    r"""

    # Fuzzing of integer takes into account the endianness

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator

    >>> fieldInt = Field(uint8le())
    >>> mutator = IntegerMutator(fieldInt.domain)
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='little')
    197

    >>> fieldInt = Field(uint8be())
    >>> mutator = IntegerMutator(fieldInt.domain)
    >>> d = mutator.generate()
    >>> int.from_bytes(d, byteorder='big')
    197

    """

def _test_pseudo_rand_interval():
    r"""

    # Fuzzing of integer follow the interval [0, 2^N - 1]
    # N is the number of bit of the integer

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Generator import Generator
    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator

    >>> v = int8()
    >>> f = Field(v)
    >>> mutator = IntegerMutator(f.domain, generator=Generator.NG_mt19937)
    >>> generated_values = set()
    >>> generated_values_signed = set()
    >>> for _ in range(30):
    ...     d = mutator.generate()
    ...     generated_values.add(int.from_bytes(d, byteorder='big', signed=False))

    >>> for _ in range(30):
    ...     d = mutator.generate()
    ...     generated_values_signed.add(int.from_bytes(d, byteorder='big', signed=True))

    >>> result = True
    >>> for x in generated_values:
    ...     if x < 0 or x > pow(2, v.getFixedBitSize()) - 1:
    ...         result = False

    >>> result
    True

    >>> result = True
    >>> atleast_one_neg = False
    >>> for x in generated_values_signed:
    ...     if abs(x) < 0 or abs(x) > pow(2, v.getFixedBitSize() - 1):        # for signed interval is [-128, 127] for 8 bit
    ...         result = False
    ...     if x < 0:
    ...         atleast_one_neg = True

    >>> result
    True
    >>> atleast_one_neg
    True

    """

def _test_determinist_generator_1():
    r"""

    # Fuzzing of integer with deterministic generator: ensure that the expected values are generated (P, Q, P-1, Q-1, P+1, Q+1, 0, -1, 1)
    # P is the min value and Q the max value

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Generators.DeterministGenerator import DeterministGenerator
    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator

    >>> v = int8(interval=(10, 20))
    >>> f = Field(v)
    >>> mutator = IntegerMutator(f.domain, generator=DeterministGenerator.NG_determinist)
    >>> generated_values = set()
    >>> for _ in range(30):
    ...     d = mutator.generate()
    ...     generated_values.add(int.from_bytes(d, byteorder='big', signed=True))

    >>> min_value = v.getMinValue()
    >>> max_value = v.getMaxValue()

    >>> expected_values = set()
    >>> expected_values.add(min_value)
    >>> expected_values.add(max_value)
    >>> expected_values.add(min_value - 1)
    >>> expected_values.add(max_value - 1)
    >>> expected_values.add(min_value + 1)
    >>> expected_values.add(max_value + 1)
    >>> expected_values.add(0)
    >>> expected_values.add(-1)
    >>> expected_values.add(1)
    >>> expected_values
    {0, 1, 9, 10, 11, 19, 20, 21, -1}

    >>> all(x in generated_values for x in expected_values)
    True

    """

def _test_determinist_generator_2():
    r"""

    # Fuzzing of integer with deterministic generator: ensure that the expected values are generated (-2^k, -2^k - 1, -2^k + 1, 2^k, 2^k - 1, 2^k + 1)
    # k belongs to [0, 1, ..., N-2] ; N is the number of bit of the integer

    >>> from netzob.all import *
    >>> from netzob.Fuzzing.Generators.DeterministGenerator import DeterministGenerator
    >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator

    >>> v = int8()
    >>> f = Field(v)
    >>> mutator = IntegerMutator(f.domain, generator=DeterministGenerator.NG_determinist)
    >>> generated_values = set()
    >>> for _ in range(50):
    ...     d = mutator.generate()
    ...     generated_values.add(int.from_bytes(d, byteorder='big', signed=True))

    >>> v = int8()
    >>> f = Field(v)
    >>> mutator = IntegerMutator(f.domain, generator=DeterministGenerator.NG_determinist)
    >>> generated_values = set()
    >>> for _ in range(50):
    ...     d = mutator.generate()
    ...     generated_values.add(int.from_bytes(d, byteorder='big', signed=True))

    >>> expected_values = set()
    >>> for k in range(v.getFixedBitSize() - 2):
    ...     expected_values.add(pow(-2, k))
    ...     expected_values.add(pow(-2, k) - 1)
    ...     expected_values.add(pow(-2, k) + 1)
    ...     expected_values.add(pow(2, k))
    ...     expected_values.add(pow(2, k) - 1)
    ...     expected_values.add(pow(2, k) + 1)
    
    >>> all(x in generated_values for x in expected_values)
    True

    """
