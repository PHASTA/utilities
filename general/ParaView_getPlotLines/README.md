These files and directories show how to loop through different timesteps of
data and save a csv of sample points defined by the PlotOverLine filter in
ParaView. This was originally mean to sample data for use in spectral analysis,
but could be extended/used for any number of different applications.

The directory these script were originally run with look like this:
```
.
├── runSpectraCalc.sh
├── SpectraLinePVTrace.py
├── CRS_4delta_6-15_28000.phts
├── locations
├── timesteps
├── spectra_csvs
│   └── [csv files]
└── spectra-procs_case
    ├── geombc-dat.1 -> ../../1920-procs_case/geombc-dat.1
    ├── [.... etc]
    └── geombc-dat.20 -> ../../1920-procs_case/geombc-dat.9
```

### `SpectraLinePVTrace.py`
This is run by `pvbatch` to actually loop through `timesteps` and get csvs at
`locations`. It handles moving the files that it needs for `timesteps`.

The top of the file contains the necessary inputs for the script. CSVs are
written to the `spectra_csvs` directory.

### `runSpectraCalc.sh`
This runs the `SpectraLinePVTrace.py` using `pvbatch`. It takes number of MPI
processes as it's first argument. It was written for Cooley explicitly.

### `locations`
Text file of space-delimited values that denote the name and locations at which
the PlotOverLine should be sampled. They take the format:

```
# [location name] [x location] [y location]
STG_2p60_uu -2.6  0.141592653589793

STG_2p60_uv   -2.6  0.181659399273
```

### `timesteps`
Text file of newline-delimited integers representing the timesteps that should
be looped over:

```
70500
74350
[....]
```

As the file successfully loops over a timestep, it is removed from the
`timesteps` file.
