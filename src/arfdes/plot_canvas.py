#MatPlotLib imports
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class PlotCanvas(FigureCanvasQTAgg):
    ''' This class creates a canvas for plotting the airfoil using Matplotlib. '''
    def __init__(self, program, project, params):
        self.AIRFLOW = program
        self.project = project
        self.params = params
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        super().__init__(self.fig)

    def plot_airfoil(self, Current_Airfoil):
        '''
        Plots an airfoil based on objects Airfoil stored in obj.arf.py defined by folowing gorup of parameters:

        Base parameters:
            chord, origin_X, origin_Y
        Leading Edge parameters:
            le_thickness, le_depth, le_offset, le_angle
        Trailing Edge parameters:
            te_thickness, te_depth, te_offset, te_angle
        Pressure Side parameters:
            ps_fwd_angle, ps_rwd_angle, ps_fwd_accel, ps_rwd_accel
        Suction Side parameters:    
            ss_fwd_angle, ss_rwd_angle, ss_fwd_accel, ss_rwd_accel
        '''

        self.ax.clear()

        # Extract parameters
        Current_Airfoil.update_airfoil()

        # Plot
        if self.AIRFLOW.airfoil_designer['show_construction'] == True:
            self.ax.plot(Current_Airfoil.constr['le'][0], Current_Airfoil.constr['le'][1], 'b--', marker='o', label='LE Control Polygon')
            self.ax.plot(Current_Airfoil.constr['ps'][0], Current_Airfoil.constr['ps'][1], 'g--', marker='o', label='PS Control Polygon')
            self.ax.plot(Current_Airfoil.constr['ss'][0], Current_Airfoil.constr['ss'][1], 'r--', marker='o', label='SS Control Polygon')
            self.ax.plot(Current_Airfoil.constr['te'][0], Current_Airfoil.constr['te'][1], 'y--', marker='o', label='TE Control Polygon')

        self.ax.plot(Current_Airfoil.geom['le'][0],Current_Airfoil.geom['le'][1],'b',linewidth=2.0,label='LE B-spline curve')
        self.ax.plot(Current_Airfoil.geom['ps'][0],Current_Airfoil.geom['ps'][1],'g',linewidth=2.0,label='PS B-spline curve')
        self.ax.plot(Current_Airfoil.geom['ss'][0],Current_Airfoil.geom['ss'][1],'r',linewidth=2.0,label='SS B-spline curve')
        self.ax.plot(Current_Airfoil.geom['te'][0],Current_Airfoil.geom['te'][1],'y',linewidth=2.0,label='TE B-spline curve')

        # Appearance
        self.ax.legend(loc='best')
        self.ax.set_title("Airfoil Designer")
        self.ax.axis('equal')
        self.ax.set_aspect("equal")
        self.ax.grid(True)

        self.draw()

    def plot_reference(self, Up_ref_points, Dwn_ref_points):
        ''' Plot the reference airfoil. '''
        print("Plotting reference airfoil")

        self.ax.plot(Up_ref_points[0],Up_ref_points[1],'--',linewidth=2.0,label='Ref curve')
        self.ax.plot(Dwn_ref_points[0],Dwn_ref_points[1],'--',linewidth=2.0,label='Ref curve')
        
        # Appearance
        self.ax.legend(loc='best')
        self.ax.set_title("Airfoil Designer")
        self.ax.axis('equal')
        self.ax.set_aspect("equal")
        self.ax.grid(True)

        self.draw()

    def update_plot(self, index, Up_ref_points=None, Dwn_ref_points=None):
        ''' Update the plot with new parameters. '''
        print("Updating plot with new parameters")
        selected_airfoil = self.project.project_airfoils[index]
        #self.params = params
        self.plot_airfoil(selected_airfoil)
        if Up_ref_points is not None and Dwn_ref_points is not None:
            self.plot_reference(Up_ref_points, Dwn_ref_points)

    def clear_plot(self):
        ''' Clear the plot. '''
        print("Clearing plot")
        self.ax.clear()
        self.ax.set_title("Airfoil Designer")
        self.ax.axis('equal')
        self.ax.set_aspect("equal")
        self.ax.grid(True)
        self.draw()