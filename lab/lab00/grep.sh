# grep (Global Regular Expression Print)

echo 
echo ---'finding which port protocol SMTP uses'---
fgrep smtp /etc/services 

echo 
echo ---'displays line numbers and lines with "ICMP" in ping.sh'---
grep -n "ICMP" ./ping.sh

echo 
echo ---'searches for "TCP"s recursively in all files in local folder'---
grep -r "TCP" ./

echo 
echo ---'counts the number of lines has "TCP"s in local folder'---
grep -c -r "TCP" ./

