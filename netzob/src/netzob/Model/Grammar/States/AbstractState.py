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
import uuid
import abc

#+---------------------------------------------------------------------------+
#| Related third party imports                                               |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports                                                 |
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, public_api


class AbstractState(object, metaclass=abc.ABCMeta):
    """This class represents the interface of the abstract state. Every
    kind of state usable in the grammar of a protocol should inherit
    from this abstract class.

    The AbstractState constructor expects some parameters:

    :param name: The name of the state. The default value is `None`.
    :type name: :class:`str`, optional

    """

    def __init__(self, name=None):
        self.__id = uuid.uuid4()
        self.name = name
        self.active = False
        self.cbk_modify_transition = []

    def __str__(self):
        return str(self.name)

    # Execution abstract methods

    @abc.abstractmethod
    def executeAsInitiator(self, abstractionLayer):
        pass

    @abc.abstractmethod
    def executeAsNotInitiator(self, abstractionLayer):
        pass

    # Properties

    @property
    def id(self):
        """Unique identifier of the state

        :type: :class:`uuid.UUID`
        :raise: TypeError if not valid
        """
        return self.__id

    @id.setter  # type: ignore
    @typeCheck(uuid.UUID)
    def id(self, _id):
        if id is None:
            raise TypeError("id cannot be None")
        self.__id = _id

    @public_api
    @property
    def name(self):
        """Optional Name of the state

        :type: str
        :raise: TypeError is not a str
        """
        return self.__name

    @name.setter  # type: ignore
    @typeCheck(str)
    def name(self, name):
        if name is None:
            name = "State"

        self.__name = name

    @public_api
    @property
    def active(self):
        """Represents the current execution status of the state.
        If a state is active, it means none of its transitions has yet
        been fully executed and that its the current state.

        :type: :class:`bool`
        """
        return self.__active

    @active.setter  # type: ignore
    @typeCheck(bool)
    def active(self, active):
        if active is None:
            raise TypeError("The active info cannot be None")
        self.__active = active

    def add_cbk_modify_transition(self, cbk_method):
        """Add a function called during state execution to help choose the
        next transition (in a client context) or modifying the current
        transition (in a server context).

        The callable function should have the following prototype:

        .. code-block:: python

           def cbk_method(availableTransitions,
                          nextTransition,
                          current_state,
                          last_sent_symbol,
                          last_sent_message,
                          last_received_symbol,
                          last_received_message):

        Where:

          :attr:`availableTransitions`
            Corresponds to the :class:`list` of available transitions
            (:class:`~netzob.Model.Grammar.Transitions.Transition.Transition`)
            starting from the current state.

          :attr:`nextTransition`
            Currently selected transition, either the initial transition or
            the transition returned by the previous callback.

          :attr:`current_state`
            Current state in the automaton.

          :attr:`last_sent_symbol`
            Last sent symbol (:class:`~netzob.Model.Vocabulary.Symbol.Symbol`)
            on the abstraction layer, and thus makes it possible to create relationships
            with the previously sent symbol.

          :attr:`last_sent_message`
            Corresponds to the last sent message (:class:`bitarray`) on the
            abstraction layer, and thus makes it possible to create relationships with
            the previously sent message.

          :attr:`last_received_symbol`
            Corresponds to the last received symbol
            (:class:`~netzob.Model.Vocabulary.Symbol.Symbol`) on the
            abstraction layer, and thus makes it possible to create relationships with
            the previously received symbol.

          :attr:`last_received_message`
            Corresponds to the last received message (:class:`bitarray`) on the
            abstraction layer, and thus makes it possible to create relationships with
            the previously received message.

        The callback function should return a transition (which could
        be the original transition or another one in the available
        transitions).

        :type: :class:`func`
        :raise: :class:`TypeError` if ``cbk_method`` is not a callable function

        """

        if not callable(cbk_method):
            raise TypeError("'cbk_modifyTransition' should be a callable function")
        self.cbk_modify_transition.append(cbk_method)
