---
title: "ChronoModel 1.0: sette anni per rilasciare"
date: 2019-04-06
tags: [ruby, postgresql, rails, open-source]
description: "ChronoModel raggiunge la 1.0 dopo sette anni, 506 commit e 31 release. L'idea di base non e' mai cambiata — tutto il resto si'."
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
Dopo la v1.0.0, [Geremia Taglialatela](https://github.com/tagliala) ha preso in mano la manutenzione e l'ha portato alla [v5.0.0](https://rubygems.org/gems/chrono_model/versions/5.0.0) con supporto per Rails 8.1 e Ruby 4.0. La gem e' a 201 stelle e ancora attivamente mantenuta. Altri sette anni di produzione all'IFAD — e si continua — oltre i sette che ci sono voluti per arrivare alla 1.0. La [documentazione API](https://vjt.github.io/chronomodel/) e il [repo](https://github.com/ifad/chronomodel) sono entrambi vivi.
{{< /retrospective >}}

Sette anni fa ho [rilasciato ChronoModel v0.1.0](/it/posts/2012-05-07-chronomodel-time-travel-postgresql/) — una gem Ruby che da' ai modelli ActiveRecord capacita' temporali su PostgreSQL. Cinque giorni di hacking, trentasei commit, nessun test, e una confessione sul monkey-patching della costante dell'adapter PostgreSQL.

Oggi taggo la [v1.0.0](https://github.com/ifad/chronomodel/commit/aa07e74). Il [messaggio di commit](https://github.com/ifad/chronomodel/commit/aa07e74) e' `:gem: this is v1.0.0`. Non proprio un discorso memorabile, ma il codice parla da solo: 506 commit, 31 release, 52 file modificati, 5.392 righe aggiunte. L'[idea di base](/it/posts/2012-05-07-chronomodel-time-travel-postgresql/#larchitettura) — viste aggiornabili su `public`, dati correnti su `temporal`, storico su `history` con table inheritance — non e' mai cambiata. Tutto il resto si'.

<!--more-->

## Cosa e' cambiato

Tre cose erano sbagliate nella v0.1.0, e l'avevo detto io stesso. Tutte e tre sono risolte.

### Regole → trigger INSTEAD OF

Il [design originale](/it/posts/2012-05-07-chronomodel-time-travel-postgresql/#larchitettura) usava le [regole](http://www.postgresql.org/docs/9.1/static/rules.html) di PostgreSQL per rendere scrivibili le viste public. Le regole funzionano, ma hanno spigoli vivi — riscrivono le query a parse time, non gestiscono bene le clausole `RETURNING`, e il debugging e' un incubo.

Il [giorno di San Valentino 2014](https://github.com/ifad/chronomodel/tree/v0.6.0), le ho [strappate tutte](https://github.com/ifad/chronomodel/commit/05aff8cc) e sostituite con trigger INSTEAD OF. Stesso comportamento, modello di esecuzione piu' pulito. I trigger scattano al momento dell'esecuzione, gestiscono `RETURNING` naturalmente, e si possono davvero debuggare. Il messaggio di commit dice "BREAKING CHANGE" — perche' lo era. Ogni tabella temporale aveva bisogno di una migration per passare al nuovo sistema.

### box()/point() → tsrange

Il [vincolo di esclusione originale](/it/posts/2012-05-07-chronomodel-time-travel-postgresql/#larchitettura) era il mio hack piu' orgoglioso — abusare degli indici geometrici GiST per impedire entry storiche sovrapposte codificando gli intervalli temporali come box 2D. Funzionava, ma era un hack. [PostgreSQL 9.2](https://www.postgresql.org/docs/9.2/rangetypes.html) ha introdotto i range type nativi, e dalla [9.3](https://www.postgresql.org/docs/9.3/rangetypes.html) erano solidi.

[Stesso giorno](https://github.com/ifad/chronomodel/commit/be57527), stessa v0.6.0: sostituito l'hack geometrico con colonne `tsrange` native. Il vincolo di esclusione adesso si legge come quello che effettivamente significa:

```sql
EXCLUDE USING gist (id WITH =, validity WITH &&)
```

Prima:

```sql
-- v0.1.0: codifica il tempo come geometria, spera nel meglio
EXCLUDE USING gist (
  box(
    point( date_part('epoch', valid_from), id ),
    point( date_part('epoch', valid_to - INTERVAL '1 msec'), id )
  ) WITH &&
)
```

Dopo:

```sql
-- v0.6.0: dici quello che intendi
EXCLUDE USING gist ( id WITH =, validity WITH && )
```

Il database capisce quello che sta enforcing.

### Monkey-patching → adapter corretto

La ["verita' scomoda"](/it/posts/2012-05-07-chronomodel-time-travel-postgresql/#la-verita-scomoda) della v0.1.0:

```ruby
silence_warnings do
  ActiveRecord::ConnectionAdapters::PostgreSQLAdapter = ChronoModel::Adapter
end
```

Sparita. ChronoModel adesso si [registra](https://github.com/ifad/chronomodel/commit/c11b30f) come sottoclasse dell'adapter. Si configura in `database.yml` con `adapter: chronomodel` e ActiveRecord lo carica attraverso la sua risoluzione standard degli adapter. Nessuna costante e' stata maltrattata.

## San Valentino 2014

La [release v0.6.0](https://github.com/ifad/chronomodel/tree/v0.6.0) merita una menzione a parte. Tre breaking change in un giorno — trigger, tsrange, registrazione dell'adapter. Una riscrittura completa del layer database mantenendo l'API Ruby identica. Se la v0.1.0 era "questo funziona," la v0.6.0 era "questo funziona *correttamente*."

La versione minima di PostgreSQL e' saltata dalla 9.0 alla 9.3. Alcuni utenti hanno dovuto aggiornare i loro database. Nessuno si e' lamentato — la nuova implementazione era visibilmente migliore.

## I test

Il post della v0.1.0 diceva "nessun test per ora — arriveranno, promesso." Sono arrivati. La [v0.3.0](https://github.com/ifad/chronomodel/tree/v0.3.0) (giugno 2012, sei settimane dopo) ha aggiunto spec RSpec complete. Alla v1.0.0 ci sono [5.000+ righe di codice di test](https://github.com/ifad/chronomodel/tree/v1.0.0/spec) che coprono tabelle temporali, query storiche, associazioni, time query, STI, indici, migration, schema dump, e comportamento standard di ActiveRecord.

La suite di test gira su multiple versioni di Rails via [Appraisal](https://github.com/thoughtbot/appraisal) — [Rails 5.0, 5.1, e 5.2](https://github.com/ifad/chronomodel/tree/v1.0.0/gemfiles) per la v1.0.0. La [v0.13.1](https://github.com/ifad/chronomodel/tree/v0.13.1), taggata trenta minuti prima della v1.0.0, e' l'ultima versione a supportare Rails 4.2.

## Il weekend del 6 aprile

Lo sprint finale e' un weekend. Il [supporto Rails 5.0-5.2](https://github.com/ifad/chronomodel/commit/f2bbdb3) arriva nel pomeriggio, [Rails 4.2 viene droppato](https://github.com/ifad/chronomodel/commit/ab10280), le spec vengono [aggiunte](https://github.com/ifad/chronomodel/commit/f043ef7), i deprecation warning vengono risolti. Poi tre release in meno di un'ora:

- **20:25** — [v0.13.1](https://github.com/ifad/chronomodel/tree/v0.13.1): "the last version to support Rails 4.2"
- **20:54** — [v1.0.0](https://github.com/ifad/chronomodel/tree/v1.0.0): `:gem: this is v1.0.0`
- **21:17** — [v1.0.1](https://github.com/ifad/chronomodel/tree/v1.0.1), perche' ovviamente c'e' una v1.0.1

Poi il refactoring va avanti fino alle 5 di mattina — [estrazione dell'adapter in moduli puliti](https://github.com/ifad/chronomodel/commit/45f4db0), [riscrittura di `on_schema`](https://github.com/ifad/chronomodel/commit/aa8a5c5) con thread-local storage, fix degli smell di CodeClimate, aumento della coverage. Perche' taggare la 1.0 non significa che ti fermi. Significa che finalmente hai il permesso di fare pulizia come si deve.

## Cosa non e' cambiato

L'architettura a tre schemi. L'opzione `temporal: true` nelle migration. Il mixin `include ChronoModel::TimeMachine`. L'interfaccia di query `as_of`. L'idea che i dati temporali appartengono al database, non ai callback dell'applicazione.

```ruby
# Questo funzionava nel 2012. Funziona ancora nel 2019.
Country.as_of(1.year.ago).find_by(code: 'IT')
```

506 commit per rendere gli internals all'altezza dell'interfaccia. Sette anni di produzione all'[IFAD](http://www.ifad.org/) senza un singolo incidente di perdita dati.

Il [sorgente e' su GitHub](https://github.com/ifad/chronomodel), la [documentazione API](https://vjt.github.io/chronomodel/) copre ogni metodo pubblico. `gem 'chrono_model', '~> 1.0'` e sei a posto.

Viaggiare nel tempo non dovrebbe costare una licenza Oracle. E ancora non la costa.
