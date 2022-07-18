from Nlib import NolanPy

N = NolanPy("https://docs.google.com/spreadsheets/d/11T2xbPFjlk1UI3NbdFFFGPQioUYW1i9S6bakjBpuovY/edit#gid=0")

N.load_data(force=False, verbose=True)
N.plot(show=True)
N.send_email(receiver_address='simone.vadilonga@gmail.com', send=False)
   