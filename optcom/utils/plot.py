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
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Protocol

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from mpl_toolkits import mplot3d  # unused import (for '3d')

import optcom.utils.constants as cst
import optcom.utils.utilities as util


# For color, see https://matplotlib.org/examples/color/named_colors.html
linecolors = ['violet', 'orange', 'red', 'greenyellow', 'silver', 'brown',
              'pink', 'gray', 'black', 'blue', 'navy', 'gold',
              'cyan', 'palegreen', 'deepskyblue', 'lime',]


plot3d_types = {"plot_surface": ("mesh", "color"),
                "plot_wireframe": ("mesh", "nocolor"),
                "contour3D": ("mesh", "nocolor"),
                "contourf3D": ("mesh", "nocolor"),
                "plot_trisurf": ("ravel", "color"),
                "plot3D": ("ravel", "color"), "scatter3D": ("ravel", "color")}


axis_labels = { "t" : r"Time, $t \, (ps)$", \
               "nu" : r"Frequency, $\nu \, (THz)$", \
               "Lambda" : r"Wavelength, $\lambda \, (nm)$", \
               "omega" : r"Angular frequency, $\omega \, (THz)$", \
               "P_t" : r"Power, $|A(z, t)|^2 \, (W)$", \
               "P_nu" : r"Power, $|\tilde{A}(z, \nu)|^2 \, (a.u.)$", \
               "P_lambda" : r"Power, $|\tilde{A}(z, \lambda|^2 \, (a.u.)$$", \
               "z" : r"Fibre length, $z \, (km)$", \
               "phi_t" : r"Phase, $\phi(t) \, (rad)$", \
               "phi_nu" : r"Phase, $\phi(\nu) \, (rad)$", \
               "chirp" : r"Frequency chirp, $\delta \omega \, (rad / ps)$", \
               "t_normal" : r"Normalised time, $\frac{t}{T_0}$", \
               "xi" : r"Normalised distance, $\xi = \frac{z}{L_D}$", \
               "xi_prime" : r"Normalised distance, $\xi' = \frac{z}{L_D'}$",\
               "sigma_a" : r"Cross sections, $\sigma_a \, (nm^2)$",\
               "sigma_e" : r"Cross sections, $\sigma_e \, (nm^2)$",\
               "beta2" : r"$\beta_2 \, (ps^2 \cdot km^{-1})$",\
               "dispersion": r"Dispersion $(ps \cdot nm^{-1} \cdot km^{-1})$",\
               "dispersion_slope": r"Dispersion slope "
                                    r"$(ps \cdot nm^{-2} \cdot km^{-1})$",
               "population": r"Population density $(m^{-3})$",
               "n_2": r"Non-linear index, $n_2 \, (m^2\cdot W^{-1})$",
               "gamma": r"Non-linear coefficient, $\gamma \,"
                         r"(rad\cdot W^{-1}\cdot km^{-1})$",
               "h_R": r"Raman response, $h_R \, (ps^{-1})$" }


def check_axis_labels(labels_to_check: List[Optional[str]],
                      labels: Dict[str, str]) -> List[Optional[str]]:
    """Check if can assimilate given label to recorded ones."""
    for i in range(len(labels_to_check)):
        to_check = labels_to_check[i]
        if (to_check is not None):
            record_label = labels.get(to_check)
            if (record_label is not None):
                labels_to_check[i] = record_label

    return labels_to_check


def add_subplot_para(plt_to_add, x_label: Optional[str] = None,
                     y_label: Optional[str] = None,
                     z_label: Optional[str] = None,
                     x_range: Optional[str] = None,
                     y_range: Optional[str] = None,
                     z_range: Optional[str] = None,
                     plot_title: Optional[str] = None) -> None:
    if (x_label != None):
        plt_to_add.set_xlabel(x_label)
    if (y_label != None):
        plt_to_add.set_ylabel(y_label)
    if (z_label != None):
        plt_to_add.set_zlabel(z_label)
    if (x_range != None):
        plt_to_add.set_xlim(x_range)
    if (y_range != None):
        plt_to_add.set_ylim(y_range)
    if (z_range != None):
        plt_to_add.set_zlim(z_range)
    if (plot_title != None):
        plt_to_add.set_title(plot_title)


# Trick for typing of method's atttribute
class TypingMethodAttribute(Protocol):
    counter: int
    def __call__(self, *args: Any): ...

