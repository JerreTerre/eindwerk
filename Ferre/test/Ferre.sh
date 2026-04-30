echo "van welk getal wil je het kwadraad:type 0 om af te sluiten"
read getal
while [ $getal -ne 0 ] 
do
kwadraad=$(($getal*$getal))
echo "het kwadraad van $getal is $kwadraad"
echo "van welk getal wil je het kwadraad:type 0 om af te sluiten"
read getal
done
