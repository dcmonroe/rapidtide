#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright 2016-2024 Blaise Frederick
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#
import argparse
import copy
import logging
import os
import sys

import numpy as np

import rapidtide.filter as tide_filt
import rapidtide.io as tide_io
import rapidtide.miscmath as tide_math
import rapidtide.multiproc as tide_multiproc
import rapidtide.resample as tide_resample
import rapidtide.util as tide_util
import rapidtide.workflows.glmfrommaps as tide_glmfrommaps
import rapidtide.workflows.parser_funcs as pf

LGR = logging.getLogger("GENERAL")
ErrorLGR = logging.getLogger("ERROR")
TimingLGR = logging.getLogger("TIMING")

DEFAULT_GLMDERIVS = 0


def _get_parser():
    """
    Argument parser for glmfilt
    """
    parser = argparse.ArgumentParser(
        prog="retroglm",
        description="Do the rapidtide GLM filtering using the maps generated from a previous analysis.",
        allow_abbrev=False,
    )

    # Required arguments
    parser.add_argument(
        "fmrifile",
        type=lambda x: pf.is_valid_file(parser, x),
        help="The name of 4D nifti fmri file to filter.",
    )
    parser.add_argument(
        "datafileroot",
        type=str,
        help="The root name of the previously run rapidtide dataset (everything up to but not including the underscore.)",
    )
    parser.add_argument(
        "--alternateoutput",
        dest="alternateoutput",
        type=str,
        help="Alternate output root (if not specified, will use the same root as the previous dataset).",
        default=None,
    )
    parser.add_argument(
        "--glmderivs",
        dest="glmderivs",
        action="store",
        type=int,
        metavar="NDERIVS",
        help=(
            f"When doing final GLM, include derivatives up to NDERIVS order. Default is {DEFAULT_GLMDERIVS}"
        ),
        default=DEFAULT_GLMDERIVS,
    )
    parser.add_argument(
        "--nprocs",
        dest="nprocs",
        action="store",
        type=int,
        metavar="NPROCS",
        help=(
            "Use NPROCS worker processes for multiprocessing. "
            "Setting NPROCS to less than 1 sets the number of "
            "worker processes to n_cpus."
        ),
        default=1,
    )
    parser.add_argument(
        "--numskip",
        dest="numskip",
        action="store",
        type=int,
        metavar="NUMSKIP",
        help=("Skip NUMSKIP points at the beginning of the fmri file."),
        default=0,
    )
    parser.add_argument(
        "--limitoutput",
        dest="saveall",
        action="store_false",
        help=("Only save the filtered data and the R value."),
        default=True,
    )
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        help=("Output lots of helpful information."),
        default=False,
    )
    return parser


