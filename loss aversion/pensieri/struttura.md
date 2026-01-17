
## Implementazione del modello

### Obiettivo

L’obiettivo del modello è esplorare **in che misura l’avversione alle perdite (loss aversion)** venga influenzata dallo stress e in quali condizioni ambientali essa possa rappresentare una **strategia adattiva per la sopravvivenza** degli agenti, piuttosto che un **ostacolo decisionale**.

Per indagare questo fenomeno, è stato implementato un **modello ad agenti** (Agent-Based Model) basato sulla libreria *Mesa (versione 3.1.5)* in Python.
Ogni agente rappresenta un individuo che prende decisioni economiche in un ambiente naturale semplificato (non si intende economico finanziario, ma situazioni dove si presentano guadagni e perdite), dove può scegliere tra un’opzione **sicura** e una **rischiosa**, e la sua sopravvivenza dipende dall’equilibrio tra rischio e conservazione delle risorse.


I valori utilizzati per definire l’ambiente stabile (probabilità di perdita pari a 0.1 e ricompensa sicura di 0.05) non provengono da misurazioni empiriche dirette, bensì da una modellizzazione teorica coerente con la letteratura sulla *risk-sensitive foraging theory*. In tali modelli, un ambiente stabile è caratterizzato da bassa variabilità delle risorse e da un rischio contenuto di incorrere in perdite. I parametri adottati rientrano negli intervalli comunemente utilizzati nella simulazione computazionale del comportamento decisionale (Stephens & Krebs 1986; Real & Caraco 1986; McNamara & Houston 1987). Essi rappresentano quindi condizioni sperimentali controllate più che stime ecologiche reali.

* Gintis (2009) *The Bounds of Reason* (risk & decision models)
* Dayan & Daw (2008) (RL in uncertain environments)
* Niv et al. (2012) (computational models di decisione e incertezza)


Analogamente, i parametri utilizzati per rappresentare l’ambiente instabile (probabilità di perdita elevata e ricompensa sicura ridotta) non intendono riprodurre un ecosistema specifico, ma simulare condizioni di alta variabilità ambientale, scarsità di risorse e imprevedibilità degli esiti. Tale impostazione è coerente con i modelli di decisione sotto incertezza sviluppati nell’ecologia comportamentale e nelle scienze cognitive, dove gli ambienti instabili vengono definiti da un aumento della varianza nelle ricompense e da un rischio maggiore di incorrere in eventi avversi.

| Parametro                 |                              Significato | Valori consigliati (default)        | Nota/giustificazione                                                         |
| ------------------------- | ---------------------------------------: | ----------------------------------- | ---------------------------------------------------------------------------- |
| `lambda` (basso)          |                   loss aversion baseline | **1.2**                             | sotto la media; utile per confronti                                          |
| `lambda` (tipico)         |                 loss aversion “standard” | **2.0 – 2.25**                      | valore vicino alla stima classica. ([wrap.warwick.ac.uk][1])                 |
| `lambda` (alto)           |                    loss aversion elevata | **3.0**                             | estremo plausibile per test robustezza                                       |
| `stress multiplier`       | moltiplicatore acuto su λ durante stress | **1.2 – 1.8**                       | studi mostrano aumento moderato; usa 1.5 come valore centrale. ([PubMed][2]) |
| `p_loss (stabile)`        |         probabilità di perdita in gamble | **0.05 – 0.15** (default **0.1**)   | ambiente low-variance. (modellistico)                                        |
| `p_loss (instabile)`      |         probabilità di perdita in gamble | **0.3 – 0.5** (default **0.4**)     | ambiente high-variance. (modellistico)                                       |
| `safe_reward (stabile)`   |                    payoff opzione sicura | **0.04 – 0.06** (default **0.05**)  | scala relativa a gain/loss del gamble                                        |
| `safe_reward (instabile)` |                    payoff opzione sicura | **0.01 – 0.03** (default **0.02**)  | risorse più scarse                                                           |
| `gain` (gamble)           |                   payoff positivo gamble | **0.15 – 0.25** (default **0.2**)   | scala coerente con esempi                                                    |
| `loss` (gamble)           |                   payoff negativo gamble | **-0.05 – -0.2** (default **-0.1**) | perdita moderata                                                             |
| `stress p (baseline)`     |    probabilità di evento stress per step | **0.05 – 0.15** (default **0.10**)  | manipolabile                                                                 |
| `sex adjustment`          |                   differenza λ tra sessi | **F = λ * 1.1** (≈ +10%)            | riflette letteratura su rischio; testare robustezza. ([rady.ucsd.edu][3])    |

