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
import random

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode
from netzob.Model.Vocabulary.Domain.Parser.ParsingPath import ParsingPath
from netzob.Model.Vocabulary.Domain.Specializer.SpecializingPath import SpecializingPath

# Class used to denote current variable, in order to handle self recursivity
class SELF(object):
    pass


@NetzobLogger
class Agg(AbstractVariableNode):
    r"""The Agg class is a node variable that represents a concatenation of variables.

    An Aggregate node concatenates the values that are accepted by
    its children nodes. It can be used to specify a succession of
    tokens.

    The Agg constructor expects some parameters:

    :param children: The sequence of variable elements contained in
                     the aggregate.
    :param last_optional: A flag indicating if the last element of the children is optional or not.
    :param svas: The SVAS strategy defining how the Aggregate
                 behaves during abstraction and specialization. The default strategy is SVAS.EPHEMERAL.
    :type children: a :class:`list` of :class:`AbstractVariable <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable>`, optional
    :type last_optional: :class:`bool`
    :type svas: :class:`SVAS <netzob.Model.Vocabulary.Domain.Variables.SVAS.SVAS>`, optional


    For example, the following code represents a field that
    accepts values that are made of a String of 3 to 20 random
    characters followed by a ".txt" extension:

    >>> from netzob.all import *
    >>> t1 = String(nbChars=(3,20))
    >>> t2 = String(".txt")
    >>> f = Field(Agg([t1, t2]))

    The following example shows an aggregate between BitArray
    variables:

    >>> from netzob.all import *
    >>> from bitarray import bitarray
    >>> f0 = Field(Agg([BitArray('01101001'), BitArray(nbBits=3), BitArray(nbBits=5)]))
    >>> s = Symbol(fields=[f0])
    >>> t = s.specialize()
    >>> len(t)
    2


    **Examples of Agg internal attribute access**

    >>> domain = Agg([Raw(), String()])
    >>> domain.varType
    'Agg'
    >>> print(domain.children[0].dataType)
    Raw=None ((0, 524288))
    >>> print(domain.children[1].dataType)
    String=None ((None, None))
    >>> domain.children.append(Agg([10, 20, 30]))
    >>> len(domain.children)
    3
    >>> domain.children.remove(domain.children[0])
    >>> len(domain.children)
    2


    **Abstraction of aggregate variables**

    This example shows the abstraction process of an Aggregate
    variable:

    >>> from netzob.all import *
    >>> v1 = String(nbChars=(1, 10))
    >>> v2 = String(".txt")
    >>> f0 = Field(Agg([v1, v2]), name="f0")
    >>> f1 = Field(String("!"), name="f1")
    >>> s = Symbol([f0, f1])
    >>> data = "john.txt!"
    >>> Symbol.abstract(data, [s])
    (Symbol, OrderedDict([('f0', b'john.txt'), ('f1', b'!')]))

    In the following example, an Aggregate variable is defined. A
    message that does not correspond to the expected model is then
    parsed, thus the returned symbol is unknown:

    >>> data = "johntxt!"
    >>> Symbol.abstract(data, [s])
    (Unknown Symbol 'johntxt!', OrderedDict())


    **Specialization of aggregate variables**

    This example shows the specialization process of an Aggregate
    variable:

    >>> from netzob.all import *
    >>> d1 = String("hello")
    >>> d2 = String(" john")
    >>> f = Field(Agg([d1, d2]))
    >>> s = Symbol(fields=[f])
    >>> s.specialize()
    b'hello john'


    **Optional last variable**

    This example shows the specialization and parsing of an aggregate
    with an optional last variable*:

    >>> from netzob.all import *
    >>> a = Agg([int8(2), int8(3)], last_optional=True)
    >>> f = Field(a)
    >>> res = f.specialize()
    >>> res == b'\x02' or res == b'\x02\x03'
    True
    >>> d = b'\x02\x03'
    >>> Field.abstract(d, [f])
    (Field, OrderedDict([('Field', b'\x02\x03')]))

    >>> d = b'\x02'
    >>> Field.abstract(d, [f])
    (Field, OrderedDict([('Field', b'\x02')]))


    **Modeling indirect imbrication**

    >>> from netzob.all import *
    >>> v0 = Agg(["?", int8(4)])
    >>> v1 = Agg(["!", int8(3), v0], last_optional=True)
    >>> v2 = Agg([int8(2), v1], last_optional=True)
    >>> f = Field(v2)
    >>>
    >>> # Test specialization
    >>> res = f.specialize()
    >>> res == b'\x02' or res == b'\x02!\x03' or res == b'\x02!\x03?\x04'
    True
    >>>
    >>> # Test parsing
    >>> (res_object, res_data) = Field.abstract(res, [f])
    >>> res_object == f
    True


    **Modeling indirect recursion**

    >>> from netzob.all import *    
    >>> v1 = Agg([])
    >>> v2 = Agg([int8(interval=(1, 3)), v1], last_optional=True)
    >>> v1.children = ["!", v2]
    >>> f = Field(v2)
    >>> res = f.specialize()
    >>> res  # doctest: +SKIP
    b'\x03!\x03!\x03!\x03'
    >>>
    >>> # Test parsing
    >>> (res_object, res_data) = Field.abstract(res, [f])
    >>> res_object == f  # doctest: +SKIP
    True


    **Modeling direct recursion**

    >>> from netzob.all import *
    >>> v = Agg([int8(interval=(1, 5)), SELF], last_optional=True)
    >>> f = Field(v)
    >>>
    >>> # Test specialization
    >>> res = f.specialize()
    >>> res  # doctest: +SKIP
    b'\x02\x04\x01'
    >>>
    >>> # Test parsing
    >>> (res_object, res_data) = Field.abstract(res, [f])
    >>> res_object == f  # doctest: +SKIP
    True


    """

    def __init__(self, children=None, last_optional=False, svas=None):
        super(Agg, self).__init__(self.__class__.__name__, children, svas=svas)

        self._last_optional = last_optional

    @typeCheck(ParsingPath)
    def parse(self, parsingPath, carnivorous=False):
        """Parse the content with the definition domain of the aggregate.
        """
        dataToParse = parsingPath.getData(self).copy()
        self._logger.debug("Parse '{}' as {} with parser path '{}'".format(
            dataToParse.tobytes(), self, parsingPath))

        # initialy, there is a unique path to test (the provided one)
        parsingPath.assignData(dataToParse.copy(), self.children[0])
        parsingPaths = [parsingPath]

        # we parse all the children with the parserPaths produced by previous children
        all_parsed = False
        for i_child in range(len(self.children)):

            # Handle optional field situation, where all data may have already been parsed before the last field
            if all_parsed == True:
                break

            current_child = self.children[i_child]
            if i_child < len(self.children) - 1:
                next_child = self.children[i_child + 1]
            else:
                next_child = None

            newParsingPaths = []

            for parsingPath in parsingPaths:
                self._logger.debug(
                    "Parse {0} with {1}".format(current_child.id, parsingPath))
                value_before_parsing = parsingPath.getData(
                    current_child).copy()
                childParsingPaths = current_child.parse(
                    parsingPath, carnivorous=carnivorous)

                for childParsingPath in childParsingPaths:
                    value_after_parsing = childParsingPath.getData(
                        current_child).copy()
                    remainingValue = value_before_parsing[len(
                        value_after_parsing):].copy()

                    if next_child is not None:
                        # Handle optional field
                        if len(remainingValue) == 0 and i_child == len(self.children) - 2 and self._last_optional:
                            all_parsed = True
                        # Else send the remaining data to the last field
                        else:
                            childParsingPath.assignData(
                                remainingValue, next_child)

                    # at least one child path managed to parse, we save the valid paths it produced
                    self._logger.debug(
                        "Children {0} succesfuly applied with the parsingPath {1}".
                        format(current_child, parsingPath))
                    newParsingPaths.append(childParsingPath)

            parsingPaths = newParsingPaths

            if len(parsingPaths) == 0:
                self._logger.debug("Children {0} didn't apply to any of the parser path we have, we stop Agg parser".format(current_child))
                return []  # return no valid paths

        # ok we managed to parse all the children, and it produced some valid parser paths. We return them
        for parsingPath in parsingPaths:
            parsedData = None
            for child in self.children:
                if parsingPath.hasData(child):
                    child_data = parsingPath.getData(child).copy()
                    if parsedData is None:
                        parsedData = child_data
                    else:
                        parsedData = parsedData + child_data

            self._logger.debug("Data successfuly parsed with {}: '{}'".format(self, parsedData.tobytes()))
            parsingPath.addResult(self, parsedData)
        return parsingPaths

    @typeCheck(SpecializingPath)
    def specialize(self, originalSpecializingPath, fuzz=None):
        """Specializes an Agg"""

        # initialy, there is a unique path to specialize (the provided one)
        specializingPaths = [originalSpecializingPath]
        specialize_last_child = True

        # we parse all the children with the specializerPaths produced by previous children
        for idx, child in enumerate(self.children):
            newSpecializingPaths = []

            self._logger.debug("Specializing AGG child with {0} paths".format(len(specializingPaths)))

            if len(self.children) - 1 == idx and self._last_optional:
                self._logger.debug("Last child is optional")

                # Randomely select if we are going to specialize the last child
                specialize_last_child = random.choice([True, False])
                if specialize_last_child:
                    self._logger.debug("Last child is optional, and this option is taken")
                else:
                    self._logger.debug("Last child is optional, and this option is not taken")
                    break

            for specializingPath in specializingPaths:
                self._logger.debug("Specialize {0} with {1}".format(child, specializingPath))

                if type(child) == type and child == SELF:
                    # Nothing to specialize in this case (the recursive specialization is done later)
                    childSpecializingPaths = [specializingPath]
                else:
                    childSpecializingPaths = child.specialize(specializingPath, fuzz=fuzz)

                if len(childSpecializingPaths) > 0:
                    # at least one child path managed to specialize, we save the valid paths it produced
                    for childSpecializingPath in childSpecializingPaths:
                        newSpecializingPaths.append(childSpecializingPath)

            specializingPaths = newSpecializingPaths

        self._logger.debug("Specializing AGG child has produced {0} paths".format(len(specializingPaths)))

        if len(specializingPaths) == 0:
            self._logger.debug("Children {0} didn't apply to any of the specializer path we have, we stop Agg specializer".format(child))
            return []  # return no valid paths

        # Retrieve specialized data
        for specializingPath in specializingPaths:
            value = None
            for idx, child in enumerate(self.children):

                if type(child) == type and child == SELF:
                    # Nothing to retrieve in this case (the recursive specialization is done later)
                    continue

                if specializingPath.hasData(child):
                    child_data = specializingPath.getData(child)
                    if value is None:
                        value = child_data
                    else:
                        value = value + child_data

            self._logger.debug("Generated value for {}: {}".format(self, value.tobytes()))


            # Handle recursive mode
            if type(child) == type and child == SELF and specialize_last_child:
                childSpecializingPaths = self.specialize(specializingPath, fuzz=fuzz)

                if len(childSpecializingPaths) > 0:
                    specializingPath = childSpecializingPaths[0]
                    if specializingPath.hasData(self):
                        current_value = specializingPath.getData(self)
                        value =  value + current_value
                        self._logger.debug("Cumulative generated value for {}: {}".format(self, value.tobytes()))

            # Final Agg value
            specializingPath.addResult(self, value)

            
        # ok we managed to parse all the children, and it produced some valid specializer paths. We return them
        return specializingPaths
