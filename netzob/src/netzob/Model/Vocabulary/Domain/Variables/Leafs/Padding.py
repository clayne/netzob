#-*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#|             ANSSI,   https://www.ssi.gouv.fr                              |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| File contributors :                                                       |
#|       - Georges Bossert <georges.bossert (a) supelec.fr>                  |
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+
from bitarray import bitarray

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Types.String import String
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Endianness, Sign, UnitSize
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath


@NetzobLogger
class Padding(AbstractRelationVariableLeaf):
    r"""The Padding class is a variable whose content permits to produce a
    padding value that can be used to align a structure to a fixed
    size.

    The Padding constructor expects some parameters:

    :param targets: The targeted fields of the relationship.
    :param data: Specify that the produced value should be represented
                 according to this data. A callback function,
                 returning the padding value, can be used here.
    :param modulo: Specify the expected modulo size. The padding value
                   will be computed so that the whole structure aligns
                   to this value. This typically corresponds to a
                   block size in cryptography.
    :param factor: Specify that the length of the targeted structure (always
                   expressed in bits) should be
                   divided by this factor. The default value is ``1.0``.
                   For example, to express a length in bytes, the factor should
                   be ``1.0/8``, whereas to express a length in bits, the
                   factor should be ``1.0``.
    :param offset: Specify a value in bits that should be added to the length
                   of the targeted structure (after applying the factor
                   parameter). The default value is 0.
    :param name: The name of the variable. If None, the name
                 will be generated.
    :type targets: a :class:`list` of :class:`Field <netzob.Model.Vocabulary.Field>`, required
    :type data: a :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>` or a :class:`callable`, required
    :type modulo: :class:`int`, required
    :type factor: :class:`float`, optional
    :type offset: :class:`int`, optional
    :type name: :class:`str`, optional


    **Callback prototype**

    The callback function that can be used in the ``data``
    parameter has the following prototype:

    ``def cbk_data(current_length, modulo)``

    Where:

    * ``current_length`` is an :class:`int` that corresponds to the
      current size in bits of the targeted structure.
    * ``modulo`` is an :class:`int` that corresponds to the expected
      modulo size in bits.

    The callback function should return a :class:`bitarray`.


    **Padding examples**

    The following code illustrates a padding with an integer
    modulo. Here, the padding data ``b'\x00'`` is repeated ``n``
    times, where ``n`` is computed by decrementing the modulo number,
    ``128``, by the current length of the targeted structure. The
    padding length is therefore equal to ``128 - (10+2)*8 = 32`` bits.

    >>> from netzob.all import *
    >>> f0 = Field(Raw(nbBytes=10))
    >>> f1 = Field(Raw(b"##"))
    >>> f2 = Field(Padding([f0, f1], data=Raw(b'\x00'), modulo=128))
    >>> f = Field([f0, f1, f2])
    >>> d = f.specialize()
    >>> d[12:]
    b'\x00\x00\x00\x00'
    >>> len(d) * 8
    128

    The following code illustrates a padding with the use of the
    ``offset`` parameter, where the targeted field sizes is decremented by
    8 when computing the padding value length.

    >>> from netzob.all import *
    >>> f0 = Field(Raw(nbBytes=10))
    >>> f1 = Field(Raw(b"##"))
    >>> f2 = Field(Padding([f0, f1], data=Raw(b'\x00'), modulo=128, offset=8))
    >>> f = Field([f0, f1, f2])
    >>> d = f.specialize()
    >>> d[12:]
    b'\x00\x00\x00'
    >>> len(d) * 8
    120

    The following code illustrates a padding with the use of the
    ``factor`` parameter, where the targeted field sizes is divided by 2
    before computing the padding value length.

    >>> from netzob.all import *
    >>> f0 = Field(Raw(nbBytes=10))
    >>> f1 = Field(Raw(b"##"))
    >>> f2 = Field(Padding([f0, f1], data=Raw(b'\x00'), modulo=128, factor=1./2))
    >>> f = Field([f0, f1, f2])
    >>> d = f.specialize()
    >>> d[12:]
    b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    >>> len(d) * 8
    176

    The following code illustrates a padding with the use of a
    callback function that helps to determine the padding value. In
    this example, the padding value is an incrementing integer.

    >>> from netzob.all import *
    >>> f0 = Field(Raw(nbBytes=10))
    >>> f1 = Field(Raw(b"##"))
    >>> def cbk_data(current_length, modulo):
    ...     length_to_pad = modulo - (current_length % modulo)  # Length in bits
    ...     length_to_pad = int(length_to_pad / 8)  # Length in bytes
    ...     res_bytes = b"".join([t.to_bytes(1, byteorder='big') for t in list(range(length_to_pad))])
    ...     res_bits = bitarray(endian='big')
    ...     res_bits.frombytes(res_bytes)
    ...     return res_bits
    >>> f2 = Field(Padding([f0, f1], data=cbk_data, modulo=128))
    >>> f = Field([f0, f1, f2])
    >>> d = f.specialize()
    >>> d[12:]
    b'\x00\x01\x02\x03'
    >>> len(d) * 8
    128

    The following code illustrates a padding with the use of a
    callback function that helps to determine the padding value. In
    this example, the padding value is a repetition of an incrementing
    integer, thus implementing the PKCS #7 padding.

    >>> from netzob.all import *
    >>> f0 = Field(Raw(nbBytes=10))
    >>> f1 = Field(Raw(b"##"))
    >>> def cbk_data(current_length, modulo):
    ...     length_to_pad = modulo - (current_length % modulo)  # Length in bits
    ...     length_to_pad = int(length_to_pad / 8)  # Length in bytes
    ...     res_bytes = b"".join([int(length_to_pad).to_bytes(1, byteorder='big') * length_to_pad])
    ...     res_bits = bitarray(endian='big')
    ...     res_bits.frombytes(res_bytes)
    ...     return res_bits
    >>> f2 = Field(Padding([f0, f1], data=cbk_data, modulo=128))
    >>> f = Field([f0, f1, f2])
    >>> d = f.specialize()
    >>> d[12:]
    b'\x04\x04\x04\x04'
    >>> len(d) * 8
    128


    """

    def __init__(self,
                 targets,
                 data,
                 modulo,
                 factor=1.,
                 offset=0,
                 name=None):
        super(Padding, self).__init__(self.__class__.__name__, targets=targets, name=name)
        self.modulo = modulo
        self.factor = factor
        self.offset = offset

        # Handle the data parameter which can be a dataType or a method that return the padding data
        if callable(data):
            self.data_callback = data
        else:
            self.dataType = data
            self.data_callback = None

    def __key(self):
        return (self.dataType, self.factor, self.offset)

    def __eq__(x, y):
        try:
            return x.__key() == y.__key()
        except:
            return False

    def __hash__(self):
        return hash(self.__key())

    def compareValues(self, content, expectedSize, computedValue):
        return len(content) >= len(computedValue)

    @typeCheck(GenericPath)
    def computeExpectedValue(self, parsingPath):
        self._logger.debug("Compute expected value for Padding variable")

        # first checks the pointed fields all have a value
        hasNeededData = True
        size = 0
        remainingVariables = []

        for variable in self.targets:

            if variable == self:
                pass
            else:

                # Retrieve the size of the targeted variable, if it is not a Data and has a fixed size
                if not isinstance(variable, Data):
                    if hasattr(variable, "dataType"):
                        minSize, maxSize = variable.dataType.size
                        if maxSize is not None and minSize == maxSize:
                            size += minSize
                            continue
                        elif isinstance(variable.dataType, Integer):
                            size += variable.dataType.unitSize.value
                            continue
                        else:
                            raise Exception("The following targeted variable must have a fixed size: {0}".format(variable.name))

                # Else, retrieve its value if it exists
                if parsingPath.hasData(variable):
                    remainingVariables.append(variable)
                else:
                    self._logger.debug("Cannot compute the relation, because the following target variable has no value: '{0}'".format(variable))
                    hasNeededData = False
                    break

        if not hasNeededData:
            raise Exception("Expected value cannot be computed, some dependencies are missing for domain {0}".format(self))

        for variable in remainingVariables:

            # Retrieve variable value
            if variable is self:
                pass
            else:
                value = parsingPath.getData(variable)

            if value is None:
                break

            # Retrieve length of variable value
            size += len(value)

        # Compute current size of the structure targeted by the Padding
        size = int(size * self.factor + self.offset)

        # Compute the padding value according to the current size
        padding_value = bitarray(endian='big')

        if self.data_callback is not None:
            if callable(self.data_callback):
                padding_value.extend(self.data_callback(size, self.modulo))
            else:
                raise TypeError("Callback parameter is not callable.")
        else:
            mod = size % self.modulo
            length_to_pad = self.modulo - mod if mod > 0 else 0
            while len(padding_value) < length_to_pad:
                padding_value.extend(self.dataType.generate())

        self._logger.debug("Computed padding for {}: '{}'".format(self, padding_value.tobytes()))
        return padding_value

    def __str__(self):
        """The str method."""
        return "Padding({0}) - Type:{1}".format(
            str([v.name for v in self.targets]), self.dataType)

    @property
    def dataType(self):
        """The datatype used to encode the result of the computed size.

        :type: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`
        """

        return self.__dataType

    @dataType.setter
    @typeCheck(AbstractType)
    def dataType(self, dataType):
        if dataType is None:
            raise TypeError("Datatype cannot be None")
        size = dataType.unitSize
        if size is None:
            raise ValueError(
                "The datatype of a Size field must declare its unitSize")
        self.__dataType = dataType

    @property
    def factor(self):
        """Defines the multiplication factor to apply on the targeted length (in bits)"""
        return self.__factor

    @factor.setter
    @typeCheck(float)
    def factor(self, factor):
        if factor is None:
            raise TypeError("Factor cannot be None, use 1.0 for the identity.")
        self.__factor = factor

    @property
    def offset(self):
        """Defines the offset to apply on the computed length
        computed size = (factor*size(targetField)+offset)"""
        return self.__offset

    @offset.setter
    @typeCheck(int)
    def offset(self, offset):
        if offset is None:
            raise TypeError(
                "Offset cannot be None, use 0 if no offset should be applied.")
        self.__offset = offset


def _test():
    r"""
    >>> from netzob.all import *

    >>> f_data = Field(Raw(nbBytes=(0, 8)), "payload")
    >>> f_size = Field(Size([f_data], dataType=uint8(), factor=1/8), "size")
    >>> f_pad = Field(Padding([f_size, f_data], data=Raw(b"\x00"), modulo=8*16), "padding")
    >>>
    >>> s = Symbol([f_size, f_data, f_pad])
    >>> data = s.specialize()
    >>>
    >>> (abstractedSymbol, structured_data) = Symbol.abstract(data, [s])
    >>> ord(structured_data['size']) == len(structured_data['payload'])
    True
    """
