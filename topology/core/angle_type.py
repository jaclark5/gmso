import warnings
import unyt as u

from topology.core.potential import Potential
from topology.exceptions import TopologyError
from topology.utils.decorators import confirm_set_existence


class AngleType(Potential):
    """A Potential between 3-bonded partners.

    Parameters
    ----------
    name : str
    expression : str or sympy.Expression
        See `Potential` documentation for more information
    parameters : dict {str, unyt.unyt_quantity}
        See `Potential` documentation for more information
    independent vars : set of str
        See `Potential` documentation for more information
    member_types : list of topology.AtomType.name (str)
    topology: topology.core.Topology, the topology of which this angle_type is a part of, default=None
    set_ref: (str), the string name of the bookkeeping set in topology class.

    Notes
    ----
    Inherits many functions from topology.Potential:
        __eq__, _validate functions
    """

    def __init__(self,
                 name='AngleType',
                 expression='0.5 * k * (theta-theta_eq)**2',
                 parameters=None,
                 independent_variables=None,
                 member_types=None,
                 topology=None,
                 set_ref='angle_type_set'):
        if parameters is None:
            parameters = {
                'k': 1000 * u.Unit('kJ / (deg**2)'),
                'theta_eq': 180 * u.deg
            }
        if independent_variables is None:
            independent_variables = {'theta'}

        if member_types is None:
            member_types = list()

        super(AngleType, self).__init__(name=name, expression=expression,
                                        parameters=parameters, independent_variables=independent_variables,
                                        topology=topology, set_ref=set_ref)

        self._member_types = _validate_three_member_type_names(member_types)

    @property
    def member_types(self):
        return self._member_types

    @member_types.setter
    @confirm_set_existence
    def member_types(self, val):
        if self.member_types != val:
            warnings.warn("Changing an AngleType's constituent "
                          "member types: {} to {}".format(self.member_types, val))
        self._member_types = _validate_three_member_type_names(val)

    @property
    def topology(self):
        return self._topology

    @topology.setter
    def topology(self, top):
        self._topology = top
        self._set_ref = 'angle_type_set'

    def __repr__(self):
        return "<AngleType {}, id {}>".format(self.name, id(self))


def _validate_three_member_type_names(types):
    """Ensure 3 partners are involved in AngleType"""
    if len(types) != 3 and len(types) != 0:
        raise TopologyError("Trying to create an AngleType "
                            "with {} constituent types".format(len(types)))
    if not all([isinstance(t, str) for t in types]):
        raise TopologyError("Types passed to AngleType "
                            "need to be strings corresponding to AtomType names")

    return types
