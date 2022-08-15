import gspread
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import numpy as np
import smtplib
from datetime import datetime

from tqdm import tqdm

from email.message import EmailMessage
from email_credentials import Password

class NolanPy:
    """Let Us track Nolan
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
        path = os.path.join('/home/simone/Private/NolanPy/data', filename+'.npy')
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
        print('Downloading Data')
        pbar = tqdm(total=9)
        self.dates = self.load_or_download('dates',1, force=force, verbose=verbose)
        pbar.update(1)
        self.bibe_color = self.load_or_download('bibe_color',2, force=force, verbose=verbose)

        pbar.update(1)
        self.hour_bibe = self.load_or_download('hour_bibe',3, force=force, verbose=verbose)
        pbar.update(1)
        
        self.day_for_plot = self.load_or_download('day_for_plot',4, force=force, verbose=verbose)
        pbar.update(1)
        
        self.size = self.load_or_download('size',5, force=force, verbose=verbose)
        pbar.update(1)
        
        self.time_between_bibes = self.load_or_download('time_between_bibes',6, force=force, verbose=verbose)
        pbar.update(1)
        
        self.bibes_ml = self.load_or_download('bibes_ml',7, force=force, verbose=verbose)
        pbar.update(1)

        self.age_months = self.load_or_download('age_months',10, force=force, verbose=verbose)
        pbar.update(1)
        
        self.weight = self.load_or_download('weight',11, force=force, verbose=verbose)
        pbar.update(1)
        
    def plot(self, show=True):
        # fig, (axs) = plt.subplots(3, 2,figsize=(10,10))
        fig = plt.figure(figsize=(10,10))
        gs = fig.add_gridspec(3,2)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[1, 0])
        ax4 = fig.add_subplot(gs[1, 1])
        ax5 = fig.add_subplot(gs[2, 0])
        ax6 = fig.add_subplot(gs[2, 1])
        unique_days = self._unique_days()
        
        ## Number of Bibes Histogram
        x_labels = unique_days[0::5]
        # ax = axs[0,0]
        ax = ax1
        ax.hist(self.dates, bins=unique_days.shape[0], rwidth=0.8)#, bins=n_bibes.shape[0], density=True)
        x_ticks_pos = ax.get_xticks()
        x_ticks_pos = x_ticks_pos[0::5]
        ax.set_xticks(x_ticks_pos)
        ax.set_xticklabels(x_labels, rotation=90)
        ax.set_title('Drinks vs Day')
        ax.set_ylabel('Number of drinks')

        ## ml drank every day
        # ax = axs[0,1]
        ax = ax2
        dates_ml_bibes, ml_bibes = self.calculate_ml_per_day()
        dates_ml_bibes_plot = np.arange(0,len(dates_ml_bibes))
        ax.plot(dates_ml_bibes_plot,ml_bibes, marker='o')
        
        start_2m = dates_ml_bibes.index("04.05.2022") 
        end_2m   = dates_ml_bibes.index("20.05.2022") 
        start_3m = dates_ml_bibes.index("21.05.2022") 
        end_3m   = dates_ml_bibes.index("20.06.2022") 
        start_4m = dates_ml_bibes.index("21.06.2022") 
        end_4m   = dates_ml_bibes.index("20.07.2022") 
        start_5m = dates_ml_bibes.index("21.07.2022")
        end_5m   = len(dates_ml_bibes) 
        ax.plot((start_2m,end_2m),(0.7,0.7),color='orange', linestyle='dashed')
        ax.plot((start_2m,end_2m),(0.8,0.8),color='orange', linestyle='dashed')
        ax.plot((start_3m,end_3m),(0.13*6,0.13*6),color='pink', linestyle='dashed')
        ax.plot((start_3m,end_3m),(0.13*7,0.13*7),color='pink', linestyle='dashed')
        ax.plot((start_4m,end_4m),(0.17*5,0.17*5),color='g', linestyle='dashed')
        ax.plot((start_4m,end_4m),(0.17*6,0.17*6),color='g', linestyle='dashed')
        ax.plot((start_5m,end_5m),(0.2*4,0.2*4),color='purple', linestyle='dashed')
        ax.plot((start_5m,end_5m),(0.2*5,0.2*5),color='purple', linestyle='dashed')
        xticks_pos = []
        xticks_label = []
        for v,d in enumerate(dates_ml_bibes):
            if v%5==0:
                xticks_pos.append(v)
                xticks_label.append(d)
        ax.set_xticks(xticks_pos)
        ax.set_xticklabels(xticks_label, rotation=90)
        

        ml_bibes_ma       = self._moving_average(ml_bibes,4)
        dates_ml_bibes_plot       = self._moving_average(dates_ml_bibes_plot,4)
        ax.plot(dates_ml_bibes_plot,ml_bibes_ma, 'r', label='moving average')
        ax.set_title('Daily Milk Intake')
        ax.set_ylabel('Milk [litre]')
        ax.legend()

        # bubble plot
        # ax = axs[1,0]
        ax = ax3
        dates, hours, sizes, colors, patches = self._bubble_plot(shift=8)
        #ax.axvline(x=14, ymin=0, ymax=100, color='k', linestyle='dashed', label = '6 hours')

        date_n = np.arange(len(dates))
        ax.scatter(hours, date_n,c=colors, s=sizes)#, s=area, c=colors, alpha=0.5)
        ax.grid(which='both', axis='both')
        x_ticks_pos = [0,2,4,6,8,10,12,14,16,18,20,22,24]
        ax.set_xticks(x_ticks_pos)
        x_ticks_labels = ['16:00','18:00','20:00','22:00','24:00', '02:00','04:00', '06:00', '08:00','10:00','12:00','14:00','16:00']
        ax.set_xticklabels(x_ticks_labels, rotation=45)
        y_ticks_pos = ax.get_yticks()
        y_ticks_pos = np.arange(y_ticks_pos[1], y_ticks_pos[-1], 7)
        ytick_labels = []
        y_ticks_pos_new = []
        for i in y_ticks_pos:
            if i%10==0:
                try:
                    ytick_labels.append(dates[int(i)])
                    y_ticks_pos_new.append(i)
                except IndexError:
                    pass
        ax.set_yticks(y_ticks_pos_new)
        ax.set_yticklabels(ytick_labels)
        ax.set_title('Bibes: Hour vs Day')
        ax.set_xlabel('Time of the Day [h]')
        ax.set_xlim(-1,28)
        ax.legend(handles=patches,fontsize=6)

        # time between bibes
        # ax = axs[1,1]
        ax = ax4
        time_between_bibes = self._time_between_bibe()
        ax.plot(time_between_bibes)
        ax.axhline(y=10, xmin=0, xmax=len(time_between_bibes), color='r', linestyle='dashed', label = '10 hours')
        ax.axhline(y=8, xmin=0, xmax=len(time_between_bibes), color='b', linestyle='dashed', label = '8 hours')
        ax.axhline(y=6, xmin=0, xmax=len(time_between_bibes), color='orange', linestyle='dashed', label = '6 hours')
        xticks_pos = ax.get_xticks()
        xticks_pos_new = np.arange(xticks_pos[1], xticks_pos[-1], 100)
        xticks_labels = []
        for ind,i in enumerate(xticks_pos_new):
            try:
                #print (i)
                xticks_labels.append(dates[int(i+1)])
            except IndexError:
                xticks_pos_new = xticks_pos_new[0:ind]
                break
        ax.set_xticks(xticks_pos_new)
        ax.set_xticklabels(xticks_labels, rotation = 90)   
        
        ax.set_title('Time between bibes')
        ax.set_ylabel('Time [h]')
        ax.legend()
        
        # weight
        ax = ax5
        percentil = self._get_percentil()
        percentil_list = ['3rd', '5th', '10th', '25th','50th', '75th', '90th', '95th', '97th']
        age_months, weight = self._get_Nolan_age_weight()
        ax.plot(age_months, weight, 'r', marker='o', linewidth=3, label='Nolan')
        color_list = ['navy', 'royalblue', 'cornflowerblue', 'lightskyblue', 'grey', 'lightpink', 'hotpink', 'orchid','darkviolet']
        for ind,p in enumerate(percentil_list):
            if p == '50th':
                ls = 'solid'
            else:
                ls = 'dashed'
            ax.plot(percentil[:,0], percentil[:,ind+1], color_list[ind], linestyle=ls, label=p+' percentil')
        ax.legend(loc=4,fontsize=6)
        ax.set_ylabel('Weight [kg]')
        ax.set_xlabel('Age [months]')
        ax.set_xlim(-0.02,age_months[-1]+5 )
        ax.set_ylim(1.8,weight[-1]+4 )
        ax.set_title('Weight Development')
        #ax.set_yscale('log')

        # bottles vs feeding time
        ax=ax6
        ax.hist(hours[-100:], bins=24, rwidth=0.8)#, bins=n_bibes.shape[0], density=True)
        xticks_pos=np.arange(0,24)
        xticks_labels=np.roll(np.arange(0,24),8)
        ax.set_xticks(xticks_pos+0.5)
        ax.set_xticklabels(xticks_labels,rotation = 90)   
        ax.set_title('Drinks vs Hour, since:'+str(dates[-100]))
        ax.set_xlabel('Time of the day [h]')
        ax.set_ylabel('Number of Drinks')
        plt.tight_layout()
        plt.savefig('Nolan.png')
        plt.savefig('Nolan.pdf')

        if show:
            plt.show()
    
    def _get_Nolan_age_weight(self):
        age = []
        weight = []
        for ind,a in enumerate(self.age_months):
            w = self.weight[ind]
            if a =='' or w=='':
                break
            else:
                a = a.replace(',','.')
                w = w.replace(',','.')
                age.append(float(a))
                weight.append(float(w))
                weight

        return age, weight
    
    def _get_percentil(self):
        percentil = np.genfromtxt('/home/simone/Private/NolanPy/data/weight_percentils.csv', delimiter=',')
        return percentil
    
    def _shift_time(self, x, shift):
        if x<(24-shift):
            x += shift
        else:
            x = shift - (24-x)
        return x

    def _time_between_bibe(self):
        _, hours, _, _,_ = self._bubble_plot(shift=0)
        times = []
        for ind in range(1,len(hours)):
            if hours[ind]>hours[ind-1]:
                times.append(hours[ind]-hours[ind-1])
            else:
                b = 24-hours[ind-1]
                times .append(b+hours[ind])
        return times
                
        return
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
                # time = float(self.hour_bibe[ind].replace(':','.'))
                hour, min = self.hour_bibe[ind].split(':')
                hour = int(hour)
                min = int(min)*10/60
                time = hour+min/10
                if shift:
                    time = self._shift_time(time, shift)
                hours.append(time)
                #print("DEBUG:: time", self.hour_bibe[ind],time)
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
        color_palette = ['r', 'g', 'b', 'orange','violet', 'cyan', 'magenta','k', 'purple','brown']
        patches = []
        for ind, c in enumerate(color_palette):
            if ind == 0:
                label=str(ind+1)+'st'
            elif ind == 1:
                label=str(ind+1)+'nd'
            elif ind ==2:
                label=str(ind+1)+'rd'
            else:
                label=str(ind+1)+'th'
            patches.append(mpatches.Patch(color=c, label=label))
        return dates, hours, sizes, colors, patches

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

    def send_email(self, receiver_address='simnur.shared@gmail.com', send =True):
        
        Sender_Email = "simone.vadilonga@gmail.com"
        Reciever_Email = receiver_address
        newMessage = EmailMessage()                         
        newMessage['Subject'] = "Nolan Tracking" 
        newMessage['From'] = Sender_Email                   
        newMessage['To'] = Reciever_Email                   
        newMessage.set_content('Hi,\nthe new Nolan tracking plots are here!') 
        files = ['Nolan.pdf']
        for file in files:
            with open(file, 'rb') as f:
                file_data = f.read()
                file_name = f.name
            newMessage.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
        if send:
            print('Sending results to '+receiver_address)
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(Sender_Email, Password)              
                    smtp.send_message(newMessage)
                print('Email sent to', receiver_address)
                print('Results sent to '+receiver_address)
            except:
                print('Failed sending results to '+receiver_address)
    



                
