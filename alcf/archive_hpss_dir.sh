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
Utility for archiving data on ALCF to HPSS using HSI

${UL}Usage:${RS} archive_hpss_dir [options] [dirpath|\"dirglob*\"]

${UL}Options:${RS}

dirpath         Archive the directory at dirpath
dirglob         Archive the directories matching dirglob
-h, --help      Show this help message
--print-test    Print the commands to be run, do not archive data
--trash         Create trash directory and move contents into said directory

${UL}Description:${RS}
    Saves the given directory(s) to HPSS archival system on ALCF. The path on
    the HPSS system will replicate the absolute path on ALCF, resolving all
    symlinks. So on Theta, the '/projects' directory resolves to
    '/lus/theta-fs0/projects'. This is done to ensure no conflicts if/when more
    file systems come online.

${HC}Using dirglob${RS}
    When attempting to archive multiple directories via globing (ie. using a
    *), the path ${UL}must${RS} be surrounded in double quotation marks.
"

OTHER_ARGUMENTS=()
for arg in "$@"
do
    case $arg in
        -h | --help)
            echo -e "$USAGE"
            exit 0
            ;;
        --trash)
            TRASH=1
            shift
            ;;
        --print-test)
            PRINTTEST=1
            shift
            ;;
        *)
            OTHER_ARGUMENTS+=( "$1" )
            shift
            ;;
    esac
done

# Function die called when there is a problem
function die() {
        echo -e "${1}"
        exit 1
}

module load hsi
dirtoarchive=$OTHER_ARGUMENTS

# check if the  user entered proper number of args
nargs=1
if [[ "${#OTHER_ARGUMENTS[@]}" -ne "$nargs" ]] ; then
    die "Wrong number of arguments. Need $nargs arguments. Recieved ${#OTHER_ARGUMENTS[@]}: 
    ${OTHER_ARGUMENTS[*]}"
fi

# Get the subpath
subpath=`pwd -P`
subpath=".$subpath"

# Get the date and time stamp for the log file
now=$(date +"%F_%H-%M-%S")
logfile=~/hsi.log_$now

# Print some info
echo "Archiving $dirtoarchive to $subpath on hpss"
echo "See $logfile for log info"

# The last character of the string should not be "\". Remove it if present
lastchar=`echo "$dirtoarchive" | sed -e 's/\(^.*\)\(.$\)/\2/'`
if [ "$lastchar" == "/" ]; then
  dirtoarchive=`echo ${dirtoarchive%?}`
fi

# Archive a directory to hpss and move archived dir to a TRASH directory for future removal
execstring="hsi -O $logfile -q -v 'mkdir -p $subpath ; cd $subpath ; pwd ; ls ; put -R $dirtoarchive'"
if [ $PRINTTEST ]; then
    echo $execstring
else
    echo " >" $execstring
    eval $execstring
fi

if [ $TRASH ]; then
    trashexecstring="mkdir -p TRASH ; mv $dirtoarchive TRASH"
    if [ $PRINTTEST ]; then
        echo $trashexecstring
    else
        echo " >" $trashexecstring
        eval $trashexecstring
    fi
fi
module unload hsi
