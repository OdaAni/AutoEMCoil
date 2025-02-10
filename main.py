import numpy as np
import openEMS as ems
import os

class CoilDesigner:
    def __init__(self):
        self.CSX = None
        self.fdtd = None
        self.mesh = None
        
    def setup_simulation(self):
        """Initialize OpenEMS FDTD simulation"""
        self.CSX = ems.ContinuousStructure()
        self.fdtd = ems.OpenEMS(NrTS=1e4)
        self.mesh = ems.CSXMesh.Simple()
        self.fdtd.SetCSX(self.CSX)

    def create_helical_coil(self, radius, height, turns, wire_diameter):
        """
        Create a helical coil geometry
        
        Parameters:
        radius (float): Radius of the helix
        height (float): Total height of the coil
        turns (int): Number of turns
        wire_diameter (float): Diameter of the wire
        """
        # Calculate helix parameters
        pitch = height / turns
        t = np.linspace(0, turns * 2 * np.pi, turns * 36)
        
        # Generate helix points
        x = radius * np.cos(t)
        y = radius * np.sin(t)
        z = pitch * t / (2 * np.pi)
        
        # Create metal for the coil
        metal = self.CSX.AddMetal('copper')
        
        # Add wire segments
        for i in range(len(t)-1):
            start = [x[i], y[i], z[i]]
            stop = [x[i+1], y[i+1], z[i+1]]
            metal.AddCylinder(start, stop, wire_diameter/2)
            
        return x, y, z

    def export_support_structure(self, x, y, z, support_thickness=2.0):
        """
        Export support structure for 3D printing
        
        Parameters:
        x, y, z (array): Coil coordinates
        support_thickness (float): Thickness of support structure
        """
        try:
            import cadquery as cq
        except ImportError:
            print("Please install cadquery: pip install cadquery")
            return
            
        # Create helical path for support structure
        points = [(x[i], y[i], z[i]) for i in range(len(x))]
        
        # Create support structure using CadQuery
        result = (cq.Workplane("XY")
                 .spline(points)
                 .sweep(cq.Workplane("YZ")
                       .circle(support_thickness)))
                       
        # Export as STL
        cq.exporters.export(result, 'coil_support.stl')
        
    def run_simulation(self, freq_range):
        """
        Run FDTD simulation
        
        Parameters:
        freq_range (tuple): (start_freq, stop_freq) in Hz
        """
        # Set frequency range
        f0 = sum(freq_range) / 2
        fc = f0
        
        # Add excitation and port
        port = self.CSX.AddLumpedPort(
            port_nr=1,
            R=50,
            start=[0, 0, 0],
            stop=[0, 0, 0.1],  # Adjust based on coil geometry
            p_dir='z'
        )
        
        # Set boundary conditions
        self.CSX.AddMaterial(epsilon=1, mu=1)
        self.fdtd.SetBoundaryCond(['PML_8', 'PML_8', 'PML_8', 'PML_8', 'PML_8', 'PML_8'])
        
        # Run simulation
        self.fdtd.Run()

def main():
    # Create designer instance
    designer = CoilDesigner()
    
    # Setup simulation
    designer.setup_simulation()
    
    # Create helical coil
    x, y, z = designer.create_helical_coil(
        radius=0.05,    # 5cm radius
        height=0.2,     # 20cm height
        turns=10,       # 10 turns
        wire_diameter=0.002  # 2mm wire diameter
    )
    
    # Export support structure for 3D printing
    designer.export_support_structure(x, y, z)
    
    # Run simulation
    designer.run_simulation(freq_range=(1e6, 10e6))  # 1-10 MHz

if __name__ == "__main__":
    main()
