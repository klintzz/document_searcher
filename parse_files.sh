#!/bin/bash
FILES=~/newfiles/*
for f in $FILES
do
  txt=${f//.pdf/.txt}
  newfile=${txt//newfiles/txtfiles}

  echo $newfile
  if [ -e "$newfile" ]
  then
    echo "exists"
  else
    echo "doesn't exist"
    pdftotext $f $newfile
  fi
done
