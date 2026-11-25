# Project notes — Credit Risk Engine

I built a transparent stack connecting Merton-style distance-to-default, rating-migration loss simulation, and Basel IRB risk-weight sensitivities on public equity prices with illustrative debt inputs.

**Limitations I document:** debt is not live EDGAR, and PD uses Φ(-DD) rather than a proprietary EDF map. The point is implementable risk math I can defend and independently challenge.