def apply_protocol_decorator(func: Any) -> TypingMethodAttribute:
    return func

@apply_protocol_decorator
def add_2D_subplot(plt_to_add, x_data, y_data, x_label, y_label, x_range,
                   y_range, plot_title, plot_label, plot_linestyle,
                   plot_color, opacity):
    """Plot a 2D graph."""
    x_data_ = np.array([x_data]) if (x_data.ndim < 2) else x_data
    y_data_ = np.array([y_data]) if (y_data.ndim < 2) else y_data
    x_data_ = util.modify_length_ndarray(x_data_, len(y_data_))
    multi_channel = len(y_data_) > 1
    labels_on_plot = plot_label is not None
    colors_on_plot = plot_color is not None
    if (multi_channel):
        plot_label = util.make_list(plot_label, len(y_data_))
    for i in range(len(y_data_)):
        if (multi_channel):
            if (labels_on_plot):
                plot_label_temp = plot_label[i] + " (ch.{})".format(i)
            else:
                plot_label_temp = "channel {}".format(i)
        else:
            plot_label_temp = plot_label
        if (not colors_on_plot):
            plot_color = linecolors[add_2D_subplot.counter%len(linecolors)]
            add_2D_subplot.counter += 1
        if (labels_on_plot or multi_channel):
            plt_to_add.plot(x_data_[i] , y_data_[i], ls=plot_linestyle,
                            c=plot_color, label=plot_label_temp)
        else:
            plt_to_add.plot(x_data_[i] , y_data_[i], ls=plot_linestyle,
                            c=plot_color)
        plt_to_add.fill_between(x_data_[i] , y_data_[i], alpha=opacity,
                                facecolor=plot_color)
        add_subplot_para(plt_to_add, x_label=x_label, y_label=y_label,
                         x_range=x_range, y_range=y_range,
                         plot_title=plot_title)
        if (labels_on_plot or multi_channel):
            plt_to_add.legend(loc = "best")


@apply_protocol_decorator
def add_3D_subplot(plt_to_add, x_data, y_data, z_data, x_label, y_label,
                   z_label, x_range, y_range, z_range, plot_title, plot_color,
                   opacity, plot_type):
    """Plot a 3D graph."""
    x_data_temp = np.asarray(x_data)
    if (x_data_temp.ndim > 1):  # Else single time array, nothing to pad
        if (x_data_temp.ndim == 2):
            temp = np.ones(z_data.shape)
            for i in range(len(temp)):
                temp[i] = (np.ones((z_data.shape[1], z_data.shape[2]))
                           * x_data_temp)
            x_data_temp = temp
        x_data = np.array([])
        z_data_temp = np.asarray(z_data)
        z_data = np.array([])
        x_data, z_data = util.auto_pad(x_data_temp, z_data_temp)
    colors_on_plot = plot_color is not None
    for i in range(len(z_data)):
        mesh_x, mesh_y = np.meshgrid(x_data, y_data[0])
        if (not colors_on_plot):
            plot_color = linecolors[add_3D_subplot.counter]
            add_3D_subplot.counter += 1
        if (plot3d_types[plot_type][0] == 'mesh'):
            if (plot3d_types[plot_type][1] == 'color'):
                getattr(plt_to_add, plot_type)(mesh_x, mesh_y, z_data[i],
                                               color=plot_color,
                                               rcount=100, ccount=100,
                                               alpha=opacity)
            else:
                getattr(plt_to_add, plot_type)(mesh_x, mesh_y, z_data[i],
                                               rcount=100, ccount=100,
                                               alpha=opacity)
        else:
            ravel_x = np.ravel(mesh_x)
            ravel_y = np.ravel(mesh_y)
            ravel_z = np.ravel(z_data[i])
            if (plot3d_types[plot_type][1] == 'color'):
                getattr(plt_to_add, plot_type)(ravel_x, ravel_y, ravel_z,
                                              color=plot_color,
                                              alpha=opacity)
            else:
                getattr(plt_to_add, plot_type)(ravel_x, ravel_y, ravel_z,
                                               alpha=opacity)

        add_subplot_para(plt_to_add, x_label=x_label, y_label=y_label,
                         z_label=z_label, x_range=x_range, y_range=y_range,
                         z_range=z_range, plot_title=plot_title)


