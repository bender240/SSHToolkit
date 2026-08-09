ONLY FOR USE ON AUTHORIZED SYSTEMS FOR THE PURPOSES OF PENETRATION TESTING. 



INSTALL INSTRUCTIONS:

git clone https://github.com/bender240/SSHToolkit

cd SSHToolkit

chmod +x install.sh

./install.sh
OR
sudo bash install.sh 

cd /opt/SSHToolkit

RUN:

python3 crawler.py
___________________________________________________________________________________________________________
You can add targets by modifying the opt/SSHToolkit/targets/ips.txt file or by pressing 4 in the main menu.
SSH-MITM will not work with port 22 without proper configuration check out https://github.com/ssh-mitm/ssh-mitm for more details
_____________________________________________________________________________________________________________
You can replace passwords file with your own wordlists of choice make sure they are named hydra_split_1.txt,hydra_split_2.txt, etc. Wordlists can be stacked as needed.
Check out https://weakpass.com/wordlists

FEATURES:
Run hydra in the background with large wordlists , attack multiple targets, run MITM sessions and dictionary attacks simultaneously.  
