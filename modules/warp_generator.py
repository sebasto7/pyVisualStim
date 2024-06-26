
#!/usr/bin/env python
# -*- coding: utf-8 -*-






import numpy as np
import os

import numpy as np

import numpy as np

def spherical_projection(x, y, screen_width_cm, screen_height_cm, distance_to_viewer_cm):
    """Convert screen coordinates (x, y) to spherical coordinates (u, v)"""
    # Map screen coordinates to a sphere
    x = (x - screen_width_cm / 2) / (screen_width_cm / 2)
    y = (y - screen_height_cm / 2) / (screen_height_cm / 2)
    
    z = np.sqrt(1 - x**2 - y**2)
    
    # Viewer is at (0, 0, distance_to_viewer_cm)
    distance = np.sqrt(x**2 + y**2 + z**2)
    
    theta = np.arctan2(y, x)
    phi = np.arccos(z / distance)
    
    u = 0.5 + theta / (2 * np.pi)
    v = 0.5 - phi / np.pi
    
    return u, v

def generate_warpfile(screen_width_cm, screen_height_cm, screen_width_px, screen_height_px, distance_to_viewer_cm, filename):
    """Generate a warpfile with a spherical projection."""
    mesh_type = 2  # rectangular mesh
    
    # Calculate the number of nodes based on pixel dimensions
    nx = screen_width_px
    ny = screen_height_px

    with open(filename, 'w') as file:
        file.write(f"{mesh_type}\n")
        file.write(f"{nx} {ny}\n")
        
        for i in range(ny):
            for j in range(nx):
                # Calculate physical position on the screen in cm
                x = (j / (nx - 1)) * screen_width_cm
                y = (i / (ny - 1)) * screen_height_cm
                
                # Normalize x and y to [-1, 1]
                norm_x = (x / screen_width_cm) * 2 - 1
                norm_y = (y / screen_height_cm) * 2 - 1
                
                # Get texture coordinates using spherical projection
                u, v = spherical_projection(x, y, screen_width_cm, screen_height_cm, distance_to_viewer_cm)
                
                # Full intensity for each node
                intensity = 1
                
                # Write node data to the file
                file.write(f"{norm_x} {norm_y} {u} {v} {intensity}\n")

# Example usage
screen_width_cm = 9  # width of the screen in cm
screen_height_cm = 9  # height of the screen in cm
screen_width_px = 800  # width of the screen in pixels
screen_height_px = 400  # height of the screen in pixels
distance_to_viewer_cm = 5.36  # distance from the viewer to the screen in cm



# Save warp data to a text file
dataPath = r'C:\Users\smolina\Documents\GitHub\pyVisualStim\warp_files'
fileName = 'spherical_warpfile.txt'
filePath = os.path.join(dataPath, fileName)

generate_warpfile(screen_width_cm, screen_height_cm, screen_width_px, screen_height_px, distance_to_viewer_cm, filePath)





###################################### Warping with PsychoPy's Warper class ####################################
###############################################################################################################

# import psychopy
# import os
# from psychopy import visual, monitors
# from psychopy.visual.windowwarp import Warper



# def extract_mapping_data(warper, filename):
#     """Extract and save the mapping data from the Warper object to a file."""
#     if hasattr(warper, 'vertices') and hasattr(warper, 'tcoords'):
#         vertices = warper.vertices
#         tcoords = warper.tcoords

#         # Combine vertices and tcoords into a single array
#         mapping_data = np.hstack((vertices, tcoords))

#         # Save the mapping data to a file
#         np.savetxt(filename, mapping_data, fmt='%.10f', header='2\n{} {}'.format(warper.warpGridsize, warper.warpGridsize))

#         print(f"Mapping data saved to '{filename}'")
#     else:
#         print("Error: The Warper object does not have the required attributes.")

#     return mapping_data



# mon = monitors.Monitor('dlp', width=9, distance=5.3)

