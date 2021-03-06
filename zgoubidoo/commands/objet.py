"""Zgoubi commands for the generation of Objet's.

The description of the object, i.e., initial coordinates of the ensemble of particles, must be the first procedure
in the zgoubi input data file, zgoubi.dat.

Several types of automatically generated objects are available, they are described in the following pages and
include:

    - non-random object, with various distributions : individual particles, grids, object for MATRIX, etc.
    - Monte Carlo distribution (see MCObjet), with various distributions as well : 6-D window, ellipsoids, etc.

A recurrent quantity appearing in these procedures is IMAX, the number of particles to be ray-traced.
The maximum value allowed for IMAX can be changed at leisure in the include file `MAXTRA.H` where it is defined
(that requires re-compiling zgoubi).
"""

import numpy as _np
from .commands import Command as _Command
from .commands import CommandType as _CommandType
from .commands import ZgoubidooException as _ZgoubidooException
from .. import ureg as _ureg


class ObjetType(_CommandType):
    """Type system for Objet types."""
    pass


class Objet(_Command, metaclass=ObjetType):
    """Generation of an object.


    """
    KEYWORD = 'OBJET'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'BORO': (1.0 * _ureg.kilogauss * _ureg.cm, 'Reference magnetic rigidity.'),
    }

    def __str__(s):
        return f"""
        {super().__str__().rstrip()}
        {s.BORO.to("kilogauss * cm").magnitude:.12e}
        """

    def __init__(self, label1='', label2='', *params, **kwargs):
        super().__init__(label1, label2, Objet.PARAMETERS, self.PARAMETERS, *params, **kwargs)


class Objet1(Objet):
    """Objet with initial coordinates drawn from a regular grid"""
    PARAMETERS = {
        'KOBJ': 1,
        'K2': 0,
        'IY': (1, 'Total number of points in +- Y'),
        'IT': (1, 'Total number of points in +- T'),
        'IZ': (1, 'Total number of points in +- Z (or +Z only if K2=01)'),
        'IP': (1, 'Total number of points in +- P (or +P only if K2=01)'),
        'IX': (1, 'Total number of points in +- X'),
        'ID': (1, 'Total number of points in +- D'),
        'PY': (0.1 * _ureg.centimeter, 'Step size in Y'),
        'PT': (0.1 * _ureg.milliradian, 'Step size in T'),
        'PZ': (0.1 * _ureg.centimeter, 'Step size in Z'),
        'PP': (0.1 * _ureg.milliradian, 'Step size in P'),
        'PX': (0.1 * _ureg.centimeter, 'Step size in X'),
        'PD': (0.1, 'Step size in Delta(BRHO)/BORO'),
        'YR': (0.0 * _ureg.centimeter, 'Reference Y'),
        'TR': (0.0 * _ureg.milliradian, 'Reference T'),
        'ZR': (0.0 * _ureg.centimeter, 'Reference Z'),
        'PR': (0.0 * _ureg.milliradian, 'Reference P'),
        'XR': (0.0 * _ureg.centimeter, 'Reference X'),
        'DR': (1.0, 'Reference D'),
    }

    def __str__(s) -> str:
        return f"""
        {super().__str__().rstrip()}
        {s.KOBJ}.0{s.K2}
        {s.IY} {s.IT} {s.IZ} {s.IP} {s.IX} {s.ID}
        {s.PY.to('centimeter').magnitude:.12e} {s.PT.to('milliradian').magnitude:.12e} {s.PZ.to('centimeter').magnitude:.12e} {s.PP.to('milliradian').magnitude:.12e} {s.PX.to('centimeter').magnitude:.12e} {s.PD:.12e}
        {s.YR.to('centimeter').magnitude:.12e} {s.TR.to('milliradian').magnitude:.12e} {s.ZR.to('centimeter').magnitude:.12e} {s.PR.to('milliradian').magnitude:.12e} {s.XR.to('centimeter').magnitude:.12e} {s.DR:.12e}
        """


