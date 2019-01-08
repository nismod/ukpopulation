import numpy as np
import pandas as pd
from openpyxl import load_workbook

def _read_cell_range(worksheet, topleft, bottomright):
  data_rows = []
  for row in worksheet[topleft:bottomright]:
    data_cols = []
    for cell in row:
      data_cols.append(cell.value)
    data_rows.append(data_cols)
  return np.array(data_rows)


sheet = load_workbook("./s2 Households.xlsx", read_only=True)["Households"]

raw = _read_cell_range(sheet,"A7", "AS32263")
snhp_e = pd.DataFrame(raw[1:,:], columns=raw[0,:])
#df = pd.DataFrame(a[:,1:], index=a[:,0], columns=['A', 'B','C','D'])

# remove years before 2011 census and switch years from columns to rows
snhp_e = snhp_e.drop([str(y) for y in range(2001,2011)], axis=1) \
  .melt(id_vars=["CODE", "AREA", "AGE GROUP", "HOUSEHOLD TYPE"]).drop("AREA", axis=1)
#print(snhp_e.columns.values)
# ensure count is numeric
snhp_e.value = snhp_e.value.astype(float)
#print(snhp_e.head())
# remove age categories and standardise column names
snhp_e = snhp_e.groupby(["CODE", "HOUSEHOLD TYPE", "variable"]).sum().reset_index() \
  .rename({"CODE": "GEOGRAPHY_CODE", 
           "HOUSEHOLD TYPE": "HOUSEHOLD_TYPE", 
           "variable": "PROJECTED_YEAR_NAME", 
           "value": "OBS_VALUE"}, axis=1)
#print(snhp_e.head())
#print(snhp_e.HOUSEHOLD_TYPE.unique())

snhp_e.to_csv("snhp_e.csv", index=False)
