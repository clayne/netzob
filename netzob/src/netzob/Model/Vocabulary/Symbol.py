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
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Common.Utils.TypedList import TypedList
from netzob.Model.Vocabulary.Messages.AbstractMessage import AbstractMessage
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Domain.Variables.Memory import Memory
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.BitArray import BitArray


class Symbol(AbstractField):
    """The Symbol class is a main component of the Netzob protocol model.

    A symbol represents an abstraction of all messages of the same
    type from a protocol perspective. A symbol structure is made of
    fields.

    The Symbol constructor expects some parameters:

    :param fields: The fields that participate in the symbol
                   definition, in the wire order. May be ``None`` (thus, a generic :class:`Field <netzob.Model.Vocabulary.Field.Field>`
                   instance would be defined), especially when using Symbols
                   for reverse engineering (i.e. fields identification).
    :param messages: The messages that are associated with the
                     symbol. May be ``None`` (thus, an empty :class:`list`
                     would be defined), especially when
                     modeling a protocol from scratch (i.e. the
                     fields are already known).
    :param name: The name of the symbol. If not specified, the
                 default name will be "Symbol".
    :type fields: a :class:`list` of :class:`Field <netzob.Model.Vocabulary.Field.Field>`, optional
    :type messages: a :class:`list` of :class:`AbstractMessage <netzob.Model.Vocabulary.Messages.AbstractMessage.AbstractMessage>`, optional
    :type name: :class:`str`, optional


    The Symbol class provides the following public variables:

    :var name: The name of the symbol.
    :var description: The description of the symbol.
    :var fields: The sorted list of sub-fields.
    :vartype name: :class:`str`
    :vartype description: :class:`str`
    :vartype fields: a :class:`list` of :class:`Field <netzob.Model.Vocabulary.Field.Field>`


    **Usage of Symbol for protocol modeling**

    The Symbol class may be used to model a protocol from scratch, by
    specifying its structure in terms of fields:

    >>> f0 = Field("aaaa")
    >>> f1 = Field(" # ")
    >>> f2 = Field("bbbbbb")
    >>> symbol = Symbol(fields=[f0, f1, f2])
    >>> print(symbol.str_structure())
    Symbol
    |--  Field
         |--   Data (String=aaaa ((None, None)))
    |--  Field
         |--   Data (String= #  ((None, None)))
    |--  Field
         |--   Data (String=bbbbbb ((None, None)))


    .. ifconfig:: scope in ('netzob')

       **Usage of Symbol for protocol dissecting**

       The Symbol class may be used to dissect a list of messages
       according to the fields structure:

       >>> from netzob.all import *
       >>> f0 = Field("hello", name="f0")
       >>> f1 = Field(String(nbChars=(0, 10)), name="f1")
       >>> m1 = RawMessage("hello world")
       >>> m2 = RawMessage("hello earth")
       >>> symbol = Symbol(fields=[f0, f1], messages=[m1, m2])
       >>> print(symbol.str_data())
       f0      | f1      
       ------- | --------
       'hello' | ' world'
       'hello' | ' earth'
       ------- | --------


    .. ifconfig:: scope in ('netzob')

       **Usage of Symbol for protocol reverse engineering**

       The Symbol class may be used is to do reverse engineering on a
       list of captured messages of unknown/undocumented protocols:

       >>> from netzob.all import *
       >>> m1 = RawMessage("hello aaaa")
       >>> m2 = RawMessage("hello bbbb")
       >>> symbol = Symbol(messages=[m1, m2])
       >>> Format.splitStatic(symbol)
       >>> print(symbol.str_data())
       Field-0  | Field-1
       -------- | -------
       'hello ' | 'aaaa' 
       'hello ' | 'bbbb' 
       -------- | -------

    **Usage of Symbol for traffic generation and parsing**

    A Symbol class may be used to generate concrete messages according
    to its field definition, through the
    :meth:`~netzob.Model.Vocabulary.Symbol.specialize` method, and
    may also be used to abstract a concrete message into its
    associated symbol through the
    :meth:`~netzob.Model.Vocabulary.Symbol.abstract` method:

    >>> f0 = Field("aaaa")
    >>> f1 = Field(" # ")
    >>> f2 = Field("bbbbbb")
    >>> symbol = Symbol(fields=[f0, f1, f2])
    >>> concrete_message = symbol.specialize()
    >>> concrete_message
    b'aaaa # bbbbbb'
    >>> (abstracted_symbol, structured_data) = Symbol.abstract(concrete_message, [symbol])
    >>> abstracted_symbol == symbol
    True

    """

    def __init__(self, fields=None, messages=None, name="Symbol"):
        super(Symbol, self).__init__(name)
        self.__messages = TypedList(AbstractMessage)
        if messages is None:
            messages = []
        self.messages = messages
        if fields is None:
            # create a default empty field
            fields = [Field()]
        self.fields = fields

    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return False
        if other is None:
            return False
        return self.name == other.name

    def __ne__(self, other):
        if other is None:
            return True
        if not isinstance(other, Symbol):
            return True
        return other.name != self.name

    def __key(self):
        return self.id

    def __hash__(self):
        return hash(frozenset(self.name))

    @typeCheck(Memory, object)
    def specialize(self, presets=None, fuzz=None, memory=None):
        r"""The method :meth:`specialize()` generates a :class:`bytes` sequence whose
        content follows the symbol definition.

        The specialize() method expects some parameters:

        :param presets: A dictionary of keys:values used to preset
                        (parameterize) fields during symbol
                        specialization. Values in this dictionary will
                        override any field definition, constraints or
                        relationship dependencies.
        :param fuzz: A fuzzing configuration used during the specialization process. Values
                     in this configuration will override any field
                     definition, constraints, relationship
                     dependencies or parameterized fields. See
                     :class:`Fuzz <netzob.Fuzzing.Fuzz.Fuzz>`
                     for a complete explanation of its use for fuzzing
                     purpose.
        :param memory: A memory used to store variable values during
                       specialization and abstraction of successive
                       symbols, especially to handle inter-symbol
                       relationships. If None, a temporary memory is
                       created by default and used internally during the scope of the
                       specialization process.
        :type presets: :class:`dict`, optional
        :type fuzz: :class:`Fuzz <netzob.Fuzzing.Fuzz.Fuzz>`, optional
        :type memory: :class:`Memory <netzob.Model.Vocabulary.Domain.Variables.Memory.Memory>`, optional
        :return: The produced content after specializing the symbol.
        :rtype: :class:`bytes`
        :raises: :class:`GenerationException <netzob.Model.Vocabulary.AbstractField.GenerationException>` if an error occurs while specializing the field.

        The following example shows the :meth:`specialize()` method used for a
        field which contains a String and a Size fields.

        >>> from netzob.all import *
        >>> f1 = Field(domain=String(nbChars=5))
        >>> f0 = Field(domain=Size(f1))
        >>> s = Symbol(fields=[f0, f1])
        >>> result = s.specialize()
        >>> result[0]
        5
        >>> len(result)
        6

        **Parameterized specialization of field values (`presets=` parameter)**

        It is possible to preset (parameterize) fields during symbol
        specialization, through a dict passed in the ``presets=``
        parameter of the :meth:`~netzob.Model.Vocabulary.Symbol.specialize`
        method. Values in this dictionary will override any field
        definition, constraints or relationship dependencies.

        The presets dictionary accepts a sequence of keys and values,
        where keys correspond to the fields in the symbol that we want
        to override, and values correspond to the overriding
        content. Keys are either expressed as :class:`Field
        <netzob.Model.Vocabulary.Field.Field>` objects or strings
        containing field accessors when field names are used (such as
        in ``f = Field(name="udp.dport")``). Values are either
        expressed as :class:`BitArray
        <netzob.Model.Vocabulary.Types.BitArray.BitArray>` (as it is
        the internal type for variables in the Netzob library) or in
        the type of the overridden field variable.

        The following code shows the definition of a simplified UDP
        header that will be later used as base example. This UDP
        header is made of one named field containing a destination
        port, and a named field containing a payload:

        >>> f_dport = Field(name="udp.dport", domain=Integer(unitSize=UnitSize.SIZE_8))
        >>> f_payload = Field(name="udp.payload", domain=Raw(nbBytes=2))
        >>> symbol_udp = Symbol(name="udp", fields=[f_dport, f_payload])

        The three following codes show the same way to express the
        parameterized **values** during specialization of the fields
        ``udp_dport`` and ``udp_payload``:

        >>> presets = {}
        >>> presets["udp.dport"] = 11              # udp.dport expects an int or an Integer
        >>> presets["udp.payload"] = b"\xaa\xbb"   # udp.payload expects a bytes object or a Raw object
        >>> symbol_udp.specialize(presets=presets)
        b'\x0b\xaa\xbb'

        >>> presets = {}
        >>> presets["udp.dport"] = Integer(11)        # udp.dport expects an int or an Integer
        >>> presets["udp.payload"] = Raw(b"\xaa\xbb") # udp.payload expects a bytes object or a Raw object
        >>> symbol_udp.specialize(presets=presets)
        b'\x0b\xaa\xbb'

        >>> presets = {}
        >>> presets["udp.dport"] = bitarray('00001011', endian='big')
        >>> presets["udp.payload"] = bitarray('1010101010111011', endian='big')
        >>> symbol_udp.specialize(presets=presets)
        b'\x0b\xaa\xbb'

        The previous example shows the use of BitArray as dict
        values. BitArray are always permitted for any parameterized
        field, as it is the internal type for variables in the Netzob
        library.

        The two following codes show the same way to express the
        parameterized **keys** during specialization of the fields
        ``udp_dport`` and ``udp_payload``:

        >>> presets = {}
        >>> presets[f_dport] = 11
        >>> presets[f_payload] = b"\xaa\xbb"
        >>> symbol_udp.specialize(presets=presets)
        b'\x0b\xaa\xbb'

        >>> presets = {}
        >>> presets["udp.dport"] = 11
        >>> presets["udp.payload"] = b"\xaa\xbb"
        >>> symbol_udp.specialize(presets=presets)
        b'\x0b\xaa\xbb'


        A preset value bypasses all the constraint checks on your field definition.
        For example, in the following example it can be used to bypass a size field definition.

        >>> from netzob.all import *
        >>> f1 = Field()
        >>> f2 = Field(domain=Raw(nbBytes=(10,15)))
        >>> f1.domain = Size(f2)
        >>> s = Symbol(fields=[f1, f2])
        >>> presetValues = {f1: bitarray('11111111')}
        >>> s.specialize(presets = presetValues)[0]
        255


        **Fuzzing of Fields**

        It is possible to fuzz fields during symbol specialization,
        through the ``fuzz=`` parameter of the
        :meth:`~netzob.Model.Vocabulary.Symbol.specialize`
        method. Values in this parameter will override any field
        definition, constraints, relationship dependencies or
        parameterized values.

        For more information regarding the expected ``fuzz=``
        parameter content, see the class :class:`Fuzz
        <netzob.Fuzzing.Fuzz.Fuzz>`.

        """

        from netzob.Model.Vocabulary.Domain.Specializer.MessageSpecializer import MessageSpecializer
        msg = MessageSpecializer(presets=presets, fuzz=fuzz, memory=memory)
        spePath = msg.specializeSymbol(self)

        if spePath is not None:
            return spePath.generatedContent.tobytes()

    @typeCheck(Memory, object)
    def specialize_count(self, presets=None, fuzz=None):
        r"""The method :meth:`specialize_count` computes the expected number of unique
        produced messages, considering the initial symbol model, the
        preset fields and the fuzzed fields.

        The :meth:`specialize_count` method expects the same parameters as the :meth:`specialize` method:

        :param presets: A dictionary of keys:values used to preset
                        (parameterize) fields during symbol
                        specialization. Values in this dictionary will
                        override any field definition, constraints or
                        relationship dependencies.
        :param fuzz: A dictionary of keys:values used for fuzzing
                     purpose during the specialization process. This
                     parameter is handled in the same way as the
                     ``presets`` parameter (i.e. a mutator can be
                     defined for each field we want to fuzz). Values
                     in this dictionary will override any field
                     definition, constraints, relationship
                     dependencies or parameterized fields. See
                     :class:`Mutator <netzob.Fuzzing.Mutator.Mutator>`
                     for a complete explanation of its use for fuzzing
                     purpose.
        :type presets: :class:`dict`, optional
        :type fuzz: :class:`dict`, optional

        >>> # Symbol definition
        >>> from netzob.all import *
        >>> f1 = Field(uint16(interval=(50, 1000)))
        >>> f2 = Field(uint8())
        >>> f3 = Field(uint8())
        >>> symbol = Symbol(fields=[f1, f2, f3])
        >>>
        >>> # Specify the preset fields
        >>> presetValues = {f1: bitarray('1111111111111111')}        
        >>>
        >>> # Specify the fuzzed fields
        >>> fuzz = Fuzz()
        >>> from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator
        >>> fuzz.set(f2, IntegerMutator, interval=(20, 42)) # doctest: +SKIP
        >>>
        >>> # Count the expected number of unique produced messages
        >>> symbol.specialize_count(presets=presetValues, fuzz=fuzz) # doctest: +SKIP
        279

        """

        # TODO
        pass

    def clearMessages(self):
        """Delete all the messages attached to the current symbol"""
        while (len(self.__messages) > 0):
            self.__messages.pop()

    # Properties

    @property
    def messages(self):
        """A list containing all the messages that this symbol represent.

        :type : a :class:`list` of :class:`AbstractMessage <netzob.Model.Vocabulary.Messages.AbstractMessage.AbstractMessage>`
        """
        return self.__messages

    @messages.setter
    def messages(self, messages):
        if messages is None:
            messages = []

        # First it checks the specified messages are all AbstractMessages
        for msg in messages:
            if not isinstance(msg, AbstractMessage):
                raise TypeError(
                    "Cannot add messages of type {0} in the session, only AbstractMessages are allowed.".
                    format(type(msg)))

        self.clearMessages()
        for msg in messages:
            self.__messages.append(msg)

    def __repr__(self):
        return self.name

    def __getitem__(self, field_name):
        """
        Get a field from its name in the field database.

        :param field_name: the name of the :class:`Field <netzob.Model.Vocabulary.Field.Field>` object
        :type field_name: :class:`str`
        :raise KeyError: when the field has not been found
        """
        field = self.getField(field_name)
        if field is None:
            raise KeyError("Field {} has not been found in {}"
                           .format(field_name, self))
        return field
