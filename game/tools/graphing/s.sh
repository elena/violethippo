
echo "DONT run this any more"
exit -1

for n in *.run
do
  gnuplot $n
done
