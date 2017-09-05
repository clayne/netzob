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
from typing import Dict, Union  # noqa: F401

# +---------------------------------------------------------------------------+
# | Related third party imports                                               |
# +---------------------------------------------------------------------------+

# +---------------------------------------------------------------------------+
# | Local application imports                                                 |
# +---------------------------------------------------------------------------+
from netzob.Model.Vocabulary.Domain.Variables.AbstractVariable import AbstractVariable
from netzob.Model.Vocabulary.Domain.Variables.Nodes.AbstractVariableNode import AbstractVariableNode
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Repeat import Repeat
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Alt import Alt
from netzob.Model.Vocabulary.Domain.Variables.Nodes.Agg import Agg
from netzob.Model.Vocabulary.Field import Field
from netzob.Model.Vocabulary.Symbol import Symbol
from netzob.Model.Vocabulary.Types.AbstractType import AbstractType  # noqa: F401
from netzob.Model.Vocabulary.AbstractField import AbstractField
from netzob.Model.Vocabulary.Types.Integer import Integer
from netzob.Model.Vocabulary.Types.String import String
from netzob.Model.Vocabulary.Types.Raw import Raw
from netzob.Model.Vocabulary.Types.HexaString import HexaString
from netzob.Model.Vocabulary.Types.BitArray import BitArray
from netzob.Model.Vocabulary.Types.IPv4 import IPv4
from netzob.Model.Vocabulary.Types.Timestamp import Timestamp
from netzob.Fuzzing.Mutator import Mutator
from netzob.Fuzzing.Mutators.AltMutator import AltMutator  # noqa: F401
from netzob.Fuzzing.Mutators.AggMutator import AggMutator  # noqa: F401
from netzob.Fuzzing.Mutators.RepeatMutator import RepeatMutator  # noqa: F401
from netzob.Fuzzing.Mutators.DomainMutator import DomainMutator  # noqa: F401
from netzob.Fuzzing.Mutators.IntegerMutator import IntegerMutator
from netzob.Fuzzing.Mutators.StringMutator import StringMutator
from netzob.Fuzzing.Mutators.TimestampMutator import TimestampMutator
from netzob.Fuzzing.Mutators.IPv4Mutator import IPv4Mutator
from netzob.Fuzzing.Mutators.BitArrayMutator import BitArrayMutator
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger


