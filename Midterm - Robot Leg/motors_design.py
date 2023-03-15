import math
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from collections import deque # for animation trace

# need to initialize global to use in animate without taking in as parameters b/c from examples only param can be i to iterate automatically
foot_all_x = []
foot_all_y = []
knee_all_x = []
knee_all_y = []

# function to find the linear piecewise equations based on inputted main points
def find_piecewise_eqs(main_pts):
    # main pts of trajectory (where piecewise fxn changes)
    
    slopes = [] # initialize
    y_ints = []
    
    # find linear piecewise equations (y = mx + b)
    # --- slopes ---
    for i in range(len(main_pts) - 1): # find slope for each of 3 main pieces
        x1 = main_pts[i][0]
        x2 = main_pts[i+1][0]
        y1 = main_pts[i][1]
        y2 = main_pts[i+1][1]
        
        m = (y2 - y1) / (x2 - x1)
        slopes.append(m)
        
        # y_int = b = y - (mx), use first pt of each piece to plug in as x,y
        y_int = y1 - (m * x1)
        y_ints.append(y_int)
        
        print("eq" + str(i+1) + ": y = " + str(m) + "x + " + str(y_int))
    
    return slopes, y_ints

# function to generate foot and knee (x,y) points based on piecewise equations at given interval
# I already made the points I need in Excel, but want to check here
def check_all_pts(main_pts, foots_x, foots_y):
    eq_slopes, eq_y_ints = find_piecewise_eqs(main_pts)
    
    pts_per_dist = 1 # want 1 pt per cm dist the foot moves (total, not component direction)
    
    check_foot_x = []
    check_foot_y = [] # should I make numpy arrays? not sure if need for fxns
    
    # find intermediate points for each piecewise section
    for i in range(len(main_pts) - 1):
        this_main_x = main_pts[i][0]
        this_main_y = main_pts[i][1]
        next_main_x = main_pts[i+1][0]
        next_main_y = main_pts[i+1][1]
        tot_piece_dist = math.sqrt((next_main_x - this_main_x)**2 + (next_main_y - this_main_y)**2)
        
        # start pts for this piece w start main pt for the piece
        check_foot_x.append(this_main_x)
        check_foot_y.append(this_main_y)
        num_pts_this_piece = round(tot_piece_dist * pts_per_dist) # round up or down to closest int
        # get intermediate pts and add end pt only once (so don't add here I think)
        num_intermediate_pts = num_pts_this_piece - 2
        #print("piecewise " + str(i+1) + " has " + str(num_intermediate_pts) + " intermediate pts")
        # get x intervals (need to set this to find y pts from equation, vs doing interval method for y that I did in Google Sheets)
        dist_btwn_x_pts = (next_main_x - this_main_x) / (num_intermediate_pts + 1)
        
        for j in range(num_intermediate_pts):
            x = this_main_x + ((j+1)*dist_btwn_x_pts)
            check_foot_x.append(x)
            y = (eq_slopes[i] * x) + eq_y_ints[i]
            check_foot_y.append(y)
        
    # print rough table
    print("\nfoots x, y")
    for i in range(len(check_foot_x)):
        print(check_foot_x[i], check_foot_y[i])
        
    count_diffs = 0
    # check if any diffs btwn generate x,y data and imported csv (round difference to 5 decimal places in case very small diff in carried numbers causes minimal error
    for i in range(len(check_foot_x)):
        if round(check_foot_x[i] - foots_x[i], 5) != 0:
            count_diffs += 1
        if round(check_foot_y[i] - foots_y[i], 5) != 0:
            count_diffs += 1
    print("\nthere are", count_diffs, "diffs between CSV and calculated foot position data")
    
        
    #print([all_foot_x, all_foot_y])
        
# function to plot basic path without displaying to use for just path and for path with leg positions
def plot_path_bare(main_pts, style):
    x = main_pts[:,0]
    y = main_pts[:,1]
    plt.plot(x,y, label = "Path", linestyle = style)

# function to plot foot path based on inputted list of (x,y) desired points, with labeled main markers
def plot_path(main_pts):
    plot_path_bare(main_pts, '-')
    plt.title("Foot Path")
    for i in range(len(main_pts)):
        x = main_pts[i][0]
        y = main_pts[i][1]
        label = ""
        if i == 0:
            label = "start "
        elif i == len(main_pts) - 1:
            label = "end "
        label += "(" + str(x) + ", " + str(y) + ")"
        plt.text(x, y, label)
    #plt.xlim(-20,20)
    #plt.ylim(-16.4,0)
    
    plt.show()
    
