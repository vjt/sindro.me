---
title: "ChronoModel: viaggiare nel tempo con PostgreSQL"
date: 2012-05-07
tags: [ruby, postgresql, rails, open-source]
description: "Ho appena rilasciato una gem Ruby che implementa le Flashback Queries di Oracle su PostgreSQL usando viste, regole e table inheritance. Cinque giorni dal primo commit al rilascio."
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
ChronoModel e' ancora vivo — 14 anni, 41 release, 201 stelle. Le regole sono state sostituite da trigger INSTEAD OF nella [v0.6](https://github.com/ifad/chronomodel/tree/v0.6.0) (2014), l'hack `box()`/`point()` da colonne `tsrange` native, e il monkey-patching da una corretta registrazione dell'adapter. [Geremia Taglialatela](https://github.com/tagliala) ha preso in mano la manutenzione nel 2020 e l'ha portato alla [v5.0.0](https://rubygems.org/gems/chrono_model/versions/5.0.0) con supporto per Rails 8.1 e Ruby 4.0. L'idea di base — viste aggiornabili su `public`, dati correnti su `temporal`, storico su `history` con table inheritance — non e' mai cambiata. Il [repo](https://github.com/ifad/chronomodel) e' attivo e mantenuto.
{{< /retrospective >}}

Stiamo costruendo un CRM all'[IFAD](http://www.ifad.org/) — un'agenzia specializzata delle Nazioni Unite a Roma — e uno dei requisiti chiave sono i dati temporali. Dobbiamo sapere come appariva un record in qualsiasi momento del passato. Qual era il budget di questo progetto il 15 marzo? Quando e' cambiato l'indirizzo di questo beneficiario? Chi ha approvato cosa, e come appariva il record in quel momento?

Stavo prototipando un approccio basato sullo schema di PostgreSQL — viste, regole, table inheritance — e funzionava. Poi [Amedeo](https://github.com/amedeo), il mio capo, ci ha dato un'occhiata e ha detto: "Questa roba non deve vivere dentro il CRM. Fanne un framework riusabile."

Aveva ragione. Il pattern temporale non ha niente a che fare con la logica del CRM. Va in una gem.

Cosi' ho avuto cinque giorni di concentrazione totale, e oggi rilascio [ChronoModel](https://github.com/ifad/chronomodel) — un'estensione ActiveRecord che da' ai tuoi modelli capacita' temporali complete su PostgreSQL. Quello che Oracle ti vende come [Flashback Queries](http://docs.oracle.com/cd/B28359_01/appdev.111/b28424/adfns_flashback.htm) facendoti pagare fior di quattrini, noi lo facciamo con SQL standard su Postgres 9.0+.

<!--more-->

## L'idea

La risposta da manuale per i dati temporali e' una [Slowly Changing Dimension Type 2](http://en.wikipedia.org/wiki/Slowly_changing_dimension#Type_2) — mantieni uno storico di ogni riga con timestamp di validita', e interroghi quelli. Ogni vendor di database enterprise ha una soluzione proprietaria. PostgreSQL no. Ma PostgreSQL ti da' tutti i mattoncini — viste, regole, table inheritance, indici GiST — e nessuno li aveva ancora assemblati in un pacchetto Rails-friendly. Fino ad oggi.

La mia scommessa e' stata renderlo **completamente trasparente** per l'applicazione. Nessun cambiamento di schema nei modelli, nessun metodo di salvataggio speciale, nessuna tabella di storico da gestire a mano. Aggiungi `temporal: true` nella migration e `include ChronoModel::TimeMachine` nel modello, e tutto il resto succede dietro le quinte. Il codice esistente non cambia — acquisisce semplicemente la capacita' di guardare nel passato.

Quella trasparenza e' anche la parte piu' rischiosa del design, perche' renderlo invisibile ad ActiveRecord significa entrare *molto* in intimita' con gli internals di ActiveRecord. Ma ci arriviamo dopo.

## L'architettura

ChronoModel usa tre schemi PostgreSQL che lavorano insieme:

- **`temporal`** — contiene le tabelle "correnti" reali
- **`history`** — contiene tabelle di storico che **ereditano** da quelle temporali, aggiungendo colonne `valid_from`, `valid_to` e `recorded_at`
- **`public`** — contiene **viste aggiornabili** che l'applicazione vede come tabelle normali

I tuoi modelli Rails puntano alle viste in `public`. Appaiono e si comportano esattamente come tabelle normali. Dietro le quinte, le [regole](http://www.postgresql.org/docs/9.1/static/rules.html) PostgreSQL su quelle viste intercettano ogni INSERT, UPDATE e DELETE e li instradano nel posto giusto:

- **INSERT**: crea una riga in `temporal` (dato corrente) e una riga in `history` (con `valid_from = now()`)
- **UPDATE**: chiude l'entry storica corrente (imposta `valid_to = now()`), ne apre una nuova, e aggiorna la tabella temporale
- **DELETE**: chiude l'entry storica e rimuove la riga temporale

La parte bella e' che il codice della tua applicazione non cambia per niente. Le query vanno sulle viste `public`, che mostrano i dati correnti da `temporal`. Lo storico si accumula silenziosamente in `history`.

## Il colpo di genio

Come si prevengono entry storiche sovrapposte per lo stesso record? PostgreSQL non ha supporto per vincoli temporali (ancora — c'e' una [proposta SQL:2011](http://en.wikipedia.org/wiki/SQL:2011) per questo). Ma ha le [exclusion constraint GiST](http://www.postgresql.org/docs/9.1/static/sql-createtable.html#SQL-CREATETABLE-EXCLUDE), e GiST sa indicizzare tipi geometrici.

E allora abuso della geometria. Il periodo di validita' di ogni entry storica diventa un **box** nello spazio 2D — un asse e' il tempo (come secondi epoch), l'altro e' l'ID del record:

```sql
CONSTRAINT overlapping_times EXCLUDE USING gist (
  box(
    point( extract( epoch FROM valid_from), id ),
    point( extract( epoch FROM valid_to - INTERVAL '1 millisecond'), id )
  ) WITH &&
)
```

Due box si sovrappongono (`&&`) solo se condividono sia lo stesso ID che un intervallo temporale sovrapposto. Se qualcuno prova a inserire un'entry storica contraddittoria, PostgreSQL la rifiuta a livello di vincolo. Integrita' temporale blindata usando indici spaziali. Sono irragionevolmente orgoglioso di questo hack.

## L'integrazione Rails

Far funzionare tutto questo in modo trasparente con ActiveRecord ha richiesto... creativita'. L'adapter estende `PostgreSQLAdapter` e sovrascrive ogni metodo DDL — `create_table`, `drop_table`, `rename_table`, `add_column`, `rename_column`, `change_column`, `remove_column`, `add_index`, `remove_index`, e altri. Tutti controllano se la tabella e' temporale e instradano le operazioni a entrambi gli schemi.

Dalla tua migration, e' una sola opzione:

```ruby
create_table :countries, temporal: true do |t|
  t.string :name
  t.string :code
  t.timestamps
end
```

Quel singolo `temporal: true` crea la tabella temporale, la tabella storica con ereditarieta', la vista pubblica, tutte le regole, l'indice GiST e la exclusion constraint. Plug and play.

Poi nel tuo modello:

```ruby
class Country < ActiveRecord::Base
  include ChronoModel::TimeMachine
end
```

E hai il viaggio nel tempo:

```ruby
# Dati correnti — funziona esattamente come prima
Country.where(code: 'IT')

# Come appariva l'Italia il 1 gennaio 2010?
Country.as_of(Time.utc(2010, 1, 1)).find_by(code: 'IT')

# Storico completo di un record
italy = Country.find_by(code: 'IT')
italy.history  # => tutte le versioni, con valid_from/valid_to

# Le associazioni temporali si propagano automaticamente
italy.as_of(1.year.ago).projects  # caricati anche loro a quella data
```

Ho anche aggiunto il supporto [CTE](http://www.postgresql.org/docs/9.1/static/queries-with.html) (Common Table Expression) al query builder di ActiveRecord, perche' Rails 3 non ce l'ha e le query `as_of` hanno bisogno di clausole `WITH`. Questo ha richiesto una patch a `Arel::Visitors::PostgreSQL` per emettere SQL corretto.

## La verita' scomoda

Diciamocelo chiaramente: l'hack che fa funzionare tutto. Per iniettare l'adapter, faccio cosi':

```ruby
silence_warnings do
  ActiveRecord::ConnectionAdapters::PostgreSQLAdapter = ChronoModel::Adapter
end
```

Si', sostituisco l'intera costante dell'adapter PostgreSQL. E patcho `ActiveRecord::Associations::Association` per propagare l'`as_of_time` attraverso le associazioni temporali.

Funziona. E' brutto. Andra' ripulito prima di arrivare a una 1.0. Ma funziona, e funziona in modo trasparente — il tuo codice esistente non cambia.

## Cinque giorni

Trentasei commit dal README iniziale a questo rilascio. Nessun test per ora — arriveranno, promesso. L'SQL e' solido (ho testato l'approccio a livello di schema manualmente per settimane prima di scrivere la gem), ma il lato Ruby ha bisogno di spec fatte come si deve.

Se lavori con PostgreSQL e Rails e hai mai avuto bisogno di query storiche, audit trail, o reportistica temporale: `gem install chrono_model` e prova. Il [sorgente e' su GitHub](https://github.com/ifad/chronomodel). Issue, PR e lamentele sono benvenute.

Viaggiare nel tempo non dovrebbe costare una licenza Oracle.
