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
Check if two files are the same or not.

${UL}Usage:${RS} samefile [filepath1] [filepath2]

${UL}Options:${RS}

-h, --help      Show this help message
-s, --sha256    Use sha256sum for comparison. Will simply output the
                    hash of both files.

${UL}sha256sum Option:${RS}

By default, will use 'cmp' to compare the two files given. If ${HC}-s${RS} or
${HC}--sha256${RS} is given, will print the output from 'sha256sum' from the
two files and print them in successive lines. If the hash created by
'sha256sum' is the same for both files, they are identical.  Otherwise, there
is something different.
"

OTHER_ARGUMENTS=()
for arg in "$@"
do
    case $arg in
        -h | --help)
            echo -e "$USAGE"
            exit 0
            ;;
        -s | --sha)
            SHA=1
            ;;
        *)
            OTHER_ARGUMENTS+=( "$1" )
            shift
            ;;
    esac
done

if [ ! "${#OTHER_ARGUMENTS[@]}" == 2 ]; then
    echo -e "${FRED}$(basename $0) takes 2 arguments, ${#OTHER_ARGUMENTS[@]} given${RS}"
    echo -e "$USAGE"
    exit 1;
fi

if [ $SHA ]; then
    sha256sum ${OTHER_ARGUMENTS[0]}
    sha256sum ${OTHER_ARGUMENTS[1]}
else
    cmp --silent ${OTHER_ARGUMENTS[0]} ${OTHER_ARGUMENTS[1]} && echo "They're the same!" || echo "They're the different!"
fi
