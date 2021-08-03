#!/bin/bash

# user needs:
#  1) Worst.pht file that points to worst-procs_case  
#  2)  have batchSize "pieces"  should be some multiple (1 is fine) of np
#  3) a python file (Worst48.py)
#  4) number 48 is in lots of file names that would require downstream code change j
#  5) $2 is a file that has one part number per file. I generated such a files with the following commands
#     a) python fixBrokenVTK.py > mergeLog   # you will need to edit this file to tell it cases ready to merge
#     b) sort -dk 4nr mergeLog > mergeLog_sorted
#     c) awk '{print $1}' mergeLog_sorted > mergeLog_partnum
#  6) may have to fix SourcePATH below based on where your full set of target mesh parts in posix form are located

np=$1
fileWithWorstErrors=$2 # e.g., mergeLog_partnum shown above
pythonFile=$3          # e.g., Worst48.py
shift=$5 # or however many you might have already done
i=0   # leave this alone usually s it is a local counter for this set
batchSize=48  # probably best to make this match your number of processes divided by some memory safety factor....1.5 saftey worked
numWorstCorrectors=$4
FILENAME="worstMap"
SourcePATH="../../8448-procs_case/"
while [ $i -lt $numWorstCorrectors ] # -lt because I did not want to redo all the math in my do loop that increments counters 
    do i=$(($i+1))
        j=$(($i+$shift))
        k=$(($i*$batchSize))
        echo $i,$j,$k
        mkdir worst-procs_case
        head -$k $fileWithWorstErrors | tail -$batchSize  > worst-procs_case/$FILENAME   # hardcoded elsewhere so leave it
        cd worst-procs_case

        LINES=$(cat $FILENAME)
        icount=0
        for LINE in $LINES
            do
               jcount=$(($icount + 1))
               icount=$jcount
               echo $icount, $jcount,  "$LINE"
               ln -s ${SourcePATH}geombc.dat."$LINE" geombc.dat.$icount
               ln -s ${SourcePATH}restart.0."$LINE" restart.0.$icount
            done
#        ../test.sh   # what the above does
        cd ..
        mpirun -f $COBALT_NODEFILE -np $np pvbatch $pythonFile $j 2>&1 | tee -a output.Worst$j
        mv worst-procs_case worst-procs_case_$j
    done

