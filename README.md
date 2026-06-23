# Bike Sharing Demand Forecasting (BSTS)

A data pipeline that ingests Jersey City Citi Bike trip data and historical weather data into AWS, enabling statistical analysis of urban mobility demand.

## Motivation

This project builds on a progression of earlier work. [OLS](https://github.com/ShengPeiWilliam/bikerental-ml) pointed toward count regression. [Poisson and Negative Binomial](https://github.com/ShengPeiWilliam/bikerental-poisson) improved fit but suggested that weather effects might not be uniform across contexts a rainy workday and a rainy weekend probably hit demand differently. That observation motivated adding interaction terms.

Rather than being constrained by a fixed dataset, this project builds the data pipeline from scratch automatically pulling Citibike trip data and historical weather from their sources into AWS so the features we actually want are available rather than whatever happened to be in a pre-packaged CSV.

The modeling question then becomes more specific: do member and casual riders respond to weather the same way? A member is mostly a commuter with somewhere to be. A casual rider is making a discretionary choice. BSTS with spline temperature effects and interaction terms is used to quantify whether that difference is real and how large it is.

## Design Decisions

**Why separate member and casual riders?**

Aggregating total rides forces a single weather coefficient on two groups that likely behave differently. Members are mostly commuters with a fixed destination; casual riders are making a discretionary choice. Fitting separate models lets the data answer whether that difference is real rather than assuming it away.

**Why BSTS instead of standard GLM?**

Daily demand is autocorrelated and GLM ignores that structure. More importantly, the question is how much the two groups differ, not just whether they do. Bayesian posteriors give a full distribution of plausible effect sizes; a frequentist p-value only tells you whether something clears a significance threshold.

**Why interaction between temperature and workingday?**

A commuter rides to the PATH station regardless of weather because they have somewhere to be. A casual rider is making a discretionary trip. If it's cold or rainy, they can simply not go. The `temp:workingday` interaction tests whether weather hits demand harder on non-working days, and quantifies how large that gap actually is.