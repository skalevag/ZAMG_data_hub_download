
#!/bin/bash

sy=$2
ey=$3
WDIR=$1

export SKIP_SAME_TIME=1

for y in `seq $sy $ey` ; do
	echo $y
	files=$WDIR/*_$y*.nc
	afiles=($files)
	f=${afiles[1]}
	out=${f##*/}
	out=${out%_*}
	out=$WDIR/${out}_${y}.nc
	cmd="cdo mergetime $files $out"
	echo $cmd
	$cmd
done
