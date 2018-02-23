#!/bin/sh
while true
do
    HUH=$(hostname)
    loc=`ls -1 ./pending/$HUH/*.sh 2>/dev/null | wc -l`
    if [ $loc != 0 ]; then
        for file in ./pending/$HUH/*.sh
		do
			echo 'file=' $file
			if [ -f $file ]; then
				chmod u+x $file
				src=$(readlink --canonicalize $file)
				fnm=$(basename $src)
				mv $src ./running/$HUH/$fnm
				/bin/bash ./running/$HUH/$fnm
				mv ./running/$HUH/$fnm ./done/$HUH/$fnm
				break
			fi
		done
	else
		for file in ./pending/*.sh
		do
			if [ -f $file ]; then
				chmod u+x $file
				src=$(readlink --canonicalize $file)
				fnm=$(basename $src)
		   		mv $src ./running/$HUH/$fnm
				/bin/bash ./running/$HUH/$fnm
				mv ./running/$HUH/$fnm ./done/$fnm
		   		break
			fi
		done
	fi
	file=0
	src=0
	fnm=0
	loc=0
	sleep 2
done
