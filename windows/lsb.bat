@ECHO OFF
echo Check if you started Calibre's content server:
echo http://localhost:8080 (help: http://bit.ly111IWwt)
echo Hang out at https://crypto.cat room: letssharebooks
echo Stop sharing books by pressing Ctrl+c

set /a port=%random% %%40000 +1000
echo Your temporary public URL is https://www%port%.memoryoftheworld.org

plink.exe -N -T tunnel@ssh.memoryoftheworld.org -R %port%:localhost:8080 -P 722

