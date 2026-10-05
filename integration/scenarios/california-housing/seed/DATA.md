# California housing

- File: `data/raw/housing.csv`
- One row is one census tract.
- Target column: `MedHouseVal` (median house value).
- Columns: `MedInc`, `HouseAge`, `AveRooms`, `AveBedrms`, `Population`, `AveOccup`, `Latitude`, `Longitude`.
- No dates, no groups, and no separate test table.
- Compare models with RMSE.
- Comparison model: a dummy mean predictor.
- Use 2 folds. This file contains 5,000 census tracts.
