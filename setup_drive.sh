GREEN='\033[0;32m'
NC='\033[0m'

for n in $(seq 1 $#); do
  line=$1
  echo -e "${GREEN}Create folder /media/nghia/$line ${NC}"  
  sudo mkdir -p "/media/nghia/$line"
  echo -e "${GREEN}Mount /dev/$line ${NC}"
  sudo mount "/dev/$line" "/media/nghia/$line"
  echo -e "${GREEN}Allow permission /media/nghia/$line ${NC}"
  sudo chmod a+rwx "/media/nghia/$line" 
  python3 ../chia_tool/cal.py $line
  shift
done




