from Nlib import NolanPy

N = NolanPy("https://docs.google.com/spreadsheets/d/11T2xbPFjlk1UI3NbdFFFGPQioUYW1i9S6bakjBpuovY/edit#gid=0")

N.load_data(force=True, verbose=True)
N.plot(show=False)
N.send_email(send=True)
   

