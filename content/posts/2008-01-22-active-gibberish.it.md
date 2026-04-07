---
title: Active Gibberish
date: 2008-01-22
tags: [funny, rails, ruby]
---

**AGGIORNAMENTO: non ti serve questo codice, perché a partire dalla versione 2.2 di Rails il supporto alla localizzazione è integrato.**

## Localizzazione dei messaggi di errore di Active Record

Oggi ho dovuto rispondere a una delle domande su cui ogni sviluppatore Rails
non anglofono prima o poi inciampa... come localizzare i messaggi di errore di
AR per mostrarli in modo decente a un cliente che non parla inglese ;).

Prima di tutto, grazie all'eccellente plugin gibberish di
[defunkt](http://errtheblog.com) e al modo in cui gli errori di validazione di
AR sono esposti, il compito è stato portato a termine in modo semplice e
pulito, senza mettere troppo le mani negli internals di AR.

Ho cominciato traducendo ogni messaggio di errore predefinito di AR, con questo
file di traduzione in `lang/it.yml`:

```ruby
# Active Record errors
#
ar_accepted:     "deve essere accettato" 
ar_not_a_number: "non è un numero" 
ar_blank:        "è un campo obbligatorio" 
ar_empty:        "è un campo obbligatorio" 
ar_inclusion:    "non è nella lista dei valori validi" 
ar_too_long:     "è troppo lungo (massimo %d caratteri)" 
ar_exclusion:    "è riservato" 
ar_too_short:    "è troppo corto (minimo %d caratteri)" 
ar_invalid:      "non è valido" 
ar_wrong_length: "è errato, dovrebbe essere di %d caratteri" 
ar_confirmation: "non corrisponde" 
ar_taken:        "esiste già" 
# This one is not a default key, but I use it in my validations
ar_greater_zero: "deve essere maggiore di zero" 
```

e quattro righe in `config/environment.rb`:

```ruby
Gibberish.current_language = :it
ActiveRecord::Errors.default_error_messages =
  ActiveRecord::Errors.default_error_messages.inject({}) {|h, (key, string)|
    h.update(key => string["ar_#{key}".intern]) # <em>Gibberish magic</em>
}
```

La prima riga imposta semplicemente l'italiano (:it) come lingua predefinita,
l'inject costruisce un nuovo hash `error_messages` usando Gibberish per
tradurre quelli predefiniti. Ho nominato ogni chiave di errore AR nel mio file
di traduzione con il prefisso "ar_", per evitare possibili conflitti futuri di
chiavi. Infine, l'array di AR viene sovrascritto con quello appena costruito.

Questa soluzione presuppone che l'applicazione venga mostrata in una sola
lingua; se hai bisogno di messaggi di errore localizzati in lingue diverse,
dovresti mettere questo codice in qualche `around_filter`, come suggerisce la
documentazione di Gibberish.

OK, i messaggi sono tradotti, ma i nomi dei campi? Ho usato nomi di campo in
inglese nelle mie tabelle, come tradurre anche quelli? Prima ci servono le
traduzioni effettive in lang/it.yml:

```ruby
# Field names
#
fld_multiplier:  "La dimensione" 
fld_service_id:  "Il servizio" 
fld_customer_id: "Il contraente" 
fld_address_id:  "L'indirizzo" 
fld_user_id:     "L'utente" 
fld_city_id:     "La città" 
fld_state_id:    "La provincia" 
fld_address:     "L'indirizzo" 
fld_terms_of_service: "Il testo di informativa sulla privacy" 
```

E poi un helper personalizzato che la nostra view chiamerà, liberamente basato
sull'helper Rails predefinito `error_messages_for`:


```ruby
  # error messages localization
  # uses gibberish.
  def foo_object_error_messages
    return '' if @foo_object.errors.count.zero?
    header_message = "Si prega di correggere i seguenti errori:" 
    error_messages = @foo_objects.errors.map do |field, err|
      field = field["fld_#{field}".intern] # [i]Gibberish magic[/i]
      content_tag(:li, "#{field} #{err}")
    end 
    content_tag(:div,
      content_tag(:h2, header_message) <<
        content_tag(:ul, error_messages),
      :class => 'errorExplanation',
      :id    => 'errorExplanation'
    )   
  end 
```

Qui, semplicemente, ogni nome di campo viene sostituito dalla sua controparte
tradotta, e viene costruito un div con le classi e gli id standard usati dal
[code]scaffold.css[/code] di Rails, così non devo scrivere neanche una riga di
CSS.

Nella tua view: `<%= foo_object_error_messages %>`

Questo helper potrebbe sicuramente essere migliorato, ma al momento sono un po' pigro.

Divertitevi! :D
