N=512
X=100

for path in jobs/test/*/*.template.sh;
do
  msub $path $N $X;
done
