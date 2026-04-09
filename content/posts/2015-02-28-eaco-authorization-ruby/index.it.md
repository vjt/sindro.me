---
title: "Eaco: il guardiano delle chiavi dell'Ade"
date: 2015-02-28
tags: [ruby, rails, postgresql, open-source]
description: "Ho appena estratto un framework di autorizzazione ABAC dalla nostra app interna IFAD in uno sprint di 8 giorni. Le ACL sono semplici hash, PostgreSQL jsonb fa il lavoro pesante, e ho raggiunto il 100% di coverage alle 13:33 di un sabato."
image: cover.jpg
featuredImage: cover.jpg
---

{{< retrospective year="2026" >}}
Eaco ha raggiunto la [v1.0.0](https://github.com/ifad/eaco/tree/v1.0.0) il 5 maggio 2016 — messaggio di commit: "This is v1.0.0. Two years in production." E' cresciuto fino a 54 stelle, 8 fork, 240 commit, e ha gestito l'autorizzazione all'IFAD per altri cinque anni. Il pattern ABAC con ACL-come-hash si e' rivelato esattamente la scelta giusta per un'organizzazione dove l'accesso e' determinato da posizione, dipartimento e gruppo di lavoro — non solo "admin o no." Il [repo](https://github.com/ifad/eaco) e' ancora online, e la [documentazione YARD](https://vjt.github.io/eaco/) e' ancora tra le piu' complete che abbia mai scritto per una gem.
{{< /retrospective >}}

[Scriptoria](https://github.com/ifad/scriptoria) e' un'applicazione interna di workflow all'[IFAD](http://www.ifad.org/) — un'agenzia specializzata delle Nazioni Unite a Roma — e il suo layer di autorizzazione mi sta dando sui nervi da mesi. Il codice funziona, ma e' aggrovigliato nell'app. Ogni volta che dobbiamo aggiungere un nuovo ruolo o cambiare chi puo' accedere a cosa, stiamo editando codice applicativo che non dovrebbe occuparsi di semantica di autorizzazione.

Cosi' otto giorni fa ho iniziato a estrarlo. Oggi rilascio il risultato: [Eaco](https://github.com/ifad/eaco) — un framework di Attribute-Based Access Control per Ruby, che prende il nome da [Eaco](http://it.wikipedia.org/wiki/Eaco), il guardiano delle chiavi dell'Ade nella mitologia greca.

172 commit. Cinque release. 100% di test coverage. E un sabato pomeriggio che non rivedro' mai piu'.

<!--more-->

## Perche' non Cancan/Pundit/Rolify?

Perche' pensano tutti all'autorizzazione nel modo sbagliato — o almeno, sbagliato per il nostro caso d'uso.

I framework basati sui ruoli ti danno "questo utente e' un admin" o "questo utente e' un editor." Va bene per un blog. All'IFAD ci serve "questo utente puo' leggere questo *specifico* documento perche' e' un revisore nel dipartimento Prestiti, o perche' occupa la posizione di VP a cui e' stato concesso l'accesso, o perche' e' taggato come editor di lingua inglese." L'accesso e' sulla *risorsa*, non sull'utente. Ed e' determinato dagli *attributi* dell'utente, non da una singola colonna ruolo.

Questo e' [ABAC](https://en.wikipedia.org/wiki/Attribute-based_access_control) — Attribute-Based Access Control. La risorsa ha una ACL. La ACL dice quali *designator* (attributi di sicurezza) concedono accesso e a quale livello. L'utente ha dei designator raccolti dalla sua identita', appartenenza a gruppi, dipartimento, posizione, tag — qualunque cosa assomigli alla struttura della tua organizzazione. L'intersezione determina l'accesso.

## Le ACL sono solo hash

Ecco la semplificazione radicale: una ACL e' un semplice `Hash` Ruby. Le chiavi sono stringhe designator, i valori sono simboli ruolo:

```ruby
document.acl
#=> #<Document::ACL {"user:10" => :owner, "group:reviewers" => :reader}>
```

Tutto qui. Niente tabelle di join, niente associazioni polimorfiche, niente tabelle di autorizzazione con chiavi esterne che puntano ovunque. Un hash. Salvato come una singola colonna `jsonb` in PostgreSQL.

Questo significa che controllare l'accesso e' un lookup di chiave nell'hash. Concedere accesso e' impostare una chiave. Revocare e' cancellare una chiave. E interrogare "tutti i documenti che questo utente puo' vedere" e' una singola operazione SQL usando l'operatore `?|` di PostgreSQL:

```sql
WHERE documents.acl ?| array['user:42', 'group:employees', 'tag:english']::varchar[]
```

Una query. Niente join. Niente subselect. Il database fa l'intersezione degli insiemi per te.

## Il DSL

Le regole di autorizzazione vivono in `config/authorization.rb` — un file, dichiarativo, leggibile da chiunque:

```ruby
authorize Document, using: :pg_jsonb do
  roles :owner, :editor, :reader

  permissions do
    reader   :read
    editor   reader, :edit
    owner    editor, :destroy
  end
end

actor User do
  admin do |user|
    user.admin?
  end

  designators do
    user  from: :id
    group from: :groups
    tag   from: :tags
  end
end
```

Il blocco `permissions` e' il pezzo di cui vado piu' fiero in tutta la gem. Guarda cosa succede: `reader :read` definisce il ruolo reader con il permesso `:read`. Poi `editor reader, :edit` *passa il ruolo reader come argomento* — e siccome `reader` e' adesso un metodo che restituisce il suo set di permessi, l'editor eredita tutto quello che il reader puo' fare, piu' `:edit`. E' [method_missing come DSL](https://github.com/ifad/eaco/blob/v0.8.0/lib/eaco/dsl/resource/permissions.rb#L91-L97):

```ruby
def method_missing(role, *permissions)
  if @permissions.key?(role)
    @permissions[role]
  else
    save_permission(role, permissions)
  end
end
```

La prima chiamata definisce il ruolo. La seconda restituisce i suoi permessi. L'ereditarieta' dei ruoli emerge naturalmente dall'ordine di valutazione di Ruby. Nessuna sintassi speciale necessaria.

## I Designator

I designator sono il ponte tra la struttura della tua organizzazione e il modello di autorizzazione di Eaco. Ereditano da `String` e hanno l'aspetto di `"user:42"` o `"group:reviewers"`:

```ruby
class User::Designators::Group < Eaco::Designator
  label "Group"
end
```

L'opzione `from: :groups` nel DSL dice a Eaco di chiamare `user.groups` e avvolgere ogni risultato in un designator `Group`. Quando controlli `user.can?(:read, document)`, Eaco raccoglie tutti i designator dell'utente, li interseca con le chiavi dell'ACL del documento, e verifica se qualcuno dei ruoli risultanti ha il permesso `:read`.

Il sistema dei designator e' completamente pluggabile. La tua organizzazione ha dipartimenti? Posizioni? Comitati? Strutture a matrice? Definisci una classe designator, puntala a un metodo, e Eaco gestisce il resto.

## L'adapter PostgreSQL jsonb

Qui e' dove il design ripaga davvero. L'intero [adapter sono 13 righe](https://github.com/ifad/eaco/blob/v0.8.0/lib/eaco/adapters/active_record/postgres_jsonb.rb#L25-L33):

```ruby
def accessible_by(actor)
  return scoped if actor.is_admin?

  designators = actor.designators.map {|d| sanitize(d) }
  column = "#{connection.quote_table_name(table_name)}.acl"

  where("#{column} ?| array[#{designators.join(',')}]::varchar[]")
end
```

`Document.accessible_by(user)` restituisce una normale relazione ActiveRecord — puoi concatenarla con `.where`, `.order`, `.limit`, quello che vuoi. Sotto il cofano, l'operatore `?|` di PostgreSQL controlla se l'oggetto jsonb contiene *una qualsiasi* delle chiavi date. Indice GIN sulla colonna `acl` e hai finito. Questa query scala a milioni di documenti.

Ho anche un adapter CouchDB-Lucene per un altro progetto IFAD, ma quello jsonb e' la star dello show.

## La Guardiana

Il controllo di autorizzazione nel [controller](https://github.com/ifad/eaco/blob/v0.8.0/lib/eaco/controller.rb#L92) e' sorvegliato da una figura ASCII art di 48 righe nei commenti del sorgente. Si chiama La Guardiana, e veglia su ogni chiamata `before_filter :confront_eaco`. Perche' se devi negare l'accesso, devi farlo con stile.

```ruby
class DocumentsController < ApplicationController
  before_filter :find_document

  authorize :show, [:document, :read]
  authorize :edit, [:document, :edit]

  private
    def find_document
      @document = Document.find(params[:id])
    end
end
```

Questa e' l'intera integrazione col controller. Eaco installa un `before_filter`, controlla la variabile d'istanza `@document` contro `current_user.can?(:read, @document)`, e lancia `Eaco::Forbidden` se negato. Nessuna cerimonia.

## Lo sprint

Otto giorni. 20 febbraio, ore 2:06 — [commit iniziale](https://github.com/ifad/eaco/commit/622aba1). 20 febbraio, ore 2:12 — "Import Scriptoria's authorization code." Poi e' iniziata l'estrazione: ristrutturare in una gem ben fatta, costruire il DSL, scrivere gli adapter, aggiungere supporto Rails 3.2/4.0/4.1/4.2 via [Appraisal](https://github.com/thoughtbot/appraisal), e costruire la suite di test.

[v0.5.0](https://github.com/ifad/eaco/tree/v0.5.0) il 24 febbraio — supporto Rails 3.2. [v0.6.0](https://github.com/ifad/eaco/tree/v0.6.0) il 27 febbraio. [v0.7.0](https://github.com/ifad/eaco/tree/v0.7.0) il 28 febbraio alle 2:57. Poi lo sprint finale: lo scenario Cucumber "Enterprise Authorization" con una gerarchia organizzativa NERVE completa (dipartimenti, posizioni, utenti), piu' spec, piu' feature, 100% di coverage.

```
cc3c2b4  ACHIEVEMENT UNLOCKED: 100% coverage :party:
4a5723a  This is v0.8.0
```

28 febbraio, ore 13:33. Sessantasette minuti tra il raggiungimento del 100% di coverage e il tag della release. Cinque release in otto giorni. Denominazione d'Origine Controllata.

## Come si presenta in pratica

```ruby
# Controlla il permesso
user.can? :read, document  #=> true

# Stessa verifica, altra direzione
document.allows? :read, user  #=> true

# Che ruoli ha questo utente?
document.roles_of user  #=> [:owner]

# Concedi accesso
document.grant :reader, :group, "reviewers"

# Revoca accesso
document.revoke :user, 42

# Tutti i documenti accessibili da questo utente
Document.accessible_by(user)  # => ActiveRecord::Relation
```

Entrambe le direzioni funzionano — `user.can?` e `document.allows?` — perche' a volte ragioni dalla prospettiva dell'utente e a volte da quella della risorsa. Stessa logica sotto.

## Made in Italy

La gem e' sotto licenza MIT e [su GitHub](https://github.com/ifad/eaco). La documentazione YARD copre ogni metodo pubblico. Le [feature Cucumber](https://github.com/ifad/eaco/blob/v0.8.0/features/enterprise_authorization.feature) si leggono come specifiche — lo scenario Enterprise modella una struttura organizzativa reale con la complessita' che ci si aspetta da un'agenzia ONU.

Se le tue esigenze di autorizzazione vanno oltre "admin o no" — se l'accesso dipende da *chi e' l'utente in relazione alla risorsa* — prova Eaco. `gem install eaco` e crea il tuo `config/authorization.rb`.

Le chiavi dell'Ade sono in buone mani.
