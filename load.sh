export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/mysql/lib/mysql/"
DBNAME=$1
WH=$2
HOST=127.0.0.1
STEP=100

BASEDIR=$(dirname "$0")
PROJDIR="$BASEDIR"

TPCC_LOAD=${PROJDIR}/bin/tpcc_load
${TPCC_LOAD} -h $HOST -d $DBNAME -u root -p "" -w $WH -l 1 -m 1 -n $WH >> 1.out &

x=1

while [ $x -le $WH ]
do
 echo $x $(( $x + $STEP - 1 ))
${TPCC_LOAD} -h $HOST -d $DBNAME -u root -p "" -w $WH -l 2 -m $x -n $(( $x + $STEP - 1 ))  >> 2_$x.out &
${TPCC_LOAD} -h $HOST -d $DBNAME -u root -p "" -w $WH -l 3 -m $x -n $(( $x + $STEP - 1 ))  >> 3_$x.out &
${TPCC_LOAD} -h $HOST -d $DBNAME -u root -p "" -w $WH -l 4 -m $x -n $(( $x + $STEP - 1 ))  >> 4_$x.out &
 x=$(( $x + $STEP ))
done

