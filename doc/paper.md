---
title: 'ukpopulation: unified national and subnational population estimates and projections, including variants'
tags:
  - python
  - data science
  - population
  - projection
authors:
 - name: Andrew P Smith
   orcid: 0000-0002-9951-6642
   affiliation: 1
 - name: Tom Russell
   orcid: 0000-0002-0081-400X
   affiliation: 2
affiliations:
 - name: School of Geography and Leeds Institute for Data Analytics, University of Leeds
   index: 1
 - name: Environmental Change Institute, School of Geography and the Environment, University of Oxford
   index: 2
date: 31 May 2018
bibliography: paper.bib
---

# Summary

UK statistics agencies (ONS, StatsWales, NRScotland and NISRA) produce mid-year population estimates, national and subnational  population estimates and projections, by single year of age, gender. Mid-year estimates and subnational population projections are at local authority district (or equivalent) geography; national projections are produced for England, Wales, Scotland, Northern Ireland,

At the time of writing (June 2018), mid-year estimates are available from 1991 to 2016. Subnational population projections typically have a 25-year horizon and in most cases cover the period 2016-2041. National projections have a longer horizon, extending from 2016 to 2116.  

The datasets published online in different places and in different formats, depending on the originating agency. The data may require significant preprocessing/reformatting before it can be used in e.g.  python code. 

Population projection variants (e.g. high fertility) are extremely useful for scenario analyses and a number of population projection variants available at national scale. However, the availability of variants at subnational scale is patchy at best.

This python package aims unify the retrieval of UK-wide data, providing consistent interfaces for each of the three datasets (national/subnational/mid-year estimate). It also provides a simple methodology for extrapolating the shorter-term subnational data using the longer-term national data, whilst preserving the age-gender structure present at the smaller geography. In a similar manner, it also enables the approximation of subnational projection variants from the national variants (again preserving the local age-gender structure).

This functionality allows researchers and policymakers to examine population growth trajectories and construct plausible projections, both principal and variant, at subnational scale, consistently for anywhere in the UK over longer time horizons than the official data permit.

# References
