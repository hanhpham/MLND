import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# Setup a plot such that only the bottom spine is shown
def setup(ax):
    ax.spines['right'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.yaxis.set_major_locator(ticker.NullLocator())
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.tick_params(which='major', width=1.00)
    ax.tick_params(which='major', length=5)
    ax.set_xlim(-12, 12)
    ax.set_ylim(0, 4)
    ax.patch.set_alpha(0.0)

def plot_ranges(show_error_distance_map=False):    
    plt.figure(figsize=(16, 16))
    n = 4 if show_error_distance_map else 8

    # Fixed Locator
    ax = plt.subplot(n, 1, 2)
    setup(ax)
    majors = [-100, -10, -5, -1, 1, 5, 10, 100]
    ax.xaxis.set_major_locator(ticker.FixedLocator(majors))
    ax.text(0.45, -0.25, "Percentage Change", fontsize=14,
            transform=ax.transAxes)

    ax.annotate("", xy=(12, 0), xytext=(11.8, 0), arrowprops=dict(arrowstyle="->"))
    ax.annotate("", xy=(-12, 0), xytext=(-11.8, 0), arrowprops=dict(arrowstyle="->"))

    # plot endpoints
    endpoints_open = [(-10,0.6), (-5,0.4), (-1,0.2), (1,0.2), (5, 0.4), (10,0.6)]
    endpoints_closed = [(-10,0.8), (-5, 0.6), (-1, 0.4), (1, 0.4), (5, 0.6), (10, 0.8)]
    for (x,y) in endpoints_open:
        plt.plot(x, y, 'ko', fillstyle = 'none', markersize = 10.0)
    for (x,y) in endpoints_closed:                                                                                                                                      
        plt.plot(x, y, 'ko', fillstyle = 'full', markersize = 10.0)  

    # plot lines
    # coords = [[(-12,0.6), (-10,0.6)]] #, [(-10, 0.4),(-5, 0.4)], [(-5,0.2),(-1,0.2)]] #, [(-1,0),(1,0)], [(1,0.2),(5,0.2)], [(5,0.4),(10, 0.4)], [(10,0.6), (12, 0.6)]]
    coords = [[[-12, -10], [0.8, 0.8], '#ff000d'], #bright red
              [[-10, -5], [0.6, 0.6], '#ff474c'], #light red
              [[-5, -1], [0.4, 0.4], '#ff796c'], #salmon
              [[-1, 1], [0.2, 0.2], 'gray'],
              [[12, 10], [0.8, 0.8], 'green'], 
              [[10, 5], [0.6, 0.6], '#80f9ad'], #light teal
              [[5, 1], [0.4, 0.4], '#90e4c1']] #seafoam

    for line in coords:
        plt.plot(np.array(line[0]), np.array(line[1]), color=line[2], linestyle='-', linewidth = 3.5, fillstyle = 'full', markersize = 10.0)

    ax.annotate("", xy=(12, 0.8), xytext=(11.8, 0.8), color='#ff000d', arrowprops=dict(arrowstyle="->"))
    ax.annotate("", xy=(-12, 0.8), xytext=(-11.8, 0.8), color='green', arrowprops=dict(arrowstyle="->"))
 
    if show_error_distance_map:
        y_err = 3.0
        ax.text(0.45, 1.0, "Change Grades", fontsize=14, color = 'blue', transform=ax.transAxes)
        ax.annotate("", xy=(-12, y_err), xytext=(0.1, y_err), color='blue', arrowprops=dict(arrowstyle="->"))
        ax.annotate("", xy=(12, y_err), xytext=(0, y_err), color='blue', arrowprops=dict(arrowstyle="->"))

        for (x,y) in endpoints_open:
            plt.plot(x, y_err, 'k|', fillstyle = 'none', markersize = 10.0)
        
        x = np.array([ -11, -7.5, -3, 0, 3, 7.5, 11])
        s = np.array(["-3", "-2", "-1", "0", "1", "2", "3"])
        for i in range(0, len(x)): 
            t = ax.text(x[i], y_err+0.15, s[i], ha="center", va="center", size=12, color='blue')
    
    return plt

plt = plot_ranges(True)
plt.show()