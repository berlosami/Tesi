
# **Bozza del modello**

Il modello analizza come l’impulsività emerga in funzione dello stress, della stabilità ambientale e delle differenze tra maschi e femmine, osservando gli effetti su sopravvivenza, accumulo di risorse e successo riproduttivo.
L’impulsività non è un parametro diretto del modello, ma è definita come **deviazione dalla scelta ottimale** in condizioni date di energia, età e ambiente.

Ispirato ai modelli di foraging, gli agenti operano in un ambiente naturale semplificato (simile ad un villaggio rurale), dove devono compiere scelte rischiose, di conservazione e riproduttive.

Gli step rappresentano unità temporali discrete della simulazione. Ogni step corrisponde a **un giorno**; un anno è composto da **365 step**.

Ogni step è un ciclo completo in cui tutti gli agenti: percepiscono l’ambiente, aggiornano il livello di stress, prendono decisioni, aggiornano energia, subiscono eventuali eventi di stress, si muovono tra patch, se necessario, alla ricerca di risorse migliori, tentano il mating, verificano sopravvivenza.

A ogni step gli agenti scelgono tra:

* **Opzione sicura** → guadagno energetico costante, con probabilità minima di perdita
* **Opzione rischiosa** → guadagno potenzialmente maggiore, con probabilità di perdita

Per ogni agente e per ogni step è possibile definire una **scelta ottimale**, ovvero quella che massimizza il valore atteso di fitness futura.
Il processo decisionale è influenzato da un **rumore decisionale**, che rappresenta limiti cognitivi, ridotta capacità di controllo e variabilità nel comportamento.

Il rumore decisionale non altera la struttura del problema decisionale né il valore della scelta ottimale, ma **aumenta la probabilità che l’agente non la segua**.
L’impulsività è misurata come la frequenza o l’entità di queste deviazioni dall’ottimo.

---

**ENERGIA**

Ogni agente possiede un livello energetico che aumenta con i guadagni, diminuisce con i costi di movimento e con eventuali perdite.
L’energia dell’agente determina la sopravvivenza, la possibilità di spostarsi nell'ambiente e di accedere al mating; queste ultime due richiedono di superare una soglia di energia (condizione fisiologica minima). Se l’energia scende sotto una certa soglia l'agente muore.

I livelli energetici iniziali, i costi metabolici giornalieri e i costi riproduttivi sono **differenziati tra uomini e donne**, in accordo con differenze fisiologiche.

---

Il movimento tra patch ambientali (piccole unità di territorio) simula la ricerca di nuove risorse:

* nell’ambiente **stabile** sono omogenei, prevedibili e poco variabili
* nell’ambiente **instabile** le patch variano molto in qualità, alcune possono contenere molte risorse, altre nulla, alcune con rischio di perdite, rendendo la mobilità più importante ma anche più rischiosa

Nella condizione con ambiente instabile ci sono più agenti attivi; ne consegue una maggiore competizione e pressione sulle risorse, quindi il rischio di non raggiungere la soglia riproduttiva.

---

La riproduzione avviene solo se: l’agente dispone di energia sufficiente e lo step è favorevole (viene definita una finestra temporale che simula il ciclo mestruale). In più la percentuale di possibilità riproduttiva varia in funzione dell'ambiente, se è stabile o meno.

L’età dell’agente influenza la probabilità di riproduzione, l’efficienza energetica e la mortalità naturale.

Gli agenti che riescono ad accoppiarsi contribuiscono alla fitness complessiva della strategia decisionale adottata.

---

**AMBIENTI**

Ambiente stabile → risorse prevedibili, bassa varianza tra patch, pochi imprevisti → l’opzione sicura è generalmente sufficiente per mantenere energia e accedere al mating.

Ambiente instabile → risorse imprevedibili e varianza elevata → l’opzione sicura potrebbe essere insufficiente per raggiungere la soglia riproduttiva.

---

**CONDIZIONI SPERIMENTALI**

Il modello si baserà principalmente su quattro condizioni sperimentali, che combinano due tipi di ambiente e due livelli di **rumore decisionale**:

1. **Basso rumore decisionale – ambiente stabile**
2. **Basso rumore decisionale – ambiente instabile**
3. **Alto rumore decisionale – ambiente stabile**
4. **Alto rumore decisionale – ambiente instabile**

Il rumore decisionale rappresenta la capacità dell’agente di seguire la scelta ottimale.
Un rumore basso implica decisioni più coerenti con l’ottimo; un rumore alto implica maggiore variabilità e maggiore probabilità di scelte subottimali.

L’impulsività non è una condizione sperimentale manipolata direttamente, ma **una variabile emergente** che viene misurata come deviazione media dalla scelta ottimale nelle diverse condizioni.

---

**STRESS**

Periodicamente alcuni agenti subiscono uno stress event. Gli eventi stressanti sono esclusivamente legati a **carestie e predazione**.

Lo stress è **acuto e di intensità identica** sia in ambiente stabile che instabile. Durante uno stress event il rumore decisionale aumenta temporaneamente, riducendo la capacità dell’agente di seguire la scelta ottimale; il recupero è progressivo.

Lo stress riduce l’efficienza di accumulo energetico e aumenta la probabilità di scelte subottimali durante questi step.

---

**AGENTI MASCHI E FEMMINE**

Il modello include variabilità biologica coerente con la letteratura su rischio, stress e comportamento riproduttivo.

Generalizzando, i maschi presentano una maggiore propensione al rischio, una risposta allo stress più rapida e un recupero più veloce, associati a un livello medio di rumore decisionale più elevato.

Le femmine presentano una maggiore conservazione energetica, costi riproduttivi più elevati e una minore variabilità decisionale, associate a un livello medio di rumore decisionale più basso.

---

**RICONOSCERE L’IMPULSIVITÀ**

L’impulsività emerge dal modo in cui l’agente devia dalla scelta ottimale in condizioni identiche: stesso stato energetico, stessa età, stesso ambiente, stesse probabilità di guadagno e perdita.

Se due agenti nelle stesse condizioni prendono decisioni diverse esclusivamente a causa di un diverso livello di rumore decisionale, allora la differenza osservata deriva dalla capacità di seguire l’ottimo e non dalla struttura del problema decisionale.

In questo senso l’impulsività è distinta sia dalla risk aversion (sensibilità alla varianza) sia dalla loss aversion (peso attribuito alle perdite).

---

Se vuoi, il prossimo passo naturale potrebbe essere:

* scrivere **le ipotesi sperimentali (H1–H4)** coerenti con queste condizioni
* oppure formalizzare **matematicamente il rumore decisionale (es. softmax)**
* oppure adattare il testo **direttamente in linguaggio da tesi/paper**

Dimmi tu come proseguire.