# # Create a Window
# win = visual.Window(monitor=mon, screen=1, fullscr=True, useFBO=True)

# # Instantiate the Warper object with 'spherical' warp
# warper = Warper(win,
#                 warp='spherical',
#                 warpfile='',
#                 warpGridsize=128,
#                 eyepoint=[0.5, 0.5],
#                 flipHorizontal=False,
#                 flipVertical=False)
# #Checking attribute

# attributes = dir(warper)

# # Print all attributes
# print("All attributes and methods of the Warper object:")
# for attr in attributes:
#     print(attr)

# #Print warpfile

# print(warper.warpfile)
# attribute_value = getattr(warper, 'warpfile')
# print(attribute_value)

# # Save warp data to a text file
# dataPath = r'C:\Users\smolina\Documents\GitHub\pyVisualStim\warp_files'
# fileName = 'spherical_warpfile.txt'
# filePath = os.path.join(dataPath, fileName)

# Extract and save the mapping data to a file
#mapping_data = extract_mapping_data(warper, filePath)
#print(mapping_data)


###############################################################################################################




# import numpy as np
# import matplotlib.pyplot as plt
# import os

# ###################################### Warping for PsychoPy's Warper class ####################################
# ###############################################################################################################

# # Example parameters (adjust according to your needs)
# cols = 400  # Number of columns in the grid
# rows = 800  # Number of rows in the grid
# eyepoint = (0.5, 0.5)  # Eyepoint coordinates as fraction of screen width and height

# # Generate warp data for spherical projection
# warpdata = np.zeros((cols * rows, 5))  # 5 columns: x, y, u, v, opacity

# for y in range(rows):
#     for x in range(cols):
#         index = y * cols + x

#         # Normalized coordinates
#         normalized_x = 2.0 * x / (cols - 1) - 1.0
#         normalized_y = 2.0 * y / (rows - 1) - 1.0

#         # Calculate spherical projection
#         radius = np.sqrt(normalized_x**2 + normalized_y**2)
#         theta = np.arctan2(normalized_y, normalized_x)

#         # Apply spherical correction
#         if radius > 1.0:
#             warpdata[index, 0] = normalized_x
#             warpdata[index, 1] = normalized_y
#         else:
#             warpdata[index, 0] = normalized_x * np.sqrt(1.0 - radius**2)
#             warpdata[index, 1] = normalized_y * np.sqrt(1.0 - radius**2)

#         # Texture coordinates (u, v)
#         warpdata[index, 2] = x / (cols - 1)  # u coordinate
#         warpdata[index, 3] = y / (rows - 1)  # v coordinate

#         # Opacity (default to 1.0 if not needed)
#         warpdata[index, 4] = 1.0

# # Save warp data to a text file
# dataPath = r'C:\Users\smolina\Documents\GitHub\pyVisualStim\warp_files'
# fileName = 'spherical_warpfile.txt'
# filePath = os.path.join(dataPath, fileName)

# with open(filePath, 'w') as f:
#     # Write header (filetype and dimensions)
#     f.write('2\n')  # filetype 2
#     f.write(f'{cols} {rows}\n')  # columns and rows

#     # Write warp data
#     for i in range(cols * rows):
#         f.write(f'{warpdata[i, 0]} {warpdata[i, 1]} {warpdata[i, 2]} {warpdata[i, 3]} {warpdata[i, 4]}\n')

# print(f'Warpfile "{fileName}" generated successfully.')

# #%%
# # Visualization of the warp
# # Read cols and rows from the first two lines of the warpfile
# with open(filePath, 'r') as f:
#     # Read the first line (header)
#     header = int(f.readline().strip())
        
#     # Read the second line (cols and rows)
#     cols, rows = map(int, f.readline().strip().split())

# # Load warpdata skipping the first two header lines
# warpdata = np.loadtxt(filePath, skiprows=2)

# # Check if dimensions match
# assert warpdata.shape == (cols * rows, 5), "Mismatch between dimensions in header and data"

