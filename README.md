# NYC Citibike Demand Analysis (BSTS)

[![Full Report](https://img.shields.io/badge/📄_Read_Full_Report-PDF-blue?style=for-the-badge)](report/citybike_report.tex)

Daily member vs casual ridership analysis on 1,065 days of NYC Citibike data
(2022--2024), using Bayesian Structural Time Series to separate how two
fundamentally different rider populations respond to weather and calendar
conditions.

Most demand analyses aggregate total rides into a single outcome. Fitting
BSTS models separately for member and casual counts reveals that workday
status drives a divergence of nearly **1,000 rides per day** between the
two groups (+461 member, -520 casual), while temperature sensitivity is
similar across both. Season effects vanish entirely once temperature and
weather category are controlled for.

## Motivation

This project builds on a progression of earlier work.
[OLS](https://github.com/ShengPeiWilliam/bikerental-ml) pointed toward
count regression.
[Poisson and Negative Binomial](https://github.com/ShengPeiWilliam/bikerental-poisson)
improved fit but suggested that weather effects might not be uniform across
contexts: a rainy workday and a rainy weekend probably hit demand differently
depending on whether the rider is a commuter or a tourist.

Rather than being constrained by a fixed dataset, this project builds the
data pipeline from scratch, automatically pulling Citibike trip records and
historical weather data into AWS S3 so the features needed for interaction
modeling are available from the start.

The modeling question then becomes more specific: do member and casual riders
respond to weather the same way? BSTS with spike-and-slab variable selection
and interaction terms is used to quantify whether that difference is real
and how large it is.

## Design Decisions

**Why separate member and casual riders?**

Aggregating total rides forces a single weather coefficient on two groups
that likely behave differently. Members are mostly commuters with a fixed
destination; casual riders are making a discretionary choice. Fitting
separate models lets the data answer whether that difference is real rather
than assuming it away.

**Why BSTS instead of standard GLM?**

Daily demand is autocorrelated and GLM ignores that structure. More
importantly, the question is how much the two groups differ, not just
whether they do. Bayesian posteriors give a full distribution of plausible
effect sizes; a frequentist p-value only tells you whether something clears
a significance threshold. The R-squared gap confirms this matters: BSTS
achieves 0.93 for members vs OLS's 0.72 by absorbing temporal structure
that OLS attributes to calendar dummies.

**Why interaction between temperature and workingday?**

A commuter rides regardless of weather because they have somewhere to be.
A casual rider is making a discretionary trip. The `temp_max:workingday`
interaction tests whether temperature hits casual demand harder on non-working
days. The result confirms it: on workdays, temperature sensitivity drops by
-20 rides/°C (inc.prob = 1.0) for casual riders, because leisure demand is
suppressed regardless of conditions.

## Key Results

**Headline finding**: Workday status is the dominant differentiator between member and casual ridership, producing a net divergence of ~1,000 rides per day. Season effects are not selected by BSTS once temperature is controlled for.

| Finding | Detail |
|---------|--------|
| **Workday divergence** | Working days: +461 member rides, -520 casual rides |
| **Temperature** | Similar effect for both groups (~+29 to +40 rides per °C) |
| **Season** | Not selected by BSTS (inc.prob ≈ 0); fully absorbed by temperature |
| **Weather x workday** | Casual riders less temperature-sensitive on workdays (-20 rides/°C, inc.prob = 1.0) |

| Model | Member R² | Casual R² |
|-------|-----------|-----------|
| OLS Baseline | 0.72 | 0.76 |
| **BSTS Baseline** | **0.93** | **0.86** |

## Business Recommendations

1. **Weekday capacity**: Optimize station allocation for predictable member commuting patterns, which are stable regardless of weather
2. **Weekend promotions**: Target casual rider campaigns on non-working days with favorable weather forecasts, when casual demand peaks
3. **Weather-based pricing**: Rainy-day incentives (e.g., discounted casual trips) could retain casual riders during adverse weather and build habitual usage

## Reflections & Next Steps

The main lesson: separating member and casual riders reveals structure
that aggregate models hide entirely. The 1,000-ride workday divergence is
invisible in total demand, and season effects that appear significant in OLS
turn out to be temperature in disguise once BSTS absorbs slow-moving temporal variation.

Next steps:
- **Station-level analysis**: The current model is city-level. Station-level heterogeneity in supply and demand could reveal localized patterns for more targeted interventions.
- **Causal evaluation**: A difference-in-differences design could test whether targeted promotional interventions shift the member-to-casual ratio as predicted by the model coefficients.
- **Formal convergence diagnostics**: Models used 1,000 MCMC iterations with visual monitoring. Adding R-hat statistics would strengthen the inferential claims.

## Repository

```
src/
├── citybike_ingestion.py   # Citibike trip data ingestion to AWS S3
├── weather_ingestion.py    # Open-Meteo weather data ingestion
└── processing.py           # Data merging and feature engineering
report/                     # LaTeX report and R analysis
figures/                    # EDA and model output plots
```

## Tools

**Statistical methods**: BSTS, OLS, Spike-and-slab variable selection, VIF diagnostics
**Language**: R
**Libraries**: bsts, BoomSpikeSlab, car, ggplot2
**Infrastructure**: AWS S3, Open-Meteo API

## References

Scott, S.L., & Varian, H.R. (2014). Predicting the present with Bayesian structural time series. *International Journal of Mathematical Modelling and Numerical Optimisation*, 5(1/2), 4--23.

Citibike NYC. (2024). [System Data](https://citibikenyc.com/system-data).

Open-Meteo. (2024). [Historical Weather API](https://open-meteo.com).
