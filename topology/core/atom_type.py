import warnings
import numpy as np
import sympy
import unyt as u


class AtomType(object):
    """An atom type."""

    def __init__(self,
                 name="AtomType",
                 charge=0.0,
                 nb_function='4*epsilon*((sigma/r)**12 - (sigma/r)**6)',
                 parameters={
                     'sigma': 1,
                     'epsilon': 100
                 }):

        self._name = name

        self._charge = _validate_charge(charge)

        if isinstance(parameters, dict):
            self._parameters = parameters
        else:
            raise ValueError("Please enter dictionary for parameters")

        if nb_function is None:
            self._nb_function = None
        elif isinstance(nb_function, str):
            self._nb_function = sympy.sympify(nb_function)
        elif isinstance(nb_function, sympy.Expr):
            self._nb_function = nb_function
        else:
            raise ValueError("Please enter a string, sympy expression, "
                             "or None for nb_function")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    @property
    def charge(self):
        return self._charge

    @charge.setter
    def charge(self, val):
        self._charge = _validate_charge(val)

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, newparams):
        if not isinstance(newparams, dict):
            raise ValueError("Provided parameters "
                             "{} is not a valid dictionary".format(newparams))

        self._parameters.update(newparams)
        self._validate_function_parameters()

    @property
    def nb_function(self):
        return self._nb_function

    @nb_function.setter
    def nb_function(self, function):
        # Check valid function type (string or sympy expression)
        # If func is undefined, just keep the old one
        if isinstance(function, str):
            self._nb_function = sympy.sympify(function)
        elif isinstance(function, sympy.Expr):
            self._nb_function = function
        else:
            raise ValueError("Please enter a string or sympy expression")

        self._validate_function_parameters()

    def set_nb_function(self, function=None, parameters=None):
        """ Set the nonbonded function and paramters for this atomtype

        Parameters
        ----------
        function: sympy.Expression or string
            The mathematical expression corresponding to the nonbonded potential
            If None, the function remains unchanged
        parameters: dict
            {parameter: value} in the function
            If None, the parameters remain unchanged

        Notes
        -----
        Be aware of the symbols used in the `function` and `parameters`.
        If unnecessary parameters are supplied, an error is thrown.
        If only a subset of the parameters are supplied, they are updated
            while the non-passed parameters default to the existing values
       """
        if function is not None:
            if isinstance(function, str):
                self._nb_function = sympy.sympify(function)
            elif isinstance(function, sympy.Expr):
                self._nb_function = function
            else:
                raise ValueError("Please enter a string or sympy expression")

        if parameters is not None:
            if not isinstance(parameters, dict):
                raise ValueError("Provided parameters "
                                "{} is not a valid dictionary".format(parameters))

            self._parameters.update(parameters)
            self._validate_function_parameters()

        self._validate_function_parameters()

    def _validate_function_parameters(self):
        symbols = sympy.symbols(set(self.parameters.keys()))
        if symbols != self.nb_function.free_symbols:
            extra_syms = symbols ^ self.nb_function.free_symbols
            raise ValueError("NB function and parameter"
                             " symbols do not agree,"
                             " extraneous symbols:"
                             " {}".format(extra_syms))

    def __eq__(self, other):
        return ((self.name == other.name) &
                (np.isclose(self.charge, other.charge)) &
                (self.parameters == other.parameters) &
                (self.nb_function == other.nb_function))

    def __repr__(self):
        desc = "<AtomType {}, id {}>".format(self._name, id(self))
        return desc


def _validate_charge(charge):
    if not isinstance(charge, u.unyt_array):
        warnings.warn("Charges are assumed to be elementary charge")
        charge *= u.elementary_charge
    elif charge.units.dimensions != u.elementary_charge.units.dimensions:
        warnings.warn("Charges are assumed to be elementary charge")
        charge = charge.value * u.elementary_charge
    else:
        pass

    return charge
