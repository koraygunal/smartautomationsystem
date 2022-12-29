import random
from itertools import count
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

plt.style.use('fivethirtyeight')  #https://matplotlib.org/stable/gallery/style_sheets/fivethirtyeight.html

x_vals = []
y_vals = []


#we want to run and show program forever.With this function we can do it.

def animate(i):
    data = pd.read_csv('20221116N1.csv')  #convert to pandas
    index=len(data.index)                     #I used the sample of data for x axis.
    #y1 = data['Temperature']
    x = data['D_N']                          #How many data we have
    y2 = data['TMP']                  #Temperature measurements.

    plt.cla()

    #plt.plot(x, y1, label='Channel 1')
    plt.plot(x, y2, label='Channel 2')

    plt.legend(loc='upper left')
    plt.tight_layout()


ani = FuncAnimation(plt.gcf(), animate, interval=2000)

plt.tight_layout()
plt.show()




