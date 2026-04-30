echo "naam"
read naam
echo "leeftijd"
read leeftijd
if [ $leeftijd -lt 20 ]; then
echo "je bent een peuter"
elif [ $leeftijd -gt 20 ]; then
echo "je bent een boomer"
fi
