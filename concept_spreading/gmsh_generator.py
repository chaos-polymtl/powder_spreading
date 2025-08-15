"""
Making round spreader.

By: Olivier Gaboriault
Date: February 16th, 2024
"""
# Import modules:
import gmsh
import numpy as np
import sys


def round_blade(radius, n_points, angle_fraction, dept):
    """
    Creates a gmsh of the rounded blade and saves it in ./gmsh
    :param radius: Radius at the bottom of the blade.
    :param n_points: Number of points used to create the radius on each sides of the blade
    :param angle_fraction: The last point on the radius will be at this value. Usually between 0.5 and 1.0
    :param dept: Thickness of the blade in the z direction.
    """
    # Initialize gmsh:
    gmsh.initialize()

    # Delta theta used for the radius
    delta_theta = angle_fraction * np.pi / (n_points - 1)

    # Useful constant
    z0 = 0.0  # First side
    z1 = dept  # Second side
    y1 = 0.03  # Top of the blade

    # Initialize arrays
    points_id_0 = []
    points_id_1 = []
    lines_id_z0_2_Z1 = []
    lines_id_diag = []
    lines_id_z0 = []
    lines_id_z1 = []
    line_loops = []
    plane_surfaces = []

    # Points at z0 and z1 
    points_id_0.append(gmsh.model.geo.addPoint(0.0, y1, z0, meshSize=1.))
    points_id_1.append(gmsh.model.geo.addPoint(0.0, y1, z1, meshSize=1.))
    for i in range(n_points):
        points_id_0.append(
            gmsh.model.geo.addPoint(radius * (-1 + np.cos(i * delta_theta)), radius * (1. + np.sin(-i * delta_theta)),
                                    z0,
                                    meshSize=1.))
        points_id_1.append(
            gmsh.model.geo.addPoint(radius * (-1 + np.cos(i * delta_theta)), radius * (1. + np.sin(-i * delta_theta)),
                                    z1,
                                    meshSize=1.))
    # Last point
    points_id_0.append(gmsh.model.geo.addPoint(radius * (-1 + np.cos(i * delta_theta)), y1, z0, meshSize=1.))
    points_id_1.append(gmsh.model.geo.addPoint(radius * (-1 + np.cos(i * delta_theta)), y1, z1, meshSize=1.))

    # Last point

    # Now we need to make triangles.
    # Z1[n]   <----------------- Z1[n]
    #  ^    \__                    ^
    #  |       \__                 |
    #  |          \__              |
    #  |             \__           |
    #  |                \__        |
    #  |                   \__>    |
    # Z1[n+1] <----------------- Z1[n+1]
    #
    for index, p0 in enumerate(points_id_0):
        # Lines going from Z0 to Z1
        lines_id_z0_2_Z1.append(gmsh.model.geo.add_line(p0, points_id_1[index]))

    for j in range(len(points_id_0) - 1):
        # Lines going from Z1 to Z0[ + 1]
        lines_id_diag.append(gmsh.model.geo.add_line(points_id_1[j], points_id_0[j + 1]))

    for j in range(len(points_id_0) - 1):
        # Lines going from Z0[+1] to Z0[]
        lines_id_z0.append(gmsh.model.geo.add_line(points_id_0[j + 1], points_id_0[j]))
        lines_id_z1.append(gmsh.model.geo.add_line(points_id_1[j + 1], points_id_1[j] ))

    for j in range(len(points_id_1) - 1):
        line_loops.append(gmsh.model.geo.addCurveLoop([lines_id_z0_2_Z1[j], lines_id_diag[j], lines_id_z0[j]]))
        line_loops.append(gmsh.model.geo.addCurveLoop([lines_id_diag[j], lines_id_z0_2_Z1[j + 1], lines_id_z1[j]]))

    for j in range(len(line_loops)):
        plane_surfaces.append(gmsh.model.geo.addPlaneSurface([line_loops[j]]))

    gmsh.model.geo.synchronize()
    gmsh.model.addPhysicalGroup(2, plane_surfaces)
    gmsh.model.geo.synchronize()

    # Generate mesh:
    gmsh.model.mesh.generate(2)

    # Write mesh data:
    gmsh.write("gmsh/Blade.msh")

    # Creates  graphical user interface
    """
    if 'close' not in sys.argv:
        gmsh.fltk.run()
    """
    # Finalize the Gmsh API
    gmsh.finalize()

    print(f"gmsh/Blade.msh saved")
    return


