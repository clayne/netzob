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
#|       - Frédéric Guihéry <frederic.guihery (a) amossys.fr>                |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports                                                  |
#+---------------------------------------------------------------------------+
import abc

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Endianness, Sign
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
from netzob.Model.Vocabulary.Types.Integer import Integer


class AbstractChecksum(AbstractRelationVariableLeaf, metaclass=abc.ABCMeta):
    r"""The AbstractChecksum interface specifies the methods to implement
    in order to create a new checksum relationship.

    The following methods have to be implemented:

    * :meth:`calculate`
    * :meth:`getBitSize`

    """

    ## Interface methods ##

    @abc.abstractmethod
    def calculate(self, data):
        # type: (bytes) -> bytes
        """This is a computation method that takes a :attr:`data` and returns
        its checksum value.

        :param data: The input data on which to compute the checksum relationship.
        :type data: :class:`bytes`, required
        :return: The checksum value.
        :rtype: :class:`bytes`

        """

    @abc.abstractmethod
    def getBitSize(self):
        # type: () -> int
        """This method should return the unit size in bits of the produced
        checksum (such as ``16`` bits or ``UnitSize.SIZE_16.value``).

        :return: The output unit size in bits.
        :type: :class:`int`

        """


    ## Internal methods ##

    def __init__(self, targets, dataType=None, name=None):
        if dataType is None:
            dataType = Raw(nbBytes=self.getByteSize())
            # The computed checksum is generally on 16 bits
        super(AbstractChecksum, self).__init__(self.__class__.__name__,
                                               dataType=dataType,
                                               targets=targets,
                                               name=name)

    def getByteSize(self):
        return int(self.getBitSize() / 8)

    def relationOperation(self, data):
        """The relationOperation receive a bitarray object and should return a
        bitarray object.

        """
        # Convert bitarray input into bytes
        data = data.tobytes()

        # Compute checksum
        result = self.calculate(data)

        # Convert the result in a BitArray (be carefull with the src_unitSize)
        result = TypeConverter.convert(result, Integer, BitArray,
                    src_endianness=Endianness.LITTLE,
                    dst_endianness=self.dataType.endianness,
                    src_unitSize=AbstractType.getUnitSizeEnum(self.getBitSize()),
                    dst_unitSize=self.dataType.unitSize,
                    src_sign=Sign.UNSIGNED)

        return result