@NetzobLogger
class Fuzz(object):
    r"""The Fuzz class is the entry point for the fuzzing component.

    We can apply fuzzing on symbols, fields, variables and types
    through the :meth:`set <.Fuzz.set>` method.

    The Fuzz constructor expects some parameters:

    :param counterMax: The max number of mutations to produce (a :class:`int` should be used to represent an absolute value, whereas a :class:`float` should be use to represent a ratio in percent).
    :type counterMax: :class:`int` or :class:`float`, defaults to :attr:`COUNTER_MAX_DEFAULT`


    The following examples show the different usages of the fuzzing
    component.

    **Basic fuzzing example**

    >>> from netzob.all import *
    >>> fuzz = Fuzz()
    >>> f_data = Field(domain=int8())
    >>> symbol = Symbol(fields=[f_data])
    >>> fuzz.set(f_data)
    >>> symbol.specialize(fuzz=fuzz)
    b'D'


    **Fuzzing example of a field that contains an integer**

    >>> from netzob.all import *
    >>> fuzz = Fuzz()
    >>> f_data = Field(name="data", domain=int16(interval=(1, 4)))
    >>> symbol = Symbol(name="sym", fields=[f_data])
    >>> fuzz.set(f_data, interval=(20, 32000))
    >>> symbol.specialize(fuzz=fuzz)
    b'`n'


    **Fuzzing example of a field that contains a size relationship with another field**

    >>> from netzob.all import *
    >>> fuzz = Fuzz()
    >>> f_data = Field(name="data", domain=int16(3))
    >>> f_size = Field(name="size", domain=Size([f_data], Integer(unitSize=UnitSize.SIZE_16)))
    >>> symbol = Symbol(name="sym", fields=[f_data, f_size])
    >>> fuzz.set(f_size, interval=(20, 32000))
    >>> symbol.specialize(fuzz=fuzz)
    b'\x00\x03`n'


    **Fuzzing example in mutation mode of a field that contains an integer**

    >>> from netzob.all import *
    >>> fuzz = Fuzz()
    >>> f_data = Field(name="data", domain=int16(2))
    >>> symbol = Symbol(name="sym", fields=[f_data])
    >>> fuzz.set(f_data, mode=MutatorMode.MUTATE, interval=(20, 32000))
    >>> res = symbol.specialize(fuzz=fuzz)
    >>> res != b'\x00\x02'
    True


    **Multiple fuzzing call on the same symbol**

    >>> from netzob.all import *
    >>> fuzz = Fuzz()
    >>> f_data = Field(name="data", domain=int16(2))
    >>> symbol = Symbol(name="sym", fields=[f_data])
    >>> fuzz.set(f_data, interval=(20, 30000))
    >>> nbFuzz = 1000
    >>> result = set()
    >>> for i in range(nbFuzz):
    ...     result.add(symbol.specialize(fuzz=fuzz))
    >>> len(result) == 980
    True


    **Fuzzing of a field that contains sub-fields**

    >>> from netzob.all import *
    >>> fuzz = Fuzz()
    >>> f_data1 = Field(name="data1", domain=int8())
    >>> f_data2 = Field(name="data2", domain=int16())
    >>> f_parent = Field(name="parent", domain=[f_data1, f_data2])
    >>> symbol = Symbol(name="sym", fields=[f_parent])
    >>> fuzz.set(f_parent)
    >>> symbol.specialize(fuzz=fuzz)
    b'DEt'


    **Fuzzing of a whole symbol, and covering all fields storage spaces with default fuzzing strategy per types**

    >>> from netzob.all import *
    >>> fuzz = Fuzz()
    >>> f_data1 = Field(name="data1", domain=int8(interval=(2, 4)))
    >>> f_data2 = Field(name="data2", domain=int8(interval=(5, 8)))
    >>> symbol = Symbol(name="sym", fields=[f_data1, f_data2])
    >>> fuzz.set(symbol, interval=MutatorInterval.FULL_INTERVAL)
    >>> symbol.specialize(fuzz=fuzz)
    b'DD'


    **Fuzzing of a whole symbol except one field, and covering all fields storage spaces**

    >>> from netzob.all import *
    >>> fuzz = Fuzz()
    >>> f_data1 = Field(name="data1", domain=int8(2))
    >>> f_data2 = Field(name="data2", domain=int8(4))
    >>> symbol = Symbol(name="sym", fields=[f_data1, f_data2])
    >>> fuzz.set(symbol, interval=MutatorInterval.FULL_INTERVAL)
    >>> fuzz.unset(f_data2)
    >>> symbol.specialize(fuzz=fuzz)
    b'D\x04'


    **Fuzzing of a field with default fuzzing strategy, and covering field storage space**

    >>> from netzob.all import *
    >>> fuzz = Fuzz()
    >>> f_data1 = Field(name="data1", domain=int8(2))
    >>> f_data2 = Field(name="data2", domain=int8(4))
    >>> symbol = Symbol(name="sym", fields=[f_data1, f_data2])
    >>> fuzz.set(f_data2, interval=MutatorInterval.FULL_INTERVAL)
    >>> symbol.specialize(fuzz=fuzz)
    b'\x02D'


    **Fuzzing and changing the default fuzzing strategy for types**

    >>> from netzob.all import *
    >>> fuzz = Fuzz()
    >>> f_data1 = Field(name="data1", domain=int8(2))
    >>> f_data2 = Field(name="data2", domain=int8(4))
    >>> symbol = Symbol(name="sym", fields=[f_data1, f_data2])
    >>> fuzz.set(Integer, seed=142)
    >>> fuzz.set(f_data2)
    >>> symbol.specialize(fuzz=fuzz)
    b'\x02\x04'


    **Fuzzing configuration with a maximum number of mutations**

    >>> from netzob.all import *
    >>> fuzz = Fuzz(counterMax=1)
    >>> f_alt = Field(name="alt", domain=Alt([int8(interval=(1, 4)),
    ...                                       int8(interval=(5, 8))]))
    >>> symbol = Symbol(name="sym", fields=[f_alt])
    >>> fuzz.set(f_alt)
    >>> symbol.specialize(fuzz=fuzz)
    b'\x07'
    >>> symbol.specialize(fuzz=fuzz)
    Traceback (most recent call last):
    Exception: Max mutation counter reached
    >>> fuzz = Fuzz()  # This is needed to restore globalCounterMax default value for unit test purpose

    """

    mappingTypesMutators = {}   # type: Dict[AbstractType, Union[DomainMutator, dict]]
    mappingFieldsMutators = {}  # type: Dict[Field, DomainMutator]

    # Initialize mapping of types with their mutators
    @staticmethod
    def _initializeMappings():
        Fuzz.mappingFieldsMutators = {}

        Fuzz.mappingTypesMutators = {}
        Fuzz.mappingTypesMutators[Integer] = (IntegerMutator, {})
        Fuzz.mappingTypesMutators[String] = (StringMutator, {})
        Fuzz.mappingTypesMutators[HexaString] = (IntegerMutator, {})
        Fuzz.mappingTypesMutators[Raw] = (IntegerMutator, {})
        Fuzz.mappingTypesMutators[BitArray] = (BitArrayMutator, {})
        Fuzz.mappingTypesMutators[IPv4] = (IPv4Mutator, {})
        Fuzz.mappingTypesMutators[Timestamp] = (TimestampMutator, {})
        Fuzz.mappingTypesMutators[Repeat] = (RepeatMutator, {})
        Fuzz.mappingTypesMutators[Alt] = (AltMutator, {})
        Fuzz.mappingTypesMutators[Agg] = (AggMutator, {})

    def __init__(self, counterMax=Mutator.COUNTER_MAX_DEFAULT):  # type: Union[int, float]

        # Initialize variables from parameters
        self.counterMax = counterMax

        # Initialize mapping between Types and default Mutators with default configuration
        Fuzz._initializeMappings()
        self.mappingTypesMutators = Fuzz.mappingTypesMutators

        # Initialize mapping between Field/Symbols and Mutators
        self.mappingFieldsMutators = Fuzz.mappingFieldsMutators

    def set(self, key, **kwargs):
        r"""The method :meth:`set <.Fuzz.set>` specifies the fuzzing
        strategy for a symbol, a field, a variable or a type.

        The :meth:`set <.Fuzz.set>` method expects some parameters:

        :param key: The targeted object (either a symbol, a field, a
                    variable or a type) (required).
        :param kwargs: Some context dependent parameters (see below) (optional).
        :type key: :class:`Field
                   <netzob.Model.Vocabulary.Field.Field>`,
                   or :class:`Symbol
                   <netzob.Model.Vocabulary.Symbol.Symbol>`,
                   or :class:`AbstractVariable
                   <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`,
                   or :class:`AbstractType
                   <netzob.Model.Vocabulary.Types.AbstractType.AbstractType>`

        Each type have 4 common parameters, described in the following table:

        .. tabularcolumns:: |p{3cm}|p{10cm}|

        ==========  =============================================================
          Option                          Description
        ==========  =============================================================
        mode        The fuzzing strategy, which can be either:

                    * ``MutatorMode.MUTATE``: in this mode, the specialization process generates a legitimate message from a symbol, then some mutations are applied on it.
                    * ``MutatorMode.GENERATE``: in this mode, the fuzzing component directly produces a random message.

                    Default value is :attr:`MutatorMode.GENERATE`.

        generator   The underlying generator (:class:`iter`) used to produce pseudo-random or deterministic values.

                    Default generator is :attr:`NG_mt19937` from the :class:`randomstate` module.

        seed        An integer (:class:`int`) used to initialize the underlying generator.

                    Default value is :attr:`SEED_DEFAULT` = 10.

        counterMax  An integer (:class:`int`) used to limit the number of mutations.

                    Defaults value is :attr:`COUNTER_MAX_DEFAULT` = 65536.
        ==========  =============================================================

        Each type have specific parameters, described in the following table:

        .. tabularcolumns:: |p{2cm}|p{3cm}|p{8cm}|

        ==========  =============  =================================================
           Type        Option                      Description   
        ==========  =============  =================================================
        Integer     interval       The scope of values to generate.

                                   * If set to :attr:`MutatorInterval.DEFAULT_INTERVAL`, the values will be generated between the min and max values of the domain.
                                   * If set to :attr:`MutatorInterval.FULL_INTERVAL`, the values will be generated in [0, 2^N-1], where N is the bitsize (storage) of the field.
                                   * If it is a tuple of integers (min, max), the values will be generate between min and max.

                                   Default value is :attr:`MutatorInterval.DEFAULT_INTERVAL`.

        ..          bitsize        The size in bits of the memory on which the generated values have to be encoded.
                                   It is only used with a determinist generator.

                                   Default value is `None`, which indicates to use the unit size set in the field domain.

        String      endchar        
        ..          interval
        ..          lengthBitSize
        ..          naughtStrings
        Raw 
        HexaString
        BitArray
        Timestamp
        IPv4
        Alt
        Agg
        Repeat
        ==========  =============  =================================================

        """

        if isinstance(key, type):

            # Update default Mutator parameters for the associated type
            for t in self.mappingTypesMutators:
                if issubclass(key, t):  # Use issubclass() to handle cases where partial() is used (e.g. on Integer types)
                    mutator, mutator_default_parameters = self.mappingTypesMutators[t]
                    mutator_default_parameters.update(kwargs)
                    self.mappingTypesMutators[t] = mutator, mutator_default_parameters
                    break
            else:
                raise TypeError("Unsupported type for key: '{}'".format(type(key)))

        elif isinstance(key, (AbstractField, AbstractVariable)):

            self.mappingFieldsMutators[key] = kwargs
            self._normalize_mappingFieldsMutators()

        else:
            raise TypeError("Unsupported type for key: '{}'".format(type(key)))

    def unset(self, key):
        r"""The method :meth:`unset <.Fuzz.set>` deactivates the fuzzing for a
        symbol, a field or a variable. It is not possible to unset the
        fuzzing on a type.

        The :meth:`unset <.Fuzz.set>` method expects some parameters:

        :param key: The targeted object (either a symbol, a field or a
                    variable) (required).
        :type key: :class:`Field
                   <netzob.Model.Vocabulary.Field.Field>`,
                   or :class:`Symbol
                   <netzob.Model.Vocabulary.Symbol.Symbol>`,
                   or :class:`AbstractVariable
                   <netzob.Model.Vocabulary.Domain.Variables.AbstractVariable.AbstractVariable>`.

        """

        keys_to_remove = []
        # Handle case where k is a Variable -> nothing to do
        if isinstance(key, AbstractVariable):
            keys_to_remove.append(key)

        # Handle case where k is a Field containing sub-Fields -> we retrieve all its field variables
        elif isinstance(key, Field) and len(key.fields) > 0:
            subfields = key.fields
            keys_to_remove.append(key)
            for f in subfields:
                keys_to_remove.append(f.domain)

        # Handle case where k is a Field -> retrieve the associated variable
        elif isinstance(key, Field):
            keys_to_remove.append(key.domain)

        # Handle case where k is a Symbol -> we retrieve all its field variables
        elif isinstance(key, Symbol):
            subfields = key.getLeafFields(includePseudoFields=True)
            keys_to_remove.append(key)
            for f in subfields:
                keys_to_remove.append(f.domain)
        else:
            raise Exception("Key must be a Symbol, a Field or a Variable"
                            ", but not a '{}'".format(type(key)))

        # Update keys
        for old_key in keys_to_remove:
            if old_key in self.mappingFieldsMutators.keys():
                self.mappingFieldsMutators.pop(old_key)

    def get(self, key):
        if isinstance(key, type):
            # We return the associated mutator class
            if key in self.mappingTypesMutators:
                return self.mappingTypesMutators[key]
            else:
                return None
        elif isinstance(key, (AbstractField, AbstractVariable)) or isinstance(key, str):
            # We return the associated mutator instance
            if key in self.mappingFieldsMutators:
                return self.mappingFieldsMutators[key]
            else:
                return None
        else:
            raise TypeError("Unsupported type for key: '{}'".format(type(key)))

    @staticmethod
    def _retrieveDefaultMutator(domain, mapping, **kwargs):
        """Instanciate and return the default mutator according to the
        provided domain.

        """

        mutator = None
        mutator_default_parameters = {}
        for t in mapping:

            # Handle mutators for node variables (such as Repeat, Alt and Agg)
            if isinstance(domain, t):
                mutator, mutator_default_parameters = mapping[t]
                break

            # Handle mutators for leaf variables
            else:
                # Two type checks are made here, in order to handle cases where partial() is used (e.g. on Integer types)
                if type(getattr(domain, 'dataType', None)) == t or isinstance(getattr(domain, 'dataType', None), t):
                    mutator, mutator_default_parameters = mapping[t]
                    break
        else:
            raise Exception("Cannot find a default Mutator for the domain '{}'.".format(domain))

        # Update default Mutator parameters with explicitly provided parameters
        mutator_default_parameters.update(kwargs)

        # Instanciate the mutator
        mutatorInstance = mutator(domain, **mutator_default_parameters)

        return mutatorInstance

    def _normalize_mappingFieldsMutators(self):
        """Normalize the fuzzing configuration.

        Fields described with field name are converted into field
        object, and then all key elements are converted into
        variables.

        """

        # Normalize fuzzing keys
        self._normalizeKeys()

        # Normalize fuzzing values
        self._normalizeValues()

        # Second loop, to handle cases where domains are complex (Alt, Agg or Repeat)
        new_keys = {}
        for k, v in self.mappingFieldsMutators.items():
            new_keys[k] = v
            if isinstance(k, AbstractVariableNode):
                new_keys.update(self._propagateMutation(k, v))
        self.mappingFieldsMutators.update(new_keys)

        # Second loop to normalize fuzzing values, after handling complex domains (that may have added news keys:values)
        self._normalizeValues()

    def _normalizeKeys(self):
        # Normalize fuzzing keys
        new_keys = {}
        keys_to_remove = []
        for k, v in self.mappingFieldsMutators.items():

            # Handle case where k is a Variable -> nothing to do
            if isinstance(k, AbstractVariable):
                pass

            # Handle case where k is a Field containing sub-Fields -> we retrieve all its field variables
            elif isinstance(k, Field) and len(k.fields) > 0:
                subfields = k.fields
                keys_to_remove.append(k)
                for f in subfields:
                    # We check if the variable is not already present in the variables to mutate
                    if f.domain not in self.mappingFieldsMutators.keys():
                        new_keys[f.domain] = v

            # Handle case where k is a Field -> retrieve the associated variable
            elif isinstance(k, Field):
                keys_to_remove.append(k)
                new_keys[k.domain] = v

            # Handle case where k is a Symbol -> we retrieve all its field variables
            elif isinstance(k, Symbol):
                subfields = k.getLeafFields(includePseudoFields=True)
                keys_to_remove.append(k)
                for f in subfields:
                    # We check if the variable is not already present in the variables to mutate
                    if f.domain not in self.mappingFieldsMutators.keys():
                        new_keys[f.domain] = v

            else:
                raise Exception("Fuzzing keys must contain Symbols, Fields or Variables"
                                ", but not a '{}'".format(type(k)))

        # Update keys
        for old_key in keys_to_remove:
            self.mappingFieldsMutators.pop(old_key)
        self.mappingFieldsMutators.update(new_keys)

    def _normalizeValues(self):
        # Normalize fuzzing values
        keys_to_update = {}
        keys_to_remove = []

        from netzob.Fuzzing.Mutator import Mutator
        for k, v in self.mappingFieldsMutators.items():

            # If the value is already a Mutator instance -> we do nothing
            if isinstance(v, Mutator):
                pass
            # Else, we instanciate the default Mutator according to the type of the object
            else:
                mut_inst = Fuzz._retrieveDefaultMutator(domain=k, mapping=Fuzz.mappingTypesMutators, **v)
                keys_to_update[k] = mut_inst

        # Update keys
        for old_key in keys_to_remove:
            self.mappingFieldsMutators.pop(old_key)
        self.mappingFieldsMutators.update(keys_to_update)

    def _propagateMutation(self, variable, mutator):
        """This method aims at propagating the fuzzing to the children of a
        complex variable (such as Repeat, Alt or Agg). The propagation
        strategy is included in the mutator associated to the parent
        variable.
        """

        tmp_new_keys = {}

        if isinstance(variable, Repeat) and isinstance(mutator, RepeatMutator) and mutator.mutateChild:

            # We check if the variable is not already present in the variables to mutate
            if variable.children[0] not in self.mappingFieldsMutators.keys():
                mut_inst = Fuzz._retrieveDefaultMutator(domain=variable.children[0], mapping=mutator.mappingTypesMutators)
                tmp_new_keys[variable.children[0]] = mut_inst

                # Propagate mutation to the child if it is a complex domain
                if isinstance(variable.children[0], AbstractVariableNode):
                    tmp_new_keys.update(self._propagateMutation(variable.children[0], mut_inst))

        elif isinstance(variable, Alt) and isinstance(mutator, AltMutator) and mutator.mutateChild:

            for child in variable.children:
                # We check if the variable is not already present in the variables to mutate
                if child not in self.mappingFieldsMutators.keys():
                    mut_inst = Fuzz._retrieveDefaultMutator(domain=child, mapping=mutator.mappingTypesMutators)
                    tmp_new_keys[child] = mut_inst

                    # Propagate mutation to the child if it is a complex domain
                    if isinstance(child, AbstractVariableNode):
                        tmp_new_keys.update(self._propagateMutation(child, mut_inst))

        elif isinstance(variable, Agg) and isinstance(mutator, AggMutator) and mutator.mutateChild:

            for child in variable.children:
                # We check if the variable is not already present in the variables to mutate
                if child not in self.mappingFieldsMutators.keys():
                    mut_inst = Fuzz._retrieveDefaultMutator(domain=child, mapping=mutator.mappingTypesMutators)
                    tmp_new_keys[child] = mut_inst

                    # Propagate mutation to the child if it is a complex domain
                    if isinstance(child, AbstractVariableNode):
                        tmp_new_keys.update(self._propagateMutation(child, mut_inst))

        return tmp_new_keys


    ## PROPERTIES ##

    @property
    def counterMax(self):
        return Mutator.globalCounterMax

    @counterMax.setter
    def counterMax(self, counterMax):
        Mutator.globalCounterMax = counterMax