def get_graph_layout(plot_groups: Optional[List[int]], split: bool, length: int
                     ) -> Tuple[List[List[int]], int]:
    nbr_graphs: int = 0
    graphs: List[List[int]] = []
    if (plot_groups is not None):
        nbr_graphs = max(plot_groups) + 1
        graphs = [[] for i in range(nbr_graphs)]
        for i in range(len(plot_groups)):
            graphs[plot_groups[i]].append(i)
    else:
        if (split):
            nbr_graphs = length
            graphs = [[i] for i in range(length)]
        else:
            nbr_graphs = 1
            graphs = [[i for i in range(length)]]

    return graphs, nbr_graphs


def get_graph_structure(nbr_graphs: int) -> Tuple[int, int]:
    nbr_row = 0
    nbr_col  = 0
    if (nbr_graphs < 3):
        nbr_row = nbr_graphs
    elif (nbr_graphs == 3 or nbr_graphs == 4):
        nbr_row = 2
    else:
        nbr_row = 3
    nbr_col = math.ceil(nbr_graphs / nbr_row)

    return nbr_row, nbr_col


def plot_graph(fig, resolution, fig_title, filename):
    if (fig_title is not None):
        fig.suptitle(fig_title, fontsize=16)
    fig.tight_layout()  # Avoiding overlapping texts (legend)
    fig.set_size_inches(resolution[0]/fig.dpi, resolution[1]/fig.dpi)
    if (filename != ""):
        fig.savefig(filename, bbox_inches='tight')
        util.print_terminal("Graph has been saved on filename '{}'"
                            .format(filename))
        fig.clf()
    else:
        plt.show()


def plot2d(x_datas: List[np.ndarray], y_datas: List[np.ndarray],
           x_labels: Optional[List[str]] = None,
           y_labels: Optional[List[str]] = None,
           x_ranges: Optional[List[Optional[Tuple[float, float]]]] = None,
           y_ranges: Optional[List[Optional[Tuple[float, float]]]] = None,
           plot_linestyles: List[str] = ['-'],
           plot_labels: Optional[List[Optional[str]]] = None,
           plot_titles: Optional[List[str]] = None,
           plot_colors: Optional[List[str]] = None,
           plot_groups: Optional[List[int]] = None,
           split: bool = False, opacity: List[float] = [0.2],
           fig_title: Optional[str] = None, filename: str = "",
           resolution: Tuple[float, float] = (1920., 1080.),
           triangle_layout: bool = False) -> None:
    """Plot an 2D graph.

    Parameters
    ----------
    x_datas :
        The data on the x axis.
    y_datas :
        The data on the y axis.
    x_label :
        The labels for each axis on each plot along the x axis.
    y_label :
        The labels for each axis on each plot along the y axis.
    x_range :
        The ranges for each axis on each plot along the x axis.
    y_range :
        The ranges for each axis on each plot along the y axis.
    plot_linestyle :
        The linestyle of the lines.
    plot_labels :
        The labels for each lines on each plot.
    plot_titles :
        The title of each plot.
    plot_colors :
        The color of each line on each plot.
    plot_groups :
        The group of each line. The line having the same number will be
        displayed on the plot.
    split :
        If True, split all the lines in one plote. If False, group all
        the lines in one plot. Only considered if plot_groups is None.
    opacity :
        The opacity of the lines.
    fig_title :
        The figure title.
    filename :
        The filename where to save the image. If provided, the
        animation will be saved.
    resolution :
        The resolution with which to save the image.
    triangle_layout :
        Option for 3 plots, if True, put the one wide plot at the bottom
        and the 2 other plots on the top.

    """
    # N.B. if y_datas comes from field, np.ndarray is multidim
    # Initializing -----------------------------------------------------
    fig = plt.gcf()
    # Managing x and y labels ------------------------------------------
    x_labels_: List[Optional[str]]
    x_labels_ = check_axis_labels(util.make_list(x_labels), axis_labels)
    y_labels_: List[Optional[str]]
    y_labels_ = check_axis_labels(util.make_list(y_labels), axis_labels)
    # Padding ----------------------------------------------------------
    y_datas_: List[np.ndarray]
    y_datas_ = util.make_list(y_datas)
    x_datas_: List[np.ndarray]
    x_datas_ = util.make_list(x_datas, len(y_datas_))
    if (len(y_datas_) < len(x_datas_)):
        util.warning_terminal("The number of y data must be equal or greater "
            "than the number of x data, graph creation aborted.")

        return None
    plot_labels_: List[Optional[str]]
    plot_labels_ = util.make_list(plot_labels, len(x_datas_))
    plot_colors_: List[Optional[str]]
    plot_colors_ = util.make_list(plot_colors, len(x_datas_))
    plot_linestyles_ = util.make_list(plot_linestyles, len(x_datas_))
    opacity_: List[float]
    opacity_ = util.make_list(opacity, len(x_datas_))
    plot_groups_: Optional[List[int]]
    if (plot_groups is not None):
        plot_groups_ = util.make_list(plot_groups, len(x_datas_))
    else:
        plot_groups_ = plot_groups
    # Preparing graph parameters
    graphs, nbr_graphs = get_graph_layout(plot_groups_, split, len(x_datas_))
    # Padding ----------------------------------------------------------
    x_labels_ = util.make_list(x_labels_, nbr_graphs)
    y_labels_ = util.make_list(y_labels_, nbr_graphs)
    x_ranges_: List[Optional[Tuple[float, float]]]
    x_ranges_ = util.make_list(x_ranges, nbr_graphs)
    y_ranges_: List[Optional[Tuple[float, float]]]
    y_ranges_ = util.make_list(y_ranges, nbr_graphs)
    plot_titles_: List[Optional[str]]
    plot_titles_ = util.make_list(plot_titles, nbr_graphs, '')
    # Nonexistent field  management (no field recorded in component) ---
    for i in range(len(x_datas_)):
        if ((y_datas_[i] is None)):
            util.warning_terminal("Try to plot a nonexistent field!")
            x_datas_[i] = np.zeros(0)
            y_datas_[i] = np.zeros(0)
    # Plot graph -------------------------------------------------------
    nbr_row: int
    nbr_col: int
    nbr_row, nbr_col = get_graph_structure(nbr_graphs)
    triangle: int = 0 if (triangle_layout and nbr_graphs == 3) else 1
    offset: int = 0  # Offset for index of plot in layout
    for i, graph in enumerate(graphs) :
        index = i + 1 + offset
        if (triangle | i):
            nbr_col_subplot = nbr_col
        else:
            nbr_col_subplot = nbr_col - 1
            offset += 1
        add_2D_subplot.counter = 0 # For own colors if not specified
        plt_to_add = fig.add_subplot(nbr_row, nbr_col_subplot, index)
        for plot in graph:
            add_2D_subplot(plt_to_add, x_datas_[plot], y_datas_[plot],
                           x_labels_[i], y_labels_[i], x_ranges_[i],
                           y_ranges_[i], plot_titles_[i], plot_labels_[plot],
                           plot_linestyles_[plot], plot_colors_[plot],
                           opacity_[plot])
    # Plotting / saving ------------------------------------------------
    plot_graph(fig, resolution, fig_title, filename)


