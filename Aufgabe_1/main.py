# main.py

import numpy as np
import matplotlib.pyplot as plt
import xlsxwriter

# Enable LaTeX in matplotlib
plt.rcParams['text.usetex'] = True

import model
import solver

def run_simulation():
    # Parameters
    m = 1.0      # mass (kg)
    k = 100000.0     # stiffness (N/m)
    d = 0.01      # damping coefficient

    # initial conditions
    iniStates = np.array([1.0, 0.0])

    # Time parameters
    t_final = 1.0
    dt = 0.0001
    num_steps = int(t_final / dt)

    # Create a model (SingleMassOscillator)
    myModel = model.SingleMassOscillator(iniStates, m, k, d)

    # Create a solver
    mySolver = solver.SolverExplicit(myModel)

    # Arrays to store time and position for plotting
    times = np.linspace(0, t_final, num_steps)
    positions = np.zeros_like(times)

    # Simulation loop
    for step in range(num_steps):
        t = step * dt
        # Store the current position for plotting
        positions[step] = myModel.get_state()[0]
        
        # Take a time step
        mySolver.step(t, dt)

    # Plotting the result
    plt.plot(times, positions)

    # Create a model (SingleMassOscillator)
    myModel = model.SingleMassOscillator(iniStates, m, k, d)

    # Create a solver
    mySolver = solver.SolverImplicit(myModel)

    # Arrays to store time and position for plotting
    times = np.linspace(0, t_final, num_steps)
    positions = np.zeros_like(times)

    # Simulation loop
    for step in range(num_steps):
        t = step * dt
        # Store the current position for plotting
        positions[step] = myModel.get_state()[0]
        
        # Take a time step
        mySolver.step(t, dt)

    # Plotting the result
    plt.plot(times, positions)
    plt.xlabel('Time (s)')
    plt.ylabel('Position (m)')
    plt.title('Single Mass Oscillator')
    plt.show()

    # Output results to an Excel file
    output_to_excel(times, positions)

def output_to_excel(time_array, position_array):
    # Create a new workbook and add a worksheet
    workbook = xlsxwriter.Workbook('simulation_results_xlsxwriter.xlsx')
    worksheet = workbook.add_worksheet()

    # Define headers
    headers = ["Time", "Position"]

    # Write the headers
    for col_num, header in enumerate(headers):
        worksheet.write(0, col_num, header)

    # Write the NumPy arrays to the worksheet
    for row_num in range(len(time_array)):
        worksheet.write(row_num + 1, 0, time_array[row_num])      # Time
        worksheet.write(row_num + 1, 1, position_array[row_num])  # Position

    # Close the workbook (this saves the file)
    workbook.close()

if __name__ == "__main__":
    run_simulation()
