# Npy

Tracking Nolan development


## Modify the crontab
`crontab -e`

To run the code everyday at 10.15 add the following line

 `15 10 * * * /home/simone/miniconda3/bin/python /home/simone/Desktop/Private/NolanPy/Npy.py`

 And then restart the cron
 
 `sudo systemctl restart cron`
