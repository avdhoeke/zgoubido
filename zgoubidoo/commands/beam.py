"""Zgoubidoo beam.

"""
from __future__ import annotations
from typing import Optional, Union
import os
import numpy as np
import pandas as pd
from zgoubidoo import _Q
from zgoubidoo.commands import CommandType as _CommandType
from zgoubidoo.commands import Command as _Command
from zgoubidoo.commands import ParticuleType as _ParticuleType
from zgoubidoo.commands import Proton as _Proton
from zgoubidoo.commands import Objet2 as _Objet2
from zgoubidoo.commands import ObjetType as _ObjetType
from zgoubidoo.kinematics import Kinematics as _Kinematics
from ..input import ParametricMapping as _ParametricMapping
from ..input import MappedParametersListType as _MappedParametersListType


class ZgoubidooBeamException(Exception):
    """Exception raised for errors when running Zgoubi."""

    def __init__(self, m):
        self.message = m


class BeamType(_CommandType):
    """Type system for Objet types."""
    pass


class Beam(_Command, metaclass=BeamType):
    """
    Beam
    """
    PARAMETERS = {
        'OBJET': ('Objet2', 'Active objet representation.'),
        'SLICE': (0, "Active slice identifier. Note: this is the number of slices, but the active slice number."),
        'REFERENCE': (0, ""),
    }
    """Parameters of the command, with their default value, their description and optinally an index used by other 
    commands (e.g. fit)."""

    def __str__(self) -> str:
        if self.REFERENCE == 1:
            return str(self.objet.clear())
        else:
            return str(self.objet)

    def post_init(self,
                  distribution: Optional[pd.DataFrame] = None,
                  particle: _ParticuleType = _Proton,
                  objet: _ObjetType = _Objet2,
                  kinematics: Union[_Kinematics, float, _Q] = None,
                  slices: int = 1,
                  *args,
                  **kwargs):
        """

        Args:
            distribution:
            particle:
            objet:
            kinematics:
            slices:
            *args:
            **kwargs:

        Returns:

        """
        self._particle: _ParticuleType = particle
        self._objet: _ObjetType = objet
        if not isinstance(kinematics, _Kinematics):
            kinematics = _Kinematics(kinematics)
        self._kinematics: _Kinematics = kinematics
        self._slices: int = slices
        self._distribution: Optional[pd.DataFrame] = None
        self._initialize_distribution(distribution, *args, **kwargs)

    def _initialize_distribution(self, distribution: pd.DataFrame = None, *args, **kwargs):
        """Try setting the internal pandas.DataFrame with a distribution.

        Args:
            distribution:
        """
        if distribution is not None:
            self._distribution = distribution
        else:
            try:
                self._distribution = pd.DataFrame(args[0])
            except (IndexError, ValueError):
                if kwargs.get("filename") is not None:
                    self._distribution = Beam.generate_from_file(kwargs.get('filename'), path=kwargs.get('path', '.'))
                else:
                    return
        if self._distribution.shape[0] == 0:
            raise ZgoubidooBeamException("Trying to initialize a beam distribution with invalid number of particles.")

    def clear(self) -> Beam:
        """

        Returns:

        """
        self._distribution = None
        return self

    @property
    def slices(self):
        """Number of slices."""
        return self._slices

    @slices.setter
    def slices(self, n):
        self._slices = n

    @property
    def active_slice(self):
        """

        Args:
            n:

        Returns:

        """
        try:
            n_tot = len(self._distribution)
        except TypeError:
            return None
        n_slices = int(np.floor(n_tot / self._slices))
        d = self._distribution.iloc[self.SLICE * n_slices:(self.SLICE + 1) * n_slices]
        d.columns = ['Y', 'T', 'Z', 'P', 'D']
        if len(d) == 0:
            return None
        else:
            return d

    @property
    def objet(self):
        """
        TODO

        Return:

        """
        _ = self._objet(self.LABEL1, BORO=self._kinematics.brho)
        _.add(self.active_slice)
        return _

    @property
    def mappings(self) -> _MappedParametersListType:
        """TODO"""
        if self.REFERENCE == 1:
            return [{f"{self.LABEL1}.REFERENCE": 1}]
        else:
            return _ParametricMapping(
                [
                    {
                        f"{self.LABEL1}.SLICE": list(range(0, self._slices))
                    },
                ]
            ).combinations

    @property
    def distribution(self) -> pd.DataFrame:
        """The beam distribution."""
        return self._distribution

    @property
    def particle(self) -> ParticuleType:
        """The beam's particle type."""
        return self._particle

    @property
    def kinematics(self):
        """The beam's kinematics properties."""
        return self._kinematics

    def from_file(self, file: str, n: int = None, path: str = '.') -> Beam:
        """

        Args:
            file:
            n:
            path:

        Returns:

        """
        self._initialize_distribution(Beam.generate_from_file(file, path, n))
        return self

    def from_5d_sigma_matrix(self, n, **kwargs) -> Beam:
        """
        Initialize a beam with a 5D particle distribution from a Sigma matrix.

        Args:
            n:
            **kwargs:

        Returns:

        """
        distribution = Beam.generate_from_5d_sigma_matrix(n, **kwargs)
        self._initialize_distribution(pd.DataFrame(distribution))
        return self

    def from_twiss_parameters(self, n, **kwargs) -> Beam:
        """
        Initialize a beam with a 5D particle distribution from Twiss parameters.

        Args:
            n:
            **kwargs:

        Returns:

        """
        keys = {'X', 'PX', 'Y', 'PY', 'DPP', 'DPPRMS', 'BETAX', 'ALPHAX', 'BETAY', 'ALPHAY', 'EMITX', 'EMITY'}
        if any([k not in keys for k in kwargs.keys()]):
            raise ZgoubidooBeamException("Invalid argument for a twiss distribution.")
        betax = kwargs.get('BETAX', 1)
        alphax = kwargs.get('ALPHAX', 0)
        gammax = (1+alphax**2)/betax
        betay = kwargs.get('BETAY', 1)
        alphay = kwargs.get('ALPHAY', 0)
        gammay = (1 + alphay ** 2) / betay

        self.from_5d_sigma_matrix(n,
                                  x=kwargs.get('X', 0),
                                  px=kwargs.get('PX', 0),
                                  y=kwargs.get('Y', 0),
                                  py=kwargs.get('PY', 0),
                                  dpp=kwargs.get('DPP', 0),
                                  dpprms=kwargs.get('DPPRMS', 0),
                                  s11=betax * kwargs['EMITX'],
                                  s12=-alphax * kwargs['EMITX'],
                                  s22=gammax * kwargs['EMITX'],
                                  s33=betay * kwargs['EMITY'],
                                  s34=-alphay * kwargs['EMITY'],
                                  s44=gammay * kwargs['EMITY']
                                  )
        return self

    @staticmethod
    def generate_from_file(file: str, path: str = '.', n: Optional[int] = None) -> pd.DataFrame:
        """
        Read a beam distribution from file.

        Args:
            file:
            path:
            n:

        Returns:

        """
        return pd.read_csv(os.path.join(path, file))[:n]

    @staticmethod
    def generate_from_5d_sigma_matrix(n: int,
                                      x: float = 0,
                                      px: float = 0,
                                      y: float = 0,
                                      py: float = 0,
                                      dpp: float = 0,
                                      s11: float = 0,
                                      s12: float = 0,
                                      s13: float = 0,
                                      s14: float = 0,
                                      s15: float = 0,
                                      s22: float = 0,
                                      s23: float = 0,
                                      s24: float = 0,
                                      s25: float = 0,
                                      s33: float = 0,
                                      s34: float = 0,
                                      s35: float = 0,
                                      s44: float = 0,
                                      s45: float = 0,
                                      dpprms: float = 0,
                                      matrix=None,
                                      ):
        """

        Args:
            n:
            x:
            px:
            y:
            py:
            dpp:
            s11:
            s12:
            s13:
            s14:
            s15:
            s22:
            s23:
            s24:
            s25:
            s33:
            s34:
            s35:
            s44:
            s45:
            dpprms:
            matrix:

        Returns:

        """
        # For performance considerations, see
        # https://software.intel.com/en-us/blogs/2016/06/15/faster-random-number-generation-in-intel-distribution-for-python
        try:
            import numpy.random_intel
            generator = numpy.random_intel.multivariate_normal
        except ModuleNotFoundError:
            import numpy.random
            generator = numpy.random.multivariate_normal

        s21 = s12
        s31 = s13
        s32 = s23
        s41 = s14
        s42 = s24
        s43 = s34
        s51 = s15
        s52 = s25
        s53 = s35
        s54 = s45
        s55 = dpprms ** 2

        if matrix is not None:
            assert matrix.shape == (5, 5)
            return generator(
                [x, px, y, py, dpp],
                matrix,
                int(n)
            )
        else:
            return generator(
                [x, px, y, py, dpp],
                np.array([
                    [s11, s12, s13, s14, s15],
                    [s21, s22, s23, s24, s25],
                    [s31, s32, s33, s34, s35],
                    [s41, s42, s43, s44, s45],
                    [s51, s52, s53, s54, s55]
                ]),
                int(n)
            )
