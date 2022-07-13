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


        ## Number of Bibes Histogram
        unique_days = self._unique_days()
        ax = axs[0,0]
        ax.hist(self.dates, bins=unique_days.shape[0])#, bins=n_bibes.shape[0], density=True)
        ax.set_xticklabels(unique_days, rotation=90)
        plt.tight_layout()
        plt.show()
        
    def _unique_days(self):
        unique_days = []
        for d in self.dates:
            if d not in unique_days:
                unique_days.append(d)
        
            
        return np.array(unique_days)

        
