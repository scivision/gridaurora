#!/usr/bin/env python
from pathlib import Path
from numpy import arange
from argparse import ArgumentParser
from matplotlib.pyplot import show
from gridaurora.filterload import getSystemT
import gridaurora.plots as gap
from typing import List
import seaborn as sns

sns.set_style("whitegrid")
sns.set_context("talk", font_scale=1.5)

R = Path(__file__).parent


def selftest(
    bg3fn: Path, windfn: Path, qefn: Path, mmsLambda: List[float], obsalt_km: float, zenang_deg: float,
):

    newLambda = arange(mmsLambda[0], mmsLambda[1] + mmsLambda[2], mmsLambda[2], dtype=float)
    return getSystemT(newLambda, bg3fn, windfn, qefn, obsalt_km, zenang_deg)


def main():
    p = ArgumentParser(description="Plots spectral transmission data from filter datasheets")
    p.add_argument(
        "--wlnm", help="START STOP STEP wavelength in nm", nargs=3, default=(400.0, 700.0, 0.1), type=float,
    )
    p.add_argument("--path", help="path to HDF5 data")
    p.add_argument("-a", "--altkm", help="observer altitude (km)", type=float, default=0.0)
    p.add_argument("--zenang", help="zenith angle (deg)", type=float, default=0.0)
    p = p.parse_args()

    inpath = Path(p.path).expanduser() if p.path else R / "gridaurora/precompute"

    flist = [
        "BG3transmittance.h5",
        "NE01transmittance.h5",
        "Wratten32transmittance.h5",
        "Wratten21transmittance.h5",
        "HoyaV10transmittance.h5",
    ]
    flist = [inpath / f for f in flist]

    windFN = inpath / "ixonWindowT.h5"
    qeFN = inpath / "emccdQE.h5"
    # %%
    Ts = []
    for f in flist:
        T = selftest(f, windFN, qeFN, p.wlnm, p.altkm, p.zenang)
        Ts.append(T)
        # gap.plotT(T, p.wlnm,fname)
    # %% Rayleigh 1924
    Tr = 1.0
    RayleighFilterNames = ["Hoya V-10", "Wratten 21"]
    for r in RayleighFilterNames:
        Tr *= Ts[r]["filter"]
    Tr.filename = "Rayleigh 1924"
    Ts.append(Tr)

    # %%
    gap.comparefilters(Ts, RayleighFilterNames)

    show()


if __name__ == "__main__":
    main()
