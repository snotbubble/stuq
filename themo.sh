#!/bin/sh
while true
do
	iam=`hostname -s`
	loc=`ls -1 ./pending/$iam/*.sh 2>/dev/null | wc -l`
	if [ $loc != 0 ]; then
		for file in ./pending/$iam/*.sh
			do
				if [ -f $file ]; then
					chmod u+x $file
					src=$(readlink --canonicalize $file)
					fnm=$(basename $src)
					mkdir ./running/$iam/
		   			mv $src ./running/$iam/$fnm
					/bin/bash ./running/$iam/$fnm
					mv ./running/$iam/$fnm ./done/$fnm
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
					mkdir ./running/$iam/
					mv $src ./running/$iam/$fnm
					/bin/bash ./running/$iam/$fnm
					mv ./running/$iam/$fnm ./done/$fnm
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

