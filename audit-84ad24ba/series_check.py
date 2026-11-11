#!/usr/bin/env python3
"""Value-by-value check of the historical data files behind the Black swan pages (session 84ad24ba).

The values below were read by this session on 2026-11-11 on the official listing of each series
(the "View All" table of FRED for the FHFA, BLS and BIS series; the NYU Stern table for returns)
and are compared here with the files the model reads in final/data/.

Run from the repository root:  python3 audit-84ad24ba/series_check.py
Writes audit-84ad24ba/series_check_result.json.  Only public data; no owner figure.
"""
import csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), 'final', 'data')


def nums(text):
    return [float(x) for x in text.split()]


# FHFA all-transactions index, fourth quarter (observation dated YYYY-10-01), 1975 to 2025
YEARS_Q4 = list(range(1975, 2026))
SJ = nums("""19.14 23.21 30.02 32.66 40.49 47.66 52.27 50.50 52.72 56.65 60.95 65.56 72.14 90.70 114.25 107.32
106.23 104.34 101.44 99.95 102.45 108.06 122.46 138.45 157.67 203.54 205.16 216.22 220.87 255.24 309.48 318.32
302.81 258.84 237.76 240.85 235.66 252.50 291.32 319.27 353.92 373.83 396.48 425.46 415.13 419.68 463.63 510.15
546.45 558.19 560.05""")
SF = nums("""19.28 23.70 28.62 31.52 40.23 45.17 46.03 45.89 49.44 52.64 58.13 65.71 78.06 98.50 113.64 109.68
107.13 104.16 101.60 98.88 100.94 103.59 114.45 127.97 150.39 184.16 192.89 206.94 219.05 256.29 301.62 307.14
298.91 267.06 250.31 248.26 240.50 257.01 296.34 329.82 374.38 396.57 416.06 445.81 442.90 425.06 451.73 487.95
495.49 505.79 512.99""")
CA = nums("""45.75 55.58 70.69 81.80 96.36 108.39 117.54 115.82 117.67 122.73 130.50 141.05 157.17 187.35 224.54 228.46
228.63 222.56 214.11 200.93 203.49 201.53 212.21 231.79 249.95 285.37 316.27 358.56 411.05 515.81 625.13 642.37
575.13 444.32 412.19 405.64 385.24 398.78 461.60 499.74 536.77 572.35 610.68 640.88 662.82 698.85 833.14 886.84
915.73 956.74 969.38""")

# BLS consumer price index CPIAUCSL, December (observation dated YYYY-12-01), 1974 to 2025
YEARS_CPI = list(range(1974, 2026))
CPI = nums("""51.900 55.600 58.400 62.300 67.900 76.900 86.400 94.100 97.700 101.400 105.500 109.500 110.800 115.600
120.700 126.300 134.200 138.200 142.300 146.300 150.100 153.900 159.100 161.800 164.400 168.800 174.600 177.400
181.800 185.500 191.700 198.100 203.100 211.445 211.398 217.347 220.472 227.223 231.221 234.719 236.252 237.761
242.637 247.805 252.767 258.630 262.045 280.845 298.832 308.741 317.604 326.031""")

# BIS residential property prices for Japan QJPN368BIS, percent per annum, fourth quarter, 1990 to 2020
YEARS_JP = list(range(1990, 2021))
JP = nums("""12.3206 -0.1597 -4.8000 -3.5854 -1.8013 -1.6272 -1.7143 -1.2240 -2.1995 -3.4526 -4.0026 -4.7163 -5.6313
-6.4234 -5.7271 -4.2654 -2.1152 -0.7356 -2.5475 -2.8462 2.0014 -0.9977 -0.4367 2.8003 0.5907 1.9576 2.5280 1.8102
2.5138 0.9569 1.5699""")

