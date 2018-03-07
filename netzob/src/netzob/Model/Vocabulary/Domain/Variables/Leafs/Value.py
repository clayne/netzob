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

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Leafs.AbstractRelationVariableLeaf import AbstractRelationVariableLeaf
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Model.Vocabulary.Domain.GenericPath import GenericPath


@NetzobLogger
class Value(AbstractRelationVariableLeaf):
    r"""The Value class is a variable whose content is the value of another field.

    It is possible to define a field so that its value is equal to the
    value of another field, on which a transformation operation can be
    performed.

    The Value constructor expects some parameters:

    :param target: The targeted field of the relationship.
    :param name: The name of the variable. If None, the name
                     will be generated.
    :param operation: An optional transformation operation to be
                      applied to the targeted field value, through a callback.
                      The default is None.
    :type target: :class:`Field <netzob.Model.Vocabulary.Field>`, required
    :type name: :class:`str`, optional
    :type operation: :class:`Callable <collections.abc.Callable>`, optional


    The Value class provides the following public variables:

    :var: target: The variable that is required before computing
                  the value of this relation.
    :var operation: Defines the operation to be performed on the found value.
                    The prototype of this callback is detailed below.
    :var varType: The type of the variable (Read-only).
    :vartype target: :class:`~netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable`
    :vartype operation: :class:`Callable <collections.abc.Callable>`
    :vartype varType: :class:`str`


    **Callback prototype**

    A callback function can be used to specify a complex
    relationship. The callback function that can be used in the
    ``operation`` parameter has the following prototype:

    ``def cbk_operation(data, parsed_structure, value):``

    Where:

    * ``data`` is a :class:`bitarray <bitarray>` that contains the value of the
      targeted field.
    * ``parsed_structure`` is a data structure that allows access to the values
      of the parsed ``Variable`` elements.
    * value is the Value variable

    The callback function is expected to implement relationship
    operations based on the provided data.

    The callback function should return a :class:`bitarray
    <bitarray>`.


    **Value usage**

    The following example shows how to define a field with a copy of
    another field value, in specialization mode:

    >>> from netzob.all import *
    >>> f0 = Field(String("abcd"))
    >>> f1 = Field(Value(f0))
    >>> fheader = Field([f0, f1])
    >>> fheader.specialize()
    b'abcdabcd'


    .. ifconfig:: scope in ('netzob')

       The following example shows how to define a field with a copy of
       another field value, in abstraction mode:

       >>> from netzob.all import *
       >>> data = "john;john!"
       >>> f1 = Field(String(nbChars=(2, 8)), name="f1")
       >>> f2 = Field(String(";"), name="f2")
       >>> f3 = Field(Value(f1), name="f3")
       >>> f4 = Field(String("!"), name="f4")
       >>> s = Symbol(fields=[f1, f2, f3, f4])
       >>> Symbol.abstract(data, [s])  # doctest: +NORMALIZE_WHITESPACE
       (Symbol, OrderedDict([('f1', b'john'), ('f2', b';'), ('f3', b'john'), ('f4', b'!')]))


    **Value field with a variable as a target**

    The following example shows the specialization process of a Value
    field whose target is a variable:

    >>> from netzob.all import *
    >>> d = Data(String("john"))
    >>> f1 = Field(domain=d, name="f1")
    >>> f2 = Field(String(";"), name="f2")
    >>> f3 = Field(Value(d), name="f3")
    >>> f4 = Field(String("!"), name="f4")
    >>> f = Field([f1, f2, f3, f4])
    >>> f.specialize()
    b'john;john!'


    **Specialization of Value objects**

    The following examples show the specialization process of Value
    objects. The first example illustrates a case where the Value
    variable is placed before the targeted variable.

    >>> from netzob.all import *
    >>> f1 = Field(String("john"), name="f1")
    >>> f2 = Field(String(";"), name="f2")
    >>> f3 = Field(Value(f1), name="f3")
    >>> f4 = Field(String("!"), name="f4")
    >>> f = Field([f1, f2, f3, f4])
    >>> f.specialize()
    b'john;john!'

    The second example illustrates a case where the Value variable is
    placed after the targeted variable.

    >>> from netzob.all import *
    >>> f3 = Field(String("john"), name="f3")
    >>> f2 = Field(String(";"), name="f2")
    >>> f1 = Field(Value(f3), name="f1")
    >>> f4 = Field(String("!"), name="f4")
    >>> f = Field([f1, f2, f3, f4])
    >>> f.specialize()
    b'john;john!'


    **Transformation operation on targeted field value**

    A named callback function can be used to specify a more complex
    relationship. The following example shows a relationship where the
    computed value corresponds to the reversed bits of the targeted
    field value. The ``data`` parameter of the ``cbk`` function contains a
    bitarray object of the targeted field value. The ``cbk`` function
    returns a bitarray object.

    >>> from netzob.all import *
    >>> def cbk(data, parsed_structure, value):
    ...    ret = data.copy()
    ...    ret.reverse()
    ...    return ret
    >>> f0 = Field(Raw(b'\x01'))
    >>> f1 = Field(Value(f0, operation = cbk))
    >>> f = Field([f0, f1])
    >>> f.specialize()
    b'\x01\x80'

    """

    def __init__(self, target, name=None, operation=None):
        super(Value, self).__init__(
            self.__class__.__name__, targets=[target], name=name)
        self.operation = operation

    @typeCheck(GenericPath)
    def valueCMP(self, parsingPath, acceptCallBack=True, carnivorous=False):
        self._logger.debug("ValueCMP")
        results = []
        if parsingPath is None:
            raise Exception("ParsingPath cannot be None")

        content = parsingPath.getData(self)
        if content is None:
            raise Exception("No data assigned.")

        # we verify we have access to the expected value
        expectedValue = self.computeExpectedValue(parsingPath)

        self._logger.debug("Expected value to parse: {0}".format(expectedValue))

        if expectedValue is None:
            self._logger.debug("Let's compute what could be the possible value based on the target datatype")
            if self.target.isnode():
                minSizeDep = 0
                maxSizeDep = len(content)
            else:
                (minSizeDep, maxSizeDep) = self.target.dataType.size

                if minSizeDep > len(content):
                    self._logger.debug("Size of the content to parse is smaller than the min expected size of the dependency field")
                    return results

            for size in range(min(maxSizeDep, len(content)), minSizeDep - 1, -1):
                # we create a new parsing path and returns it
                newParsingPath = parsingPath.duplicate()
                newParsingPath.addResult(self, content[:size].copy())
                self._addCallBacksOnUndefinedVariables(newParsingPath)
                results.append(newParsingPath)

        # If the expectedValue contains data
        else:
            if content[:len(expectedValue)] == expectedValue:
                self._logger.debug("add result: {0}".format(expectedValue.copy().tobytes()))
                parsingPath.addResult(self, content[:len(expectedValue)].copy())
                results.append(parsingPath)

        return results

    @typeCheck(ParsingPath)
    def domainCMP(self, parsingPath, acceptCallBack=True, carnivorous=False):
        """This method participates in the abstraction process.

        It creates a result in the provided path if the remainingData
        (or some if it) follows the type definition

        """

        return self.valueCMP(parsingPath, acceptCallBack)

    def computeExpectedValue(self, parsingPath):
        self._logger.debug("Compute expected value for Value field")

        variable = self.target
        if variable is None:
            raise Exception("No dependency field specified.")

        if not parsingPath.hasData(variable):
            return None
        else:
            return self._applyOperation(parsingPath.getData(variable),
                                        parsingPath)

    def _applyOperation(self, data, parsed_structure):
        """This method can be used to apply the specified operation function.
        If no operation function is known, the data parameter is returned."""

        if self.__operation is None:
            return data

        return self.__operation(data, parsed_structure, self)

    def __str__(self):
        """The str method."""
        return "Value({0})".format(str(self.target.name))

    @property
    def operation(self):
        """
        Property (getter.setter  # type: ignore).
        Defines the operation to be performed on the found value.
        This operation takes the form of a python function that accepts
        a single parameter of BitArray type and returns a BitArray.

        :type: :class:`Callable <collections.abc.Callable>`
        """
        return self.__operation

    @operation.setter  # type: ignore
    def operation(self, operation):
        if operation is not None and not callable(operation):
            raise TypeError("Operation must be a function")
        self.__operation = operation

    @property
    def target(self):
        return self.targets[0]

    def _test(self):
        """

        The following example shows how to define a field with a copy of
        another field value:

        >>> from netzob.all import *
        >>> data = "john;john!"
        >>> f3 = Field(String(nbChars=4), name="f3")
        >>> f1 = Field(Value(f3), name="f1")
        >>> f2 = Field(String(";"), name="f2")
        >>> f4 = Field(String("!"), name="f4")
        >>> s = Symbol(fields=[f1, f2, f3, f4])
        >>> Symbol.abstract(data, [s])  # doctest: +NORMALIZE_WHITESPACE
        (Symbol, OrderedDict([('f1', b'john'), ('f2', b';'), ('f3', b'john'), ('f4', b'!')]))

        """
