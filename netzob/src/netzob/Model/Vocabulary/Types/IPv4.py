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
import struct
import random
import unittest

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+
from netaddr import IPAddress, IPNetwork
from bitarray import bitarray

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import NetzobLogger
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType, Endianness, Sign, UnitSize


@NetzobLogger
class IPv4(AbstractType):
    r"""This class defines an IPv4 type.

    The IPv4 type encodes a :class:`bytes` object in an IPv4
    representation, and conversely decodes an IPv4 into a raw
    object.

    The IPv4 constructor expects some parameters:

    :param value: An IP value expressed in standard dot notation
                  (ex: "192.168.0.10"). The default value is None.
    :param network: A network address expressed in standard
                    dot notation (ex: "192.168.0.0/24"). The default value is None.
    :param endianness: The endianness of the current value. Values must be Endianness.BIG or Endianness.LITTLE. The default value is Endianness.BIG.
    :type value: :class:`str` or :class:`netaddr.IPAddress`, optional
    :type network: :class:`str` or :class:`netaddr.IPNetwork`, optional
    :type endianness: :class:`Endianness <netzob.Model.Vocabulary.Types.AbstractType.Endianness>`, optional

    .. note::
       :attr:`value` and :attr:`network` attributes are mutually exclusive.


    The IPv4 class provides the following public variables:

    :var typeName: The name of the implemented data type.
    :var value: The current value of the instance. This value is represented
                under the bitarray format.
    :var network: A constraint over the network. The parsed data belongs to this network or not.
    :vartype typeName: :class:`str`
    :vartype value: :class:`bitarray`
    :vartype network: :class:`str` or :class:`netaddr.IPNetwork`


    The following examples show the use of an IPv4 type:

    >>> from netzob.all import *
    >>> ip = IPv4("192.168.0.10")
    >>> ip.value
    bitarray('11000000101010000000000000001010')

    .. ifconfig:: scope in ('netzob')

       >>> f1 = Field("IP=", name="magic")
       >>> f2 = Field(IPv4(), name="ip4")
       >>> raw_data = ip.value.tobytes()
       >>> Symbol.abstract(raw_data, [f2])
       (ip4, OrderedDict([('ip4', b'\xc0\xa8\x00\n')]))
       >>> raw_data = f1.specialize() + raw_data
       >>> Symbol.abstract(raw_data, [f1, f2])  # doctest: +SKIP
       >>> s = Symbol(fields=[f1,f2])
       >>> msgs = [RawMessage(s.specialize()) for x in range(10)]
       >>> len(msgs)
       10

    It is also possible to specify an IPv4 type that accepts a range
    of IP addresses, through the :attr:`network` parameter, as shown in the
    following example:

    >>> from netzob.all import *
    >>> ip = IPv4(network="10.10.10.0/27")
    >>> IPv4(ip.generate())  # initialize with the generated bitarray value
    10.10.10.19

    """

    def __init__(self,
                 value=None,
                 network=None,
                 unitSize=UnitSize.SIZE_32,
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign()):

        if value is not None and network is not None:
            raise ValueError("An IPv4 should have either its value or its network set, but not both")

        if value is not None and not isinstance(value, bitarray):
            from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
            from netzob.Model.Vocabulary.Types.BitArray import BitArray
            value = TypeConverter.convert(
                value,
                IPv4,
                BitArray,
                src_unitSize=unitSize,
                src_endianness=endianness,
                src_sign=sign,
                dst_unitSize=unitSize,
                dst_endianness=endianness,
                dst_sign=sign)

        self.network = network

        size = (0, 1 << unitSize.value)

        super(IPv4, self).__init__(
            self.__class__.__name__,
            value,
            size,
            unitSize=UnitSize.SIZE_32,
            endianness=AbstractType.defaultEndianness(),
            sign=AbstractType.defaultSign())

    def __str__(self):
        if self.value is not None:
            return "{}(\"{}\")".format(self.typeName, IPv4.encode(self.value.tobytes()))
        elif self.network is not None:
            return "{}(\"{}\")".format(self.typeName, self.network)
        else:
            return "{}()".format(self.typeName)

    def count(self, presets=None, fuzz=None):
        r"""

        >>> from netzob.all import *
        >>> IPv4("127.0.0.1").count()
        1

        >>> IPv4().count()
        4294967296

        >>> IPv4(network='192.168.0.0/24').count()
        256

        >>> IPv4(network='192.168.0.0/23').count()
        512

        """

        if self.value is not None:
            return 1
        if self.network is not None:
            return self.network.size
        else:
            return (1 << self.unitSize.value)

    def getMinStorageValue(self):
            return 0

    def getMaxStorageValue(self):
            return 2**self.unitSize.value - 1

    def generate(self, generationStrategy=None):
        r"""Generates a random IPv4 which follows the constraints.

        >>> from netzob.all import *
        >>> f = Field(IPv4())
        >>> len(f.specialize())
        4

        >>> f = Field(IPv4("192.168.0.20"))
        >>> f.specialize()
        b'\xc0\xa8\x00\x14'

        >>> f = Field(IPv4(network="10.10.10.0/24"))
        >>> len(f.specialize())
        4

        """
        from netzob.Model.Vocabulary.Types.BitArray import BitArray
        from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
        from netzob.Model.Vocabulary.Types.Raw import Raw

        if self.value is not None:
            return self.value
        elif self.network is not None:
            ip = random.choice(self.network)
            return TypeConverter.convert(
                ip.packed,
                Raw,
                BitArray,
                src_unitSize=self.unitSize,
                src_endianness=self.endianness,
                src_sign=self.sign,
                dst_unitSize=self.unitSize,
                dst_endianness=self.endianness,
                dst_sign=self.sign)
        else:
            not_valid = [10, 127, 169, 172, 192]

            first = random.randrange(1, 256)
            while first in not_valid:
                first = random.randrange(1, 256)

            strip = ".".join([
                str(first), str(random.randrange(1, 256)),
                str(random.randrange(1, 256)), str(random.randrange(1, 256))
            ])

            ip = IPv4.encode(strip)
            return TypeConverter.convert(
                ip.packed,
                Raw,
                BitArray,
                src_unitSize=self.unitSize,
                src_endianness=self.endianness,
                src_sign=self.sign,
                dst_unitSize=self.unitSize,
                dst_endianness=self.endianness,
                dst_sign=self.sign)

    def canParse(self,
                 data,
                 unitSize=AbstractType.defaultUnitSize(),
                 endianness=AbstractType.defaultEndianness(),
                 sign=AbstractType.defaultSign()):
        r"""Computes if specified data can be parsed as an IPv4 with the predefined constraints.

        >>> from netzob.all import *
        >>> ip = IPv4()
        >>> ip.canParse("192.168.0.10")
        True
        >>> ip.canParse("198.128.0.100")
        True
        >>> ip.canParse("256.0.0.1")
        False
        >>> ip.canParse("127.0.0.1")
        True
        >>> ip.canParse("127.0.0.-1")
        False
        >>> ip.canParse("::")
        False
        >>> ip.canParse("0.0.0.0")
        True
        >>> ip.canParse(b"\1\2\3\4")
        True


        And with some constraints over the expected IPv4:


        >>> ip = IPv4("192.168.0.10")
        >>> ip.canParse("192.168.0.10")
        True
        >>> ip.canParse("192.168.1.10")
        False
        >>> ip.canParse(3232235530)
        True
        >>> ip = IPv4("167.20.14.20")
        >>> ip.canParse(3232235530)
        False
        >>> ip.canParse(3232235530)
        False


        or with contraints over the expected network the ipv4 belongs to:


        >>> ip = IPv4(network="192.168.0.0/24")
        >>> ip.canParse("192.168.0.10")
        True
        >>> ip.canParse("192.168.1.10")
        False

        :param data: the data to check
        :type data: python raw
        :return: True if data can be parsed as a Raw which is always the case (if len(data)>0)
        :rtype: bool
        :raise: TypeError if the data is None
        """

        if data is None:
            raise TypeError("data cannot be None")
        if isinstance(data, bitarray):
            data = data.tobytes()

        try:
            ip = IPv4.encode(
                data, unitSize=unitSize, endianness=endianness, sign=sign)
            if ip is None or ip.version != 4:
                return False
        except:
            return False
        try:
            if self.value is not None:
                from netzob.Model.Vocabulary.Types.TypeConverter import TypeConverter
                from netzob.Model.Vocabulary.Types.BitArray import BitArray
                return self.value == TypeConverter.convert(
                    data,
                    IPv4,
                    BitArray,
                    src_unitSize=unitSize,
                    src_endianness=endianness,
                    src_sign=sign,
                    dst_unitSize=self.unitSize,
                    dst_endianness=self.endianness,
                    dst_sign=self.sign)
            elif self.network is not None:
                return ip in self.network
        except:
            return False

        return True

    def _isValidIPv4Network(self, network):
        """Computes if the specified network is a valid IPv4 network.

        >>> from netzob.all import *
        >>> ip = IPv4()
        >>> ip._isValidIPv4Network("192.168.0.10")
        True
        >>> ip._isValidIPv4Network("-1.168.0.10")
        False

        """
        if network is None:
            raise TypeError("None is not valid IPv4 network")
        try:
            net = IPNetwork(network)
            if net is not None and net.version == 4:
                return True
        except:
            return False
        return False

    @property
    def network(self):
        """A constraint over the network the parsed data belongs to this network or not."""
        return self.__network

    @network.setter  # type: ignore
    def network(self, network):
        if network is not None:
            if not self._isValidIPv4Network(network):
                raise TypeError(
                    "Specified network constraints is not valid IPv4 Network.")
            self.__network = IPNetwork(network)
        else:
            self.__network = None

    @staticmethod
    def decode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        r"""Decode the specified IPv4 data into its raw representation.

        >>> from netzob.all import *
        >>> IPv4.decode("127.0.0.1")
        b'\x7f\x00\x00\x01'

        """

        if data is None:
            raise TypeError("Data cannot be None")
        ip = IPv4()
        if not ip.canParse(data):
            raise TypeError("Data is not a valid IPv4, cannot decode it.")
        ip = IPAddress(data)
        return ip.packed

    @staticmethod
    def encode(data,
               unitSize=AbstractType.defaultUnitSize(),
               endianness=AbstractType.defaultEndianness(),
               sign=AbstractType.defaultSign()):
        """Encodes the specified data into an IPAddress object

        :param data: the data to encode into an IPAddress
        :type data: str or raw bytes (BBBB)
        :return: the encoded IPAddress
        """
        if isinstance(data, (str, bytes, int)):
            try:
                ip = IPAddress(data)
                if ip is not None and ip.version == 4:
                    return ip
            except:
                pass
        try:

            structFormat = ">"
            if endianness == Endianness.BIG:
                structFormat = ">"

            if not sign == Sign.SIGNED:
                structFormat += "bbbb"
            else:
                structFormat += "BBBB"
            quads = list(map(str, struct.unpack(structFormat, data)))
            strIP = '.'.join(quads)

            ip = IPAddress(strIP)
            if ip is not None and ip.version == 4:
                return ip
        except Exception as e:
            raise TypeError("Impossible to encode {0} into an IPv4 data ({1})".
                            format(data, e))

    def getFixedBitSize(self):
        self._logger.debug("Determine the deterministic size of the value of "
                           "the type")
        return self.unitSize.value


def _test():
    r"""

    >>> from netzob.all import *
    >>> t = IPv4()
    >>> print(t)
    IPv4()
    >>> t.size
    (0, 4294967296)
    >>> t.unitSize
    UnitSize.SIZE_32

    >>> t = IPv4(network="192.168.0.0/24")
    >>> print(t)
    IPv4("192.168.0.0/24")

    >>> t = IPv4("192.168.1.1")
    >>> print(t)
    IPv4("192.168.1.1")


    # test abstraction arbitrary values

    >>> domains = [
    ...    IPv4("1.2.3.4"), IPv4(),
    ... ]
    >>> symbol = Symbol(fields=[Field(d, str(i)) for i, d in enumerate(domains)])
    >>> data = b''.join(f.specialize() for f in symbol.fields)
    >>> assert Symbol.abstract(data, [symbol])[1]


    # Verify that you cannot create an IPv4 with a value AND a network:

    >>> i = IPv4('10.0.0.1', network="10.10.10.0/24")
    Traceback (most recent call last):
    ...
    ValueError: An IPv4 should have either its value or its network set, but not both

    """
