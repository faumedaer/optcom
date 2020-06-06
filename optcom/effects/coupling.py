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
from optcom.domain import Domain
from optcom.effects.abstract_effect import AbstractEffect
from optcom.utils.taylor import Taylor


class Coupling(AbstractEffect):
    r"""The core coupling effect.

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

    """

    def __init__(self, kappa: Union[List[float], Callable],
                 order_taylor: int = 1, start_taylor: int = 0,
                 skip_taylor: List[int] = []) -> None:
        r"""
        Parameters
        ----------
        kappa :
            The coupling coefficients. :math:`[km^{-1}]` If a callable
            is provided, variable must be angular frequency.
            :math:`[ps^{-1}]`
        order_taylor :
            The order of kappa coefficients Taylor series expansion to
            take into account. (will be set to the length of the kappa
            array if one is provided)
        start_taylor :
            The order of the derivative from which to start the Taylor
            series expansion.
        skip_taylor :
            The order_taylors of the derivative to not consider.

        """
        super().__init__()
        self._order_taylor: int = order_taylor
        self._start_taylor: int = start_taylor
        self._skip_taylor: List[int] = skip_taylor
        # The coupling coefficient -------------------------------------
        self._op: np.ndarray = np.array([])
        self._kappa_op: np.ndarray = np.array([])
        self._kappa: Union[np.ndarray, Callable]
        if (callable(kappa)):
            self._kappa = kappa
        else:
            kappa_ = np.asarray(util.make_list(kappa))
            self._kappa = lambda omega: util.hstack_like(kappa_, omega)
            self._order_taylor = len(kappa_) - 1
    # ==================================================================
    @property
    def order_taylor(self) -> int:

        return self._order_taylor
    # ------------------------------------------------------------------
    @order_taylor.setter
    def order_taylor(self, order_taylor: int) -> None:
        self._order_taylor = order_taylor
    # ==================================================================
    def delay_factors(self, id: int) -> List[float]:
        res = []
        for i in range(1, len(self._kappa_op[id]), 2):
            res.append(self._kappa_op[id][i])

        return res
    # ==================================================================
    def set(self, center_omega: np.ndarray = np.array([]),
            abs_omega: np.ndarray = np.array([])) -> None:

        self._kappa_op = self._kappa(center_omega).reshape((-1,1))
        self._op = np.zeros((len(center_omega), len(self._omega)),
                            dtype=cst.NPFT)
        for i in range(len(center_omega)):
            self._op[i] = Taylor.series(self._kappa_op[i], self._omega,
                                        self._start_taylor,
                                        skip=self._skip_taylor)
    # ==================================================================
    def op(self, waves: np.ndarray, id: int,
           corr_wave: Optional[np.ndarray] = None) -> np.ndarray:
        """The operator of the coupling effect."""

        return 1j * self._op[id]
    # ==================================================================
    def term(self, waves: np.ndarray, id: int,
             corr_wave: Optional[np.ndarray] = None) -> np.ndarray:
        res = np.zeros(waves[id].shape, dtype=cst.NPFT)
        for i in range(len(waves)):
            if (i != id):
                res += waves[i]

        return self.op(waves, id, corr_wave) * res
