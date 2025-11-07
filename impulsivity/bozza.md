# **Bozza del modello**

Il modello analizza come l’impulsività emerga in funzione dello stress, della stabilità ambientale e delle differenze tra maschi e femmine, osservando gli effetti su sopravvivenza, accumulo di risorse e successo riproduttivo.
L’impulsività non è una condizione sperimentale manipolata direttamente, ma emerge dal comportamento degli agenti, osservabile come preferenza tra ricompensa immediata e differita/rischiosa in funzione di energia, età e ambiente.

Ispirato ai modelli di foraging, gli agenti operano in un ambiente naturale semplificato (simile a un villaggio rurale), dove devono compiere scelte rischiose, di conservazione e riproduttive.

Gli step rappresentano unità temporali discrete della simulazione. Ogni step corrisponde a un giorno; un anno è composto da 365 step.

Ogni step è un ciclo completo in cui tutti gli agenti: percepiscono l’ambiente, aggiornano il livello di stress, prendono decisioni, aggiornano energia, subiscono eventuali eventi di stress, si muovono tra patch, se necessario, alla ricerca di risorse migliori, tentano il mating, verificano sopravvivenza.

A ogni step gli agenti scelgono tra:

* **Opzione sicura** → guadagno energetico piccolo ma immediato, con probabilità minima di perdita
* **Opzione rischiosa** → guadagno potenzialmente maggiore, ottenibile solo dopo un periodo di attesa, con probabilità di perdita

Gli agenti scelgono tra opzione sicura e opzione rischiosa/differita, valutando naturalmente il trade-off energia/attesa.
Dopo qualche ciclo di simulazione, ci si aspetta di osservare la direzione prevalente delle scelte degli agenti, da cui emerge la strategia dominante.


**ENERGIA**

Ogni agente possiede un livello energetico che aumenta con i guadagni, diminuisce con i costi di movimento e con eventuali perdite.
L’energia dell’agente determina la sopravvivenza, la possibilità di spostarsi nell'ambiente e di accedere al mating; queste ultime due richiedono di superare una soglia di energia (condizione fisiologica minima). Se l’energia scende sotto una certa soglia l'agente muore.

I livelli energetici iniziali, i costi metabolici giornalieri e i costi riproduttivi sono differenziati tra uomini e donne, in accordo con differenze fisiologiche.

Il movimento tra patch ambientali (piccole unità di territorio) simula la ricerca di nuove risorse:

* nell’ambiente **stabile** i patch sono omogenei, prevedibili e poco variabili
* nell’ambiente **instabile** i patch variano molto in qualità, alcuni possono contenere molte risorse, altri nulla, alcuni con rischio di perdite, rendendo la mobilità più importante ma anche più rischiosa


La riproduzione avviene solo se: l’agente dispone di energia sufficiente e lo step è favorevole (viene definita una finestra temporale che simula il ciclo mestruale). In più la percentuale di possibilità riproduttiva varia in funzione dell'ambiente, se è stabile o meno.

L’età dell’agente influenza la probabilità di riproduzione, l’efficienza energetica e la mortalità naturale.

Gli agenti che riescono ad accoppiarsi contribuiscono alla fitness complessiva della strategia decisionale adottata.

**AMBIENTI**

Ambiente stabile → risorse prevedibili, bassa varianza tra patch, pochi imprevisti → l’opzione sicura è generalmente sufficiente per mantenere energia e accedere al mating.

Ambiente instabile → risorse imprevedibili e varianza elevata → l’opzione sicura potrebbe essere insufficiente per raggiungere la soglia riproduttiva.

**CONDIZIONI SPERIMENTALI**

Il modello si baserà principalmente su quattro condizioni sperimentali, che combinano due tipi di ambiente e due livelli di attesa/ricompensa:

1. **Ambiente stabile – opzione sicura**
2. **Ambiente stabile – opzione rischiosa/differita**
3. **Ambiente instabile – opzione sicura**
4. **Ambiente instabile – opzione rischiosa/differita**


**STRESS**

Periodicamente alcuni agenti subiscono uno stress event. Gli eventi stressanti sono legati a carestie e predazione.

Lo stress è acuto e di intensità identica sia in ambiente stabile che instabile. Durante uno stress event gli agenti accumulano energia in modo meno efficiente e il rischio di mortalità è più alto.

**AGENTI MASCHI E FEMMINE**

Il modello include variabilità biologica coerente con la letteratura su rischio, stress e comportamento riproduttivo.

Generalizzando, i maschi presentano una maggiore propensione al rischio, una risposta allo stress più rapida e un recupero più veloce, associati a una preferenza naturale per opzioni rischiose quando il guadagno atteso è alto.

Le femmine presentano una maggiore conservazione energetica, costi riproduttivi più elevati e una preferenza per opzioni sicure/immediate, associate a un comportamento più conservativo.

**RICONOSCERE L’IMPULSIVITÀ**

L’impulsività emerge dal modo in cui l’agente sceglie tra opzione sicura/immediata e opzione differita/rischiosa nelle stesse condizioni di energia, età e ambiente.

Se due agenti nelle stesse condizioni prendono decisioni diverse, la differenza osservata deriva dalle caratteristiche individuali e dalla valutazione temporale della ricompensa, e non dalla struttura del problema decisionale.



