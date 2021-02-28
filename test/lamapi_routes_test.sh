IP="localhost:5000"
RIDS="[11007,39499,39434]"

usage ()
{
	printf "Usage : wp3api_routes_test [-options]\n";
	printf "Args :\n";
  printf "Options :\n";
	printf "\t--ip=<IP>         : server IP, Default: \"localhost::5000\";\n";
  printf "\t--rids=<RIDS>       : resources IDs to test on, Default: \"[11007, 11008, 11012]\";\n";
  printf "Example :\n";
	printf "sh wp3api_routes_test.sh --ip '$IP' --rids 30435";
}


OPTS=$( getopt -o h -l ip:,rids:,help -- "$@");
if [ $? != 0 ] ; then echo "Failed parsing options." >&2 ; exit 1 ; fi;
eval set -- "$OPTS";

while true; do
  case "$1" in
    --ip )
        IP=$2 ;
        shift 2 ;;
    --rids )
        RIDS=$2 ;
        shift 2 ;;
		--help | -h )
        usage ;
        exit 0 ;;
    -- )
        shift ;
        break ;;
    * )
        echo "Invalid option: $1" >&2 ;
        shift ;;
  esac;
done;


# Test Http requests for WP3 api:
echo "Temporal Services testing..."
echo "Testing : temporal/continuousdoc2vec/fetch"
curl -X POST "http://$IP/temporal/continuousdoc2vec/fetch" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_ids\": $RIDS}"
read -p "Press Enter to continue testing:" VAR
echo "Testing : temporal/continuouswikifier/fetch"
curl -X POST "http://$IP/temporal/continuouswikifier/fetch" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_ids\": $RIDS}"
read -p "Press Enter to continue testing:" VAR
echo "Testing : temporal/continuouswikifier/wikify/res"
curl -X POST "http://$IP/temporal/continuouswikifier/wikify/res" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_ids\": $RIDS}"
read -p "Press Enter to continue testing:" VAR
echo "Testing : temporal/continuouswikifier/wikify/text"
curl -X POST "http://$IP/temporal/continuouswikifier/wikify/text" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_texts\": [ \"Go play away...\", \"Go play away...\" ]}"
read -p "Press Enter to continue testing:" VAR

echo "Distance Services testing..."
echo "Testing : /distance/doc2vec/fetch"
curl -X POST "http://$IP/distance/doc2vec/fetch" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_ids\": $RIDS}"
read -p "Press Enter to continue testing:" VAR
echo "Testing : distance/doc2vec/knn"
curl -X POST "http://$IP/distance/doc2vec/knn" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_id\": 65478, \"n_neighbors\": 20}"
read -p "Press Enter to continue testing:" VAR
echo "Testing : distance/text2tfidf/fetch"
curl -X POST "http://$IP/distance/text2tfidf/fetch" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_ids\": $RIDS}"
read -p "Press Enter to continue testing:" VAR
echo "Testing : distance/wikifier/fetch"
curl -X POST "http://$IP/distance/wikifier/fetch" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_ids\": $RIDS, \"wikification_type\": \"FULL\"}"
read -p "Press Enter to continue testing:" VAR
echo "Testing : distance/wikifier/knn"
curl -X POST "http://$IP/distance/wikifier/knn" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_id\": 39434, \"n_neighbors\": 20}"
read -p "Press Enter to continue testing:" VAR


echo "Difficulty Services testing..."
echo "Testing : difficulty/charpersec/res"
curl -X POST "http://$IP/difficulty/charpersec/res" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_ids\": $RIDS}"
read -p "Press Enter to continue testing:" VAR
echo "Testing : difficulty/charpersec/text"
curl -X POST "http://$IP/difficulty/charpersec/text" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_texts\": [ \"Go play away...\", \"Go play away...\" ]}"
read -p "Press Enter to continue testing:" VAR
echo "Testing : difficulty/conpersec/res"
curl -X POST "http://$IP/difficulty/conpersec/res" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_ids\": $RIDS}"
read -p "Press Enter to continue testing:" VAR
echo "Testing : difficulty/conpersec/text"
curl -X POST "http://$IP/difficulty/conpersec/text" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_texts\": [ \"Go play away...\", \"Go play away...\" ]}"
read -p "Press Enter to continue testing:" VAR
echo "Testing : difficulty/tfidf2technicity/res"
curl -X POST "http://$IP/difficulty/tfidf2technicity/res" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_ids\": $RIDS}"
read -p "Press Enter to continue testing:" VAR
echo "Testing : difficulty/tfidf2technicity/text"
curl -X POST "http://$IP/difficulty/tfidf2technicity/text" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_texts\": [ \"Go play away...\", \"Go play away...\" ]}"
read -p "Press Enter to continue testing:" VAR


echo "Missing ressource services testing..."
echo "Testing : missingresource/missingresources/predictmissing"
curl -X POST "http://$IP/missingresource/missingresources/predictmissing" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"previous\": 39434, \"after\": 39499, \"candidates_ids\": $RIDS}"
read -p "Press Enter to continue testing:" VAR


echo "Ordonize services testing..."
echo "Testing : ordonize/continuouswikification2order/reordonize"
curl -X POST "http://$IP/ordonize/continuouswikification2order/reordonize" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_id\": 39420, \"candidate_ids\": $RIDS}"
read -p "Press Enter to continue testing:" VAR

echo "Preproccess Services testing..."
echo "Testing : preprocess/res"
curl -X POST "http://$IP/preprocess/res" -H "accept: application/json" -H "Content-Type: application/json" -d "{ \"resource_ids\": $RIDS}"
read -p "Press Enter to continue testing:" VAR

echo "Testing done!"
