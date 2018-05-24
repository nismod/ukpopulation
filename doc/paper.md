---
title: 'ukpopulation: unified national and subnational population projections, including variants'
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
   orcid: TODO Tom...
   affiliation: 2
affiliations:
 - name: School of Geography and Leeds Institute for Data Analytics, University of Leeds
   index: 1
 - name: TODO Tom..., University of Oxford
   index: 2
date: 31 May 2018
bibliography: paper.bib
---

# Summary

UK statistics agencies (ONS, StatsWales, NRScotland and NISRA) produce national and subnational population projections, by single year of age, gender, and by either country (for national), or local authority district or equivalent (for subnational). The publication dates and time horizons typically differ between national (currently 2016-2116) and subnational (currently 2014-2039), and the actual data are published online in different places and in different formats, depending on the originating agency. There are a number of projection variants available at national scale, but coverage of variants at subnational scale is patchy at best.

This python package unifies the retrieval of UK-wide data into a single interface for each dataset (national/subnational). It also provides functionality to extrapolate the shorter-term subnational data using the longer-term national data, whilst preserving the age-gender structure present at the smaller geography. In a similar manner, national projection variants can be applied at subnational scale (again preserving age-gender structure).

This functionality allows researchers and policymakers to construct plausible projections, both principal and variant, at subnational scale, consistently for anywhere in the UK, and over longer time horizons than the official data permit. 

# References