def plot3d(x_datas: List[np.ndarray], y_datas: List[np.ndarray],
           z_datas: Optional[List[np.ndarray]] = None,
           x_labels: Optional[List[str]] = None,
           y_labels: Optional[List[str]] = None,
           z_labels: Optional[List[str]] = None,
           x_ranges: Optional[List[Optional[Tuple[float, float]]]] = None,
           y_ranges: Optional[List[Optional[Tuple[float, float]]]] = None,
           z_ranges: Optional[List[Optional[Tuple[float, float]]]] = None,
           plot_titles: Optional[List[str]] = None,
           plot_colors: Optional[List[str]] = None,
           plot_groups: Optional[List[int]] = None,
           split: bool = False, opacity: List[float] = [0.8],
           fig_title: Optional[str] = None, filename: str = "",
           resolution: Tuple[float, float] = (1920., 1080.),
           plot_types: List[str] = [cst.DEF_3D_PLOT],
           triangle_layout: bool = False) -> None:
    """Plot an 3D graph.

    Parameters
    ----------
    x_datas :
        The data on the x axis.
    y_datas :
        The data on the y axis.
    z_datas :
        The data on the z axis.
    x_label :
        The labels for each axis on each plot along the x axis.
    y_label :
        The labels for each axis on each plot along the y axis.
    z_label :
        The labels for each axis on each plot along the z axis.
    x_range :
        The ranges for each axis on each plot along the x axis.
    y_range :
        The ranges for each axis on each plot along the y axis.
    z_range :
        The ranges for each axis on each plot along the z axis.
    plot_linestyle :
        The linestyle of the lines.
    plot_labels :
        The labels for each lines on each plot.
    plot_titles :
        The title of each plot.
    plot_colors :
        The color of each line on each plot.
    plot_groups :
        The group of each line. The line having the same number will be
        displayed on the plot.
    split :
        If True, split all the lines in one plote. If False, group all
        the lines in one plot. Only considered if plot_groups is None.
    opacity :
        The opacity of the lines.
    fig_title :
        The figure title.
    filename :
        The filename where to save the image. If provided, the
        animation will be saved.
    resolution :
        The resolution with which to save the image.
    plot_types :
        The type of each plot, see matplotlib documentation for more.
    triangle_layout :
        Option for 3 plots, if True, put the one wide plot at the bottom
        and the 2 other plots on the top.

    """
    # N.B. if y_datas comes from field, np.ndarray is multidim
    # Initializing -----------------------------------------------------
    fig = plt.gcf()
    # Managing x and y and z labels ------------------------------------
    x_labels_: List[Optional[str]]
    x_labels_ = check_axis_labels(util.make_list(x_labels), axis_labels)
    y_labels_: List[Optional[str]]
    y_labels_ = check_axis_labels(util.make_list(y_labels), axis_labels)
    z_labels_: List[Optional[str]]
    z_labels_ = check_axis_labels(util.make_list(z_labels), axis_labels)
    # Padding ----------------------------------------------------------
    if (z_datas is None):
        util.warning_terminal("Three dimensional data must be provided to "
            "plot three dimensional plot.")

        return None
    z_datas_: List[np.ndarray]
    y_datas_: List[np.ndarray]
    x_datas_: List[np.ndarray]
    z_datas_ = util.make_list(z_datas)
    y_datas_ = util.make_list(y_datas, len(z_datas_))
    x_datas_ = util.make_list(x_datas, len(y_datas_))
    if (len(z_datas_) < len(y_datas_)):
        util.warning_terminal("The number of z data must be equal or greater "
            "than the number of y data, graph creation aborted.")

        return None
    if (len(y_datas_) < len(x_datas_)):
        util.warning_terminal("The number of y data must be equal or greater "
            "than the number of x data, graph creation aborted.")

        return None
    plot_colors_: List[Optional[str]]
    plot_colors_ = util.make_list(plot_colors, len(x_datas_))
    opacity_: List[float]
    opacity_ = util.make_list(opacity, len(x_datas_))
    plot_types_: List[str]
    plot_types_ = util.make_list(plot_types, len(x_datas_))
    for i in range(len(plot_types_)):
        if (plot3d_types.get(plot_types_[i]) is None):
            util.warning_terminal("3D plot type '{}' does not exist, replace by "
                "'{}'.".format(plot_types_[i], cst.DEF_3D_PLOT))
            plot_types_[i] = cst.DEF_3D_PLOT
    plot_groups_: Optional[List[int]]
    if (plot_groups is not None):
        plot_groups_= util.make_list(plot_groups, len(x_datas_))
    else:
        plot_groups_ = plot_groups
    # Preparing graph parameters
    graphs, nbr_graphs = get_graph_layout(plot_groups_, split, len(x_datas_))
    # Padding ----------------------------------------------------------
    x_labels_ = util.make_list(x_labels_, nbr_graphs)
    y_labels_ = util.make_list(y_labels_, nbr_graphs)
    z_labels_ = util.make_list(z_labels_, nbr_graphs)
    x_ranges_: List[Optional[Tuple[float, float]]]
    x_ranges_ = util.make_list(x_ranges, nbr_graphs, None)
    y_ranges_: List[Optional[Tuple[float, float]]]
    y_ranges_ = util.make_list(y_ranges, nbr_graphs, None)
    z_ranges_: List[Optional[Tuple[float, float]]]
    z_ranges = util.make_list(z_ranges, nbr_graphs, None)
    plot_titles_: List[Optional[str]]
    plot_titles_ = util.make_list(plot_titles, nbr_graphs, '')
    # Nonexistent field  management (no field recorded in component) ---
    for i in range(len(x_datas_)):
        if ((y_datas_[i] is None) or (z_datas_[i] is None)):
            util.warning_terminal("Try to plot a nonexistent field! (graph at "
                "position {} will be ignored)".format(i))
            x_datas_[i] = np.zeros(0)
            y_datas_[i] = np.zeros(0)
            z_datas_[i] = np.zeros(0)
    # Plot graph -------------------------------------------------------
    nbr_row: int
    nbr_col: int
    nbr_row, nbr_col = get_graph_structure(nbr_graphs)
    triangle: int = 0 if (triangle_layout and nbr_graphs == 3) else 1
    offset: int = 0  # Offset for index of plot in layout
    for i, graph in enumerate(graphs) :
        index = i + 1 + offset
        if (triangle | i):
            nbr_col_subplot = nbr_col
        else:
            nbr_col_subplot = nbr_col - 1
            offset += 1
        add_3D_subplot.counter = 0 # For own colors if not specified
        plt_to_add = fig.add_subplot(nbr_row, nbr_col_subplot, index,
                                     projection='3d')
        for plot in graph:
            add_3D_subplot(plt_to_add, x_datas_[plot], y_datas_[plot],
                           z_datas_[plot], x_labels_[i], y_labels_[i],
                           z_labels_[i], x_ranges_[i], y_ranges_[i],
                           z_ranges[i], plot_titles_[i], plot_colors_[plot],
                           opacity_[plot], plot_types_[plot])
    # Plotting / saving ------------------------------------------------
    plot_graph(fig, resolution, fig_title, filename)


