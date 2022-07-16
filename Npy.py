from Nlib import NolanPy

N = NolanPy("https://docs.google.com/spreadsheets/d/11T2xbPFjlk1UI3NbdFFFGPQioUYW1i9S6bakjBpuovY/edit#gid=0")

N.load_data(force=True, verbose=True)
N.plot(show=False)
N.send_email(receiver_address='simnur.shared@gmail.com',send=True)
N.send_email(receiver_address='gloriana.rangone@gmail.com',send=True)
   

