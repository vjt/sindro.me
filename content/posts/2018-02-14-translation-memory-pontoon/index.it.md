---
title: "Un importatore senza vergogna di Translation Memory in Pontoon"
date: 2018-02-14
tags: [ruby, postgresql, i18n, open-source, ifad]
description: "Avevamo i traduttori intrappolati in un CAT desktop, a scambiarsi file XML come fosse il 2003. Propongo Mozilla Pontoon per la traduzione collaborativa sul web. La fregatura: anni di translation memory legacy in quattro formati diversi devono venire con noi."
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
Il repo a [github.com/ifad/translation-memory](https://github.com/ifad/translation-memory) è ancora pubblico, ancora senza README, e il fork di Pontoon a cui parla resta privato. [L'upstream di Mozilla](https://github.com/mozilla/pontoon) è aperto e molto vivo. Se qualcuno all'IFAD usi ancora Pontoon otto anni dopo, sinceramente non lo so — l'ho costruito per un progetto sulla mia scrivania, non come cambio di workflow aziendale. La regex che strippa i caratteri non-word ha fatto il suo lavoro per i mesi in cui mi serviva. Poi, presumibilmente, la successiva migration dello schema di Pontoon ha rotto qualcosa. È quello che succede alle integrazioni che parlano direttamente con un database.
{{< /retrospective >}}

L'[IFAD](http://www.ifad.org/) è un'agenzia ONU che opera in [inglese, francese, spagnolo e arabo](https://www.ifad.org/en/web/operations/languages). Ogni stringa visibile delle nostre app Rails deve esistere in quattro lingue, il che significa che abbiamo un team di traduzione, il che significa che abbiamo un workflow di traduzione, che sulla maggior parte dei progetti prevede un [CAT desktop](https://it.wikipedia.org/wiki/Computer_assisted_translation), file allegati alle email, e translation memory che girano in formato XML.

Quel workflow non sopravvive a un progetto su cui sto lavorando in questo momento. È un'app web Rails con una scadenza stretta, le stringhe sorgente cambiano ogni settimana, e nel tempo che un traduttore impiega per finire un file TM e rimandarlo via email le stringhe si sono già spostate. Mi servono traduttori e sviluppatori che guardano lo stesso database in tempo reale. Scelgo [Mozilla Pontoon](https://pontoon.mozilla.org/) — open-source, gratis, adattabile, scritto in Django, basato su Postgres — e lo tiro su per il mio progetto. La fregatura: c'è un corpus di traduzioni dal tool precedente che voglio usare per fare il seed di Pontoon dal primo giorno, così i traduttori non partono dal nulla.

Oggi inizio un repo [translation-memory](https://github.com/ifad/translation-memory) e scrivo il primo parser. Il progetto è descritto, con tutta la dovuta umiltà ingegneristica, come ["Parser per file TMX, SDL/XLIFF e TXML e importatore senza vergogna in Mozilla Pontoon"](https://github.com/ifad/translation-memory). Quel "senza vergogna" sta facendo molto lavoro in quella frase.

<!--more-->

## Cos'è una translation memory?

Una translation memory (TM) è un mucchio di coppie sorgente-target: *"Submit your application"* → *"Soumettez votre candidature"*, con metadati (chi, quando, in quale documento). Quando un traduttore incontra di nuovo *"Submit your application"*, il CAT propone la traduzione precedente. Quando incontra *"Submit your loan application"*, propone un fuzzy match e gli permette di modificarlo. La TM è la memoria istituzionale del team, plasmata negli anni.

In un mondo desktop la TM è un file. Compri un CAT, importi la TM, traduci, esporti la TM aggiornata, la mandi via email alla persona successiva. In un mondo web la TM è un database — lo stesso database che contiene le stringhe attive, con storia completa, editing concorrente, diff e review.

Stiamo passando dal primo mondo al secondo. Per farlo senza perdere nulla, ogni traduzione che abbiamo mai fatto deve atterrare dentro la tabella `base_translation` di Pontoon.

## Pontoon, in breve

[Pontoon](https://pontoon.mozilla.org/) è la piattaforma che Mozilla usa per fare crowdsourcing della localizzazione di Firefox, MDN, e di una lunga coda di proprietà Mozilla in [centinaia di lingue](https://pontoon.mozilla.org/teams/). I traduttori hanno una UI web con la stringa sorgente, la traduzione precedente, suggerimenti dalla TM, hint di traduzione automatica, e un thread di commenti. I revisori approvano o rifiutano. Tutto è versionato in git lato back-end.

Il modello dati è, fortunatamente, semplice. Un `Project` ha molti `Locale` e molte `Resource` (una per file sorgente). Una `Resource` ha molte righe `Entity` (una per stringa sorgente). Ogni `Entity` ha molte `Translation`, una per locale, con flag `approved` e `rejected` e un `User` che l'ha scritta.

Voglio spingere la TM legacy dentro questa forma, locale per locale, mentre un vero processo Pontoon continua a servire lo stesso database ai traduttori sul mio progetto. Questo significa transazioni, niente cambi di schema, niente operazioni distruttive.

## Lo zoo della TM

La prima cosa che imparo è che *"file di translation memory"* non è una cosa sola. Il corpus che devo importare vive in almeno quattro formati:

- **[TMX](https://en.wikipedia.org/wiki/Translation_Memory_eXchange)** — il formato XML standard del settore. Translation Memory eXchange. È quello che ogni CAT può leggere e scrivere, e quindi quello che ogni CAT implementa con creative variazioni.
- **TXML** — un XML stile Wordbee con annidamento `<conceptGrp>` / `<languageGrp>` / `<termGrp>`. Meno standard, più verboso, sempre XML.
- **[XLIFF](https://en.wikipedia.org/wiki/XLIFF)** — lo standard OASIS per l'interscambio di localizzazione. Ce lo passano in salsa [SDL Trados](https://en.wikipedia.org/wiki/SDL_Trados_Studio) con `urn:oasis:names:tc:xliff:document:1.2` più estensioni `http://sdl.com/FileTypes/SdlXliff/1.0`. Metadati come autore e date vivono in `<sdl:seg-defs>`, il che significa XPath namespace-aware.
- **TCSV** — un formato CSV custom su cui il team interno si mette d'accordo per le stringhe che non entrano da nessuna parte. Sei colonne. Punto e virgola. Alla fine aggiungiamo una variante *"simple"* quando l'originale è troppo rigido.

Scrivo un parser Nokogiri per ciascun formato — [`tmx.rb`](https://github.com/ifad/translation-memory/blob/master/tmx.rb), [`txml.rb`](https://github.com/ifad/translation-memory/blob/master/txml.rb), [`xliff.rb`](https://github.com/ifad/translation-memory/blob/master/xliff.rb), [`tcsv.rb`](https://github.com/ifad/translation-memory/blob/master/tcsv.rb) — e un piccolo value object `Translation` che tutti producono. La forma che condividono è in [`shared.rb`](https://github.com/ifad/translation-memory/blob/master/shared.rb):

```ruby
class Translation
  attr_accessor :language, :source, :target, :user,
                :created_at, :updated_at, :resource, :key

  def user=(user)
    # Remove DOMAIN\\
    @user = user.sub(/^.+\\/, '')
  end

  def language_code
    language.sub(/-\w+$/, '').downcase # Remove country specifier
  end
end
```

I due metodi in cima non sono accademici. Il tool desktop girava su Active Directory, quindi ogni `created_by` arriva come `IFAD\\m.barnaba`. E ogni locale arriva come `fr-FR`, `es-ES`, `ar-AE`, mentre Pontoon le memorizza come `fr`, `es`, `ar`. Entrambe le trasformazioni avvengono in assegnazione, una volta sola, e il resto del codice smette di preoccuparsene.

Ogni parser format-specific espone lo stesso metodo `translations`. Il [parser TMX](https://github.com/ifad/translation-memory/blob/master/tmx.rb) itera `/tmx/body/tu` e tira fuori gli elementi `<seg>` sorgente/target dal `<tuv>` giusto. Il [parser TXML](https://github.com/ifad/translation-memory/blob/master/txml.rb) cammina nell'albero conceptGrp e accoppia il primo language group con ognuno degli altri. Il [parser XLIFF](https://github.com/ifad/translation-memory/blob/master/xliff.rb) registra i namespace OASIS e SDL:

```ruby
class XMLObject < ::XMLObject
  def namespaces
    { oasis: 'urn:oasis:names:tc:xliff:document:1.2',
      sdl:   'http://sdl.com/FileTypes/SdlXliff/1.0'
    }
  end
end
```

…e tira fuori autore e data da `./sdl:seg-defs/sdl:seg[last()]` perché la definizione del segmento che vogliamo è, empiricamente, l'ultima. C'è un commento `# last() HACK` nel sorgente. È corretto.

Una volta che il parser produce un array `[Translation, Translation, ...]`, la dimensione del formato sparisce. Tutto da qui in poi è lo stesso code path.

## Un importatore senza vergogna

Pontoon ha un'API JSON perfettamente ragionevole per importare traduzioni. Non la uso. L'API si aspetta che le stringhe combacino esattamente, le processa una alla volta, e mi farebbe scrivere un wrapper in Python, deployarlo accanto al processo Pontoon, e gestire auth e rate-limiting. Ho un cassetto pieno di TM e una deadline misurata in giorni. So anche perfettamente cosa sto facendo: questo è un tool di migrazione one-shot con un accoppiamento fragile allo schema Postgres interno di Pontoon, e nel momento in cui Mozilla rilascia una migration del database i miei modelli vanno in fumo e l'import si rompe. Va bene così. L'import deve funzionare *adesso*. Apro [`pontoon.rb`](https://github.com/ifad/translation-memory/blob/master/pontoon.rb) invece.

Il trucco è che Pontoon è Django, Django mette tutto in Postgres, lo schema è pubblicato, e ad ActiveRecord non importa quale framework abbia scritto le tabelle. Dichiaro i modelli che mi servono con i nomi di tabella che Django ha scelto:

```ruby
class Project < ActiveRecord::Base
  self.table_name = 'base_project'

  has_many :resources,       inverse_of: :project
  has_many :memories,        inverse_of: :project
  has_many :project_locales, inverse_of: :project

  has_many :entities,     through: :resources
  has_many :translations, through: :entities
  has_many :locales,      through: :project_locales

  belongs_to :latest_translation, class_name: 'Translation'
end
```

Ci sono nove modelli del genere nel file: `Project`, `Locale`, `ProjectLocale`, `Resource`, `TranslatedResource`, `Entity`, `Translation`, `ChangedEntityLocale`, `Memory`, più uno `User` mappato su `auth_user`. Formano un piccolo specchio del modello dati di Pontoon che ActiveRecord può scopare, joinare e aggiornare. Una `connect!` che legge `PGUSER`, `PGHOST`, `PGDATABASE`, `PGPASSWORD` dall'ambiente, e siamo dentro il database:

```ruby
def self.connect!
  pg_env = %w( PGUSER PGHOST PGDATABASE PGPASSWORD )
  missing = pg_env.select {|k| ENV[k].blank? }
  raise "Please set #{missing.join(' and ')}" if missing.present?

  ActiveRecord::Base.logger = Logger.new($stderr)
  ActiveRecord::Base.logger.level = :info

  cheer "Connecting to #{ENV['PGHOST']}"
  ActiveRecord::Base.establish_connection(adapter: 'postgresql')
end
```

Ogni traduzione importata entra dentro una transazione, con gli stessi callback che il codice di Pontoon stesso scatena — `update_latest_translation_ids`, `increment_translated_string_counter`, `mark_entity_as_changed`, `create_memory` — perché li ho ricostruiti in Ruby proprio accanto ai loro corrispettivi. Dal punto di vista di Pontoon, un importatore esterno è indistinguibile da un traduttore che batte molto veloce.

Questo è cosa significa *"shameless"* nella descrizione del repo.

## Le translation memory del mondo reale sono sporche

Il primo run di import trova il 30% delle stringhe e si lamenta del resto. I traduttori guardano il report e mi dicono, gentilmente, che quelle stringhe *sono* nella TM, sono io che guardo male. Hanno ragione. Le translation memory del mondo reale sono lerce.

Una stringa sorgente nell'app Rails è `Submit your application`. La stessa stringa nella TM è `Submit your application.` (punto finale). O `Submit\u00a0your application` (spazio non separabile). O `Submit your application` seguita da un tab e tre spazi che un traduttore ha aggiunto copia-incollando da Word. O `"Submit your application"` con virgolette tipografiche. L'occhio dice che sono uguali; `=` dice di no.

Faccio match in tre passi su tre giorni.

**Passo uno — match esatto.** Quello con cui sono partito. Imbarazzante in retrospettiva:

```ruby
scope :by_string, ->(string) { where(string: string) }
```

**Passo due — normalizza gli spazi.** [`da71f51`](https://github.com/ifad/translation-memory/commit/da71f51), mercoledì 28 febbraio 2018 alle 20:39 con il commit message "More aggressive string matching…":

```ruby
scope :by_string, ->(string) {
  where(%[regexp_replace(lower(trim(string)), '\\s\\s*', ' ') =
          regexp_replace(lower(trim(?)), '\\s\\s*', ' ')], string)
}
```

Lowercase, trim, collassa le sequenze di whitespace a un singolo spazio. Recupera un altro venti per cento delle stringhe.

**Passo tre — ti arrendi sulla punteggiatura.** [`a7c9a02`](https://github.com/ifad/translation-memory/commit/a7c9a02), la mattina dopo alle 11:54, con il commit message ["Even more aggressive matching"](https://github.com/ifad/translation-memory/commit/a7c9a02). Cancello ogni carattere non-word su entrambi i lati prima di confrontare:

```ruby
scope :by_string, ->(string) {
  where(%[regexp_replace(lower(trim(string)), '[^\\w]+', '', 'g') =
          regexp_replace(lower(trim(?)), '[^\\w]+', '', 'g')], string)
}
```

Questa è la versione che va in produzione. Il match rate salta al 95%+. Il restante 5% sono modifiche genuine alla sorgente dove la stringa Rails è stata editata ma la TM tiene ancora il vecchio wording, e quelle hanno bisogno di un umano comunque.

Sono molto contento della regex maleducata. I traduttori sul progetto si loggano e trovano le loro vecchie traduzioni nel pannello suggerimenti. Postgres sta bene. Tutti su questo specifico progetto stanno bene.

## bark, hmmm, cheer

Importare migliaia di traduzioni significa migliaia di righe di log. Il modo ingenuo è `puts` e un tail. Il modo leggermente meno ingenuo su cui atterro è stderr colorato più un log CSV di audit, in [`pontoon.rb`](https://github.com/ifad/translation-memory/blob/master/pontoon.rb):

```ruby
def self.bark(woof)
  ActiveRecord::Base.logger.info("\e[1;31m#{woof}\e[0;0m")  # rosso
end

def self.hmmm(woof)
  ActiveRecord::Base.logger.info("\e[1;33m#{woof}\e[0;0m")  # giallo
end

def self.cheer(woof)
  ActiveRecord::Base.logger.info("\e[1;32m#{woof}\e[0;0m")  # verde
end
```

Rosso è "non ho trovato un'entity target per questa traduzione", giallo è "ne ho trovata una ma è già tradotta, la lascio stare", verde è "importata". Ogni operazione scrive anche una riga in `IMPORT-2018-02-28.184412.csv` così un umano può rileggere il run più tardi e capire esattamente cosa è successo a ogni stringa. Il CSV è quello che viene allegato all'email post-import ai traduttori sul progetto.

## Il giro di andata e ritorno

La migrazione è metà della storia. L'altra metà è che alcuni traduttori su questo progetto vogliono ancora lavorare nel loro tool desktop in certi giorni — vecchie abitudini, treni offline, internet che va e viene. Quindi [`export.rb`](https://github.com/ifad/translation-memory/blob/master/export.rb) e [`export-missing.rb`](https://github.com/ifad/translation-memory/blob/master/export-missing.rb) camminano Pontoon all'indietro: dato un progetto e un locale, scrivono fuori le entity mancanti su CSV, opzionalmente collassando le stringhe duplicate in una sola riga con tutte le chiavi unite da punto e virgola.

```ruby
def self.export_condensed_entities(entities, output)
  entities_by_string = entities.inject({}) do |h, entity|
    string = entity.string.downcase.strip
    (h[string] ||= []).push(entity)
    h
  end

  entities_by_string.each do |string, es|
    keys = es.map {|e| [e.resource.path, e.key].join(':') }.join(';')
    output << [keys, es.first.string, '', ...]
  end

  gain = ((1 - entities_by_string.count.to_f/entities.count.to_f) * 100).round(2)
  cheer "Exported #{entities.count} entities as #{entities_by_string.count} rows (#{gain}% gain)"
end
```

Il "gain" è la percentuale di stringhe duplicate tra resource — che su una vera app Rails è deprimentemente alta, perché chiamiamo i bottoni "Submit" ovunque. Il traduttore traduce *Submit* una volta sola, l'importatore lo riespande in tutte le `n` entity al ritorno. Il giro di ritorno significa che i traduttori sul mio progetto non devono scegliere tra Pontoon e la loro abitudine desktop in un dato giorno.

## Un lungo sprint di San Valentino

Guardando il [commit log](https://github.com/ifad/translation-memory/commits/master/) la forma del progetto diventa chiara:

- **14 febbraio 2018** — "Initial parsing of translation memory XML." Primo commit, [`9f50b5b`](https://github.com/ifad/translation-memory/commit/9f50b5b). Ci sto lavorando il giorno di San Valentino, il che è appropriato per un progetto sulla *translation memory*.
- **19 febbraio** — "Import translations as suggestions." Primo run di import end-to-end.
- **28 febbraio** — sedici commit in una sera. Parser XLIFF, supporto namespace, gestione segment vuoti, gestione timestamp mancanti, "More aggressive string matching…" alle 20:39.
- **1 marzo** — "Even more aggressive matching" la mattina dopo. La regex che va in produzione.
- **5 marzo** — exporter per le traduzioni mancanti e calcolo del gain.
- **15 marzo** — importer TCSV per il formato interno.
- **27 marzo** — API `approve!` / `reject!` / `unapprove!`, perché una volta che hai i dati dentro, qualcuno vuole approvarli in massa.
- **17 ottobre 2018** — ultimo commit. La migrazione è fatta. Il tool gira ogni volta che ricevo un nuovo file TM da qualcuno sul progetto.

L'intero arco prende tre settimane di lavoro intenso e sette mesi di manutenzione strascicata. Cinquantadue commit in totale. 1.300 righe di Ruby, di cui 688 sono l'importatore senza vergogna [`pontoon.rb`](https://github.com/ifad/translation-memory/blob/master/pontoon.rb).

## Cosa mi porto a casa

Tre cose, principalmente.

**Bypassa l'API quando l'API è sbagliata per il tuo lavoro.** L'endpoint di import di Pontoon va bene per un traduttore che incolla un file TMX dal browser. Non va bene per migrare un corpus con quirk di formato, di encoding, di whitespace, e fuzzy matching per stringa. Lo schema è proprio lì nel loro repo git. Parlarci direttamente toglie una settimana di round trip HTTP dal tempo di import, e mi permette di usare le stesse transazioni Postgres che usa Django.

**La conoscenza del dominio batte il codice furbo.** La regex `[^\\w]+` è due caratteri di lavoro. Quello che ci è voluto per scoprire che mi serviva è ciò di cui il progetto parla davvero: stare seduto accanto a un traduttore mentre mi spiegava perché una stringa che l'importer rifiutava era *ovviamente* la stessa stringa. Il `# last() HACK` in XLIFF è uguale — una volta che capisci il modello di segmentazione di SDL, l'hack è la risposta giusta.

**Piccoli tool per grandi migrazioni.** Questo non è un prodotto. Questo è uno [script Ruby single-purpose](https://github.com/ifad/translation-memory/blob/master/import.rb) che lanci puntandolo a un file alla volta:

```sh
ruby import.rb tmx project-slug path/to/file.tmx
```

Fa una cosa. Logga cosa ha fatto. Scrive un CSV che puoi mandare via email. Quando la migrazione è finita smetti di farlo girare. Il repo resta pubblico, il README non viene mai scritto ([scusate](https://github.com/ifad/translation-memory)), e la successiva migration dello schema di Pontoon prima o poi rompe il model layer. Per allora l'import ha fatto il suo lavoro. Per tool del genere, è abbastanza.

Pontoon, tra l'altro, è eccellente. Se il tuo team si sta ancora mandando file XML via email, [vai a guardarlo](https://pontoon.mozilla.org/).