# # Create meshgrid for plotting
# x_coords = warpdata[:, 0].reshape((rows, cols))
# y_coords = warpdata[:, 1].reshape((rows, cols))
# u_coords = warpdata[:, 2].reshape((rows, cols))
# v_coords = warpdata[:, 3].reshape((rows, cols))



# plt.figure(figsize=(12, 6))

# # Plot 1: Vertex Positions (x, y) with texture coordinate u
# plt.subplot(1, 2, 1)
# plt.imshow(u_coords, cmap='viridis', extent=[x_coords.min(), x_coords.max(), y_coords.min(), y_coords.max()])
# plt.colorbar(label='Texture Coordinate u')
# plt.title('Vertex Positions (x, y) with Texture Coordinate u')
# plt.xlabel('Vertex Position x')
# plt.ylabel('Vertex Position y')
# plt.axis('equal')

# # Plot 2: Vertex Positions (x, y) with texture coordinate v
# plt.subplot(1, 2, 2)
# plt.imshow(v_coords, cmap='viridis', extent=[x_coords.min(), x_coords.max(), y_coords.min(), y_coords.max()])
# plt.colorbar(label='Texture Coordinate v')
# plt.title('Vertex Positions (x, y) with Texture Coordinate v')
# plt.xlabel('Vertex Position x')
# plt.ylabel('Vertex Position y')
# plt.axis('equal')

# plt.tight_layout()
# plt.show()








########################################### Other option to generate warp files ###############################
###############################################################################################################

# def generate_ellipsoid_warp_grid(grid_size, width_ratio=1.0, height_ratio=1.0):
#     x = np.linspace(-1, 1, grid_size)
#     y = np.linspace(-1, 1, grid_size)
#     grid_x, grid_y = np.meshgrid(x, y)
    
#     # Ellipsoid (spherical if width_ratio == height_ratio) transformation
#     r = np.sqrt(grid_x**2 + (grid_y * height_ratio / width_ratio)**2)
#     with np.errstate(invalid='ignore'):  # Ignore invalid values during sqrt calculation
#         warped_x = grid_x * np.sqrt(1 - (grid_y**2) / (height_ratio**2))
#         warped_y = grid_y * np.sqrt(1 - (grid_x**2) / (width_ratio**2))
    
#     # Handle the NaNs resulting from the sqrt of negative numbers
#     warped_x[np.isnan(warped_x)] = 0
#     warped_y[np.isnan(warped_y)] = 0
    
#     # Normalize warped coordinates to keep them within [-1, 1] range
#     max_x = np.max(np.abs(warped_x))
#     max_y = np.max(np.abs(warped_y))
#     warped_x /= max_x
#     warped_y /= max_y
    
#     return grid_x, grid_y, warped_x, warped_y

# grid_size = 300
# original_x, original_y, warp_x, warp_y = generate_ellipsoid_warp_grid(grid_size)


# # Visualize the original and warped grids
# fig, ax = plt.subplots(1, 2, figsize=(12, 6))

# # Original grid
# ax[0].scatter(original_x, original_y, c='blue', s=1)
# ax[0].set_title('Original Grid')
# ax[0].set_aspect('equal')

# # Warped grid
# ax[1].scatter(warp_x, warp_y, c='red', s=1)
# ax[1].set_title('Warped Grid (Ellipsoid)')
# ax[1].set_aspect('equal')

# plt.show()

# # Save the warp grid to a file
# dataPath = r'C:\Users\smolina\Documents\GitHub\pyVisualStim\warp_files'
# fileName = 'spherical_warp_grid.npy' # 'ellipsoid_warp_grid.npy'
# filePath = os.path.join( dataPath, fileName)
# warp_grid = np.stack((warp_x, warp_y), axis=-1)
# np.save(filePath, warp_grid)

# #Exploring the file
# data = np.load(filePath)
# print(data)


# ###############################################################################################################

# %%
