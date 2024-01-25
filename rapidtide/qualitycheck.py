#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#   Copyright 2024-2024 Blaise Frederick
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
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import binary_erosion

import rapidtide.io as tide_io
import rapidtide.stats as tide_stats
from rapidtide.RapidtideDataset import RapidtideDataset


def prepmask(inputmask):
    erodedmask = binary_erosion(inputmask)
    return erodedmask


def checklag(themask, themap, histlen=201, maxgrad=3.0, debug=False):
    lagmetrics = {}

    theerodedmask = prepmask(themask.data)

    lagmetrics["pct02"] = themap.robustmin
    lagmetrics["pct25"] = themap.quartiles[0]
    lagmetrics["pct50"] = themap.quartiles[1]
    lagmetrics["pct75"] = themap.quartiles[2]
    lagmetrics["pct98"] = themap.robustmax

    thegradient = np.gradient(themap.data)
    thegradientamp = np.sqrt(
        np.square(thegradient[0] / themap.xsize)
        + np.square(thegradient[1] / themap.ysize)
        + np.square(thegradient[2] / themap.zsize)
    )
    maskedgradient = theerodedmask * thegradientamp
    if debug:
        tide_io.savetonifti(thegradientamp, themap.header, "laggradient")
        tide_io.savetonifti(maskedgradient, themap.header, "maskedlaggradient")
    (
        gradhist,
        lagmetrics["gradhistpeakheight"],
        lagmetrics["gradhistpeakloc"],
        lagmetrics["gradhistpeakwidth"],
        lagmetrics["gradhistcenterofmass"],
    ) = tide_stats.makehistogram(
        maskedgradient,
        histlen,
        refine=False,
        therange=(0.0, maxgrad),
        normalize=True,
        ignorefirstpoint=True,
        debug=True,
    )

    lagmetrics["gradhistbincenters"] = ((gradhist[1][1:] + gradhist[1][0:-1]) / 2.0).tolist()
    lagmetrics["gradhistvalues"] = (gradhist[0][-histlen:]).tolist()
    if debug:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_title("lag gradient magnitude histogram")
        plt.plot((lagmetrics["gradhistbincenters"])[1:], (lagmetrics["gradhistvalues"])[1:])
        plt.show()
    return lagmetrics


def checkstrength(themask, themap, histlen=101, debug=False):
    strengthmetrics = {}

    strengthmetrics["pct02"] = themap.robustmin
    strengthmetrics["pct25"] = themap.quartiles[0]
    strengthmetrics["pct50"] = themap.quartiles[1]
    strengthmetrics["pct75"] = themap.quartiles[2]
    strengthmetrics["pct98"] = themap.robustmax

    return strengthmetrics


def checkregressors(theregressors, debug=False):
    regressormetrics = {}
    return regressormetrics


def qualitycheck(
    datafileroot,
    anatname=None,
    geommaskname=None,
    userise=False,
    usecorrout=False,
    useatlas=False,
    forcetr=False,
    forceoffset=False,
    offsettime=0.0,
    verbose=False,
    debug=False,
):
    # read in the dataset
    thedataset = RapidtideDataset(
        "main",
        datafileroot + "_",
        anatname=anatname,
        geommaskname=geommaskname,
        userise=userise,
        usecorrout=usecorrout,
        useatlas=useatlas,
        forcetr=forcetr,
        forceoffset=forceoffset,
        offsettime=offsettime,
        verbose=verbose,
        init_LUT=False,
    )

    outputdict = {}
    themask = thedataset.overlays["lagmask"]

    thelags = thedataset.overlays["lagtimes"]
    thelags.setFuncMask(themask.data)
    thelags.updateStats()
    if debug:
        thelags.summarize()

    thewidths = thedataset.overlays["lagsigma"]

    thestrengths = thedataset.overlays["lagstrengths"]
    thestrengths.setFuncMask(themask.data)
    thestrengths.updateStats()
    if debug:
        thelags.summarize()

    theregressors = thedataset.regressors

    outputdict["lagmetrics"] = checklag(themask, thelags, debug=debug)
    outputdict["strengthmetrics"] = checkstrength(themask, thestrengths, debug=debug)
    outputdict["regressormetrics"] = checkregressors(theregressors, debug=debug)

    return outputdict