# NYU Stern table, 1928 to 2025: S&P 500 with dividends, 3-month T.Bill, 10-year T.Bond, real estate (percent)
STERN = """1928 43.81 3.08 0.84 1.49
1929 -8.30 3.16 4.20 -2.06
1930 -25.12 4.55 4.54 -4.30
1931 -43.84 2.31 -2.56 -8.15
1932 -8.64 1.07 8.79 -10.47
1933 49.98 0.96 1.86 -3.81
1934 -1.19 0.28 7.96 2.91
1935 46.74 0.17 4.47 9.77
1936 31.94 0.17 5.02 3.22
1937 -35.34 0.28 1.38 2.56
1938 29.28 0.07 4.21 -0.87
1939 -1.10 0.05 4.41 -1.30
1940 -10.67 0.04 5.40 3.31
1941 -12.77 0.13 -2.02 -8.38
1942 19.17 0.34 2.29 3.33
1943 25.06 0.38 2.49 11.45
1944 19.03 0.38 2.58 16.58
1945 35.82 0.38 3.80 11.78
1946 -8.43 0.38 3.13 24.10
1947 5.20 0.60 0.92 21.26
1948 5.70 1.05 1.95 2.06
1949 18.30 1.12 4.66 0.09
1950 30.81 1.20 0.43 3.64
1951 23.68 1.52 -0.30 6.05
1952 18.15 1.72 2.27 4.41
1953 -1.21 1.89 4.14 11.52
1954 52.56 0.94 3.29 0.92
1955 32.60 1.72 -1.34 0.00
1956 7.44 2.62 -2.26 0.91
1957 -10.46 3.22 6.80 2.72
1958 43.72 1.77 -2.10 0.66
1959 12.06 3.39 -2.65 0.11
1960 0.34 2.87 11.64 0.77
1961 26.64 2.35 2.06 0.98
1962 -8.81 2.77 5.69 0.32
1963 22.61 3.16 1.68 2.14
1964 16.42 3.55 3.73 1.26
1965 12.40 3.95 0.72 1.66
1966 -9.97 4.86 2.91 1.22
1967 23.80 4.29 -1.58 2.32
1968 10.81 5.34 3.27 4.13
1969 -8.24 6.67 -5.01 6.99
1970 3.56 6.39 16.75 8.22
1971 14.22 4.33 9.79 4.24
1972 18.76 4.06 2.82 2.98
1973 -14.31 7.04 3.66 3.42
1974 -25.90 7.85 1.99 10.07
1975 37.00 5.79 3.61 6.77
1976 23.83 4.98 15.98 8.18
1977 -6.98 5.26 1.29 14.65
1978 6.51 7.18 -0.78 15.72
1979 18.52 10.05 0.67 13.74
1980 31.74 11.39 -2.99 7.40
1981 -4.70 14.04 8.20 5.10
1982 20.42 11.09 32.81 0.56
1983 22.34 8.95 3.20 4.75
1984 6.15 9.92 13.73 4.68
1985 31.24 7.72 25.71 7.47
1986 18.49 6.15 24.28 9.61
1987 5.81 5.96 -4.96 7.85
1988 16.54 6.89 8.22 7.22
1989 31.48 8.39 17.69 4.39
1990 -3.06 7.75 6.24 -0.69
1991 30.23 5.54 15.00 -0.17
1992 7.49 3.51 9.36 0.82
1993 9.97 3.07 14.21 2.16
1994 1.33 4.37 -8.04 2.52
1995 37.20 5.66 23.48 1.79
1996 22.68 5.15 1.43 2.43
1997 33.10 5.20 9.94 4.02
1998 28.34 4.91 14.92 6.44
1999 20.89 4.78 -8.25 7.68
2000 -9.03 6.00 16.66 9.29
2001 -11.85 3.48 5.57 6.68
2002 -21.97 1.64 15.12 9.56
2003 28.36 1.03 0.38 9.81
2004 10.74 1.40 4.49 13.64
2005 4.83 3.22 2.87 13.51
2006 15.61 4.85 1.96 1.73
2007 5.48 4.48 10.21 -5.40
2008 -36.55 1.40 20.10 -12.00
2009 25.94 0.15 -11.12 -3.85
2010 14.82 0.14 8.46 -4.12
2011 2.10 0.05 16.04 -3.89
2012 15.89 0.09 2.97 6.44
2013 32.15 0.06 -9.10 10.72
2014 13.52 0.03 10.75 4.50
2015 1.38 0.05 1.28 5.19
2016 11.77 0.32 0.69 5.31
2017 21.61 0.95 2.80 6.21
2018 -4.23 1.97 -0.02 4.52
2019 31.21 2.11 9.64 3.69
2020 18.02 0.36 11.33 10.43
2021 28.47 0.04 -4.42 18.86
2022 -18.04 2.09 -17.83 5.65
2023 26.06 5.28 3.88 5.68
2024 24.88 5.18 -1.64 3.96
2025 17.78 4.21 7.80 1.58"""

