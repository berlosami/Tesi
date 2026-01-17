
# **Bozza del modello**

Il modello analizza come l’avversione alle perdite (λ) cambi in funzione dello stress, della stabilità ambientale e delle differenze tra maschi e femmine, osservando gli effetti su sopravvivenza, accumulo di risorse e successo riproduttivo.
Ispirato ai modelli di foraging, gli agenti operano in un ambiente naturale semplificato (simile ad un villaggio rurale), dove devono compiere scelte rischiose, di conservazione e riproduttive.

Gli step rappresentano unità temporali discrete della simulazione.
Ogni step è un ciclo completo in cui tutti gli agenti: percepiscono l’ambiente, prendono decisioni, aggiornano energia, subiscono eventuali eventi di stress, si muovono tra patch, se necessario, alla ricerca di risorse migliori, tentano il mating, verificano sopravvivenza.

A ogni step gli agenti scelgono (in base al valore assegnato loro di λ)tra:

* **Opzione sicura** → guadagno energetico costante, con probabilità minima di perdita
* **Opzione rischiosa** → guadagno potenzialmente maggiore, con probabilità di perdita.

**ENERGIA**

Ogni agente possiede un livello energetico che aumenta con i guadagni,diminuisce con i costi di movimento e con eventuali perdite.
L'energia dell’agente determina la sopravvivenza, la possibilità di spostarsi nell'ambiente e di accedere al mating, queste ultime due richiedono di superare una soglia di energia (condizione fisiologica minima), se scende sotto una certa soglia l'agente muore. I livelli energetici sono differenziati tra uomini e donne

Il movimento tra patch ambientali (piccole unità di territorio) simula la ricerca di nuove risorse:

* nell’ambiente **stabile** sono omogenei, prevedibili e poco variabili
* nell’ambiente **instabile** le patch variano molto in qualità, alcune possono contenere molte risorse, altre nulla, alcune con rischio di perdite, rendendo la mobilità più importante ma anche più rischiosa.

Nella condizione con ambiente instabile ci sono più agenti attivi ne consegue una maggiore competizione e pressione sulle risorse, quindi il rischio di non raggiungere la soglia riproduttiva.


La riproduzione avviene solo se: l’agente dispone di energia sufficiente e lo step è favorevole (va definita una finestra temporale in cui è possibile il concepimento come simulasse il ciclo mestruale). In più la percentuale di possibilità riproduttiva varia in funzione dell'ambiente, se è stabile o meno.

Gli agenti che riescono ad accoppiarsi contribuiscono alla fitness complessiva della strategia decisionale adottata.

**AMBIENTI**

Ambiente stabile-> risorse prevedibili, bassa varianza tra patch, pochi imprevisti e stress raro-> opzione sicura sufficiente per mantenere energia e accedere al mating.

Ambiente instabile-> risorse imprevedibili e varianza elevata, frequenti imprevisti e stress ricorrente-> opzione sicura potrebbe essere insufficiente.

**CONDIZIONI SPERIMENTALI**

Il modello si baserà principalmente su quattro condizioni sperimentali, che combinano due livelli di avversione alle perdite (λ) e due tipi di ambiente:

1. λ alto – ambiente stabile
2. λ alto – ambiente instabile
3. λ basso – ambiente stabile
4. λ basso – ambiente instabile

**STRESS**

Periodicamente alcuni agenti subiscono uno stress event: λ aumenta temporaneamente e le decisioni diventano più prudenti, il recupero è progressivo.

Questo riproduce la risposta fisiologica allo stress acuto, influenzando foraging, mobilità e probabilità di mating (energia più difficile da accumulare durante questi step).

Gli eventi stressanti verranno caratterizzati da carestie, rischi di predazione e competizione sociale. (da valutare: condizioni atmosferiche e stagionalità).

**AGENTI MASCHI E FEMMINE**

Il modello include variabilità biologica coerente con la letteratura su rischio, stress e comportamento riproduttivo:

Generalizzando i maschi presentano un lambda di base più basso, una reattività allo stress moderata, un recupero più rapido e una propensione al rischio maggiore delle femmine. In più la strategia riproduttiva risulta competitiva nei maschi e conservativa nelle femmine.

Insieme, foraging, sopravvivenza e mating permettono di osservare la loss aversion non come semplice bias, ma come strategia evolutivamente modulabile, la cui efficacia cambia al mutare dell’ambiente.

(da valutare: età di ciascun agente, da cui può dipendere la riproduzione, l'energia disponibile...)

**RICONOSCERE LA LOSS AVERSION**

La loss aversion emerge dal modo in cui l’agente reagisce a situazioni simmetriche: stesso potenziale guadagno di energia, stessa potenziale perdita di energia, stessa probabilità.
L’unica cosa che cambia è il peso attribuito alla perdita tramite λ.

Se due agenti con le stesse condizioni ambientali prendono decisioni diverse solo perché lambda è diverso, allora la differenza deriva esclusivamente dall’avversione alle perdite.
Nella risk aversion invece non importa la perdita conta solo l'incertezza.

**PARAMETRI DA RICAVARE DALLA LETTERATURA** (altri da definire)

Lambda tipico: 2 (Tversky & Kahneman, 1992)

Lambda consigliato come standard: 1.31 https://doi.org/10.1016/j.joep.2024.102740

Da valutare quale scegliere come lambda alto e basso.

Stress multiplier (moltiplicatore durante stress acuto): +10/20%    
doi: 10.3389/fnhum.2016.00444

Non ho trovato un parametro robusto che mi permetta di creare un λ distinto tra maschi e femmine, comunemente per i modelli vengono scelti valori arbitrari, i quali possono basarsi sulle conclusioni di alcuni studi https://doi.org/10.1007/s11166-019-09315-3   
doi: 10.1111/bjop.12668 iii

