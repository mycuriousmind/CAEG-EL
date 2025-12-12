from solid2 import *
import math

def create_bolt(head_radius, head_height, bolt_radius, bolt_length):
    """
    Creates a bolt with a hexagonal head and a cylindrical body.
    
    Args:
        head_radius (float): Radius of the hex head.
        head_height (float): Height of the hex head.
        bolt_radius (float): Radius of the bolt shaft.
        bolt_length (float): Length of the bolt shaft.
        
    Returns:
        SolidPython2 object
    """
    # Hexagonal head (_fn=6)
    head = cylinder(r=head_radius, h=head_height, _fn=6)
    
    # Bolt body (cylindrical, _fn=100 for smoothness)
    # Using a simple cylinder for the threaded body as per standard CAD simplified representation
    body = cylinder(r=bolt_radius, h=bolt_length, _fn=100)
    
    # Translate body to sit on top of the head
    # Alternatively, the head is usually at the "top" z-wise or "bottom" depending on orientation.
    # Here we stack them: Head at Z=0 to Z=head_height, Body from Z=head_height upwards.
    assembly = head + body.up(head_height)
    
    return assembly

def create_flange(flange_radius, pipe_radius, thickness, num_holes):
    """
    Creates a flange: a disk with a central hole and a circular array of bolt holes.
    
    Args:
        flange_radius (float): Outer radius of the flange.
        pipe_radius (float): Radius of the central pipe hole.
        thickness (float): Thickness of the flange.
        num_holes (int): Number of bolt holes in the circular array.
        
    Returns:
        SolidPython2 object
    """
    # Main disk
    base = cylinder(r=flange_radius, h=thickness, _fn=100)
    
    # Central hole (make it slightly taller to ensure clean subtraction)
    epsilon = 0.1
    central_hole = cylinder(r=pipe_radius, h=thickness + 2*epsilon, _fn=100).down(epsilon)
    
    # Calculate bolt circle radius (halfway between pipe and flange edge)
    bolt_circle_radius = (flange_radius + pipe_radius) / 2.0
    
    # Bolt hole size (estimated as proportional to width if not specified, or fixed)
    # Heuristic: 1/5th of the rim width
    hole_radius = (flange_radius - pipe_radius) * 0.15
    if hole_radius <= 0:
        hole_radius = 1 # Fallback
        
    bolt_holes = []
    angle_step = 360.0 / num_holes
    
    for i in range(num_holes):
        angle = i * angle_step
        # Create a hole, translate to bolt circle radius, then rotate
        hole = cylinder(r=hole_radius, h=thickness + 2*epsilon, _fn=100).down(epsilon)
        positioned_hole = hole.right(bolt_circle_radius).rotate([0, 0, angle])
        bolt_holes.append(positioned_hole)
        
    # Subtract central hole and keyholes from base
    result = base - central_hole
    for h in bolt_holes:
        result -= h
        
    return result

def create_nut(inner_radius, outer_radius, thickness):
    """
    Creates a hex nut.
    
    Args:
        inner_radius (float): Radius of the threaded hole.
        outer_radius (float): Outer radius of the hex shape.
        thickness (float): Height of the nut.
        
    Returns:
        SolidPython2 object
    """
    # Hex shape
    hex_body = cylinder(r=outer_radius, h=thickness, _fn=6)
    
    # Inner hole
    epsilon = 0.1
    hole = cylinder(r=inner_radius, h=thickness + 2*epsilon, _fn=100).down(epsilon)
    
    return hex_body - hole

def create_washer(inner_radius, outer_radius, thickness):
    """
    Creates a flat washer.
    
    Args:
        inner_radius (float): Radius of the hole.
        outer_radius (float): Outer radius of the washer.
        thickness (float): Thickness of the washer.
        
    Returns:
        SolidPython2 object
    """
    # Main disk
    disk = cylinder(r=outer_radius, h=thickness, _fn=100)
    
    # Central hole
    epsilon = 0.1
    hole = cylinder(r=inner_radius, h=thickness + 2*epsilon, _fn=100).down(epsilon)
    
    return disk - hole

def create_bracket(length, width, height, thickness):
    """
    Creates an L-shaped bracket made of cubes.
    
    Args:
        length (float): Length of the base leg (X direction).
        width (float): Width of the bracket (Y direction).
        height (float): Height of the upright leg (Z direction).
        thickness (float): Thickness of the material.
        
    Returns:
        SolidPython2 object
    """
    # Base leg (flat on ground)
    # Dimensions: length x width x thickness
    base = cube([length, width, thickness])
    
    # Upright leg (standing up)
    # Dimensions: thickness x width x height
    # Positioned at the start of the base (x=0) or end? Usually corner.
    # Let's place it at x=0.
    upright = cube([thickness, width, height])
    
    # Union them
    return base + upright

if __name__ == "__main__":
    # Example usage / Test
    # This block allows executing the file to generate SCAD code for testing
    print("Generating SCAD code for examples...")
    
    bolt = create_bolt(head_radius=10, head_height=5, bolt_radius=5, bolt_length=30)
    # scad_render prints or returns the code. SolidPython2 usually uses .save_as_scad() on objects or print(scad_render(obj))
    # We will print it to stdout for verification.
    try:
        print("\n--- BOLT SCAD ---")
        print(scad_render(bolt))
        
        flange = create_flange(flange_radius=50, pipe_radius=20, thickness=5, num_holes=6)
        print("\n--- FLANGE SCAD ---")
        print(scad_render(flange))
        
    except NameError:
        print("SolidPython2 not fully installed or scad_render not available in this context.")
