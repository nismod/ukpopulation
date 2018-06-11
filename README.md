[![Build Status](https://travis-ci.org/nismod/ukpopulation.png?branch=master)](https://travis-ci.org/nismod/ukpopulation) [![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://opensource.org/licenses/MIT)
[![Version 1.0.0](https://zenodo.org/badge/doi/10.5281/zenodo.1250366.svg)](https://github.com/nismod/ukpopulation/releases/tag/1.0.0)

# ukpopulation: UK Demographic Projections

The statistical agencies of the United Kingdom, that is: ONS, StatsWales, NR Scotland, and NISRA, all produce population projection data. Although the data are essentially the same, the quantity, format, and availability varies between agencies and datasets. All of the projection data is available by (single year of) age and gender.

National population projections (NPP) are the responsibility of ONS who provide the data for each country within the UK, including 15 variants covering a number of possible future scenarios. The current data is based on 2016 population estimates and project a century to 2116.

Subnational population projections (SNPP) are the responsiblity of each country's agencies (ONS for England), are based on 2014 population estimates and project 25 years to 2039.

## Coverage

The countries within the UK produce their own SNPP data, and also produce some (patchy) variant projections. The ONS currently regard these (the England ones at least) as ["experimental"](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationprojections/articles/subnationalpopulationprojectionsresearchreportonvariantprojections/2014basedprojections). 

Scenario/Variant                 | Code | E | S | W | N |NPP|
---------------------------------|------|---|---|---|---|---|
Principal                        | ppp  | x | x | x | x | x |
High fertility                   | hpp  | x | x |   |   | x |
Low fertility                    | lpp  |   | x |   |   | x |
High life expectancy             | php  |   | x |   |   | x |
Low life expectancy              | plp  |   | x |   |   | x |
Moderately high life expectancy  | pjp  |   |   |   |   | x |
Moderately low life expectancy   | plp  |   |   |   |   | x |
High migration                   | pph  |   | x |   |   | x |
Low migration                    | ppl  |   | x |   |   | x |
High population                  | hhh  |   |   | x |   | x |
Low population                   | lll  |   |   | x |   | x |
0% future EU migration           | ppq  |   |   |   |   | x |
50% future EU migration          | ppr  |   |   |   |   | x |
150% future EU migration         | pps  |   |   |   |   | x |
Zero net migration               | ppz  | x | x | x |   | x |
Young age structure              | hlh  |   |   |   |   |   |
Old age structure                | lhl  |   |   |   |   |   |
Replacement fertility            | rpp  |   |   |   |   |   |
Constant fertility               | cpp  |   |   |   |   |   |
No mortality improvement         | pnp  |   |   |   |   |   |
No change                        | cnp  |   |   |   |   |   |
Long term balanced net migration | ppb  |   |   | x |   |   |

## Accessibility

[Nomisweb](www.nomisweb.co.uk) provides an API which allows relatively easy programmatical access the to data, and by far the preferred source of data. Currently not all the data is available from this source but [this may change](https://www.nomisweb.co.uk/forum/posts.aspx?tID=565&fID=2).

Nomisweb currently hosts the ONS principal NPP data for the UK, and the SNPP data for England.  

All other data: ONS NPP variants, SNPP data for Wales, Scotland and Northern Ireland are available in different formats from the appropriate agency's website.

# Rationale

The purpose of this package is to provide a unified interface to both SNPP and NPP data, including variants:
- encapsulating the downloading, processing and cacheing of the NPP and SNPP data from the various sources.
- consistently differentiating by age (single year, up to 90) and gender over the various datasets.
- providing a unified format for all the data.
- providing a method of synthesising SNPP variant projections using SNPP principal and NPP principal/variant projections
- providing a method of extrapolating SNPP data using NPP data
- enabling easy filtering and aggregating of of the data, e.g. extracting projections of the working-age population.

# Methodology and Detail
## Data Sources
- [Nomisweb](www.nomisweb.co.uk): UK NPP by country/SYoA/gender, England SNPP by LAD/SYoA/gender
- [ONS](https://www.ons.gov.uk): UK NPP variants by country/SYoA/gender
- [Stats Wales](http://open.statswales.gov.wales): Wales SNPP by LAD/SYoA/gender
- [National Records of Scotland](https://www.nrscotland.gov.uk): Scotland SNPP by LAD equivalent/SYoA/gender
- [Northern Ireland Statistics and Research Agency](https://www.nisra.gov.uk): Northern Ireland SNPP by LAD equivalent/SYoA/gender

## Data Processing
- Note that SNPP data is 2014-based while NPP data is 2016-based.
- NPP data is broken down by country (England/Wales/Scotland/Northern Ireland), for all the variant projections indicated in the table above. 
- Column headings and category values follow the nomisweb/census conventions:
  - `GEOGRAPHY_CODE`: ONS country, LAD, or LAD-equivalent code
  - `GENDER`: 1=Male, 2=Female
  - `C_AGE`: 0-90, where 90 represents 90 or over. To avoid ambiguity, this is an exception - nomisweb census values are typically age+1)
  - `PROJECTED_YEAR_NAME`: 2014-2116   
  - `OBS_VALUE`: count of persons
- All data are cached for swift retrieval.  

# Extrapolation 

The extrapolation methodology is explained by the following equation for the aggregate SNPP _S(g,y)_ for a given geography and year.

![eq1](doc/img/Extrapolate_eqn.gif)

where _N_ is the NPP, _a_ is age, _s_ is gender, _y bar_ is a reference year (typically the final year in the SNPP data), and _c(g)_ represents a mapping from a SNPP geography (LAD) to a NPP one (country).

# Projection of Variants

Similarly the methodology for synthesising SNPP variants from SNPP and NPP data is:

![eq2](doc/img/Variant_eqn.gif)

where the subscripts _V_ and _0_ refer to the variant and the principal projections respectively. 

# Installation

## Requirements

### API Key
This package uses the [UKCensusAPI](http://github.com/virgesmith/UKCensusAPI) package to obtain some of the projection data. The package requires an API key to function correctly, see [here](https://github.com/virgesmith/UKCensusAPI/blob/master/README.md) for details. 

### Python

Requires Python 3.5 or higher. Dependencies *should* resolve automatically, but if not see [troubleshooting](#troubleshooting) 

```bash
$ pip3 install git+https://github.com/nismod/population.git
```

Some of the examples (see below) plot graphs and have a dependency on matplotlib, which can be installed with
```bash
$ pip3 install matplotlib
```

## Testing

The test data cache directory contains a file NOMIS_API_KEY which defines a dummy key for testing purposes only. The test suit can be run using:

```bash
$ ./setup.py test
```

## Troubleshooting

If installation has missing dependencies, try:
```bash
$ pip install -r requirements.txt
$ ./setup.py install
```
The UKCensusAPI dependency *should* be resolved automatically, but if not you can force installation using
```bash
pip3 install git+https://github.com/virgesmith/UKCensusAPI.git
```

If (with python 3.5?) you encounter 
```bash
AttributeError: module 'html5lib.treebuilders' has no attribute '_base'
```
then
```bash
$ pip3 install html5lib=0.9999999
```
should fix it. But better solution is to upgrade to python3.6

If matplotlib fails to install due to a missing dependency (tkinter), this can be fixed on Debian variants by

```bash
$ sudo apt install python3-tk
```

If your problem isn't addressed above, please post an issue including as much supporting information as possible.

# Usage Examples

## Retrieve SNPP for specific LADs
### Detailed data
This example fetches the 2018 projection for Newcastle by gender and age. 
```python
>>> import ukpopulation.snppdata as SNPPData
>>> snpp = SNPPData.SNPPData()
```
```
Cache directory:  ./raw_data/
using cached LAD codes: ./raw_data/lad_codes.json
Collating SNPP data for England...
./raw_data/NM_2006_1_metadata.json found, using cached metadata...
Using cached data: ./raw_data/NM_2006_1_56aba41fc0fab32f58ead6ae91a867b4.tsv
./raw_data/NM_2006_1_metadata.json found, using cached metadata...
Using cached data: ./raw_data/NM_2006_1_dbe6c087fb46306789f7d54b125482e4.tsv
Collating SNPP data for Wales...
Collating SNPP data for Scotland...
Collating SNPP data for Northern Ireland...
```
```python
>>> newcastle=snpp.filter("E08000021", 2018)
>>> newcastle.head()
```
```
   C_AGE  GENDER GEOGRAPHY_CODE  OBS_VALUE  PROJECTED_YEAR_NAME
0      0       1      E08000021     1814.0                 2018
1      1       1      E08000021     1780.0                 2018
2      2       1      E08000021     1770.0                 2018
3      3       1      E08000021     1757.0                 2018
4      4       1      E08000021     1747.0                 2018
```

### Aggregated data
This example fetches the total population projections for Newcastle from 2018 to 2039.
```python 
>>> import ukpopulation.snppdata as SNPPData
>>> snpp = SNPPData.SNPPData()
```
```
Cache directory:  ./raw_data/
using cached LAD codes: ./raw_data/lad_codes.json
Collating SNPP data for England...
./raw_data/NM_2006_1_metadata.json found, using cached metadata...
Using cached data: ./raw_data/NM_2006_1_56aba41fc0fab32f58ead6ae91a867b4.tsv
./raw_data/NM_2006_1_metadata.json found, using cached metadata...
Using cached data: ./raw_data/NM_2006_1_dbe6c087fb46306789f7d54b125482e4.tsv
Collating SNPP data for Wales...
Collating SNPP data for Scotland...
Collating SNPP data for Northern Ireland...
```python
>>> newcastle=snpp.aggregate(["GENDER", "C_AGE"], "E08000021", range(2018,2039))
>>> newcastle.head()
```
```
  GEOGRAPHY_CODE  PROJECTED_YEAR_NAME  OBS_VALUE
0      E08000021                 2018   299132.0
1      E08000021                 2019   300530.0
2      E08000021                 2020   301699.0
3      E08000021                 2021   302729.0
4      E08000021                 2022   303896.0
```

## Retrieve NPP data filtered by age
Here's how to get the total working-age population by country from 2016 to 2050:

```python
>>> import ukpopulation.nppdata as NPPData
>>> npp = NPPData.NPPData()
```
```
Cache directory:  ./raw_data/
using cached LAD codes: ./raw_data/lad_codes.json
Loading NPP principal (ppp) data for England, Wales, Scotland & Nortern Ireland
./raw_data/NM_2009_1_metadata.json found, using cached metadata...
Using cached data: ./raw_data/NM_2009_1_444caf1f672f0646722e389963289973.tsv
```
```python
>>> uk_working_age=npp.aggregate(["GENDER", "C_AGE"], "ppp", NPPData.NPPData.UK, range(2016,2051), ages=range(16,75))
>>> uk_working_age.head()
  GEOGRAPHY_CODE  PROJECTED_YEAR_NAME  OBS_VALUE
0      E92000001                 2016   40269470
1      E92000001                 2017   40460118
2      E92000001                 2018   40591965
3      E92000001                 2019   40704521
4      E92000001                 2020   40834471
```
And this aggregates the figures for Great Britain:
```python
>>> gb_working_age=npp.aggregate(["GEOGRAPHY_CODE", "GENDER", "C_AGE"], "ppp", NPPData.NPPData.GB, range(2016,2051), ages=range(16,75))
>>> gb_working_age.head()
   PROJECTED_YEAR_NAME  OBS_VALUE
0                 2016   46590014
1                 2017   46801693
2                 2018   46944219
3                 2019   47063069
4                 2020   47201882
```
NB SNPP data can also be filtered by age and/or gender and/or geography in the same way.

## Retrieve NPP variants for England & Wales

First detailed data (by age, gender and country), then aggregated by age and gender.

```python
>>> import ukpopulation.nppdata as NPPData
>>> npp=NPPData.NPPData()
Cache directory:  ./raw_data/
using cached LAD codes: ./raw_data/lad_codes.json
Loading NPP principal (ppp) data for England, Wales, Scotland & Nortern Ireland
./raw_data/NM_2009_1_metadata.json found, using cached metadata...
Using cached data: ./raw_data/NM_2009_1_444caf1f672f0646722e389963289973.tsv
>>> high_growth = npp.detail("hhh", NPPData.NPPData.EW)
>>> high_growth.head()
   C_AGE  GENDER  OBS_VALUE  PROJECTED_YEAR_NAME GEOGRAPHY_CODE
0      0       1     343198                 2016      E92000001
1      0       1     334025                 2017      E92000001
2      0       1     345332                 2018      E92000001
3      0       1     349796                 2019      E92000001
4      0       1     354274                 2020      E92000001
>>> high_growth_agg = npp.aggregate(["GENDER", "C_AGE"], "hhh", NPPData.NPPData.EW)
>>> high_growth_agg.head()
  GEOGRAPHY_CODE  PROJECTED_YEAR_NAME  OBS_VALUE
0      E92000001                 2016   55268067
1      E92000001                 2017   55660155
2      E92000001                 2018   56115027
3      E92000001                 2019   56568795
4      E92000001                 2020   57019007
>>>
```

## Extrapolate SNPP using NPP data

### Single Area

Construct aggregate SNPP data for Newcastle from 2018-2065:
- use the SNPP data up to 2039, aggregated by age and gender. 
- extrapolate the NPP data whilst preserving Newcastle's (2039) age-gender structure.
- aggregrate the extrapolated data by age and gender
- plot the data. 

[Source Code](doc/example_extrapolate.py)

![Extrapolated Newcastle Population Projection](doc/img/Newcastle_ex.png)

### Bulk Calculation

In this example we extraplolate and aggregrate the SNPP for every LAD in Wales:
- for each area, 
  - extrapolate from 2039 to 2050 using the 2039 age-gender structure.
  - aggregate the extrapolated data by age and gender.
  - append to full dataset.
- save Wales dataset as csv:

| GEOGRAPHY_CODE | PROJECTED_YEAR_NAME | OBS_VALUE |
| -------------- | ------------------- | --------- |
| W06000011 | 2040 | 262903.24103359133 |
| W06000011 | 2041 | 262933.2340468692 |
| W06000011 | 2042 | 263162.3661643687 |
| W06000011 | 2043 | 263332.96819104964 |
| W06000011 | 2044 | 263593.29826455784 |
| W06000011 | 2045 | 263923.03553008236 |
| W06000011 | 2046 | 264243.6253810904 |
| W06000011 | 2047 | 264168.2113917932 |
| W06000011 | 2048 | 264211.4576059673 |
| ...       | ...  | ...               |

[Source Code](doc/example_extrapolate_all.py)

## Construct an SNPP variant by applying NPP variant to a specific LAD

Here we apply the "hhh" (high growth) and "lll" (low growth) NPP variants to the SNPP data for Newcastle:
- calculate the principal ("ppp") projection by simply aggregrating the SNPP data for Newcastle, 2018-2039, by age and gender.
- calculate the variants by weighting the unaggregated data (i.e. by age and gender) by the ratio of the NPP variant/principal.
- aggregrate the variant data by age and gender.
- plot the results.
 
[Source Code](doc/example_variant.py)

![Newcastle Population Projection Variants](doc/img/Newcastle_var.png)

## Extrapolating an SNPP variant

Here we build on the examples above by not only applying the NPP variant, but extrapolating too. The process first involves extrapolating the SNPP by the NPP principal variant. The extrapolated data then has the variant adjustments applied to it.  
 
[Source Code](doc/example_variant_ex.py)

![Newcastle Population Projection Variants](doc/img/Newcastle_var_ex.png)


# Code Documentation
Package documentation can be viewed like so:
```python
import ukpopulation.nppdata as NPPData
help(NPPData)
```
and
```python
import ukpopulation.snppdata as SNPPData
help(SNPPData)
```
# Acknowledgements
This package was developed as a component of the EPSRC sponsored [MISTRAL](https://www.itrc.org.uk/) programme, part of the Infrastructure Transition Research Consortium.