# function to set the plot characteristics for all leg position plots
def set_leg_subplot_params(ax, num_pos): # set num_pos as -1 if not using within loop
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlim((-20,20))
    ax.set_ylim((-17.4,1))
    #ax.set_xlabel('X-Position (cm)') -- switched to super label later
    #ax.set_ylabel('Y-Position (cm)')
    if num_pos != -1:
        ax.set_label("Position " + str(num_pos + 1)) # for good measure so when display legend for all-in-one plot can see all labels, won't show for indiv plots b/c not showing legend
        ax.set_title("Position " + str(num_pos + 1))
    
# function to read in txt file with 4 columns and save each column as a separate numpy array
def read_leg_coords(filename):
    #leg_coords = pd.read_csv(filename)
    leg_coords = np.loadtxt(filename, dtype=float, skiprows=1, delimiter=',') # skip header row
    # each row/outer index is an overall leg position/point in time,
    # inner values are [foot_x, foot_y, knee_x, knee_y]
    foots_x = leg_coords[:,0]
    foots_y = leg_coords[:,1]
    knees_x = leg_coords[:,2]
    knees_y = leg_coords[:,3]
    return leg_coords, foots_x, foots_y, knees_x, knees_y

# function to generate a plot based on inputted (x,y) coordinates for foot and knee (but not show yet, done in functions that use this)
# with proper labels based on inputted index (applies for generating subplots for proper titles related to different plots
def plot_leg_pos(axis, index, foot_x, foot_y, knee_x, knee_y):
    # data = [foot_pos, knee_pos, shoulder_pos]
    # all shoulder positions are the same (x,y) = (0,0), I set as datum and shoulder is stationary
    x = np.array([foot_x,knee_x,0])
    y = np.array([foot_y,knee_y,0])
    
    axis.plot(x,y)
    set_leg_subplot_params(axis, index)
    #plt.show()

# function to make inputted number of subplots based on inputted foot and knee (x,y) coordinates
# used for both making figure of many subplots for separate leg positions
# and making figure of one big plot of overlaying separate leg positions (used subplot for the aspect ratio feature, which I couldn't figure out in plain "plot"
def make_multiple_leg_pos_plots(foots_x, foots_y, knees_x, knees_y, num_rows_plots, num_cols_plots):
    # want rows of plots to fit nicely across screen so
    num_positions = len(foots_x)
    
    #width_oneplot = 40 / 2.54 # inches, bounds are -20,20
    #height_oneplot = 17.4 / 2.54 # inches, bounds are -16.4, 1
    #width_all = width_oneplot * num_cols_plots / 2
    #height_all = height_oneplot * num_rows_plots / 2
    fig, axs = plt.subplots(num_rows_plots, num_cols_plots, sharex=True, sharey=True)#, figsize=(width_all, height_all))
    
    # loop to create array of x,y data for one leg position/point in time and add subplot
    for i in range(num_positions): # loop for each leg position
        # format data from bottom to top (foot_pos, knee_pos, shoulder_pos)
        # shoulder pos is always (x,y) = (0,0) b/c that joint is stationary in time
        ax = axs
        if (num_rows_plots + num_cols_plots) > 2: # only flatten if there is more than one plot
            ax = axs.flat[i] # make sure call ax as input diff than axs b/c if just reassign axs, the first time it doesn't work and get error
        plot_leg_pos(ax, i, foots_x[i], foots_y[i], knees_x[i], knees_y[i])
        # not sure if it is wise to put subplot within plot_leg_pos function, but seems like should keep order of getting (x,y) data, subplot, plot, set params
    #plt.tight_layout()
    #plt.show()
    return ax, fig
    
# function to show each leg position for one swing in separate plots, with 'global' labels (to save space/improve readability)
def display_leg_pos_subplots(foots_x, foots_y, knees_x, knees_y):
    num_positions = len(foots_x)
    num_rows_plots = 3
    num_cols_plots = int((num_positions / num_rows_plots) + 0.5) # add 0.5 so have enough cols if odd num positions
    axis, figure = make_multiple_leg_pos_plots(foots_x, foots_y, knees_x, knees_y, num_rows_plots, num_cols_plots)
    figure.suptitle("Robot Leg Positions For One 5-cm Swing Over Time")
    figure.supxlabel("X-Position (cm)")
    figure.supylabel("Y-Position (cm)")
    plt.show()
    
# function to show all the leg positions on just one plot
def display_leg_pos_all_plot(main_pts, foots_x, foots_y, knees_x, knees_y):
    # plot all leg positions
    axis, figure = make_multiple_leg_pos_plots(foots_x, foots_y, knees_x, knees_y, 1, 1)

    # plot path
    plot_path_bare(main_pts, '--')
    
    # hardcode legend (can't get to work with setting labels during subplots, probably missing some setting b/c all on same figure, not worth time to figure out more just override here)
    labels = []
    for i in range(len(foots_x)):
        labels.append('Position ' + str(i+1))
    labels.append('Path')
    
    plt.legend(labels)
    plt.title('All Leg Positions (with Dash-Line Path)')
    plt.show() # switch to axis from plot so can get proper legend...or else I'll hardcode