def reservoir_plate(length, dept):
    """
    Created the gmsh for the reservoir plate and saves it in ./gmsh
    :param length:
    :param dept:
    """
    # Initialize gmsh:
    gmsh.initialize()

    # Useful constant
    y = 0.
    x0 = 0.
    x1 = length
    z0 = 0.
    z1 = dept

    # Add point
    point0 = gmsh.model.geo.addPoint(x0, y, z0, meshSize=1.)
    point1 = gmsh.model.geo.addPoint(x1, y, z0, meshSize=1.)
    point2 = gmsh.model.geo.addPoint(x1, y, z1, meshSize=1.)
    point3 = gmsh.model.geo.addPoint(x0, y, z1, meshSize=1.)

    # Add lines
    lines0 = gmsh.model.geo.add_line(point0, point1)
    lines1 = gmsh.model.geo.add_line(point1, point2)
    lines2 = gmsh.model.geo.add_line(point2, point0)
    lines3 = gmsh.model.geo.add_line(point0, point3)
    lines4 = gmsh.model.geo.add_line(point3, point2)

    # Add triangles
    line_loops = []
    plane_surfaces = []

    line_loops.append(gmsh.model.geo.addCurveLoop([lines0, lines1, lines2]))
    line_loops.append(gmsh.model.geo.addCurveLoop([lines2, lines3, lines4]))

    for j in range(len(line_loops)):
        plane_surfaces.append(gmsh.model.geo.addPlaneSurface([line_loops[j]]))

    # Show and save
    gmsh.model.geo.synchronize()
    gmsh.model.addPhysicalGroup(2, plane_surfaces)
    gmsh.model.geo.synchronize()

    # Generate mesh:
    gmsh.model.mesh.generate(2)

    # Write mesh data:
    gmsh.write("gmsh/Reservoir.msh")

    # Creates  graphical user interface
    """
    if 'close' not in sys.argv:
        gmsh.fltk.run()
    """
    # Finalize the Gmsh API
    gmsh.finalize()

    print(f"gmsh/Reservoir.msh saved")

    return


def build_plate(length, dept):
    """
    Created the gmsh for the build plate and saves it in ./gmsh
    :param length:
    :param dept:
    """
    # Initialize gmsh:
    gmsh.initialize()

    # Useful constant
    y = 0.
    x0 = 0.
    x1 = length
    z0 = 0.
    z1 = dept

    # Add point
    point0 = gmsh.model.geo.addPoint(x0, y, z0, meshSize=1.)
    point1 = gmsh.model.geo.addPoint(x1, y, z0, meshSize=1. )
    point2 = gmsh.model.geo.addPoint(x1, y, z1, meshSize=1.)
    point3 = gmsh.model.geo.addPoint(x0, y, z1, meshSize=1.)

    # Add lines
    lines0 = gmsh.model.geo.add_line(point0, point1)
    lines1 = gmsh.model.geo.add_line(point1, point2)
    lines2 = gmsh.model.geo.add_line(point2, point0)
    lines3 = gmsh.model.geo.add_line(point0, point3)
    lines4 = gmsh.model.geo.add_line(point3, point2)

    # Add triangles
    line_loops = []
    plane_surfaces = []

    line_loops.append(gmsh.model.geo.addCurveLoop([lines0, lines1, lines2]))
    line_loops.append(gmsh.model.geo.addCurveLoop([lines2, lines3, lines4]))

    for j in range(len(line_loops)):
        plane_surfaces.append(gmsh.model.geo.addPlaneSurface([line_loops[j]]))

    # Show and save
    gmsh.model.geo.synchronize()
    gmsh.model.addPhysicalGroup(2, plane_surfaces)
    gmsh.model.geo.synchronize()

    # Generate mesh:
    gmsh.model.mesh.generate(2)

    # Write mesh data:
    gmsh.write("gmsh/Build_plate.msh")

    # Creates  graphical user interface
    """
    if 'close' not in sys.argv:
        gmsh.fltk.run()
    """
    # Finalize the Gmsh API
    gmsh.finalize()

    print(f"gmsh/Build_plate.msh saved")

    return


def separator_1(total_length, dept, gap, after_gap_length, y_min):
    """
    Created the gmsh for the first separator and saves it in ./gmsh
    :param total_length: total length of the separator.
    :param gap: Length of the gap.
    :param after_gap_length: Distance between the end of the gap and the start of the build plate.
    :param dept: Dept of the domain in the z direction.
    :param y_min: Bottom of the domain in the y direction.
    """
    # Initialize gmsh:
    gmsh.initialize()

    # Useful constant
    x0 = 0.
    x3 = total_length
    x2 = x3 - after_gap_length
    x1 = x2 - gap

    # Container
    plane_surfaces = []

    # Before gap
    inverse_U(x0, x1, y_min, dept, plane_surfaces)

    # After gap
    inverse_U(x2, x3, y_min, dept, plane_surfaces)

    # Show and save
    gmsh.model.geo.synchronize()
    gmsh.model.addPhysicalGroup(2, plane_surfaces)
    gmsh.model.geo.synchronize()

    # Generate mesh:
    gmsh.model.mesh.generate(2)

    # Write mesh data:
    gmsh.write("gmsh/Separateur_1.msh")

    # Creates  graphical user interface
    """
    if 'close' not in sys.argv:
        gmsh.fltk.run()
    """
    # Finalize the Gmsh API
    gmsh.finalize()

    print(f"gmsh/Separateur_1.msh saved")

    return


