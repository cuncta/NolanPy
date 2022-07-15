import gspread
import string
import matplotlib.pyplot as plt
import os
import numpy as np


class NolanPy:
    """RayUIRunner class implements all logic to start a RayUI process
    """
    def __init__(self, url) -> None:
        self.url = url
        if not os.path.isdir('data'):
            os.makedirs('data')
        self.connected = False
        
    def connect(self):
        self.gc = gspread.oauth()
        self.sh = self.gc.open_by_url(self.url)
        self.connected = True
        
    
    def load_or_download(self, filename, column, force=False,verbose=False):
        path = os.path.join('data', filename+'.npy')
        if os.path.exists(path) and force==False:
            self.data = np.load(path)
            if verbose:
                print('loading', filename)
        else:
            if verbose:
                print('downloading', filename)
            if self.connected == False:
                self.connect()
            self.data = np.array(self.sh.sheet1.col_values(column)[1:])
            np.save(path, self.data)
        return self.data
        
    
    def load_data(self, force=False,verbose=False):
        self.dates = self.load_or_download('dates',1, force=force, verbose=verbose)
        
        self.bibe_color = self.load_or_download('bibe_color',2, force=force, verbose=verbose)
        
        self.hour_bibe = self.load_or_download('hour_bibe',3, force=force, verbose=verbose)
        
        self.day_for_plot = self.load_or_download('day_for_plot',4, force=force, verbose=verbose)
        
        self.size = self.load_or_download('size',5, force=force, verbose=verbose)
        
        self.time_between_bibes = self.load_or_download('time_between_bibes',6, force=force, verbose=verbose)
        
        self.bibes_ml = self.load_or_download('bibes_ml',7, force=force, verbose=verbose)

        self.age_months = self.load_or_download('age_months',10, force=force, verbose=verbose)
        
        self.weight = self.load_or_download('weight',11, force=force, verbose=verbose)
        
    def plot(self):
        fig, (axs) = plt.subplots(4, 2,figsize=(10,10))

        unique_days = self._unique_days()
        ## Number of Bibes Histogram
        
        x_labels = unique_days[0::3]
        ax = axs[0,0]
        ax.hist(self.dates, bins=unique_days.shape[0], rwidth=0.8)#, bins=n_bibes.shape[0], density=True)
        x_ticks_pos = ax.get_xticks()
        x_ticks_pos = x_ticks_pos[0::3]
        ax.set_xticks(x_ticks_pos)
        ax.set_xticklabels(x_labels, rotation=90)

        ## ml drank every day
        ax = axs[0,1]
        dates_ml_bibes, ml_bibes = self.calculate_ml_per_day()
        ax.scatter(dates_ml_bibes, ml_bibes)

        x_labels = dates_ml_bibes[0::3]
        x_ticks_pos = ax.get_xticks()
        x_ticks_pos = x_ticks_pos[0::3]
        ax.set_xticks(x_ticks_pos)
        ax.set_xticklabels(x_labels, rotation=90)

        ml_bibes_ma       = self._moving_average(ml_bibes,4)
        ax.plot(ml_bibes_ma, 'r', label='moving average')

        # bubble plot
        ax = axs[1,0]
        dates, hours, sizes, colors = self._bubble_plot(shift=8)
        date_n = np.arange(len(dates))
        ax.scatter(hours, date_n,c=colors, s=sizes)#, s=area, c=colors, alpha=0.5)
        ax.grid(which='both', axis='both')
        x_ticks_pos = ax.get_xticks()
        x_ticks_labels = ['',16, 21, 1, 6, 11, '']
        ax.set_xticklabels(x_ticks_labels)
        y_ticks_pos = ax.get_yticks()
        print(y_ticks_pos)
        y_ticks_pos = np.arange(y_ticks_pos[1], y_ticks_pos[-1], 7)
        ytick_labels = []
        for i in y_ticks_pos:
            try:
                ytick_labels.append(dates[int(i)])
            except IndexError:
                pass
        ax.set_yticklabels(ytick_labels)
        ax.set_xlabel('Hour')
        plt.tight_layout()
        plt.show()
        
    def _shift_time(self, x, shift):
        if x<(24-shift):
            x += shift
        else:
            x = shift - (24-x)
        return x




    def _bubble_plot(self, shift = 0):
        dates  = []
        sizes  = []
        hours  = []
        colors = []
        if len(self.size) < len(self.dates):
            r = len(self.size)
        else:
            r = len(self.dates)
        
        previous_date = self.dates[0]
        color_palette = ['r', 'g', 'b', 'orange','violet', 'cyan', 'magenta','k', 'purple','brown']
        color_ind = 0
        for ind in range(r-1):
            try:
                # bibe ml
                bibe_ml = self.size[ind].replace(',','.')                        
                bibe_ml = float(bibe_ml)
                #dates
                dates.append(self.dates[ind])
                # sizes
                sizes.append((bibe_ml*40)**2)
                # time
                time = float(self.hour_bibe[ind].replace(':','.'))
                if shift:
                    time = self._shift_time(time, shift)
                hours.append(time)
                # colors
                #print('date',self.dates[ind],'previous',previous_date)
                if self.dates[ind]==previous_date:
                    colors.append(color_palette[color_ind])
                    color_ind += 1
                else:
                    color_ind = 0
                    colors.append(color_palette[color_ind])
                    color_ind +=1
                previous_date = self.dates[ind]
            except ValueError:
                break
        return dates, hours, sizes, colors

    def calculate_ml_per_day(self):
        ml_bibes = []
        dates = [self.dates[0]]
        date_before = self.dates[1]
        temp_ml = 0
        for ind,bibe_ml in enumerate(self.size):
            try:
                bibe_ml = bibe_ml.replace(',','.')                        
                bibe_ml = float(bibe_ml)
            except ValueError:
                break
            if self.dates[ind] == date_before:
                temp_ml +=  bibe_ml
            else:
                ml_bibes.append(temp_ml)
                temp_ml = bibe_ml
                date_before = self.dates[ind]
                dates.append(self.dates[ind])
        if len(dates)!= len(ml_bibes):
            dates = dates[:-1]
        return dates, ml_bibes
    
    def _moving_average(self, x, w):
        if w == 0:
            return x
        return np.convolve(x, np.ones(w), 'valid') / w


    def _unique_days(self):
        unique_days = []
        for d in self.dates:
            if d not in unique_days:
                unique_days.append(d)
        
            
        return np.array(unique_days)

        