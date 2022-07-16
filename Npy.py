import gspread
import string
import matplotlib.pyplot as plt


from Nlib import NolanPy


#gc = gspread.oauth()


#sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/11T2xbPFjlk1UI3NbdFFFGPQioUYW1i9S6bakjBpuovY/edit#gid=0")




N = NolanPy("https://docs.google.com/spreadsheets/d/11T2xbPFjlk1UI3NbdFFFGPQioUYW1i9S6bakjBpuovY/edit#gid=0")

N.load_data(force=False, verbose=True)

N.plot(show=False)
N.send_email2()
   

