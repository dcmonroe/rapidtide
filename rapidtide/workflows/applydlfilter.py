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
import os
import sys

import numpy as np

import rapidtide.correlate as tide_corr
import rapidtide.dlfilter as tide_dlfilt
import rapidtide.filter as tide_filt
import rapidtide.fit as tide_fit
import rapidtide.io as tide_io
import rapidtide.miscmath as tide_math
import rapidtide.util as tide_util
import rapidtide.workflows.parser_funcs as pf


def _get_parser():
    """
    Argument parser for plethquality
    """
    parser = argparse.ArgumentParser(
        prog="applydlfilter",
        description=("Apply a deep learning filter to a timecourse."),
        allow_abbrev=False,
    )

    # Required arguments
    parser.add_argument(
        "infilename",
        type=lambda x: pf.is_valid_file(parser, x),
        help="The name of the input text file (or a list of names of input files).",
    )
    parser.add_argument(
        "outfilename",
        help="The name of the output text file (or a list of names of output files).",
    )

    # add optional arguments
    parser.add_argument(
        "--model",
        dest="model",
        action="store",
        metavar="MODELROOT",
        type=str,
        help=("Use model named MODELROOT (default is model_revised)."),
        default="model_revised",
    )
    parser.add_argument(
        "--filesarelists",
        dest="filesarelists",
        action="store_true",
        help=("Input file contains lists of filenames, rather than data."),
        default=False,
    )
    parser.add_argument(
        "--nodisplay",
        dest="display",
        action="store_false",
        help=("Do not plot the data (for noninteractive use)."),
        default=True,
    )
    parser.add_argument(
        "--verbose",
        dest="verbose",
        action="store_true",
        help=("Print a lot of internal information."),
        default=False,
    )
    return parser


def checkcardmatch(reference, candidate, samplerate, refine=True, zeropadding=0, debug=False):
    thecardfilt = tide_filt.NoncausalFilter(filtertype="cardiac")
    trimlength = np.min([len(reference), len(candidate)])
    thexcorr = tide_corr.fastcorrelate(
        tide_math.corrnormalize(
            thecardfilt.apply(samplerate, reference),
            detrendorder=3,
            windowfunc="hamming",
        )[:trimlength],
        tide_math.corrnormalize(
            thecardfilt.apply(samplerate, candidate),
            detrendorder=3,
            windowfunc="hamming",
        )[:trimlength],
        usefft=True,
        zeropadding=zeropadding,
    )
    xcorrlen = len(thexcorr)
    sampletime = 1.0 / samplerate
    xcorr_x = np.r_[0.0:xcorrlen] * sampletime - (xcorrlen * sampletime) / 2.0 + sampletime / 2.0
    searchrange = 5.0
    trimstart = tide_util.valtoindex(xcorr_x, -2.0 * searchrange)
    trimend = tide_util.valtoindex(xcorr_x, 2.0 * searchrange)
    (
        maxindex,
        maxdelay,
        maxval,
        maxsigma,
        maskval,
        failreason,
        peakstart,
        peakend,
    ) = tide_fit.findmaxlag_gauss(
        xcorr_x[trimstart:trimend],
        thexcorr[trimstart:trimend],
        -searchrange,
        searchrange,
        3.0,
        refine=refine,
        zerooutbadfit=False,
        useguess=False,
        fastgauss=False,
        displayplots=False,
    )
    if debug:
        print(
            "CORRELATION: maxindex, maxdelay, maxval, maxsigma, maskval, failreason, peakstart, peakend:",
            maxindex,
            maxdelay,
            maxval,
            maxsigma,
            maskval,
            failreason,
            peakstart,
            peakend,
        )
    return maxval, maxdelay, failreason


def applydlfilter(args):
    if args.display:
        import matplotlib as mpl

        mpl.use("TkAgg")
        import matplotlib.pyplot as plt

    if args.filesarelists:
        infilenamelist = []
        with open(args.infilename, "r") as f:
            inputlist = f.readlines()
            for line in inputlist:
                infilenamelist.append(line.strip())
                if args.verbose:
                    print(infilenamelist[-1])
        outfilenamelist = []
        with open(args.outfilename, "r") as f:
            inputlist = f.readlines()
            for line in inputlist:
                outfilenamelist.append(line.strip())
                if args.verbose:
                    print(outfilenamelist[-1])
        if len(infilenamelist) != len(outfilenamelist):
            print("list lengths do not match - exiting")
            sys.exit()
    else:
        infilenamelist = [args.infilename]
        outfilenamelist = [args.outfilename]

    # load the filter
    modelpath = os.path.join(
        os.path.split(os.path.split(os.path.split(__file__)[0])[0])[0],
        "rapidtide",
        "data",
        "models",
    )
    thedlfilter = tide_dlfilt.DeepLearningFilter(modelpath=modelpath)
    thedlfilter.loadmodel(args.model)
    model = thedlfilter.model
    window_size = thedlfilter.window_size
    usebadpts = thedlfilter.usebadpts

    badpts = None
    if usebadpts:
        try:
            badpts = tide_io.readvec(args.infilename.replace(".txt", "_badpts.txt"))
        except:
            print(
                "bad points file",
                args.infilename.replace(".txt", "_badpts.txt"),
                "not found!",
            )
            sys.exit()

    for idx, infilename in enumerate(infilenamelist):
        # read in the data
        if args.verbose:
            print("reading in", infilename)
        fmridata = tide_io.readvec(infilename)

        if args.verbose:
            print("filtering...")
        predicteddata = thedlfilter.apply(fmridata, badpts=badpts)

        if args.verbose:
            print("writing to", outfilenamelist[idx])
        tide_io.writevec(predicteddata, outfilenamelist[idx])

        maxval, maxdelay, failreason = checkcardmatch(fmridata, predicteddata, 25.0, debug=False)
        print(infilename, "max correlation input to output:", maxval)

        if args.display:
            plt.figure()
            plt.plot(fmridata)
            plt.plot(predicteddata)
            plt.show()
