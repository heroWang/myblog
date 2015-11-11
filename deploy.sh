echo '***sync local src to remote server***' 
rsync -ravz blog root@123.57.76.162:/root/blog/ --exclude=log


echo '***execute remote deploy.sh to restart service***'
ssh -nf root@123.57.76.162 'cd /root/blog/;./deploy.sh'

sleep 1s
echo '***done***'