[1]: https://wrap.warwick.ac.uk/id/eprint/185745/13/1-s2.0-S0167487024000485-main.pdf?utm_source=chatgpt.com "A meta-analysis of loss aversion in risky contexts"
[2]: https://pubmed.ncbi.nlm.nih.gov/33989652/?utm_source=chatgpt.com "Early stages of the acute physical stress response increase ..."
[3]: https://rady.ucsd.edu/_files/faculty-research/uri-gneezy/gender-differences-preference.pdf?utm_source=chatgpt.com "Gender Differences in Preferences"

---

### Struttura dell’ambiente

Il contesto simulato è caratterizzato da due **tipologie di ambiente**:

1. **Ambiente stabile**

   * Probabilità di perdita (*p_loss*) = 0.1
   * Guadagno sicuro (*safe_reward*) = 0.05
   * Le risorse sono relativamente prevedibili e il rischio di perdita è basso.

2. **Ambiente instabile**

   * Probabilità di perdita (*p_loss*) = 0.4
   * Guadagno sicuro (*safe_reward*) = 0.02
   * Le risorse sono meno affidabili e le perdite sono più frequenti.

Questa distinzione consente di osservare se l’avversione alle perdite può risultare più o meno vantaggiosa in contesti ambientali differenti.

---

### Parametro psicologico: λ (Loss Aversion)

Ogni agente possiede un parametro λ (lambda) che rappresenta il grado di **avversione alle perdite**.
Il parametro deriva dalla *Prospect Theory* (Kahneman & Tversky, 1979), secondo la quale le perdite vengono percepite come più rilevanti dei guadagni di pari entità.

* **λ alto (es. 2.0)** → l’agente percepisce le perdite come due volte più pesanti rispetto ai guadagni equivalenti.
* **λ basso (es. 1.2)** → le perdite e i guadagni hanno un impatto più bilanciato.

Per simulare l’effetto dello **stress**, a ogni passo temporale un sottoinsieme di agenti (circa il 10%) subisce un incremento temporaneo di λ.
Questo meccanismo rappresenta l’effetto dello **stress acuto** che aumenta la sensibilità alle perdite e induce comportamenti più conservativi.

---

### Meccanismo decisionale

A ogni iterazione della simulazione, ogni agente valuta due opzioni:

* **Opzione sicura:** guadagno fisso e privo di rischio (*safe_reward*).
* **Opzione rischiosa:** guadagno maggiore ma con una probabilità di perdita (*p_loss*).

La decisione è guidata dal **valore soggettivo (Subjective Value)** calcolato come:

[
SV = \text{guadagno} - \lambda \times \text{perdita}
]

L’agente sceglie l’alternativa con il valore soggettivo più elevato.
Se la scelta comporta una perdita, il valore di ricchezza (wealth) dell’agente diminuisce in misura proporzionale, altrimenti aumenta.

---

### Condizioni sperimentali

Sono state implementate quattro condizioni sperimentali, che combinano due livelli di avversione alle perdite (λ) e due tipi di ambiente:

1. λ alto – ambiente stabile
2. λ alto – ambiente instabile
3. λ basso – ambiente stabile
4. λ basso – ambiente instabile

Ogni simulazione segue un numero prefissato di step temporali (ad esempio 20), e viene registrata l’evoluzione della **ricchezza media** della popolazione di agenti nel tempo.
Questo consente di analizzare in quale combinazione di parametri l’avversione alle perdite favorisca la stabilità e la sopravvivenza nel lungo periodo.

---

### Output e interpretazione

Nel modello base, si osserva che la **ricchezza media** degli agenti aumenta progressivamente nel tempo, indicando una capacità adattiva del sistema.
Tuttavia, l’entità e la stabilità dell’aumento variano in base alla combinazione tra **livello di λ** e **stabilità ambientale**:

* In ambienti **stabili**, un λ **moderato o basso** tende a favorire la crescita costante delle risorse.
* In ambienti **instabili**, un λ **più alto** può proteggere gli agenti da perdite gravi, aumentando la probabilità di sopravvivenza.

