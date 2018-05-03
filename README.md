# Population and Demographics Projection

Population and demographics projection module, developed for ITRC/MISTRAL.

ONS produce projections of the count of persons by gender and single year of age, specifically:
 - National (UK) and country-level population projections (NPP) with variants as listed in the table below. The data is currently 2016-based and projects to 2116.
 - Subnational (England at LAD level) *principal-only* population projections. The data is currently 2014-based and projects to 2039.
 
With the exeption of the NPP variants Nomisweb hosts the ONS data. [This may change](https://www.nomisweb.co.uk/forum/posts.aspx?tID=565&fID=2)

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

The purpose of the code in this repo is provide a unified interface to SNPP and NPP data, including variants:
- encapsulate the downloading of the NPP and SNPP data from the various sources.
- unify the format of the NPP and SNPP data from the various sources.
- provide a method of synthesising SNPP variant projections using SNPP principal and NPP principal/variant projections
- provide a method of extrapolating SNPP data using NPP data
- enable easy subsetting of the data, e.g. extracting projections of the working-age population.
