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

from typing import List, Tuple

import optcom.utils.constants as cst
import optcom.utils.utilities as util
from optcom.components.abstract_pass_comp import AbstractPassComp
from optcom.components.abstract_pass_comp import call_decorator
from optcom.domain import Domain
from optcom.field import Field


default_name = 'Field Saver'


class SaveField(AbstractPassComp):
    """This component allows one to save one or multiple field, can be
    access via fields attribute.

    Attributes
    ----------
    name : str
        The name of the component.
    ports_type : list of int
        Type of each port of the component, give also the number of
        ports in the component. For types, see
        :mod:`optcom/utils/constant_values/port_types`.
    save : bool
        If True, will save each field going through each port. The
        recorded fields can be accessed with the attribute
        :attr:`fields`.
    call_counter : int
        Count the number of times the function
        :func:`__call__` of the Component has been called.
    wait :
        If True, will wait for specified waiting port policy added
        with the function :func:`AbstractComponent.add_wait_policy`.
    pre_call_code :
        A string containing code which will be executed prior to
        the call to the function :func:`__call__`. The two parameters
        `input_ports` and `input_fields` are available.
    post_call_code :
        A string containing code which will be executed posterior to
        the call to the function :func:`__call__`. The two parameters
        `output_ports` and `output_fields` are available.
    fields : list of Field
        List of fields which have been saved.

    Notes
    -----
    Component diagram::

        [0] __________________

    """

    _nbr_instances: int = 0
    _nbr_instances_with_default_name: int = 0

    def __init__(self, name: str = default_name, save: bool = False,
                 pre_call_code: str = '', post_call_code: str = '') -> None:
        """
        Parameters
        ----------
        name :
            The name of the component.
        pre_call_code :
            A string containing code which will be executed prior to
            the call to the function :func:`__call__`. The two parameters
            `input_ports` and `input_fields` are available.
        post_call_code :
            A string containing code which will be executed posterior to
            the call to the function :func:`__call__`. The two parameters
            `output_ports` and `output_fields` are available.

        """
        # Parent constructor -------------------------------------------
        ports_type = [cst.ANY_IN]
        super().__init__(name, default_name, ports_type, save,
                         pre_call_code=pre_call_code,
                         post_call_code=post_call_code)
        # Attr ---------------------------------------------------------
        self.fields: List[Field] = []
    # ==================================================================
    @call_decorator
    def __call__(self, domain: Domain, ports: List[int], fields: List[Field]
                 ) -> Tuple[List[int], List[Field]]:

        for field in fields:
            self.fields.append(field)

        return [], []


if __name__ == "__main__":
    """Give an example of LoadField usage.
    This piece of code is standalone, i.e. can be used in a separate
    file as an example.
    """

    from typing import List

    import numpy as np

    import optcom.utils.plot as plot
    from optcom.components.gaussian import Gaussian
    from optcom.components.save_field import SaveField
    from optcom.domain import Domain
    from optcom.field import Field
    from optcom.layout import Layout
    from optcom.utils.utilities_user import temporal_power, spectral_power,\
                                            temporal_phase, spectral_phase

    lt: Layout = Layout()
    gssn_1: Gaussian = Gaussian(channels=1, width=[5.0],
                                field_name='field 1 to be saved in file')
    field_saver_1: SaveField = SaveField()
    gssn_2: Gaussian = Gaussian(channels=1, width=[10.0],
                                field_name='field 2 to be saved in file')
    field_saver_2: SaveField = SaveField()

    lt.link((gssn_1[0], field_saver_1[0]), (gssn_2[0], field_saver_2[0]))
    lt.run(gssn_1, gssn_2)

    fields: List[Field] = field_saver_1.fields + field_saver_2.fields

    x_datas: List[np.ndarray] = [fields[0].time, fields[1].time,
                                 fields[0].nu, fields[1].nu]
    y_datas: List[np.ndarray] = [temporal_power(fields[0].channels),
                                 temporal_power(fields[1].channels),
                                 spectral_power(fields[0].channels),
                                 spectral_power(fields[1].channels)]

    plot.plot2d(x_datas, y_datas, x_labels=["t", "t", "nu","nu"],
                y_labels=["P_t", "P_t", "P_nu", "P_nu"],
                plot_titles=["Gaussian pulse which has been saved"],
                plot_groups=[0,0,1,1])
