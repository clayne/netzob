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
import abc
import uuid
from bitarray import bitarray
import random
import collections
from enum import Enum

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.SVAS import SVAS


class Endianness(Enum):
    """Enum class used to specify the endianness of a type.
    """
    BIG = 'big'
    """Endianness.BIG can be used to specify the endianness of a type."""
    LITTLE = 'little'
    """Endianness.LITTLE can be used to specify the endianness of a type."""
    __repr__ = Enum.__str__


class Sign(Enum):
    """Enum class used to specify the sign of a type.
    """
    SIGNED = 'signed'
    """Sign.SIGNED can be used to specify the sign of a type."""
    UNSIGNED = 'unsigned'
    """Sign.UNISGNED can be used to specify the sign of a type."""
    __repr__ = Enum.__str__


class UnitSize(Enum):
    """Enum class used to specify the unit size of a type (i.e. the space in bits that a unitary element takes).
    """
    SIZE_1 = 1
    """UnitSize.SIZE_1 can be used to specify the unit size of a type."""
    SIZE_4 = 4
    """UnitSize.SIZE_4 can be used to specify the unit size of a type."""
    SIZE_8 = 8
    """UnitSize.SIZE_8 can be used to specify the unit size of a type."""
    SIZE_16 = 16
    """UnitSize.SIZE_16 can be used to specify the unit size of a type."""
    SIZE_24 = 24
    """UnitSize.SIZE_24 can be used to specify the unit size of a type."""
    SIZE_32 = 32
    """UnitSize.SIZE_32 can be used to specify the unit size of a type."""
    SIZE_64 = 64
    """UnitSize.SIZE_64 can be used to specify the unit size of a type."""
    __repr__ = Enum.__str__


