---
name: project-cgan-limitation
description: "Known limitation of the cGAN in 0602_cGAN_Training.ipynb — generates near-1:1 variations anchored to the source trip, not a true continuous manifold"
metadata: 
  node_type: memory
  type: project
  originSessionId: 4291a574-4976-487d-87b0-97b0c72a9507
---

The cGAN (Generator/Discriminator v4/v5 in `Phase_6_Generative_Moonshots/0602_cGAN_Training.ipynb`) does not have mode collapse and the synthetic physics output is nearly 1:1 with the real dataset — but this is itself the limitation. With only 5 continuous physics vars (`upfront_fare`, `est_trip_time_sec`, `est_trip_dist_km`, `time_to_pickup_sec`, `dist_to_pickup_km`) conditioned on 6 discrete categorical switches (hour, day_of_week, product_category, dropoff_zone_id, pickup_zone_id, reason_primary_fk), the generator learns a near-deterministic mapping per context combination — the latent noise input ends up with little real influence because the discriminator punishes any deviation from the real support within a given context cell.

Practical effect (as described by user 2026-07-04): feeding one real trip's context yields ~10K variations that are all minimal, physics-respecting perturbations tightly anchored to that source trip — "the real base exploded into all possible combinations," not a genuinely novel/infinite universe. Good enough for anonymization-style resampling, not for modeling genuinely new scenarios.

**Why:** conditional overfitting — {real trip} × {noise ≈ ignored}, not a continuous learned distribution over the physics space. Root cause is architectural/training (discriminator too dominant relative to noise signal, no diversity-promoting loss term like minibatch discrimination or feature matching), not a data or mode-collapse problem.

**How to apply:** Do not attempt to fix this via retraining/architecture changes while in the Streamlit results/demo phase — out of scope for now, explicitly deferred by user. If a more "infinite manifold" feel is needed for a demo, the cheap workaround discussed (not yet implemented) is to perturb the sampling/conditioning at inference time — e.g. jitter to neighboring zones/hours or blend switches from 2-3 similar real trips — rather than touching the model. Revisit the actual architecture/training fix only if the user later asks to open [[project_perf_tricks]]-style backlog work on this model, similar treatment to that deferred-until-feature-complete list.
