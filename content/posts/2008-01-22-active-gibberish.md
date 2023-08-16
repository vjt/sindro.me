---
title: Active Gibberish
date: 2008-01-22
tags: [gibberish, localization, rails, ruby]
categories: [development, all]
---

**UPDATE: you don’t need this code, because starting from the 2.2 version of Rails, localization support is built-in.**

## Localization for Active Record error messages

Today i had to answer to one of the questions every non-english Rails developer
stumbles upon now or after.. how to localize AR error messages for pleasant
appearance to a non-english customer ;).

First off, thanks to [defunkt’s](http://errtheblog.com) excellent gibberish
plugin and to the way AR validation errors are exposed, the task was
accomplished in an easy and clean manner, without messing too much with AR’s
internals.

I started by translating every default AR error message, with this translation
file located in `lang/it.yml`:

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

and four lines in `config/environment.rb`:

```ruby
Gibberish.current_language = :it
ActiveRecord::Errors.default_error_messages =
  ActiveRecord::Errors.default_error_messages.inject({}) {|h, (key, string)|
    h.update(key => string["ar_#{key}".intern]) # <em>Gibberish magic</em>
}
```

The first one simply sets Italian (:it) as the default language, the inject
builds a new `error_messages` hash using Gibberish to translate the default ones.
I named every AR error key in my translation file with an “ar_” prefix, in
order to avoid possible future key clashes. Finally, AR array is overwritten
with the new one freshly built.

This solution assumes that the application will show only in a single language,
if you need localized error messages in different language you should put this
code in some `around_filter`, like Gibberish documentation suggests.

OK, messages are translated, but what about field names? I used english field
names in my tables, how about translating them as well? First, we need the
actual translations in lang/it.yml:

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

And then a customized helper that our view will call, loosely based on the
default `error_messages_for` Rails helper:


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

Here, easily, every field name is substituted by its translated counterpart,
and a div is built with the plain vanilla class and id used by Rails’
[code]scaffold.css[/code], so that I won’t have to write a single line of CSS.

In your view: `<%= foo_object_error_messages %>`

This helper could be of course improved, but I’m a bit lazy right now.

Have fun! :D