class Objet2(Objet):
    """Objet with all initial coordinates entered explicitely.

    This object type can be used to simulate a bunch with an explicit list of coordinates. That's the method Zgoubidoo
    uses when tracking bunches.

    Examples:
        >>> zi = Input()
        >>> objet = Objet2()
        >>> objet.add()
        >>> zi += objet
        >>> zi
        >>> objet.clear()
        >>> objet
    """
    PARAMETERS = {
        'KOBJ': (2, ''),
        'K2': (0, ''),
        'IDMAX': (1, ''),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def post_init(self, **kwargs):
        """Post initialization routine."""
        self._PARTICULES = None

    @property
    def IMAX(self):
        """

        Returns:

        """
        return self.PARTICULES.shape[0]

    @property
    def IEX(self):
        """

        Returns:

        """
        return self.PARTICULES[:, 6]

    @property
    def PARTICULES(self):
        """The particles list."""
        if isinstance(self._PARTICULES, list):
            self._PARTICULES = _np.array(self._PARTICULES).reshape(1, 7)
        if self._PARTICULES is None:
            self._PARTICULES = _np.zeros((1, 7))
            self._PARTICULES[:, 5] = 1.0  # D = 1
            self._PARTICULES[:, 6] = 1.0  # IEX
        return self._PARTICULES

    def clear(self):
        """Reset the object's content, remove all particles."""
        self._PARTICULES = None
        return self

    def __iadd__(self, other):
        self.add(other)
        return self

    def add(self, p):
        """

        Args:
            p:

        Returns:

        """
        if self._PARTICULES is None:
            if not hasattr(p, 'columns'):
                self._PARTICULES = p
            elif list(p.columns) == ['Y', 'T', 'Z', 'P', 'D']:
                p = p.copy()
                p['X'] = 0.0
                p['IEX'] = 1.0
                p['D'] += 1.0
                self._PARTICULES = p[['Y', 'T', 'Z', 'P', 'X', 'D', 'IEX']].values
        else:
            self._PARTICULES = _np.append(self._PARTICULES, p, axis=0)
        return self

    def __str__(s) -> str:
        c = f"""
        {super().__str__().rstrip()}
        {s.KOBJ}.0{s.K2}
        {s.IMAX} {s.IDMAX}
        """
        for p in s.PARTICULES[:, 0:6]:
            c += f"""
        {p[0]:.12e} {p[1]:.12e} {p[2]:.12e} {p[3]:.12e} {p[4]:.12e} {p[5]:.12e} A
        """.lstrip()
        c += " ".join(map(lambda x: f"{int(x):d}", s.IEX)) + "\n"
        return c


class Objet3(Objet):
    """

    Examples:
        Test
    """

    PARAMETERS = {
        'KOBJ': 3,
        'NN': 1,  # 00 to store the file as '[b_]zgoubi.fai'
        'IT1': 1,
        'IT2': 1,
        'ITSTEP': 1,
        'IP1': 1,
        'IP2': 1,
        'IPSTEP': 1,
        'YF': 0,
        'TF': 0,
        'ZF': 0,
        'PF': 0,
        'XF': 0,
        'DF': 0,
        'TAG': '*',  # No effect if '*'
        'YR': 0,
        'ZR': 0,
        'PR': 0,
        'XR': 0,
        'DR': 0,
        'InitC': 0,
        'FNAME': 'zgoubi.fai',  # (NN in KOBJ=3.NN determines storage FORMAT)
    }

    def __str__(s) -> str:
        if s.NN == 1:
            return f"""
            {super().__str__().rstrip()}
            {s.KOBJ}.{s.NN}
            {s.IT1} {s.IT2} {s.ITSTEP}
            {s.IP1} {s.IP2} {s.IPSTEP}
            {s.YF:.12e} {s.TF:.12e} {s.ZF:.12e} {s.PF:.12e} {s.XF:.12e} {s.DF:.12e} {s.TF:.12e} {s.TAG:.12e}
            {s.YR:.12e} {s.TR:.12e} {s.ZR:.12e} {s.PR:.12e} {s.XR:.12e} {s.DR:.12e} {s.TR:.12e}
            {s.InitC}
            {s.FNAME}
           """
        else:
            raise _ZgoubidooException("NN != 1 not supported")


class Objet4(Objet):
    pass

    PARAMETERS = {
        'KOBJ' : 3,
        'NN' : 1,  # 00 to store the file as '[b_]zgoubi.fai'
        'IT1' : 1,
        'IT2': 1,
        'ITSTEP': 1,
        'IP1': 1,
        'IP2': 1,
        'IPSTEP': 1,
        'YF': 0,
        'TF': 0,
        'ZF': 0,
        'PF': 0,
        'XF': 0,
        'DF': 0,
        'TF': 0,
        'TAG': '*', # No effect if '*'
        'YR': 0,
        'TR': 0,
        'ZR': 0,
        'PR': 0,
        'XR': 0,
        'DR': 0,
        'TR': 0,
        'InitC': 0,
        'FNAME': 'zgoubi.fai', #(NN in KOBJ=3.NN determines storage FORMAT)
    }

    def __str__(s) -> str:
        if s.NN == 1:
            return f"""
            {super().__str__().rstrip()}
            {s.IT1} {s.IT2} {s.ITSTEP}
            {s.IP1} {s.IP2} {s.IPSTEP}
            {s.YF:.12e} {s.TF:.12e} {s.ZF:.12e} {s.PF:.12e} {s.XF:.12e} {s.DF:.12e} {s.TF:.12e} {s.TAG:.12e}
            {s.YR:.12e} {s.TR:.12e} {s.ZR:.12e} {s.PR:.12e} {s.XR:.12e} {s.DR:.12e} {s.TR:.12e}
            {s.InitC}
            {s.FNAME}
           """
        else:
            raise _ZgoubidooException("NN != 1 not supported")


class Objet5(Objet):
    """Generation of 11 particles, or 11*NN if I ≥ 2 (for use with MATRIX, IORD = 1).

    Examples:
        test
    """

    PARAMETERS = {
        'KOBJ': 5,
        'NN': 1,
        'PY': 1e-3,
        'PT': 1e-3,
        'PZ': 1e-3,
        'PP': 1e-3,
        'PX': 1e-3,
        'PD': 1e-3,
        'YR': 0,
        'TR': 0,
        'ZR': 0,
        'PR': 0,
        'XR': 0,
        'DR': 1,
        'ALPHA_Y': 0,
        'BETA_Y': 0,
        'ALPHA_Z': 0,
        'BETA_Z': 0,
        'ALPHA_X': 0,
        'BETA_X': 0,
        'D_Y': 0,
        'D_YP': 0,
        'D_Z': 0,
        'D_ZP': 0,
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(s) -> str:
        command = []
        c = f"""
        {super().__str__().rstrip()}
        {s.KOBJ}.0{s.NN}
        {s.PY:.12e} {s.PT:.12e} {s.PZ:.12e} {s.PP:.12e} {s.PX:.12e} {s.PD:.12e}
        {s.YR:.12e} {s.TR:.12e} {s.ZR:.12e} {s.PR:.12e} {s.XR:.12e} {s.DR:.12e}
        """
        command.append(c)
        if s.NN == 1:
            c = f"""
            {s.ALPHA_Y:.12e} {s.BETA_Y:.12e} {s.ALPHA_Z:.12e} {s.BETA_Z:.12e} {s.ALPHA_X:.12e} {s.BETA_X:.12e}
            {s.D_Y:.12e} {s.D_YP:.12e} {s.D_Z:.12e} {s.D_ZP:.12e}
            """
            command.append(c)
        elif s.NN in range(2, 99):
            c = f"""
            {s.YR:.12e} {s.TR:.12e} {s.ZR:.12e} {s.PR:.12e} {s.XR:.12e} {s.DR:.12e}
            """
            command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command)) + '\n'


