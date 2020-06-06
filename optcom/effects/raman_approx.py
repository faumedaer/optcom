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

from typing import Optional

import numpy as np

import optcom.utils.constants as cst
import optcom.utils.utilities as util
from optcom.effects.raman import Raman
from optcom.effects.abstract_effect import AbstractEffect
from optcom.utils.fft import FFT

class RamanApprox(AbstractEffect):
    r"""The approximation of the Raman scattering effect.

    Attributes
    ----------
    omega : numpy.ndarray of float
        The angular frequency array. :math:`[ps^{-1}]`
    time : numpy.ndarray of float
        The time array. :math:`[ps]`
    domega : float
        The angular frequency step. :math:`[ps^{-1}]`
    dtime : float
        The time step. :math:`[ps]`
    T_R :
        The raman coefficient. :math:`[]`
    self_term :
        If True, trigger the self-term of the effect.
    cross_term :
        If True, trigger the cross-term influence in the effect.
    eta :
        Positive term multiplying the cross terms in the effect.
    approx_type :
        The type of the NLSE approximation.

    """

    def __init__(self, T_R: float, self_term: bool = True,
                 cross_term: bool = False, eta: float = cst.XNL_COEFF,
                 approx_type: int = cst.DEFAULT_APPROX_TYPE) -> None:
        r"""
        Parameters
        ----------
        T_R :
            The raman coefficient. :math:`[]`
        self_term :
            If True, trigger the self-term of the effect.
        cross_term :
            If True, trigger the cross-term influence in the effect.
        eta :
            Positive term multiplying the cross terms in the effect.
        approx_type :
            The type of the NLSE approximation.

        """
        super().__init__()
        self.self_term: bool = self_term
        self.cross_term: bool = cross_term
        self.eta: float = eta
        self.T_R: float = T_R
        self.approx_type: int = approx_type
    # ==================================================================
    def set(self, center_omega: np.ndarray = np.array([]),
            abs_omega: np.ndarray = np.array([])) -> None:

        return None
    # ==================================================================
    def op(self, waves: np.ndarray, id: int,
           corr_wave: Optional[np.ndarray] = None) -> np.ndarray:
        """The approximation of the operator of the Raman effect."""
        res = np.zeros(waves[id].shape, dtype=cst.NPFT)
        if (self.self_term):
            res += self._op_approx_self(waves, id, corr_wave)
        if (self.cross_term):
            res += self.eta * self._op_approx_cross(waves, id, corr_wave)

        return res
    # ==================================================================
    def _op_approx_self(self, waves: np.ndarray, id: int,
                       corr_wave: Optional[np.ndarray] = None) -> np.ndarray:
        """The approximation of the operator of the Raman effect for the
        considered wave."""
        A = waves[id]
        res = np.zeros(A.shape, dtype=cst.NPFT)

        if (self.approx_type == cst.approx_type_1
                or self.approx_type == cst.approx_type_2):

            res =  FFT.dt_to_fft(A*np.conj(A), self._omega, 1)

        if (self.approx_type == cst.approx_type_3):

            res = (np.conj(A)*FFT.dt_to_fft(A, self._omega, 1)
                   + A*FFT.dt_to_fft(np.conj(A), self._omega, 1))

        return -1j * self.T_R * res
    # ==================================================================
    def _op_approx_cross(self, waves: np.ndarray, id: int,
                        corr_wave: Optional[np.ndarray] = None) -> np.ndarray:
        """The approximation operator of the cross terms of the Raman
        effect."""
        res = np.zeros(waves[id].shape, dtype=cst.NPFT)
        if (self.approx_type == cst.approx_type_1
                or self.approx_type == cst.approx_type_2
                or self.approx_type == cst.approx_type_3):
            for i in range(len(waves)):
                if (i != id):
                    res += waves[i] * np.conj(waves[i])
            res = FFT.dt_to_fft(res, self._omega, 1)

        return -1j * self.T_R * res