def separator_2(total_length, dept, gap, before_gap_length, y_min):
    """
    Created the gmsh for the first separator and saves it in ./gmsh
    :param total_length: total length of the separator.
    :param gap: Length of the gap.
    :param before_gap_length: Distance between the end of the build plate and the start of the gap.
    :param dept: Dept of the domain in the z direction.
    :param y_min: Bottom of the domain in the y direction.
    """
    # Initialize gmsh:
    gmsh.initialize()

    # Useful constant
    x0 = 0.
    x1 = before_gap_length
    x2 = x1 + gap
    x3 = total_length

    # Container
    plane_surfaces = []

    # Before gap
    inverse_U(x0, x1, y_min, dept, plane_surfaces)

    # After gap
    inverse_U(x2, x3, y_min, dept, plane_surfaces)

    # Show and save
    gmsh.model.geo.synchronize()
    gmsh.model.addPhysicalGroup(2, plane_surfaces)
    gmsh.model.geo.synchronize()

    # Generate mesh:
    gmsh.model.mesh.generate(2)

    # Write mesh data:
    gmsh.write("gmsh/Separateur_2.msh")

    # Creates  graphical user interface
    """
    if 'close' not in sys.argv:
        gmsh.fltk.run()
    """
    # Finalize the Gmsh API
    gmsh.finalize()

    print(f"gmsh/Separateur_2.msh saved")

    return


def inverse_U(x0, x1, y0, z1, plane_surfaces):
    """
    Append plane surface of an inverse U shape separator in the container plane_surfaces
    :param x0: Start of the first wall
    :param x1: Start of the second wall
    :param y0: Bottom of both walls
    :param z1: Dept of the wall
    :param plane_surfaces: Container where plane surfaces are being added.
    """
    # Useful variables
    y1 = z0 = 0
    line_loops = []

    # First wall
    point0 = gmsh.model.geo.addPoint(x0, y0, z0, meshSize=1.)
    point1 = gmsh.model.geo.addPoint(x0, y0, z1, meshSize=1.)
    point2 = gmsh.model.geo.addPoint(x0, y1, z1, meshSize=1.)
    point3 = gmsh.model.geo.addPoint(x0, y1, z0, meshSize=1.)

    # Second wall
    point4 = gmsh.model.geo.addPoint(x1, y0, z0, meshSize=1.)
    point5 = gmsh.model.geo.addPoint(x1, y0, z1, meshSize=1.)
    point6 = gmsh.model.geo.addPoint(x1, y1, z1, meshSize=1.)
    point7 = gmsh.model.geo.addPoint(x1, y1, z0, meshSize=1.)

    # Add lines
    # First wall
    lines0 = gmsh.model.geo.add_line(point0, point1)
    lines1 = gmsh.model.geo.add_line(point1, point2)
    lines2 = gmsh.model.geo.add_line(point2, point0)
    lines3 = gmsh.model.geo.add_line(point0, point3)
    lines4 = gmsh.model.geo.add_line(point3, point2)  # Also top wall

    # Top wall
    lines5 = gmsh.model.geo.add_line(point2, point7)
    lines6 = gmsh.model.geo.add_line(point7, point3 )
    lines7 = gmsh.model.geo.add_line(point7, point6 )  # Also second wall
    lines8 = gmsh.model.geo.add_line(point6, point2 )

    # Second wall
    lines9 = gmsh.model.geo.add_line(point6, point4)
    lines10 = gmsh.model.geo.add_line(point4, point7)
    lines11 = gmsh.model.geo.add_line(point4, point5)
    lines12 = gmsh.model.geo.add_line(point5, point6)

    # Add triangles to the container
    line_loops.append(gmsh.model.geo.addCurveLoop([lines0, lines1, lines2]))
    line_loops.append(gmsh.model.geo.addCurveLoop([lines2, lines3, lines4]))
    line_loops.append(gmsh.model.geo.addCurveLoop([lines4, lines5, lines6]))
    line_loops.append(gmsh.model.geo.addCurveLoop([lines5, lines7, lines8]))
    line_loops.append(gmsh.model.geo.addCurveLoop([lines7, lines9, lines10]))
    line_loops.append(gmsh.model.geo.addCurveLoop([lines9, lines11, lines12]))

    gmsh.model.geo.synchronize()
    for j in range(len(line_loops)):
        plane_surfaces.append(gmsh.model.geo.addPlaneSurface([line_loops[j]]))

    return