def retroglm(args):
    rt_floatset = np.float64
    rt_floattype = "float64"
    rt_outfloatset = np.float64
    rt_outfloattype = "float64"

    thecommandline = " ".join(sys.argv[1:])

    if args.nprocs < 1:
        args.nprocs = tide_multiproc.maxcpus()
    # don't use shared memory if there is only one process
    if args.nprocs == 1:
        usesharedmem = False
    else:
        usesharedmem = True

    # read the necessary input files
    print("reading fmrifile")
    fmri_input, fmri_data, fmri_header, fmri_dims, fmri_sizes = tide_io.readfromnifti(
        args.fmrifile
    )
    print(f"{fmri_data.shape=}")
    xdim, ydim, slicedim, fmritr = tide_io.parseniftisizes(fmri_sizes)
    xsize, ysize, numslices, timepoints = tide_io.parseniftidims(fmri_dims)
    numspatiallocs = int(xsize) * int(ysize) * int(numslices)
    fmri_data_spacebytime = fmri_data.reshape((numspatiallocs, timepoints))
    print(f"{fmri_data_spacebytime.shape=}")

    # read the runoptions file
    print("reading runoptions")
    runoptionsfile = f"{args.datafileroot}_options"
    therunoptions = tide_io.readoptionsfile(runoptionsfile)

    print("reading maskfile")
    maskfile = f"{args.datafileroot}_desc-processed_mask.nii.gz"
    mask_input, lagmask, mask_header, mask_dims, mask_sizes = tide_io.readfromnifti(maskfile)
    if not tide_io.checkspacematch(fmri_header, mask_header):
        raise ValueError("mask dimensions do not match fmri dimensions")
    lagmask_spacebytime = lagmask.reshape((numspatiallocs))
    print(f"{lagmask_spacebytime.shape=}")

    print("reading lagtimes")
    lagtimesfile = f"{args.datafileroot}_desc-maxcorr_map.nii.gz"
    (
        lagtimes_input,
        lagtimes,
        lagtimes_header,
        lagtimes_dims,
        lagtimes_sizes,
    ) = tide_io.readfromnifti(lagtimesfile)
    if not tide_io.checkspacematch(fmri_header, lagtimes_header):
        raise ValueError("lagtimes dimensions do not match fmri dimensions")
    print(f"{lagtimes.shape=}")
    lagtimes_spacebytime = lagtimes.reshape((numspatiallocs))
    print(f"{lagtimes_spacebytime.shape=}")

    startpt = args.numskip
    endpt = timepoints - 1
    validtimepoints = endpt - startpt + 1
    skiptime = startpt * fmritr
    initial_fmri_x = (
        np.linspace(0.0, validtimepoints * fmritr, num=validtimepoints, endpoint=False) + skiptime
    )

    if therunoptions["arbvec"] is not None:
        # NOTE - this vector is LOWERPASS, UPPERPASS, LOWERSTOP, UPPERSTOP
        # setfreqs expects LOWERSTOP, LOWERPASS, UPPERPASS, UPPERSTOP
        theprefilter = tide_filt.NoncausalFilter(
            "arb",
            transferfunc=therunoptions["filtertype"],
        )
        theprefilter.setfreqs(
            therunoptions["arbvec"][2],
            therunoptions["arbvec"][0],
            therunoptions["arbvec"][1],
            therunoptions["arbvec"][3],
        )
    else:
        theprefilter = tide_filt.NoncausalFilter(
            therunoptions["filterband"],
            transferfunc=therunoptions["filtertype"],
            padtime=therunoptions["padseconds"],
        )

    # read the lagtc generator file
    print("reading lagtc generator")
    lagtcgeneratorfile = f"{args.datafileroot}_desc-lagtcgenerator_timeseries"
    genlagtc = tide_resample.FastResamplerFromFile(lagtcgeneratorfile)

    # select the voxels in the mask
    print("figuring out valid voxels")
    validvoxels = np.where(lagmask_spacebytime > 0)[0]
    print(f"{validvoxels.shape=}")
    numvalidspatiallocs = np.shape(validvoxels)[0]
    print(f"{numvalidspatiallocs=}")
    internalvalidspaceshape = numvalidspatiallocs
    internalvalidspaceshapederivs = (
        internalvalidspaceshape,
        args.glmderivs + 1,
    )
    internalvalidfmrishape = (numvalidspatiallocs, np.shape(initial_fmri_x)[0])
    print(f"validvoxels shape = {numvalidspatiallocs}")
    print(f"internalvalidfmrishape shape = {internalvalidfmrishape}")

    # slicing to valid voxels
    print("selecting valid voxels")
    fmri_data_valid = fmri_data_spacebytime[validvoxels, :]
    lagtimes_valid = lagtimes_spacebytime[validvoxels]
    lagmask_valid = lagmask_spacebytime[validvoxels]
    print(f"{fmri_data_valid.shape=}")

    if usesharedmem:
        print("allocating shared memory")
        glmmean, dummy, dummy = tide_util.allocshared(internalvalidspaceshape, rt_outfloatset)
        rvalue, dummy, dummy = tide_util.allocshared(internalvalidspaceshape, rt_outfloatset)
        r2value, dummy, dummy = tide_util.allocshared(internalvalidspaceshape, rt_outfloatset)
        fitNorm, dummy, dummy = tide_util.allocshared(
            internalvalidspaceshapederivs, rt_outfloatset
        )
        fitcoeff, dummy, dummy = tide_util.allocshared(
            internalvalidspaceshapederivs, rt_outfloatset
        )
        movingsignal, dummy, dummy = tide_util.allocshared(internalvalidfmrishape, rt_outfloatset)
        lagtc, dummy, dummy = tide_util.allocshared(internalvalidfmrishape, rt_floatset)
        filtereddata, dummy, dummy = tide_util.allocshared(internalvalidfmrishape, rt_outfloatset)
    else:
        print("allocating memory")
        glmmean = np.zeros(internalvalidspaceshape, dtype=rt_outfloattype)
        rvalue = np.zeros(internalvalidspaceshape, dtype=rt_outfloattype)
        r2value = np.zeros(internalvalidspaceshape, dtype=rt_outfloattype)
        fitNorm = np.zeros(internalvalidspaceshapederivs, dtype=rt_outfloattype)
        fitcoeff = np.zeros(internalvalidspaceshapederivs, dtype=rt_outfloattype)
        movingsignal = np.zeros(internalvalidfmrishape, dtype=rt_outfloattype)
        lagtc = np.zeros(internalvalidfmrishape, dtype=rt_floattype)
        filtereddata = np.zeros(internalvalidfmrishape, dtype=rt_outfloattype)

    oversampfactor = int(therunoptions["oversampfactor"])
    if args.alternateoutput is None:
        outputname = therunoptions["outputname"]
    else:
        outputname = args.alternateoutput
    print(f"{outputname=}")
    oversamptr = fmritr / oversampfactor
    try:
        threshval = therunoptions["glmthreshval"]
    except KeyError:
        threshval = 0.0
    mode = "glm"

    initialvariance = tide_math.imagevariance(fmri_data_valid, theprefilter, 1.0 / fmritr)

    print("calling glmmfrommaps")
    voxelsprocessed_glm = tide_glmfrommaps.glmfrommaps(
        fmri_data_valid,
        glmmean,
        rvalue,
        r2value,
        fitNorm,
        fitcoeff,
        movingsignal,
        lagtc,
        filtereddata,
        lagtimes_valid,
        lagmask_valid,
        genlagtc,
        mode,
        outputname,
        oversamptr,
        LGR,
        TimingLGR,
        validvoxels,
        initial_fmri_x,
        threshval,
        nprocs_makelaggedtcs=args.nprocs,
        nprocs_glm=args.nprocs,
        glmderivs=0,
        mp_chunksize=50000,
        showprogressbar=True,
        alwaysmultiproc=False,
        memprofile=False,
        debug=True,
    )

    finalvariance = tide_math.imagevariance(filtereddata, theprefilter, 1.0 / fmritr)
    divlocs = np.where(finalvariance > 0.0)
    varchange = initialvariance * 0.0
    varchange[divlocs] = 100.0 * (finalvariance[divlocs] / initialvariance[divlocs] - 1.0)

    outputpath = os.path.dirname(outputname)
    rawsources = [
        os.path.relpath(args.fmrifile, start=outputpath),
        os.path.relpath(lagtimesfile, start=outputpath),
        os.path.relpath(maskfile, start=outputpath),
        os.path.relpath(runoptionsfile, start=outputpath),
        os.path.relpath(lagtcgeneratorfile, start=outputpath),
    ]
    bidsbasedict = {
        "RawSources": rawsources,
        "Units": "arbitrary",
        "CommandLineArgs": thecommandline,
    }

    theheader = copy.deepcopy(lagtimes_header)
    if mode == "glm":
        maplist = [
            (rvalue, "lfofilterR", "map", None),
            (r2value, "lfofilterR2", "map", None),
            (glmmean, "lfofilterMean", "map", None),
            (fitcoeff, "lfofilterCoeff", "map", None),
            (fitNorm, "lfofilterNorm", "map", None),
            (initialvariance, "lfofilterInbandVarianceBefore", "map", None),
            (finalvariance, "lfofilterInbandVarianceAfter", "map", None),
            (varchange, "lfofilterInbandVarianceChange", "map", None),
        ]
    else:
        maplist = [
            (rvalue, "CVRR", "map", None),
            (r2value, "CVRR2", "map", None),
            (fitcoeff, "CVR", "map", "percent"),
            (initialvariance, "lfofilterInbandVarianceBefore", "map", None),
            (finalvariance, "lfofilterInbandVarianceAfter", "map", None),
            (varchange, "CVRVariance", "map", None),
        ]

    bidsdict = bidsbasedict.copy()

    # write the 3D maps
    tide_io.savemaplist(
        outputname, maplist, validvoxels, (xsize, ysize, numslices), theheader, bidsdict
    )

    # write the 4D maps
    theheader = copy.deepcopy(fmri_header)
    maplist = [
        (movingsignal, "lfofilterRemoved", "bold", None),
        (filtereddata, "lfofilterCleaned", "bold", None),
    ]
    if args.debug:
        maplist.append((fmri_data_valid, "inputdata", "bold", None))
    tide_io.savemaplist(
        outputname,
        maplist,
        validvoxels,
        (xsize, ysize, numslices, validtimepoints),
        theheader,
        bidsdict,
    )