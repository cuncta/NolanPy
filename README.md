# Npy

Tracking Nolan development


## Modify the crontab
`crontab -u username -e`

To run the code everyday at 10.15 add the following line

 `15 10 * * * echo "Executing Npy.py: $(date)" >> /home/simone/Desktop/Private/NolanPy/Npy_log.txt`
`15 10 * * * /home/simone/miniconda3/bin/python /home/simone/Desktop/Private/NolanPy/Npy.py >> /home/simone/Desktop/Private/NolanPy/Npy_log.txt`
`

 And then restart the cron
 
 `sudo systemctl restart cron`
