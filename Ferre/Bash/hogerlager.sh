echo "Quizmaster,wat is het getal:"
read getal
while [ true ]
do
echo "raad getal"
read teradengetal
((loops++))
if [ $getal -lt $teradengetal ]
then
echo "het getal is kleiner"
elif [ $getal -gt $teradengetal ]
then
echo "het getal is groter"
else [ $getal -eq $teradengetal ]
echo "je hebt het geraden in $loops keer"
break
fi
done