@NetzobLogger
class AbstractType(object, metaclass=abc.ABCMeta):
    """AbstractType is the abstract class of all the classes that represents netzob types.

    A type defines a definition domain as a unique value or specified
    with specific rules.  For instance, an integer under a specific
    interval, a string with a number of chars and an IPv4 of a
    specific netmask.

    The constructor for an AbstractType expects some parameters:

    :param typeName: The name of the type (we highly recommand the use of __class__.__name__).
    :param value: The current value of the type instance.
    :param size: The size in bits that this value takes.
    :param unitSize: The unitsize of the current value. Values must be one of UnitSize.SIZE_*. If None, the value is the default one.
    :param endianness: The endianness of the current value. Values must be Endianness.BIG or Endianness.LITTLE. If None, the value is the default one.
    :param sign: The sign of the current value. Values must be Sign.SIGNED or Sign.UNSIGNED. If None, the value is the default one.
    :type typeName: :class:`str`, optional
    :type value: :class:`bitarray.bitarray`, required
    :type size: a tuple with the min and the max size specified as :class:`int`, optional
    :type unitSize: :class:`UnitSize <netzob.Model.Vocabulary.Types.AbstractType.UnitSize>`, optional
    :type endianness: :class:`Endianness <netzob.Model.Vocabulary.Types.AbstractType.Endianness>`, optional
    :type sign: :class:`Sign <netzob.Model.Vocabulary.Types.AbstractType.Sign`, optional

    The following unit sizes are available:

    * UnitSize.SIZE_1
    * UnitSize.SIZE_4
    * UnitSize.SIZE_8 (default value)
    * UnitSize.SIZE_16
    * UnitSize.SIZE_24
    * UnitSize.SIZE_32
    * UnitSize.SIZE_64

    The following endianness are available:

    * Endianness.BIG (default value)
    * Endianness.LITTLE

    The following signs are available:

    * Sign.SIGNED (default value)
    * Sign.UNSIGNED


    **Internal representation of Type objects**

    Regarding the internal representation of variables, the Python
    module :class:`bitarray.bitarray` is used, thus allowing to
    specify objects at the bit granularity. As an example, the
    following code show how to access the internal representation of
    the value of an Integer object::

    >>> from netzob.all import *
    >>> i = Integer(20)
    >>> print(i)
    Integer=20 ((None, None))
    >>> i.value
    bitarray('00010100')

    """

    # This value will be used if generate() method is called
    # without any upper size limit
    # 65535*8 bits (which equals to 2^16 * 8 bits) is a completly arbitrary value used to limit data generation
    MAXIMUM_GENERATED_DATA_SIZE = 8 * (1 << 16)

    @staticmethod
    def supportedTypes():
        """Official list of supported types"""
        from netzob.Model.Vocabulary.Types.String import String
        from netzob.Model.Vocabulary.Types.Raw import Raw
        from netzob.Model.Vocabulary.Types.BitArray import BitArray
        from netzob.Model.Vocabulary.Types.Integer import Integer
        from netzob.Model.Vocabulary.Types.HexaString import HexaString
        from netzob.Model.Vocabulary.Types.IPv4 import IPv4
        from netzob.Model.Vocabulary.Types.Timestamp import Timestamp

        return [
            # an array of bits: [1,0,0,1,1,0..]
            BitArray,
            # original python way of encoding data, raw data
            Raw,
            # string data
            String,
            # integer
            Integer,
            # hexstring
            HexaString,
            # IPv4
            IPv4,
            # Timestamp
            Timestamp
        ]

    @staticmethod
    def supportedUnitSizes():
        """Official unit sizes"""
        return [
            UnitSize.SIZE_1, UnitSize.SIZE_4,
            UnitSize.SIZE_8, UnitSize.SIZE_16,
            UnitSize.SIZE_24, UnitSize.SIZE_32,
            UnitSize.SIZE_64
        ]

    @staticmethod
    def getUnitSizeEnum(size):
        """Returns the enum value corresponding to the given size.
        If size is invalid, returns None."""
        if size == 1:
            return UnitSize.SIZE_1
        elif size == 4:
            return UnitSize.SIZE_1
        elif size == 4:
            return UnitSize.SIZE_4
        elif size == 8:
            return UnitSize.SIZE_8
        elif size == 16:
            return UnitSize.SIZE_16
        elif size == 24:
            return UnitSize.SIZE_24
        elif size == 32:
            return UnitSize.SIZE_32
        elif size == 64:
            return UnitSize.SIZE_64
        return None

    @staticmethod
    def supportedEndianness():
        """Official endianness supported"""
        return [Endianness.BIG, Endianness.LITTLE]

    @staticmethod
    def supportedSign():
        """Official sign supported"""
        return [Sign.SIGNED, Sign.UNSIGNED]

    @staticmethod
    def defaultUnitSize():
        """Return the default unit size

        :return: the default unit size
        :rtype: :class:`Enum`
        """
        return UnitSize.SIZE_8

    @staticmethod
    def defaultEndianness():
        """Return the default endianness

        :return: the default endianness
        :type endianness: :class:`Enum`
        """
        return Endianness.BIG

    @staticmethod
    def defaultSign():
        """Return the default sign

        :return: the default sign
        :type sign: :class:`Enum`
        """
        return Sign.SIGNED

    def __init__(self,
                 typeName,
                 value,
                 size=(None, None),
                 unitSize=None,
                 endianness=None,
                 sign=None):
        self.id = uuid.uuid4()
        self.typeName = typeName

        # If 'value' is defined, 'size' should not
        if value is not None:
            if not( isinstance(size, tuple) and len(size) == 2 and size[0] is None and size[1] is None ):
                raise Exception("'value' and 'size' parameter cannot be defined at the same time for a type: value={}, size={}".format(value, size))

        self.value = value
        self.size = size

        # Handle encoding attributes
        if unitSize is None:
            unitSize = AbstractType.defaultUnitSize()
        self.unitSize = unitSize
        if endianness is None:
            endianness = AbstractType.defaultEndianness()
        self.endianness = endianness
        if sign is None:
            sign = AbstractType.defaultSign()
        self.sign = sign

    def __str__(self):
        from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
        from netzob.Model.Vocabulary.Types.BitArray import BitArray
        if self.value is not None:
            return "{0}={1} ({2})".format(
                self.typeName,
                TypeConverter.convert(self.value, BitArray,
                                      self.__class__), self.size)
        else:
            return "{0}={1} ({2})".format(self.typeName, self.value, self.size)

    def __repr__(self):
        if self.value is not None:
            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray
            return str(
                TypeConverter.convert(self.value, BitArray, self.__class__,
                                      dst_unitSize=self.unitSize,
                                      dst_endianness=self.endianness,
                                      dst_sign=self.sign))
        else:
            return str(self.value)

    def __key(self):
        # Note: as bitarray objects cannot be hashed in Python3 (because bitarray objects are mutable), we cast a bitarray object in a tuple (which is immutable)
        if self.value is None:
            return (self.typeName, self.size, self.unitSize,
                    self.endianness, self.sign)
        else:
            return (self.typeName, tuple(self.value), self.size, self.unitSize,
                    self.endianness, self.sign)

    def __eq__(x, y):
        return x.__key() == y.__key()

    def __hash__(self):
        return hash(self.__key())

    @typeCheck(type)
    def convert(self,
                typeClass,
                dst_unitSize=None,
                dst_endianness=None,
                dst_sign=None):
        """Convert the current data type in a destination type specified in
        parameter.

        :param typeClass: The Netzob type class to which the current data
                          must be converted.
        :param dst_unitSize: The unitsize of the destination
                             value. Values must be one of
                             UnitSize.SIZE_*. If None, the
                             value is the default one (UnitSize.SIZE_8).
        :param dst_endianness: The endianness of the destination
                               value. Values must be
                               Endianness.BIG or
                               Endianness.LITTLE. If None,
                               the value is the default one (Endianness.BIG).
        :param dst_sign: The sign of the destination. Values must be
                         Sign.SIGNED or
                         Sign.UNSIGNED. If None, the
                         value is the default one (Sign.SIGNED).
        :type typeClass: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType`, required
        :type dst_unitSize: :class:`UnitSize <netzob.Model.Vocabulary.Types.AbstractType.UnitSize>`, optional
        :type dst_endianness: :class:`Endianness <netzob.Model.Vocabulary.Types.AbstractType.Endianness>`, optional
        :type dst_sign: :class:`Sign <netzob.Model.Vocabulary.Types.AbstractType.Sign>`, optional
        :return: The converted current value in the specified data type.
        :rtype: :class:`AbstractType <netzob.Model.AbstractType.AbstractType>`

        """
        if typeClass is None:
            raise TypeError("TypeClass cannot be None")
        if typeClass not in AbstractType.supportedTypes():
            raise TypeError("Requested typeClass ({0}) is not supported.".
                            format(typeClass))

        if dst_unitSize is None:
            dst_unitSize = AbstractType.defaultUnitSize()
        if dst_endianness is None:
            dst_endianness = AbstractType.defaultEndianness()
        if dst_sign is None:
            dst_sign = AbstractType.defaultSign()

        if dst_unitSize not in AbstractType.supportedUnitSizes():
            raise TypeError("dst_unitsize is not supported.")
        if dst_endianness not in AbstractType.supportedEndianness():
            raise TypeError("dst_endianness is not supported.")
        if dst_sign not in AbstractType.supportedSign():
            raise TypeError("sign is not supported.")

        from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
        from netzob.Model.Vocabulary.Types.BitArray import BitArray
        return typeClass(
            TypeConverter.convert(
                self.value,
                BitArray,
                typeClass,
                src_unitSize=self.unitSize,
                src_endianness=self.endianness,
                src_sign=self.sign,
                dst_unitSize=dst_unitSize,
                dst_endianness=dst_endianness,
                dst_sign=dst_sign),
            unitSize=dst_unitSize,
            endianness=dst_endianness,
            sign=dst_sign)

    def generate(self, generationStrategy=None):
        """Generates a random data that respects the current data type.
        This is the minimal generation strategy, some types extends this.

        >>> from netzob.all import *
        >>> a = String(nbChars=20)
        >>> l = a.generate()
        >>> len(l)
        160

        >>> a = HexaString(nbBytes=20)
        >>> l = a.generate()
        >>> len(l)
        160

        >>> a = HexaString(b"aabbccdd")
        >>> a.generate()
        bitarray('10101010101110111100110011011101')

        """

        # Return the self.value in priority if it is defined
        if self.value is not None:
            return self.value

        # Else, generate a data that respects the permitted min and max sizes
        minSize, maxSize = self.size
        if maxSize is None:
            maxSize = AbstractType.MAXIMUM_GENERATED_DATA_SIZE

        generatedSize = random.randint(minSize, maxSize)
        randomContent = [random.randint(0, 1) for i in range(0, generatedSize)]
        return bitarray(randomContent, endian=self.endianness.value)

    @typeCheck(str)
    def mutate(self, prefixDescription=None):
        """Generate various mutations of the current types.

        This specific method generates mutations on the bit level.
        If any type accepts bit level mutations, it should call this method. This method
        introduce the following mutations:

        * Original Version in little endian
        * Original Version in big endian
        * Inversed bytes in little endian
        * Inversed bytes in big endian

        >>> from netzob.all import *
        >>> t = String("helloworld")
        >>> print(t.mutate())
        OrderedDict([('ascii-bits(bigEndian)', bitarray('01101000011001010110110001101100011011110111011101101111011100100110110001100100')), ('ascii-bits(littleEndian)', bitarray('00010110101001100011011000110110111101101110111011110110010011100011011000100110')), ('ascii(inversed)-bits(bigEndian)', bitarray('01100100011011000111001001101111011101110110111101101100011011000110010101101000')), ('ascii(inversed)-bits(littleEndian)', bitarray('00100110001101100100111011110110111011101111011000110110001101101010011000010110')), ('ascii(upper)-bits(bigEndian)', bitarray('01001000010001010100110001001100010011110101011101001111010100100100110001000100')), ('ascii(upper)-bits(littleEndian)', bitarray('00010010101000100011001000110010111100101110101011110010010010100011001000100010')), ('ascii(inversed-upper)-bits(bigEndian)', bitarray('01000100010011000101001001001111010101110100111101001100010011000100010101001000')), ('ascii(inversed-upper)-bits(littleEndian)', bitarray('00100010001100100100101011110010111010101111001000110010001100101010001000010010'))])

        >>> t = Integer(100)
        >>> print(t.mutate())
        OrderedDict([('bits(bigEndian)', bitarray('01100100')), ('bits(littleEndian)', bitarray('00100110'))])

        >>> t = Integer()
        >>> mutations = t.mutate()
        >>> print(len(mutations['bits(littleEndian)']))
        8

        :keyword prefixDescription: prefix to attach to the description of the generated mutation.
        :type prefixDescription: :class:`str`
        :return: a dict of computed mutations having the same types than the initial one.
        :rtype: :class:`dict`<str>=:class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`
        """
        if prefixDescription is None:
            prefixDescription = ""
        else:
            prefixDescription += "-"

        mutations = collections.OrderedDict()

        # If no value is known, we generate a new one
        if self.value is None:
            val = self.generate()
        else:
            val = self.value

        if self.endianness == Endianness.LITTLE:
            mutations["{0}bits(littleEndian)".format(prefixDescription)] = val
            bigEndianValue = bitarray(val, endian=Endianness.BIG.value)
            mutations["{0}bits(bigEndian)".format(
                prefixDescription)] = bigEndianValue
        else:
            mutations["{0}bits(bigEndian)".format(prefixDescription)] = val
            littleEndianValue = bitarray(
                val, endian=Endianness.LITTLE.value)
            mutations["{0}bits(littleEndian)".format(
                prefixDescription)] = littleEndianValue

        return mutations

    @staticmethod
    @abc.abstractmethod
    def decode(data, unitSize=None, endianness=None, sign=None):
        """This method convert the specified data in python raw format.

        :param data: The data encoded in current type which will be decoded in raw.
        :param unitSize: The unit size of the specified data.
        :param endianness: The endianness of the specified data.
        :param sign: The sign of the specified data.
        :type data: the current type
        :type unitSize: :class:`int`
        :type endianness: :class:`str`
        :type sign: :class:`str`

        :return: data encoded in python raw
        :rtype: python raw
        :raise: TypeError if parameters are not valid.
        """
        raise NotImplementedError(
            "Internal Error: 'decode' method not implemented")

    @staticmethod
    @abc.abstractmethod
    def encode(data, unitSize=None, endianness=None, sign=None):
        """This method convert the python raw data to the current type.

        :param data: The data encoded in python raw which will be encoded in current type.
        :param unitSize: The unit size of the specified data.
        :param endianness: The endianness of the specified data.
        :param sign: The sign of the specified data.
        :type data: python raw
        :type unitSize: :class:`int`
        :type endianness: :class:`str`
        :type sign: :class:`str`
        :return: data encoded in python raw
        :rtype: python raw
        :raise: TypeError if parameters are not valid.
        """
        raise NotImplementedError(
            "Internal Error: 'encode' method not implemented")

    @abc.abstractmethod
    def canParse(self, data):
        """This method computes if the specified data can be parsed
        with the current type and its contraints

        :param data: the data encoded in python raw to check
        :type data: python raw
        :return: True if the data can be parsed will the curren type
        :rtype: bool
        """
        raise NotImplementedError(
            "Internal Error: 'canParse' method not implemented")

    @property
    def value(self):
        """The current value of the instance. This value is represented
        under the bitarray format.

        :type: :class:`bitarray.bitarray`
        """

        return self.__value

    @value.setter
    @typeCheck(bitarray)
    def value(self, value):
        self.__value = value

    @property
    def size(self):
        """The size of the expected Type defined
         by a tuple (min, max).
         Instead of a tuple, an int can be used to represent both min and max value.

         The value 'None' can be set for min and/or max to represent no limitations.

         For instance, to create a String field of at least 10 chars:

         >>> from netzob.all import *
         >>> f = Field(String(nbChars=(10,None)))
         >>> f.domain.dataType.size
         (80, None)

         while to create a Raw field which content has no specific limits:

         >>> from netzob.all import *
         >>> f = Field(Raw())

         :type: tuple (int, int)
         :raises: :class:`TypeError` or :class:`ValueError` if parameters are not valid.

         """
        return self.__size

    @size.setter
    def size(self, size):

        if size is None:
            size = (None, None)
        elif isinstance(size, int):
            size = (size, size)

        if isinstance(size, tuple):
            minSize, maxSize = size

            if minSize is not None and not isinstance(minSize, int):
                raise TypeError("Size must be defined with a tuple of int")

            if maxSize is not None and not isinstance(maxSize, int):
                raise TypeError("Size must be defined with a tuple of int")

            self.__size = (minSize, maxSize)
        else:
            raise TypeError(
                "Size must be defined by a tuple an int or with None")

    @staticmethod
    def normalize(data):
        """Given the specified data, this static methods normalize its representation
        using Netzob types.

        :parameter data: the data to normalize
        :type data: :class:`object`
        :return: an abstractType which value is data
        :rtype: :class:`AbstractType <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`

        >>> from netzob.all import *
        >>> normalizedData = AbstractType.normalize("john")
        >>> normalizedData.__class__
        <class 'netzob.Model.Vocabulary.Types.String.String'>
        >>> normalizedData.value
        bitarray('01101010011011110110100001101110')
        """

        if data is None:
            raise TypeError("Cannot normalize None data")

        normalizedData = None

        if isinstance(data, AbstractType):
            return data
        elif isinstance(data, int):
            from netzob.Model.Vocabulary.Types.Integer import Integer
            return Integer(value=data)
        elif isinstance(data, bytes):
            from netzob.Model.Vocabulary.Types.Raw import Raw
            normalizedData = Raw(value=data)
        elif isinstance(data, str):
            from netzob.Model.Vocabulary.Types.String import String
            normalizedData = String(value=data)
        elif isinstance(data, bitarray):
            from netzob.Model.Vocabulary.Types.BitArray import BitArray
            normalizedData = BitArray(value=data)

        if normalizedData is None:
            raise TypeError(
                "Not a valid data ({0}), impossible to normalize it.",
                type(data))

        return normalizedData

    def buildDataRepresentation(self):
        """It creates a :class:`Data <netzob.Model.Vocabulary.Domain.Variables.Leafs.Data.Data>` following the specified type.

        for instance, user can specify a domain with its type which is much more simple than creating a Data with the type

        >>> from netzob.all import *
        >>> ascii = String("hello john !")
        >>> ascii.typeName
        'String'
        >>> data = ascii.buildDataRepresentation()
        >>> data.currentValue.tobytes()
        b'hello john !'
        >>> print(data.dataType)
        String=hello john ! ((None, None))

        :return: a Data of the current type
        :rtype: :class:`Data <netzob.Model.Vocabulary.Domain.Variables.Leads.Data.Data>`

        """
        from netzob.Model.Vocabulary.Domain.Variables.Leafs.Data import Data

        svas = None

        if self.value is not None:
            svas = SVAS.CONSTANT
        else:
            svas = SVAS.EPHEMERAL

        return Data(dataType=self, originalValue=self.value, svas=svas)

    @property
    def id(self):
        """Unique identifier of the type.

        This value must be a unique UUID instance (generated with uuid.uuid4()).

        :type: :class:`uuid.UUID`
        :raises: :class:`TypeError`, :class:`ValueError`
        """

        return self.__id

    @id.setter
    @typeCheck(uuid.UUID)
    def id(self, id):
        if id is None:
            raise ValueError("id is Mandatory.")
        self.__id = id

    @property
    def typeName(self):
        """The name of the implemented type. We recommend
        to set this value with the name of :  Type.__class__.__name__.

        :type: `str`
        :raises: :class: `TypeError` if typeName is not a string
        """
        return self.__typeName

    @typeName.setter
    @typeCheck(str)
    def typeName(self, typeName):
        if typeName is None:
            raise TypeError("typeName cannot be None")
        self.__typeName = typeName

    @property
    def unitSize(self):
        """The unitSize of the current value.

        :type: `str`
        :raises: :class: `TypeError` if unitSize is not a string and not a supported value.

        """
        return self.__unitSize

    @unitSize.setter
    @typeCheck(UnitSize)
    def unitSize(self, unitSize):
        if unitSize is None:
            raise TypeError("UnitSize cannot be None")
        if not unitSize in AbstractType.supportedUnitSizes():
            raise TypeError(
                "Specified UnitSize is not supported, please refer to the list in AbstractType.supportedUnitSize()."
            )
        self.__unitSize = unitSize

    @property
    def endianness(self):
        """The endianness of the current value.
        The endianness definition is synchronized with the bitarray value.

        :type: `str`
        :raises: :class: `TypeError` if endianness is not a string and not a supported value.

        """
        return self.__endianness

    @endianness.setter
    @typeCheck(Endianness)
    def endianness(self, endianness):
        if endianness is None:
            raise TypeError("Endianness cannot be None")
        if not endianness in AbstractType.supportedEndianness():
            raise TypeError(
                "Specified Endianness is not supported, please refer to the list in AbstractType.supportedEndianness()."
            )

        self.__endianness = endianness

        if self.value is not None and self.value.endian() != self.__endianness:
            self.value = bitarray(self.value, endian=self.__endianness.value)

    @property
    def sign(self):
        """The sign of the current value.

        :type: `str`
        :raises: :class: `TypeError` if sign is not a string and not a supported value.

        """
        return self.__sign

    @sign.setter
    @typeCheck(Sign)
    def sign(self, sign):
        if sign is None:
            raise TypeError("Sign cannot be None")
        if not sign in AbstractType.supportedSign():
            raise TypeError(
                "Specified Sign is not supported, please refer to the list in AbstractType.supportedSign()."
            )
        self.__sign = sign
