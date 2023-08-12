---
date: 2010-05-11T19:00:00Z
title: "Spent my day on Erlang-Ruby-Marshal today ;-)"
tags: [erlang, projects, ruby]
---

![Erlang logo](/posts/2010-05-11-spent-my-day-on-erlang-ruby-marshal-today/erlang.png)

In a nutshell, it adds support for unmarshaling 1.9 strings, and implements the
last missing type (`TYPE_LINK`) that was missing from the code. Tests still
lack, can someone [help](http://github.com/vjt/erlang-ruby-marshal) ? :-)

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

Fork me on GitHub: http://github.com/vjt/erlang-ruby-marshal
