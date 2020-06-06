# This file is part of Optcom.
#
# Optcom is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Optcom is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Optcom.  If not, see <https://www.gnu.org/licenses/>.

""".. moduleauthor:: Sacha Medaer"""

import math
from typing import Callable, List, Optional, overload, Union

import numpy as np

import optcom.utils.constants as cst
import optcom.utils.utilities as util
from optcom.parameters.abstract_parameter import AbstractParameter
from optcom.utils.callable_container import CallableContainer


class EnergySaturation(AbstractParameter):

    def __init__(self, eff_area: Union[float, np.ndarray, Callable],
                 sigma_a: Union[float, np.ndarray, Callable],
                 sigma_e: Union[float, np.ndarray, Callable],
                 overlap: Union[float, np.ndarray, Callable]) -> None:
        r"""
        Parameters
        ----------
        eff_area :
            The effective area. :math:`[\mu m^2]`  If a callable is
            provided, the variable must be angular frequency.
            :math:`[ps^{-1}]`
        sigma_a :
            The absorption cross sections. :math:`[nm^2]`  If a
            callable is provided, the variable must be angular
            frequency. :math:`[ps^{-1}]`
        sigma_e :
            The emission cross sections. :math:`[nm^2]`  If a callable
            is provided, the variable must be angular frequency.
            :math:`[ps^{-1}]`
        overlap :
            The overlap factors. If a callable is provided, the variable
            must be angular frequency. :math:`[ps^{-1}]`

        """
        self._eff_area: Union[float, np.ndarray, Callable] = eff_area
        self._sigma_a: Union[float, np.ndarray, Callable] = sigma_a
        self._sigma_e: Union[float, np.ndarray, Callable] = sigma_e
        self._overlap: Union[float, np.ndarray, Callable] = overlap
    # ==================================================================
    @overload
    def __call__(self, omega: float) -> float: ...
    # ------------------------------------------------------------------
    @overload
    def __call__(self, omega: np.ndarray) -> np.ndarray: ...
    # ------------------------------------------------------------------
    def __call__(self, omega):
        """Compute the energy saturation.

        Parameters
        ----------
        omega :
            The angular frequency. :math:`[rad\cdot ps^{-1}]`

        Returns
        -------
        :
            The value of the energy saturation. :math:`[J]`

        """
        fct = CallableContainer(EnergySaturation.calc_energy_saturation,
                                [omega, self._eff_area, self._sigma_a,
                                 self._sigma_e, self._overlap])

        return fct(omega)
    # ==================================================================
    @overload
    @staticmethod
    def calc_energy_saturation(omega: float, eff_area: float, sigma_a: float,
                               sigma_e: float, overlap: float) -> float: ...
    # ------------------------------------------------------------------
    @overload
    @staticmethod
    def calc_energy_saturation(omega: np.ndarray, eff_area: np.ndarray,
                               sigma_a: np.ndarray, sigma_e: np.ndarray,
                               overlap: np.ndarray) -> np.ndarray: ...
    # ------------------------------------------------------------------
    @staticmethod
    def calc_energy_saturation(omega, eff_area, sigma_a, sigma_e, overlap):
        r"""Calculate the energy saturation.

        Parameters
        ----------
        omega :
            The angular frequency. :math:`[rad\cdot ps^{-1}]`
        eff_area :
            The effective area. :math:`[\mu m^2]`
        sigma_a :
            The absorption cross sections. :math:`[nm^2]`
        sigma_e :
            The emission cross sections. :math:`[nm^2]`
        overlap :
            The overlap factors.

        Returns
        -------
        :
            Value of the energy saturation. :math:`[J]`

        Notes
        -----

        .. math:: E_{sat} = \frac{A_{eff}h\omega_0}{2\pi\Gamma
                  \big(\sigma_e(\lambda_0)+\sigma_a(\lambda_0)\big)}

        """
        eff_area *= 1e6 # um^2 -> nm^2
        num = eff_area * cst.HBAR * omega
        den = overlap * (sigma_a+sigma_e)
        if (isinstance(den, float)):
            if (den):
                res = num / den
            else:
                res = math.inf
        else:
            res = np.divide(num, den, where=den!=0)
            res[den==0] = np.inf
            res *= 1e6 # nm^2 kg ps^{-2} -> m^2 kg s^{-2} = J

        return res



if __name__ == "__main__":
    """Plot energy saturation as a function of the wavelength.
    This piece of code is standalone, i.e. can be used in a separate
    file as an example.
    """

    import math
    from typing import List

    import numpy as np

    import optcom.utils.constants as cst
    import optcom.utils.plot as plot
    from optcom.domain import Domain
    from optcom.parameters.fiber.absorption_section import AbsorptionSection
    from optcom.parameters.fiber.effective_area import EffectiveArea
    from optcom.parameters.fiber.emission_section import EmissionSection
    from optcom.parameters.fiber.energy_saturation import EnergySaturation
    from optcom.parameters.fiber.numerical_aperture import NumericalAperture
    from optcom.parameters.fiber.overlap_factor import OverlapFactor
    from optcom.parameters.fiber.v_number import VNumber
    from optcom.parameters.refractive_index.sellmeier import Sellmeier

    medium: str = "sio2"
    dopant: str = "yb"
    A_doped: float = cst.PI*25.0
    # With float
    omega: float = Domain.lambda_to_omega(1000)
    core_radius: float = 5.0
    n_core: Sellmeier = Sellmeier(medium)
    n_clad: float = 1.44
    NA_inst: NumericalAperture = NumericalAperture(n_core, n_clad)
    v_nbr_inst: VNumber = VNumber(NA_inst, core_radius)
    A_eff_inst: EffectiveArea = EffectiveArea(v_nbr_inst, core_radius)
    of_inst: OverlapFactor = OverlapFactor(A_eff_inst, A_doped)
    sigma_a_inst: AbsorptionSection = AbsorptionSection(dopant=dopant,
                                                        medium=medium)
    T: float = 293.1
    sigma_e_inst: EmissionSection = EmissionSection(dopant=dopant,
                                                    medium=medium, T=T,
                                                    sigma_a=sigma_a_inst)
    en_sat: EnergySaturation = EnergySaturation(A_eff_inst, sigma_a_inst,
                                                sigma_e_inst, of_inst)
    print(en_sat(omega))
    A_eff: float = A_eff_inst(omega)
    sigma_a: float = sigma_a_inst(omega)
    sigma_e: float = sigma_e_inst(omega)
    of: float = of_inst(omega)
    print(EnergySaturation.calc_energy_saturation(omega, A_eff, sigma_a,
                                                  sigma_e, of))
    # With np.ndarray
    lambdas: np.ndarray = np.linspace(900, 1050, 1000)
    omegas: np.ndarray = Domain.lambda_to_omega(lambdas)
    ens_sat: np.ndarray = en_sat(omegas)
    plot_titles: List[str] = ["Energy saturation as a function of the "
                              "wavelenght for Ytterbium doped fiber."]

    plot.plot2d([lambdas], [ens_sat], x_labels=['Lambda'],
                y_labels=[r'Energy saturation, $\,E_{sat}\,(J)$'],
                split=True, plot_colors=['red'], plot_titles=plot_titles,
                plot_linestyles=['-.'], opacity=[0.0])