Questi risultati permettono di discutere l’avversione alle perdite non solo come un bias cognitivo, ma come una **strategia potenzialmente adattiva** in contesti ecologicamente incerti.



## Differenze tra agenti maschili e femminili

Per indagare il ruolo delle differenze di genere nella modulazione dell’avversione alle perdite, il modello è stato esteso introducendo due **tipologie di agenti**:

* **Agenti maschili**,
* **Agenti femminili**.

Questa distinzione si basa su evidenze della **letteratura psicologica e neuroscientifica** che indicano come lo stress e la percezione del rischio vengano elaborati in modo parzialmente diverso nei due sessi.

---

### Parametri distintivi

Ogni agente è inizializzato con un attributo `sex`, che può assumere i valori `"M"` (maschio) o `"F"` (femmina).
La differenziazione tra i due gruppi non riguarda solo l’avversione alle perdite in sé, ma anche la **reattività allo stress** e la **capacità di adattamento** all’ambiente.

| Parametro              | Maschio         | Femmina         | Descrizione                                                                                             |
| ---------------------- | --------------- | --------------- | ------------------------------------------------------------------------------------------------------- |
| λ base (loss aversion) | 1.3             | 1.6             | Le femmine mostrano in media una maggiore sensibilità alle perdite, in linea con i dati sperimentali.   |
| Reattività allo stress | +0.3 temporaneo | +0.6 temporaneo | Sotto stress, le femmine aumentano più marcatamente il valore di λ, riflettendo una risposta più cauta. |
| Recupero dallo stress  | rapido (2 step) | lento (4 step)  | I maschi tornano più rapidamente ai livelli di baseline.                                                |
| Propensione al rischio | più alta        | più bassa       | I maschi sono più inclini a scelte rischiose anche in condizioni di incertezza.                         |

---

### Meccanismo implementativo

Nel codice, queste differenze si riflettono nella fase di aggiornamento di ogni agente:

1. **Assegnazione del sesso:**
   All’inizio della simulazione, gli agenti sono assegnati casualmente come maschi o femmine (es. 50%-50%).

2. **Gestione dello stress:**
   A ogni step temporale, una frazione casuale di agenti subisce uno “stress event”.

   * Se l’agente è maschio → λ aumenta di +0.3 per 2 step.
   * Se è femmina → λ aumenta di +0.6 per 4 step.

3. **Decision making differenziato:**
   Quando gli agenti valutano le opzioni di guadagno e perdita, il valore soggettivo viene calcolato tenendo conto del λ modificato, producendo quindi dinamiche decisionali diverse nei due sessi.

---

### Effetti attesi e analisi

Questa distinzione consente di testare **due ipotesi principali**:

1. **I maschi**, più propensi al rischio, traggono vantaggio in ambienti **stabili**, dove la prevedibilità riduce il costo di errori occasionali.
2. **Le femmine**, più avverse alle perdite e più sensibili allo stress, risultano **più adattive** in ambienti **instabili**, dove la cautela riduce il rischio di perdite gravi.

I risultati del modello possono essere confrontati in termini di **ricchezza media**, **tasso di sopravvivenza**, o **stabilità decisionale** tra maschi e femmine nelle quattro condizioni sperimentali (λ alto/basso × ambiente stabile/instabile).

---

### Sintesi concettuale

In sintesi, il modello integra:

* Una **base cognitiva** (Prospect Theory);
* Una **modulazione fisiologica** (effetto dello stress su λ);
* Una **differenziazione biologica** (reattività di genere);
* E una **variabile ecologica** (stabilità ambientale).

Questo approccio consente di rappresentare l’avversione alle perdite non solo come un tratto psicologico, ma come un **meccanismo adattivo evolutivo**, la cui efficacia varia in funzione del contesto e del profilo dell’agente.




Ecco una **descrizione breve, completa e presentabile** dei due ambienti umani (stabile vs instabile), già integrata con *foraging, mating, rischio, costi energetici, competizione* e meccanismi che rendono la loss aversion non banale.

---

# 🌿 **AMBIENTE STABILE (UMANO) – DESCRIZIONE BREVE E COMPLETA**

