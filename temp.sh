GREEN='\033[0;32m'
NC='\033[0m'

for i in {1..60} 
do
  line=$i
  #sudo mkdir -p "/media/nghia/$line"
  #sudo chmod a+rwx "/media/nghia/$line"   
  chia plots add -d "/media/nghia/$line"
done




