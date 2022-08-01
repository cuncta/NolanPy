# Npy

Tracking Nolan development

## Used Python Pakcages
* gspread == 5.4.0
* matplotlib == 3.5.1
* numpy == 1.22.3

## Authorizing Download of google sheet with Token
Follow the instructions [here](https://docs.gspread.org/en/latest/oauth2.html#for-end-users-using-oauth-client-id)

The first time you run the program you will be prompted to google and asked if you want to authorize the app. Once you agree a file `/home/your_user/.config/gspread/authorized_user.json` will be created. 

### Known Problem
After some time the authorization expires, so it has to be renewed. I could not do this automatically yet, so when you don't receive the email anymore just delete the file above and run the program once --> you will be prompted again to google to authorize the app.


## Modify the crontab
`crontab -u username -e`

To run the code everyday at 10.15 add the following line

 `15 10 * * * echo "Executing Npy.py: $(date)" >> /home/simone/Desktop/Private/NolanPy/Npy_log.txt`
`15 10 * * * /home/simone/miniconda3/bin/python /home/simone/Desktop/Private/NolanPy/Npy.py >> /home/simone/Desktop/Private/NolanPy/Npy_log.txt`
`

 And then restart the cron
 
 `sudo systemctl restart cron`

