"""Zgoubidoo's interfaces to Zgoubi commands related to particle types.

More details here. TODO
"""
from .commands import Command as _Command
from .commands import CommandType as _MetaCommand
from .. import ureg as _ureg


class ParticuleType(_MetaCommand):
    """
    TODO
    """
    def __str__(cls):
        return f"""
        '{cls.KEYWORD}' {cls.__name__.upper()}
        {cls.M.to('MeV_c2').magnitude:.12e} {cls.Q.to('coulomb').magnitude:.12e} {cls.G:.12e} {cls.tau:.12e} 0.0
        """


class Particule(_Command, metaclass=ParticuleType):
    """Particle characteristics."""
    KEYWORD = 'PARTICUL'
    """Keyword of the command used for the Zgoubi input data."""

    PARAMETERS = {
        'M': (0 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (0 * _ureg.coulomb, 'Charge of the particle.'),
        'G': (0, 'Factor'),
        'tau': (0, 'Lifetime of the particle.'),
    }

    def __init__(self, label1='', label2='', *params, **kwargs):
        if len(label1) == 0:
            label1 = self.__class__.__name__.upper()
        super().__init__(label1, label2, Particule.PARAMETERS, self.PARAMETERS, *params, **kwargs)

    def __str__(s) -> str:
        return f"""
        {super().__str__().strip()}
        {s.M.to('MeV_c2').magnitude:.12e} {s.Q.to('coulomb').magnitude:.12e} {s.G:.12e} {s.tau:.12e} 0.0
        """

    @property
    def mass(self):
        """Mass of the particle."""
        return self.M

    @property
    def charge(self):
        """Charge of the particle."""
        return self.Q

    @property
    def lifetime(self):
        """Lifetime constant of the particle."""
        return self.tau


class Electron(Particule):
    """An electron particle."""
    PARAMETERS = {
        'M': (0.5109989461 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (-1.6021766208e-19 * _ureg.coulomb, 'Charge of the particle.'),
        'G': ((-2.0023193043622 - 2) / 2, 'G factor'),
    }


class Positron(Particule):
    """A positron particle."""
    PARAMETERS = {
        'M': (0.5109989461 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (-1.6021766208e-19 * _ureg.coulomb, 'Charge of the particle.'),
        'G': ((-2.0023193043622 - 2) / 2, 'G factor'),
    }


class Muon(Particule):
    """A muon particle."""
    PARAMETERS = {
        'M': (105.6583745 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (-1.60217653e-1 * _ureg.coulomb, 'Charge of the particle.'),
        'G': ((-2.0023318418 - 2) / 2, 'G factor'),
        'tau': (2.197029e-6, 'Lifetime'),
    }


class AntiMuon(Particule):
    """An anti-muon particle."""
    PARAMETERS = {
        'M': (105.6583745 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (1.60217653e-19 * _ureg.coulomb, 'Charge of the particle.'),
        'G': ((-2.0023318418 - 2) / 2, 'G factor'),
        'tau': (2.197029e-6, 'Lifetime'),
    }


class ImmortalMuon(Muon):
    """A muon particle (no decay)."""
    PARAMETERS = dict(AntiMuon.PARAMETERS, **{
        'tau': (0.0, 'Half-life of the particle.'),
    })


class ImmortalAntiMuon(AntiMuon):
    """An anti-muon particle (no decay)."""
    PARAMETERS = dict(Muon.PARAMETERS, **{
        'tau': (0.0, 'Half-life of the particle.'),
    })


class Pion(Particule):
    """A pion particle."""
    PARAMETERS = {
        'M': (139.57018 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (1.60217653e-19 * _ureg.coulomb, 'Charge of the particle.'),
        'G': (0, 'G factor'),
        'tau': (2.6033e-8, 'Half-life of the particle.'),
    }


class Proton(Particule):
    """A proton particle."""
    PARAMETERS = {
        'M': (938.27203 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (1.602176487e-19 * _ureg.coulomb, 'Charge of the particle.'),
        'G': ((5.585694701 - 2) / 2, 'G factor'),
    }


class AntiProton(Particule):
    """An anti-proton particle."""
    PARAMETERS = {
        'M': (938.27203 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (-1.602176487e-19 * _ureg.coulomb, 'Charge of the particle.'),
        'G': ((5.585694701 - 2) / 2, 'G factor'),
    }


class HMinus(Particule):
    """An H- ion."""
    PARAMETERS = {
        'M': (938.27203 * _ureg.MeV_c2, 'Mass of the particle.'),
        'Q': (+1.602176487e-19 * _ureg.coulomb, 'Charge of the particle.'),
        'G': ((5.585694701 - 2) / 2, 'G factor'),
    }


class Ion(Particule):
    """Base class for ion particles."""
    def charge_state(self):
        """Modify the charge state of the ion."""
        # TODO
        pass


class HeliumIon(Particule):
    """A fully stripped Helium ion"""
    PARAMETERS = {
        'M': (1, ''),
        'Q': (1, ''),
        'G': (1, ''),
    }


class CarbonIon(Particule):
    """A fully stripped Carbon ion"""
    PARAMETERS = {
        'M': (1, ''),
        'Q': (1, ''),
        'G': (1, ''),
    }


class OxygenIon(Particule):
    """A fully stripped Oxygen ion"""
    PARAMETERS = {
        'M': (1, ''),
        'Q': (1, ''),
        'G': (1, ''),
    }


class LeadIon(Particule):
    """A fully stripped Lead ion"""
    PARAMETERS = {
        'M': (1, ''),
        'Q': (1, ''),
        'G': (1, ''),
    }


class SulfurIon(Particule):
    """A fully stripped Sulfur ion"""
    PARAMETERS = {
        'M': (1, ''),
        'Q': (1, ''),
        'G': (1, ''),
    }


class XenonIon(Particule):
    """A fully stripped Sulfur ion"""
    PARAMETERS = {
        'M': (1, ''),
        'Q': (1, ''),
        'G': (1, ''),
    }