# set global variables to be used in animate(i) and animate_leg_expected(),
# since I couldn't figure out how to add more inputs to the animate(i) function besides "i" that don't mess up the automatic iteration of i as the function runs repeatedly
line = ''
trace = ''
history_len = 500
history_x, history_y = deque(maxlen=history_len), deque(maxlen=history_len)

leave_legs = False # switch to True to trace leg positions rather than foot path

# function to generate line and trace for animation of global foot and knee (x,y) points
def animate(i):
    this_foot_x = foot_all_x[i]
    this_foot_y = foot_all_y[i]
    x = np.array([this_foot_x,knee_all_x[i],0])
    y = np.array([this_foot_y,knee_all_y[i],0])
    
    global history_x
    global history_y
    if i==0:
        history_x.clear()
        history_y.clear()
        
    if not leave_legs:
        history_x.appendleft(x[0])
        history_y.appendleft(y[0])
    else:
        history_x.appendleft(x)
        history_y.appendleft(y)
    
    line.set_data(x, y)
    trace.set_data(history_x, history_y)
    return line, trace,


# function to create animation of leg using global foot and knee coordinates, with trace of either foot or leg path
# (change "leave_legs" above previous function to change which part is traced in animation, and all related labels change automatically)
# hardcoding all for now b/c not sure if worth adjusting existing functions...
def animate_leg_expected():
    fig, ax = plt.subplots()
    
    # x,y for first position
    x = np.array([foot_all_x[0],knee_all_x[0],0])
    y = np.array([foot_all_y[0],knee_all_y[0],0])
    global line
    line, = ax.plot(x, y)
    global trace
    trace, = ax.plot(x, y, '.-', lw=1, ms=2)
    
    ms_btwn_frames = 250
    ani = animation.FuncAnimation(fig, animate, len(foot_all_x), interval=ms_btwn_frames, blit=True, save_count=50)
    #global leave_legs
    #leave_legs = True
    #ani_fun = animation.FuncAnimation(fig, animate, len(foot_all_x), interval=50, blit=True, save_count=50)
    set_leg_subplot_params(ax, -1) # num_pos not changing so set as -1
    title_temp = "Robot Leg Positions and "
    trace_legend_temp = "Trace of "
    save_file_temp = r"C:\Users\rckch\Downloads\animation_"
    if not leave_legs:
        title_temp += "Foot Path Over Time"
        trace_legend_temp += "Foot Path"
        save_file_temp += "foot_traced.gif"
    else: # if leave_legs is True
        title_temp += "Path Over Time"
        trace_legend_temp += "Leg Positions"
        save_file_temp += "leg_traced.gif"
    ax.set_title(title_temp)
    ax.set_xlabel('X-Position (cm)')
    ax.set_ylabel('Y-Position (cm)')
    ax.legend(["Robot Leg", trace_legend_temp])
    
    
    # save animation as GIF to my hard drive
    f = save_file_temp # named above based on if want to trace leg or foot path
    #f2 = r"C:\Users\rckch\Downloads\animation2.gif"
    writergif = animation.PillowWriter(fps=1000/ms_btwn_frames) # ms_btwn_frames chosen above for animation, so the GIF saves w leg moving at same speed (diff units here frames-per-second vs. before interval (milliseconds) between position changes)
    ani.save(f, writer=writergif)
    #ani_fun.save(f2, writer=writergif)
    
    plt.show()


def main():
    main_points = np.array([[-1, -16.4], [0, -12], [9.7, -12], [10.7, -16.4]])
    
    piecewise_slopes, piecewise_y_ints = find_piecewise_eqs(main_points)
    
    plot_path(main_points)
    
    # add code:
    # function to loop plot leg pos for all pts (decide how to structure array inputs by foot/knee/shldr or x,y)
    # and save those to display in (1) subplots separately (2) same plot overlayed with path underneath
    # so also need to use function to plot path from above, maybe take show out so show until funciton w path underneath
    global foot_all_x
    global foot_all_y
    global knee_all_x
    global knee_all_y # set these variables to be used globally by 'animate' later...not sure if will mess with returns so far but I think this is the only place I modify (and need to therefore declare global), vs. just use
    all_leg_coords, foot_all_x, foot_all_y, knee_all_x, knee_all_y = read_leg_coords(r'C:\Users\rckch\Downloads\me35_midterm_armxycoords.csv')
    
    display_leg_pos_subplots(foot_all_x, foot_all_y, knee_all_x, knee_all_y)    
    
    display_leg_pos_all_plot(main_points, foot_all_x, foot_all_y, knee_all_x, knee_all_y)

    animate_leg_expected()
    
    check_all_pts(main_points, foot_all_x, foot_all_y)

main()




