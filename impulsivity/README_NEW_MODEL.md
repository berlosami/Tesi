# NEW model

## Struttura
- `NEW_agent.py`: agente, lambda, delay reale, costo, mortalità, movimento.
- `NEW_baseline_model.py`: baseline puro.
- `NEW_uniform_mortality_model.py`: mortalità uniforme.
- `NEW_age_dependent_model.py`: mortalità dipendente dall'età.
- `NEW_run.py`: simulazioni, grafici e CSV.

## Parametri
- 1 step = 1 anno
- età iniziale = 10
- T = 120 anni
- R1 = 2
- R2 = 20
- D2 = 7
- lambda ~ Uniform(0.05, 0.50)
- METABOLIC_COST = 0

## Strategia
lambda* = ln(R2/R1)/D2 ≈ 0.329.
Sotto la soglia: paziente. Sopra: impulsivo.

## Visualizzazione
Il lambda reale non viene trasformato.
Solo i reporter:
- Mean Lambda: ×100
- Lambda Variance: ×1000

## Mortalità age-dependent
10–19: 0.01136
20–39: 0.01247
40–59: 0.01953
60–79: 0.05795
80–119: 0.05795

## Analisi
Baseline:
- energia pazienti vs impulsivi

Mortalità:
- popolazione
- frazioni pazienti/impulsivi
- lambda medio
- varianza lambda
- energia per strategia
- morti per strategia
