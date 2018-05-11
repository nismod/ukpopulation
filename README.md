[![Build Status](https://travis-ci.org/nismod/population.png?branch=master)](https://travis-ci.org/nismod/population) [![License](https://img.shields.io/github/license/mashape/apistatus.svg)](https://opensource.org/licenses/MIT)

# population: Demographic Projections

Population and demographics projection module, developed for ITRC/MISTRAL.

ONS produce projections of the count of persons by gender and single year of age, specifically:
 - National (UK) and country-level population projections (NPP) with variants as listed in the table below. The data is currently 2016-based and projects to 2116.
 - Subnational (England at LAD level) *principal-only* population projections. The data is currently 2014-based and projects to 2039.
 
With the exception of the NPP variants Nomisweb hosts the ONS data. [This may change](https://www.nomisweb.co.uk/forum/posts.aspx?tID=565&fID=2)

Other countries within the UK produce (and host) their own SNPP data, typically in spreadsheet format. 

 
**E**ngland **S**cotland **W**ales and **N**orthern Ireland statistics authorities
separately produce sub-national population projections (at LAD or LAD-equivalent
level) for the variants as indicated by an `x` in the table. The ONS currently regard these (the England ones at least) as ["experimental"](https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationprojections/articles/subnationalpopulationprojectionsresearchreportonvariantprojections/2014basedprojections).


scenario                         | code | E | S | W | N |
---------------------------------|------|---|---|---|---|
Principal                        | ppp  | x | x | x | x |
High fertility                   | hpp  | x | x |   |   |
Low fertility                    | lpp  |   | x |   |   |
High life expectancy             | php  |   | x |   |   |
Low life expectancy              | plp  |   | x |   |   |
High migration                   | pph  |   | x |   |   |
Low migration                    | ppl  |   | x |   |   |
High population                  | hhh  |   |   | x |   |
Low population                   | lll  |   |   | x |   |
Zero net migration               | ppz  | x | x | x |   |
Young age structure              | hlh  |   |   |   |   |
Old age structure                | lhl  |   |   |   |   |
Replacement fertility            | rpp  |   |   |   |   |
Constant fertility               | cpp  |   |   |   |   |
No mortality improvement         | pnp  |   |   |   |   |
No change                        | cnp  |   |   |   |   |
Long term balanced net migration | ppb  |   |   | x |   |

# Rationale

The purpose of the code in this repo is provide a unified interface to both SNPP and NPP data, including variants:
- encapsulate the downloading, processing and cacheing of the NPP and SNPP data from the various sources.
- unify the format of the NPP and SNPP data from the various sources.
- provide a method of synthesising SNPP variant projections using SNPP principal and NPP principal/variant projections
- provide a method of extrapolating SNPP data using NPP data
- enable easy filtering and aggregating of of the data, e.g. extracting projections of the working-age population.

# Methodology and Detail
## Data Sources
- [Nomisweb](www.nomisweb.co.uk): UK NPP by country/SYoA/gender, England SNPP by LAD/SYoA/gender
- [ONS](https://www.ons.gov.uk): UK NPP variants by country/SYoA/gender
- [Stats Wales](http://open.statswales.gov.wales): Wales SNPP by LAD/SYoA/gender
- [National Records of Scotland](https://www.nrscotland.gov.uk): Scotland SNPP by LAD equivalent/SYoA/gender
- [Northern Ireland Statistics and Research Agency](https://www.nisra.gov.uk): Northern Ireland SNPP by LAD equivalent/SYoA/gender

## Data Processing
- Note that SNPP data is 2014-based while NPP data is 2016-based.
- NPP data is broken down by country (England/Wales/Scotland/Northern Ireland), with the following variants available:
  - hhh: High population, 
  - hpp: High fertility,
  - lll: Low population,
  - lpp: Low fertility,
  - php: High life expectancy,
  - pjp: Moderately high life expectancy,
  - pkp: Moderately low life expectancy,
  - plp: Low life expectancy,
  - pph: High migration,
  - ppl: Low migration,
  - ppp: Principal,
  - ppq: 0% future EU migration (non-ONS),
  - ppr: 50% future EU migration (non-ONS),
  - pps: 150% future EU migration (non-ONS),
  - ppz: Zero net migration
- Column headings and category values follow the nomisweb/census conventions:
  - `GEOGRAPHY_CODE`: ONS country, LAD, or LAD-equivalent code
  - `GENDER`: 1=Male, 2=Female
  - `C_AGE`: 0-90, where 90 represents 90 or over. To avoid ambiguity, this is an exception - nomisweb census values are typically age+1)
  - `PROJECTED_YEAR_NAME`: 2014-2116   
  - `OBS_VALUE`: count of persons
- All data are cached for swift retrieval.  

# Installation

## Requirements
Python 3.5 or higher, dependencies should resolve automatically

```bash
$ pip3 install git+https://github.com/nismod/population.git
```

## Testing

Requires that `NOMIS_API_KEY` is defined, but set to "DUMMY" so that the cached data filenames match those in the test dataset:

```bash
$ NOMIS_API_KEY=DUMMY ./setup.py test
```

## Troubleshooting

Please post any issues you encounter in the repo, with as much supporting information as possible.

If installation has missing dependencies, try:
```bash
$ pip install -r requirements.txt
$ ./setup.py install
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

# Usage Examples

## Retrieve SNPP for specific LADs
### Detailed data
```python
>>> import population.snppdata as SNPPData
>>> snpp = SNPPData.SNPPData("./raw_data")
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
>>>
```

### Aggregated data
TODO...

## Retrieve NPP and SNPP filtered by age
TODO...

## Retrieve NPP variants for England & Wales
TODO...

## Extrapolate SNPP using NPP data
TODO...

## Construct an SNPP variant by applying NPP variant to a specific LAD
TODO...

## Extrapolating an SNPP variant