class Objet6(Objet):
    """Generation of 61 particles.

    Examples:
        >>> 1 + 1 # TODO
    """

    PARAMETERS = {
        'KOBJ': 6,
        'NN': 1,
        'PY': 1e-3,
        'PT': 1e-3,
        'PZ': 1e-3,
        'PP': 1e-3,
        'PX': 1e-3,
        'PD': 1e-3,
        'YR': 6,
        'TR': 6,
        'ZR': 6,
        'PR': 6,
        'XR': 6,
        'DR': 1,
    }

    def __str__(s) -> str:
        command = []
        c = f"""
        {super().__str__().rstrip()}
        {s.KOBJ}.0{s.NN}
        {s.PY:.12e} {s.PT:.12e} {s.PZ:.12e} {s.PP:.12e} {s.PX:.12e} {s.PD:.12e}
        {s.YR:.12e} {s.TR:.12e} {s.ZR:.12e} {s.PR:.12e} {s.XR:.12e} {s.DR:.12e}
        """
        command.append(c)

        return ''.join(map(lambda _: _.rstrip(), command)) + '\n'


class Objet7(Objet):
    """

    """
    pass


class Objet8(Objet):
    """"""

    pass


class ObjetA(_Command):
    """Object from Monte-Carlo simulation of decay reaction.

    Examples:
        Test
    """
    KEYWORD = 'OBJETA'
    """Keyword of the command used for the Zgoubi input data."""

