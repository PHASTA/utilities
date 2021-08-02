# Contributing Guidelines

## What goes here?

No hard rules, but two guidelines:

1. Small (ie. single file) scripts/programs that may or may not be used frequently
2. Series of tools which aren't used frequently, but important to keep track of

## Layout

The utilities are split between machine specific and general utilities.

## Script Guidelines

These are some general guidelines for the creation of utility scripts that can
be added here.

### Utility scripts should support `-h` and/or `--help` flags

A simple example of this in a bash script is:

```bash
#!/bin/bash

HELPMSG="Here is a helpful message about how to use this utility.

You can even break it into multiple lines if you want."

if [ "$1" == "-h" ] || [ "$1" = "--help" ]; then
    echo $HELPMSG
fi
```

In python, you can use something like `argparse` if you have more complicated
options overview, or just want to have the help documentation generated
automagically.

### When in doubt, comment

As these are utilities developed for research tasks, they are probably going to
be built for a specific task. If someone (or yourself) wants to adapt it to do
something slightly different, comments help tremendously.
