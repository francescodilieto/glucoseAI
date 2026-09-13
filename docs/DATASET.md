# Demo dataset

The CSVs in `data/demo/` are a small derived subset of the **BIG IDEAs Lab
Glycemic Variability and Wearable Device Data** dataset, used here to
demonstrate the application end-to-end without any real, identifiable
patient data.

- Source: https://physionet.org/content/big-ideas-glycemic-wearable/1.1.2/
- License: Open Data Commons Attribution License v1.0 (ODC-By) — redistribution
  and reuse are permitted with attribution.
- What we kept: only the Dexcom G6 continuous glucose monitor (CGM) stream
  (`Dexcom_XXX.csv`, "EGV" rows) for 3 participants, first 3 days each.
  Wearable signals (accelerometer, EDA, heart rate, etc.), food logs and
  demographics were dropped — they aren't used by this project.
- Regenerate with: `python3 scripts/extract_demo_data.py`

## Citation

> Cho, P., Kim, S., Bent, B., & Dunn, J. (2023). BIG IDEAs Lab Glycemic
> Variability and Wearable Device Data (version 1.1.2). PhysioNet.
>
> Bent, B., Cho, P.J., Wittmann, A. et al. Engineering digital biomarkers
> of interstitial glucose from noninvasive smartwatches. *npj Digital
> Medicine* 4, 89 (2021).

The original dataset participants are already de-identified and their
timestamps time-shifted by the dataset authors; no additional anonymization
was needed for this demo subset.
