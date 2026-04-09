---
date: 2010-05-11T19:00:00Z
title: "Oggi ho speso la giornata su Erlang-Ruby-Marshal ;-)"
tags: [erlang, projects, ruby]
---

{{< retrospective year="2026" >}}
Ruby 1.9 ha raggiunto la fine del ciclo di vita nel 2015 e Ruby 3.x ha ulteriormente cambiato il formato marshal. La repo `erlang-ruby-marshal` su GitHub è archiviata e non mantenuta. Se oggi hai bisogno di interoperabilità Erlang-Ruby, meglio usare JSON, MessagePack o Protocol Buffers.
{{< /retrospective >}}

![Erlang logo](/posts/2010-05-11-spent-my-day-on-erlang-ruby-marshal-today/erlang.png)

In sintesi, aggiunge il supporto per l'unmarshaling delle stringhe 1.9, e
implementa l'ultimo tipo mancante (`TYPE_LINK`) che mancava dal codice. I test
ancora latitano, qualcuno vuole [dare una mano](http://github.com/vjt/erlang-ruby-marshal)? :-)

```
Added TYPE_LINK, needed because of how ruby 1.9 marshals strings.

In 1.9, Ruby marshals the string encoding in the binary output, and
uses an Ivar construct (TYPE_IVAR) to wrap the string and adds an
"encoding" instance variable (notice: without a leading @) whose
value is the encoding itself.

While the Ivar code worked correctly, the values of the encodings
are actually *strings*, that are being reused via the TYPE_LINK
construct, that wasn't implemented.

So, the get() and put() primitives are being used to store not
only tuples {id, sym} for symbols, but now store either

  {{symbol, ID}, sym}

  OR

  {{value,  ID}, val}

for the other types that use TYPE_LINK.

By reading the ruby marshal.c source code, it looks like that MANY
data types save their values in the arg->data hashtable, but by
inspecting the binary marshal output of, e.g, an array of floats,
links aren't used.

Thus, in this unmarshaler, links are considered, for now, only for
strings and regexes.
```

Forkami su GitHub: http://github.com/vjt/erlang-ruby-marshal