Un ambiente **prevedibile**, a bassa variabilità ecologica e sociale, dove gli eventi negativi sono rari ma non assenti. Non garantisce abbondanza: garantisce **regolarità**.

### **Caratteristiche principali**

* **Risorse regolari**: la disponibilità di cibo/energia oscilla poco tra uno step e l’altro.
* **Bassa variabilità nei rischi**: incidenti, predatori, malattie → rari e con probabilità quasi costante.
* **Competizione moderata**: molte strategie sono sostenibili, nessuna domina sempre.
* **Stress basso**: pochi shock improvvisi → lo stress fisiologico rimane episodico.
* **Ciclo vitale prevedibile**: ci sono periodi adatti per il mating, ma non c’è pressione estrema.

### **Contesti inclusi nel modello**

* **Foraging**:

  * *strategia sicura*: guadagno modesto garantito.
  * *strategia rischiosa*: guadagno alto, ma piccola probabilità di perdita energetica.
* **Mating**: possibile solo se l’energia supera una soglia; vantaggi riproduttivi se l’agente riesce ad accumulare risorse nel tempo.
* **Sopravvivenza**: soglia energetica minima → morte.
* **Movimento**: ricerca di patch leggermente migliori, ma differenze moderate tra celle.

### **Perché la loss aversion non è banale**

In un ambiente stabile:

* il rischio non è automaticamente conveniente, perché la perdita energetica può compromettere la possibilità di riprodursi;
* accumulo costante → anche piccole perdite possono rallentare la crescita a lungo termine;
* la competizione rende costoso tentare gamble troppo spesso.

**Risultato atteso:**
λ basso accelera la crescita ma espone a perdita di opportunità riproduttive se si sbaglia;
λ alto rallenta la crescita ma aumenta la sopravvivenza in caso di errori.

---

# 🌪 **AMBIENTE INSTABILE (UMANO) – DESCRIZIONE BREVE E COMPLETA**

Ambiente altamente variabile, con risorse imprevedibili e shock frequenti. È simile a scenari di scarsità, conflitti, crisi ecologiche o climatiche.

### **Caratteristiche principali**

* **Risorse che oscillano molto**: periodi di abbondanza seguiti da carestie improvvise.
* **Rischio elevato e non costante**: predatori, incidenti, fallimenti, malattie → probabilità variabile.
* **Competizione forte**: i momenti ricchi vengono rapidamente saturati dagli altri agenti.
* **Stress elevato e ricorrente**: shock ambientali che alterano temporaneamente λ.
* **Ciclo vitale irregolare**: possibilità di accoppiamento meno prevedibile.

### **Contesti inclusi nel modello**

* **Foraging**:

  * *safe option*: può diventare insufficiente nei periodi di scarsità.
  * *risky option*: i guadagni alti possono essere essenziali per sopravvivere, ma la probabilità di perdita aumenta.
* **Mating**: fortemente influenzato dalla disponibilità energetica; molti agenti non raggiungono la soglia necessaria.
* **Sopravvivenza**: mortalità più alta; scelte sbagliate hanno impatto immediato.
* **Movimento**: costante ricerca di patch migliori, perché la stabilità locale non esiste.

### **Perché la loss aversion diventa interessante**

In un ambiente instabile:

* λ alto può essere **maladattivo**: troppa avversione alle perdite porta a evitare rischi necessari per sopravvivere.
* λ basso può essere **adattivo**: permette di sfruttare rapidamente i momenti di abbondanza prima che finiscano.
* λ moderato può essere ottimale: evita rischi inutili ma permette di cogliere opportunità.

**Risultato atteso:**
L’adattività della loss aversion emerge solo osservando la sopravvivenza e il successo riproduttivo in un ambiente volatile.

---

# 🎯 **Riepilogo super compatto (da dire al prof)**

> In ambiente stabile gli agenti affrontano bassa variabilità, rischi rari e risorse prevedibili.
> È presente foraging (safe/risky), mating con soglia energetica, competizione moderata e mortalità da mancanza di energia.
> La loss aversion può risultare sia protettiva che limitante, ma non in modo banale.
>
> In ambiente instabile, invece, risorse e rischi oscillano rapidamente; gli shock sono frequenti, lo stress aumenta e l’energia diventa imprevedibile.
> Le strategie devono adattarsi a una distribuzione molto più ampia di possibili esiti: qui la loss aversion può diventare maladattiva perché impedisce di prendere rischi vitali.
>
> In pratica, lo stesso tratto (λ) può essere adattivo o non adattivo **a seconda stabilità, variabilità, e ritmo di shock del contesto ambientale**.

