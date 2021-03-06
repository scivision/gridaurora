#!/usr/bin/env python
"""
Computes Eigenprofiles of Ionospheric response to flux tube input via the following steps:
1. Generate unit input differential number flux vs. energy
2. Compute ionospheric energy deposition and hence production/loss rates for the modeled kinetic chemistries (12 in total)

unverified for proper scaling, fitted exponential curve to extrapolate original
Zettergren grid from 50eV-18keV up to 100MeV

example:
python MakeIonoEigenprofile.py -t 2013-01-31T09:00:00Z -c 65 -148 -o ~/data/eigen.h5

Michael Hirsch
"""
from argparse import ArgumentParser
from gridaurora.loadtranscargrid import loadregress, makebin, doplot
from gridaurora.writeeigen import writeeigen
from gridaurora.zglow import glowalt
from glowaurora.eigenprof import makeeigen, ekpcolor
from glowaurora.plots import plotprodloss, plotenerdep
from gridaurora.plots import ploteigver
from reesaurora.rees_model import reesiono
from reesaurora.plots import plotA
from pathlib import Path
from collections import namedtuple
from matplotlib.pyplot import show
from dateutil import rrule
from dateutil.parser import parse
import seaborn as sns  # optional pretty plots

sns.color_palette(sns.color_palette("cubehelix"))
sns.set(context="talk", style="whitegrid")
sns.set(rc={"image.cmap": "cubehelix_r"})  # for contour


def main():
    p = ArgumentParser(description="Makes unit flux eV^-1 as input to GLOW or Transcar to create ionospheric eigenprofiles")
    p.add_argument(
        "-i", "--inputgridfn", help="original Zettergren input flux grid to base off of", default="zettflux.csv",
    )
    p.add_argument("-o", "--outfn", help="hdf5 file to write with ionospheric response (eigenprofiles)")
    p.add_argument(
        "-t", "--simtime", help="yyyy-mm-ddTHH:MM:SSZ time of sim", nargs="+", default=["1999-12-21T00:00:00Z"],
    )
    p.add_argument(
        "-c", "--latlon", help="geodetic latitude/longitude (deg)", type=float, nargs=2, default=[65, -148.0],
    )
    #    p.add_argument('-m', '--makeplot', help='show to show plots, png to save pngs of plots', nargs='+', default=['show'])
    p.add_argument("-M", "--model", help="specify auroral model (glow,rees,transcar)", default="glow")
    p.add_argument(
        "-z", "--zlim", help="minimum,maximum altitude [km] to plot", nargs=2, default=(None, None), type=float,
    )
    p.add_argument(
        "--isotropic", help="(rees model only) isotropic or non-isotropic pitch angle", action="store_true",
    )
    p.add_argument(
        "--vlim", help="plotting limits on energy dep and production plots", nargs=2, type=float, default=(1e-7, 1e1),
    )

    p = p.parse_args()

    if not p.outfn:
        print("you have not specified an output file with -o options, so I will only plot and not save result")

    #    makeplot = p.makeplot

    if len(p.simtime) == 1:
        T = [parse(p.simtime[0])]
    elif len(p.simtime) == 2:
        T = list(rrule.rrule(rrule.HOURLY, dtstart=parse(p.simtime[0]), until=parse(p.simtime[1])))
    # %% input unit flux
    Egrid = loadregress(Path(p.inputgridfn).expanduser())
    Ebins = makebin(Egrid)[:3]
    EKpcolor, EK, diffnumflux = ekpcolor(Ebins)
    # %% ionospheric response
    """ three output eigenprofiles
    1) ver (optical emissions) 4-D array: time x energy x altitude x wavelength
    2) prates (production) 4-D array:     time x energy x altitude x reaction
    3) lrates (loss) 4-D array:           time x energy x altitude x reaction
    """
    model = p.model.lower()
    glat, glon = p.latlon

    if model == "glow":
        ver, photIon, isr, phitop, zceta, sza, prates, lrates, tezs, sion = makeeigen(
            EK, diffnumflux, T, p.latlon, p.makeplot, p.outfn, p.zlim
        )

        writeeigen(p.outfn, EKpcolor, T, ver.z_km, diffnumflux, ver, prates, lrates, tezs, p.latlon)
        # %% plots
        # input
        doplot(p.inputgridfn, Ebins)

        # output
        sim = namedtuple("sim", ["reacreq", "opticalfilter"])
        sim.reacreq = sim.opticalfilter = ""

        for t in ver:  # TODO for each time
            # VER eigenprofiles, summed over wavelength
            ploteigver(
                EKpcolor, ver.z_km, ver.sum("wavelength_nm"), (None,) * 6, sim, "{} Vol. Emis. Rate ".format(t),
            )
            # volume production rate, summed over reaction
            plotprodloss(
                prates.loc[:, "final", ...].sum("reaction"), lrates.loc[:, "final", ...].sum("reaction"), t, glat, glon, p.zlim,
            )
            # energy deposition
            plotenerdep(tezs, t, glat, glon, p.zlim)

    elif model == "rees":
        assert len(T) == 1, "only one time with rees for now."
        z = glowalt()
        q = reesiono(T, z, Ebins.loc[:, "low"], glat, glon, p.isotropic)

        writeeigen(p.outfn, Ebins, T, z, prates=q, tezs=None, latlon=(glat, glon))

        plotA(q, "Volume Production Rate {}  {} {}".format(T, glat, glon), p.vlim)
    elif model == "transcar":
        raise NotImplementedError("Transcar by request")
    else:
        raise NotImplementedError("I am not yet able to handle your model {}".format(model))
    # %% plots

    show()


if __name__ == "__main__":
    main()