SOURCES = {
    'FHFA index, San Jose, fourth quarter': 'https://fred.stlouisfed.org/data/ATNHPIUS41940Q',
    'FHFA index, San Francisco, fourth quarter': 'https://fred.stlouisfed.org/data/ATNHPIUS41884Q',
    'FHFA index, California, fourth quarter': 'https://fred.stlouisfed.org/data/CASTHPI',
    'Consumer price index, December': 'https://fred.stlouisfed.org/data/CPIAUCSL',
    'Japan residential property prices, fourth quarter': 'https://fred.stlouisfed.org/data/QJPN368BIS',
    'NYU Stern returns table': 'https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html',
}


def rows(name):
    return {int(r['year']): r for r in csv.DictReader(open(os.path.join(DATA, name), encoding='utf-8'))}


def main():
    out, bad = [], []

    def compare(label, years, official, table, column, tol=0.0005):
        assert len(years) == len(official), (label, len(years), len(official))
        n = miss = 0
        for y, v in zip(years, official):
            cell = table.get(y, {}).get(column, '')
            if cell in ('', None):
                continue                                   # the data file has no value for that year
            n += 1
            if abs(float(cell) - v) > tol:
                miss += 1
                bad.append('%s %d: file %s, official %s' % (label, y, cell, v))
        out.append(dict(series=label, official_listing=SOURCES[label], values_compared=n, differences=miss,
                        first_year=years[0], last_year=years[-1]))

    fred = rows('hist_fred.csv')
    compare('FHFA index, San Jose, fourth quarter', YEARS_Q4, SJ, fred, 'hpi_sanjose_ATNHPIUS41940Q_q4')
    compare('FHFA index, San Francisco, fourth quarter', YEARS_Q4, SF, fred, 'hpi_sf_ATNHPIUS41884Q_q4')
    compare('FHFA index, California, fourth quarter', YEARS_Q4, CA, fred, 'hpi_ca_CASTHPI_q4')
    compare('Consumer price index, December', YEARS_CPI, CPI, fred, 'cpi_dec_CPIAUCSL')
    compare('Japan residential property prices, fourth quarter', YEARS_JP, JP, rows('hist_japan.csv'), 'home_yoy_pct')
    stern = rows('hist_returns_damodaran.csv')
    n = miss = 0
    cols = ('sp500_total_return_pct', 'tbill_3m_pct', 'tbond_10y_return_pct', 'real_estate_national_pct')
    lines = STERN.strip().split('\n')
    for line in lines:
        p = line.split()
        y = int(p[0])
        for c, v in zip(cols, p[1:]):
            cell = stern.get(y, {}).get(c, '')
            if cell in ('', None):
                continue
            n += 1
            if abs(float(cell) - float(v)) > 0.0005:
                miss += 1
                bad.append('NYU Stern %d %s: file %s, official %s' % (y, c, cell, v))
    out.append(dict(series='NYU Stern returns table', official_listing=SOURCES['NYU Stern returns table'],
                    values_compared=n, differences=miss, first_year=int(lines[0].split()[0]), last_year=int(lines[-1].split()[0])))
    total = sum(o['values_compared'] for o in out)
    json.dump(dict(read_on='2026-11-11', series=out, values_compared=total, differences=len(bad), detail=bad),
              open(os.path.join(HERE, 'series_check_result.json'), 'w'), indent=1)
    for o in out:
        print('%-52s %4d values, %d differences' % (o['series'], o['values_compared'], o['differences']))
    for b in bad:
        print('DIFF', b)
    print('%d values compared, %d differences' % (total, len(bad)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