| Nome                    |                                                                      Descrizione |                                         Default |        Unità / scala |        Range consigliato | Nota d’uso                                                                     |
| ----------------------- | -------------------------------------------------------------------------------: | ----------------------------------------------: | -------------------: | -----------------------: | ------------------------------------------------------------------------------ |
| `environment_type`      |                                      Tipo di ambiente: `"stable"` / `"unstable"` |                                      `"stable"` |           categorico | `"stable"`, `"unstable"` | Usato per scegliere p_loss, safe_reward, pattern patch, finestra riproduttiva. |
| `n_patches`             |                                                   Numero di patch nel world grid |                                            `50` |                patch |                   10–500 | Più patch = più dispersione e competizione spaziale.                           |
| `patch_refresh_rate`    |       Frequenza con cui la qualità dei patch può cambiare (probabilità per step) |              `0.05` (stable) / `0.4` (unstable) | probabilità per step |                      0–1 | Stable → basso; unstable → alto.                                               |
| `p_loss`                |                Probabilità di perdita quando si sceglie risky (media ambientale) |             `0.10` (stable) / `0.40` (unstable) |          probabilità |                 0.01–0.6 | Influisce su SV_risky.                                                         |
| `gain_risky`            |                                           Guadagno positivo se risky ha successo |                                          `0.20` |   energia per evento |                 0.05–0.5 | Scala relativa alla safe_reward.                                               |
| `loss_risky`            |                                      Perdita (valore negativo) se risky fallisce |                                         `-0.10` |              energia |             -0.02 – -0.3 | Valore assoluto usato nel calcolo SV.                                          |
| `safe_reward`           |                                                          Guadagno opzione sicura |             `0.05` (stable) / `0.02` (unstable) |              energia |                 0.01–0.1 | Non dipende da λ.                                                              |
| `competition_intensity` | Riduzione probabilistica del reward in funzione del numero di agenti sulla patch | `linear` con coeff `0.01` per agente aggiuntivo |         coefficiente |                    0–0.1 | Modella congestione delle risorse.                                             |
| Nome                        |                                                                Descrizione |                                   Default |              Scala / unità |                      Range | Nota d’uso                                    |
| --------------------------- | -------------------------------------------------------------------------: | ----------------------------------------: | -------------------------: | -------------------------: | --------------------------------------------- |
| `initial_energy`            |                                               Energia iniziale dell’agente |                                     `1.0` |         energia (unitaria) |                    0.5–3.0 | Scala baseline; regola soglie.                |
| `energy_cost_move`          |                                    Costo energetico per muoversi tra patch |                                    `0.02` |      energia per movimento |                      0–0.2 | Influisce su mobilità selettiva.              |
| `energy_maintenance_cost`   |                                               Costo per step (metabolismo) |                                    `0.01` |           energia per step |                      0–0.1 | Forza trade-off fra foraging e conservazione. |
| `mating_threshold`          |                                          Energia minima per tentare mating |                                     `1.5` |                    energia |                    0.8–2.5 | Soglia per accedere al mating.                |
| `sex`                       |                                                              `"M"` o `"F"` |              assegnazione casuale (p=0.5) |                 categorico |                          - | Determina λ_base e reattività allo stress.    |
| `lambda_base`               |                                                   λ basale (loss aversion) |                          `M=1.3`, `F=1.6` |              dimensionless | 1.0–3.0 (test 1.2/2.0/3.0) | Valore da Prospect Theory; usato in SV.       |
| `lambda_stress_delta`       | Incremento temporaneo di λ sotto stress (valore assoluto o moltiplicativo) | `M=+0.3`, `F=+0.6` (o moltiplicatore 1.5) | absolute or multiplicative |         ±0.1–1.0 / 1.1–1.8 | Applicare per duration `stress_duration`.     |
| `stress_duration`           |                           Numero di step in cui l’incremento di λ è attivo |                              `M=2`, `F=4` |                       step |                       1–10 | Determina recovery.                           |
| `cycle_length`              |                                 Lunghezza del ciclo riproduttivo femminile |                                      `28` |  step (giorni equivalenti) |                      20–35 | Usato per finestra fertile.                   |
| `conception_probabilities`  |                                     Lista giorno-specifica di p(concepire) |                        vedi esempio sotto |            probabilità/day |                          — | Fornisce p per ogni giorno del ciclo.         |
| `reproduction_attempt_rate` |  Probabilità di tentare mating in giorno fertile (se energia >= threshold) |                                     `0.5` |                probabilità |                    0.1–1.0 | Riflette comportamento sociale/coppia.        |
| `age` (opzionale)           |                                  Età agente (per variabilità di fertilità) |                        `random int` 18–45 |                       anni |                          — | Se modellare età-fertilità.                   |
| `movement_strategy`         |                                       `"random"`, `"greedy"`, `"informed"` |                                `"greedy"` |                 categorico |                          — | Determina come scelgono patch.                |
| `memory_length` (opzionale) |             Numero di step per cui l’agente ricorda la qualità della patch |                                       `5` |                       step |                       0–50 | Per agenti informed.                          |
| Nome                         |                                                                             Descrizione |                         Default |                           Unità |    Range | Nota                                                   |
| ---------------------------- | --------------------------------------------------------------------------------------: | ------------------------------: | ------------------------------: | -------: | ------------------------------------------------------ |
| `stress_p`                   |                             Probabilità per step che un agente subisca uno stress event |                          `0.10` | probabilità per agente per step | 0.01–0.3 | Può essere modulata da patch quality o eventi globali. |
| `shock_event_p`              | Probabilità che un patch subisca uno shock che ne azzeri o riduca fortemente la qualità | `stable:0.01` / `unstable:0.15` |         prob per patch per step |    0–0.5 | Genera variazioni ambientali.                          |
| `stress_effect_on_fertility` |                           Riduzione multiplicativa della p_conception in step stressati |                           `0.5` |                  moltiplicatore |      0–1 | Opzionale: stress può abbassare la fertilità.          |
| Nome                   |                                                                Descrizione |                   Default |          Unità | Range |
| ---------------------- | -------------------------------------------------------------------------: | ------------------------: | -------------: | ----- |
| `max_move_distance`    |  Massima distanza (passi di griglia) che un agente può muovere in uno step |                       `1` |          celle | 0–5   |
| `move_cost_multiplier` |                        Moltiplicatore costo energia per spostamenti lunghi |                     `1.0` | moltiplicatore | 1–3   |
| `patch_choice_rule`    | Regola per scegliere patch: `nearest`, `highest_expected_reward`, `random` | `highest_expected_reward` |     categorico | —     |
| Nome                       |                                                                   Descrizione |                        Default |       Unità | Range       |
| -------------------------- | ----------------------------------------------------------------------------: | -----------------------------: | ----------: | ----------- |
| `reproduction_window_type` |                       `"seasonal"` / `"probabilistic"` / `"cycling_internal"` | `"cycling_internal"` per umano |  categorico | —           |
| `reproduction_window_prob` | Probabilità che uno step sia riproduttivamente favorevole (se probabilistico) |  `stable:0.5` / `unstable:0.1` |        prob | 0–1         |
| `sperm_survival_days`      |       Giorni in cui spermatozoi possono fecondare (estensione della finestra) |                            `5` | giorni/step | 0–7         |
| `offspring_cost`           |                 Costo energetico per riprodursi (prelievo energia alla madre) |            `-0.5` (una tantum) |     energia | -0.1 – -1.0 |
| `offspring_number`         |                               Numero figli generati per successo riproduttivo |                            `1` |       count | 1–4         |
| `heritability_lambda`      |                                     Se figli ereditano λ (probabilità/degree) |                          `0.5` |    frazione | 0–1         |
| Nome                   |                   Default | Nota                            |
| ---------------------- | ------------------------: | ------------------------------- |
| `n_agents`             |                     `200` | test: 50–1000 per scaling.      |
| `n_steps`              |                      `50` | 20–200 per esperimenti diversi. |
| `n_reps`               |                      `30` | ripetizioni per stima media/CI. |
| `random_seed`          | `None` (o fissare intero) | per riproducibilità.            |
| `data_record_interval` |                       `1` | step ogni cui salvare output.   |

