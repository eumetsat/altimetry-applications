"""Module responsible for building the plots."""
import numpy as np
import matplotlib.pyplot as plt
import cartopy

from correction_model.calculations import *

def set_corr_plot(self):

    with self.output_corr_plot:
        self.fig1, self.ax_corr = plt.subplots(constrained_layout=True, figsize=(5, 5))
        
        # data reading
        calculate_variables(self)
        select_reference_surface(self)

        # plot limit calculations
        datamax = np.nanmax(self.vars["data_ref"])
        datamin = np.nanmin(self.vars["data_ref"])
  
        self.ax_corr.line1a = self.ax_corr.scatter(self.vars["data_ref"], self.vars["lat"], c='k',
                                                   s=5, marker="o", edgecolors=None, linewidth=0.0, zorder=3)
        self.ax_corr.set_xlabel(self.varname)
        self.ax_corr.set_ylabel('$Latitude$')
        self.ax_corr.set_xlim([datamin - (datamax - datamin)/10.0, datamax + (datamax - datamin)/10.0])
        self.ax_corr.set_ylim([-90, 90])
        self.ax_corr.plot_legend = self.ax_corr.legend([self.ax_corr.line1a], [self.varname], fontsize=10)
        self.ax_corr.plot_legend.get_frame().set_linewidth(0.0)
        plt.show()

    self.fig1.canvas.toolbar_position = 'bottom'
    self.fig1.canvas.resizable = False
    self.fig1.canvas.header_visible = False
    self.ax_corr.grid(True, linestyle='--')

def set_spatial_plot(self):

    with self.output_spatial_plot:
        self.fig2, self.ax_spatial = plt.subplots(constrained_layout=True, figsize=(2.5, 1.75),
          subplot_kw=dict(projection=cartopy.crs.PlateCarree()))
        self.ax_spatial.add_feature(cartopy.feature.LAND, zorder=4, edgecolor='k', facecolor='#5D6D7E', linewidth=0.5)
        self.gl = self.ax_spatial.gridlines(draw_labels = True, zorder=20, color='0.0',
                                            linestyle='--', linewidth=0.5)
        self.gl.top_labels = False
        self.gl.right_labels = False
        self.gl.bottom_labels = False
        self.gl.left_labels = False
        self.gl.xlabel_style = {'color': 'black', 'size': 8}
        self.gl.ylabel_style = {'color': 'black', 'size': 8}

        self.ax_spatial.line2a = self.ax_spatial.scatter(self.vars["lon"], self.vars["lat"],
                                              c=self.vars["data_ref"],
                                              cmap=plt.cm.RdYlBu_r,
                                              s=10, marker='o', edgecolors=None,
                                              linewidth=0.0, zorder=3)

        self.ax_spatial.set_global()
        self.ax_spatial.set_aspect(1.5)

        plt.show()

    self.fig2.canvas.toolbar_position = 'bottom'
    self.fig2.canvas.resizable = False
    self.fig2.canvas.header_visible = False
    self.fig2.canvas.toolbar_visible = False
    self.fig2.canvas.header_visible = False
    self.fig2.canvas.footer_visible = False
    self.ax_spatial.grid(True)

def replot_corrections(self, make_trace):
    
    if make_trace:
        # make a plot
        try:
            # see if we already have an existing trace to remove
            self.ax_corr.line1b.remove()
            self.ax_corr.fillb.remove()
        except:
            pass
        
        # make a new trace
        self.ax_corr.line1b = self.ax_corr.scatter(self.vars["data_corr"], self.vars["lat"], c='r',
                                                   s=5, marker="o", edgecolors=None, linewidth=0.0, zorder=1)
        
        self.ax_corr.fillb = self.ax_corr.fill_betweenx(self.vars["lat"],
                                                        self.vars["data_ref"],
                                                        self.vars["data_corr"],
                                                        color='r', alpha=0.5)
        # plot limit calculations
        datamax = max([np.nanmax(self.vars["data_ref"]), np.nanmax(self.vars["data_corr"])])
        datamin = min([np.nanmin(self.vars["data_ref"]), np.nanmin(self.vars["data_corr"])])
        self.ax_corr.set_xlim([datamin - (datamax-datamin)/10, datamax + (datamax-datamin)/10])
        
        # update legend
        self.ax_corr.plot_legend.remove()
        self.ax_corr.plot_legend = self.ax_corr.legend([self.ax_corr.line1a, self.ax_corr.line1b],
                                         [self.varname, self.varname.replace("raw", "corrected")],
                                         fontsize=10, ncol=1)
        
        self.ax_corr.plot_legend.get_frame().set_linewidth(0.0)
        
    else:
        try:
            self.ax_corr.line1b.remove()
            self.ax_corr.fillb.remove()
        except:
            pass

        # plot limit calculations
        datamax = np.nanmax(self.vars["data_ref"])
        datamin = np.nanmin(self.vars["data_ref"])
        self.ax_corr.set_xlim([datamin - (datamax-datamin)/10, datamax + (datamax-datamin)/10])

        # update legend
        self.ax_corr.plot_legend.remove()
        self.ax_corr.plot_legend = self.ax_corr.legend([self.ax_corr.line1a], [self.varname], fontsize=10)
        self.ax_corr.plot_legend.get_frame().set_linewidth(0.0)
        