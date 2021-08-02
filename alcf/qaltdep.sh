#!/usr/bin/env bash

RS="\033[0m"    # reset
HC="\033[1m"    # hicolor
UL="\033[4m"    # underline
INV="\033[7m"   # inverse background and foreground
FBLK="\033[30m" # foreground black
FRED="\033[31m" # foreground red
FGRN="\033[32m" # foreground green
FYEL="\033[33m" # foreground yellow

USAGE="
Utility for automating common qalter dependency routines.

${UL}Usage:${RS} qaltdep [options] --makedepon=[none|jobid] [jobids]
       qaltdep [options] --deptrain [jobids]

${UL}Options:${RS}

-h, --help      Show this help message
--deptrain      Creates a dependency train
--makedepon=    Makes the jobs in the main argument depependent on
--print-test    Run the script, but print out the command instead of running

${UL}Description:${RS}

${HC}Make Dependent On (--makedepon):${RS}
    Example: qaltdep --makedepon=11111 123456 789012
    This will make the jobs 123456 and 789012 depend on 111111

${HC}Create Dependecy Train (--deptrain):${RS}
    Example: qaltdep --deptrain 111111 222222 333333
    This will create a train of dependencies, where the order of the jobids is 
    the order that the train will run. The example above results in

    111111 <--- 222222 <--- 333333

    where '<---' represents the dependency. The job 111111 will be the only job
    in the sequence that will not have a 'dep_held' status.
"

OTHER_ARGUMENTS=()
for arg in "$@"
do
    case $arg in
        -h | --help)
            echo -e "$USAGE"
            exit 0
            ;;
        --makedepon=*)
            DEPENDON="${arg#*=}"
            shift
            ;;
        --print-test)
            PRINTTEST=1
            shift
            ;;
        --deptrain)
            DEPTRAIN=1
            shift
            ;;
        *)
            OTHER_ARGUMENTS+=( "$1" )
            shift
            ;;
    esac
done

if [ -z $DEPENDON ] && [ -z $DEPTRAIN ]; then
    echo -e "${FRED}${HC}WARNING: $RS Either --makedepon=* or --deptrain must be set"; exit 1
fi

if [ ! -z $DEPENDON ] && [ ! -z $DEPTRAIN ]; then
    echo -e "${FRED}${HC}WARNING: $RS Flags --makedepon and --deptrain may not be set at the same time"; exit 1
fi

for i in ${!OTHER_ARGUMENTS[@]}; do
    if [ ! -z $DEPENDON ]; then
        execstring="qalter --dependencies ${DEPENDON} ${OTHER_ARGUMENTS[$i]}"
        if [ $PRINTTEST ]; then
            echo $execstring
        else
            echo " >" $execstring 
            eval $execstring
        fi
    else [ ! -z $DEPTRAIN ];
        if [ ! $i -eq 0 ]; then
            imin1=$(( $i - 1))
            execstring="qalter --dependencies ${OTHER_ARGUMENTS[$imin1]} ${OTHER_ARGUMENTS[$i]}"

            if [ $PRINTTEST ]; then
                echo $execstring
            else
                echo " >" $execstring
                eval $execstring
            fi
        fi
    fi
done