def animation2d(x_datas: np.ndarray, y_datas: np.ndarray,
                z_datas: Optional[np.ndarray] = None,
                x_label: Optional[List[str]] = None,
                y_label: Optional[List[str]] = None,
                x_range: Optional[Tuple[float, float]] = None,
                y_range: Optional[Tuple[float, float]] = None,
                plot_linestyle: str = '-', plot_linewidth: float = 1.,
                plot_labels: Optional[List[Optional[str]]] = None,
                plot_title: Optional[str] = None,
                plot_colors: Optional[List[str]] = None, opacity: float = 0.2,
                fig_title: Optional[str] = None, filename: str = "",
                resolution: Tuple[float, float] = (1920., 1080.),
                interval: float = 100., repeat: bool = True,
                repeat_delay: float = 1000.) -> None:
    """Plot an 2D animation.

    Parameters
    ----------
    x_datas :
        The data on the x axis.
    y_datas :
        The data on the y axis.
    z_datas :
        The data on the z axis.
    x_label :
        The labels for each axis along the x axis.
    y_label :
        The labels for each axis along the y axis.
    x_range :
        The ranges for each axis along the x axis.
    y_range :
        The ranges for each axis along the y axis.
    plot_linestyle :
        The linestyle of the lines.
    plot_linewidth :
        The linewidth of the lines.
    plot_labels :
        The labels for each lines.
    plot_title :
        The title of the animation.
    plot_colors :
        The color of each line.
    opacity :
        The opacity of the lines.
    fig_title :
        The figure title.
    filename :
        The filename where to save the animation. If provided, the
        animation will be saved.
    resolution :
        The resolution with which to save the animation.
    interval :
        The interval in between each frame.
    repeat :
        Either to repeat the animation when it is displayed.
    repeat_delay :
        The delay in between each repetition.

    """
    # N.B. if y_datas comes from field, np.ndarray is multidim
    # Initializing -----------------------------------------------------
    fig = plt.gcf()
    ax = plt.axes()
    # Managing x and y labels ------------------------------------------
    x_label_: Optional[str]
    x_label_ = check_axis_labels(util.make_list(x_label), axis_labels)[0]
    y_label_: Optional[str]
    y_label_ = check_axis_labels(util.make_list(y_label), axis_labels)[0]
    if (x_label_ is not None):
        plt.xlabel(x_label_)
    if (y_label_ is not None):
        plt.ylabel(y_label_)
    # Plot title -------------------------------------------------------
    if (plot_title is not None):
        plt.title(plot_title)
    # Padding ----------------------------------------------------------
    nbr_channels: int = 1
    nbr_images: int = 1
    y_datas_: np.ndarray
    x_datas_: np.ndarray
    if (y_datas.ndim == 3):  #  (channels, image, y_data)
        nbr_channels = y_datas.shape[0]
        nbr_images = y_datas.shape[1]
        if (x_datas.ndim < 2):
            x_datas_ = util.vstack_ndarray(np.array([x_datas]), nbr_images)
            x_datas_ = util.vstack_ndarray(np.array([x_datas_]), nbr_channels)
        elif (x_datas.ndim < 3):
            x_datas_ = util.vstack_ndarray(x_datas, nbr_images)
            x_datas_ = util.vstack_ndarray(np.array([x_datas_]), nbr_channels)
        else:   # Should be ndim = 3
            if (nbr_channels >  x_datas.shape[0]):
                x_datas_ = util.vstack_ndarray([x_datas_], nbr_channels)
            else:
                x_datas_ = x_datas
        y_datas_ = y_datas
    elif (y_datas.ndim == 2):   # (image, y_data)
        nbr_images = y_datas.shape[0]
        if (x_datas.ndim < 2):
            x_datas_ = util.vstack_ndarray(np.array([x_datas]), nbr_images)
        else:
            if (nbr_images > x_datas.shape[0]):
                x_datas_ = util.vstack_ndarray(x_datas, len(y_datas))
            else:
                x_datas_ = x_datas
        y_datas_ = y_datas
        x_datas_ = np.array([x_datas_])
        y_datas_ = np.array([y_datas_])
    else:
        util.warning_terminal("The y_datas must be at least two dimensional, "
            "shape can be (image, y_data) or (channels, image, y_data)")

        return None
    # Lables management ------------------------------------------------
    plot_labels = util.make_list(plot_labels, nbr_channels, '')
    plot_labels_: List[str] = []
    if (plot_labels is not None):
        for i in range(nbr_channels):
            crt_plot_label = plot_labels[i]
            if (crt_plot_label is None or crt_plot_label == ''):
                plot_labels_.append("channel {}".format(i))
            else:
                plot_labels_.append(crt_plot_label + " (ch.{})".format(i))
    # Colors management ------------------------------------------------
    if (plot_colors is not None):
        plot_colors_ = plot_colors
    else:
        plot_colors_ = linecolors
    # Line2D creation --------------------------------------------------
    lines = []
    for i in range(nbr_channels):
        line = ax.plot([],[], c=plot_colors_[i%len(plot_colors_)],
                       ls=plot_linestyle, label=plot_labels_[i],
                       lw=plot_linewidth)[0]
        lines.append(line)
    plt.ticklabel_format(axis='both', style='sci', scilimits=(-2,2))
    if (plot_labels is not None):
        plt.legend(loc = "best")
    min_y = 0.
    max_y = 0.
    if (y_range is None):
        max_y = np.amax(y_datas_)
        max_y = max_y + 0.2*max_y
        ax.set_ylim(0., max_y)
    else:
        max_y =  y_range[1]
        ax.set_ylim(y_range[0], max_y)
    # Animation creation -----------------------------------------------
    text_plot = [ax.text(0., 0., '', style='italic', fontsize=10)]
    fill_lines = []
    for j, line in enumerate(lines):
        fill_lines.append(ax.fill_between([], []))
    def update(i):
        mins: List[float] = []
        maxs: List[float] = []
        for j, line in enumerate(lines):  # Browsing channels -> plots
            fill_lines[j].remove()
            line.set_data(x_datas_[j][i], y_datas_[j][i])
            facecolor = plot_colors_[j%len(plot_colors_)]
            fill_lines[j] = ax.fill_between(x_datas_[j][i] , y_datas_[j][i],
                                            alpha=opacity,
                                            facecolor=facecolor)
            mins.append(x_datas_[j][i][0])
            maxs.append(x_datas_[j][i][-1])

        if (x_range is None):
            min_x = min(mins)
            max_x = max(maxs)
            ax.set_xlim(min_x, max_x)
        else:
            min_x = x_range[0]
            max_x = x_range[1]
            ax.set_xlim(x_range[0], x_range[1])
        if (z_datas is not None):
            x_pos = max_x - (max_x-min_x)*0.1
            y_pos = min_y + (max_y-min_y)*0.1
            text_plot[0].set_position((x_pos, y_pos))
            text_plot[0].set_text("z = {} km".format(str(z_datas[i])))

        return lines

    def init():
        for line in lines:
            line.set_data([],[])

        return lines

    ani = animation.FuncAnimation(fig, update, frames=nbr_images,
                                  interval=interval, repeat=repeat,
                                  repeat_delay=repeat_delay, init_func=init)
    # Plotting / saving ------------------------------------------------
    if (fig_title is not None):
        fig.suptitle(fig_title, fontsize=16)
    fig.tight_layout()  # Avoiding overlapping texts (legend)
    fig.set_size_inches(resolution[0]/fig.dpi, resolution[1]/fig.dpi)
    if (filename != ""):
        ani.save(filename)
        util.print_terminal("Graph has been saved on filename '{}'"
                            .format(filename))
        fig.clf()
    else:
        plt.show()
