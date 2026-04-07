---
title: Estrarre dati dalla cache di Apple Safari
date: 2008-01-20
tags: [apple, backup]
---

Cinque minuti fa ho sovrascritto il nuovissimo e fiammante foglio di stile CSS
che implementa la combinazione di colori attuale, perché volevo ripristinare
quello originale e metterlo in un nuovo tema per questo sito, così che chi
apprezzava il vecchio tema potesse continuare a usarlo. Ma, come il più
principiante degli amministratori di sistema, ho decompresso i file originali
dall'archivio di backup SOPRA quelli attuali...

Safari in soccorso! Ogni elemento nella cache di Safari è memorizzato in un
database SQLite3 che si trova in `~/Library/Caches/com.apple.Safari`,
andiamo a vedere com'è strutturato:


```
 13:54:42 vjt@voyager:~/Library/Caches/com.apple.Safari$ sqlite3 Cache.db 
SQLite version 3.5.1
Enter ".help" for instructions

sqlite> .tables
cfurl_cache_blob_data       cfurl_cache_schema_version
cfurl_cache_response      

sqlite> .schema cfurl_cache_response 
CREATE TABLE cfurl_cache_response(
  entry_ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
  version INTEGER,
  hash_value INTEGER,
  storage_policy INTEGER,
  request_key TEXT UNIQUE,
  time_stamp NOT NULL DEFAULT CURRENT_TIMESTAMP);

sqlite> .schema cfurl_cache_blob_data
CREATE TABLE cfurl_cache_blob_data(
  entry_ID INTEGER PRIMARY KEY,
  response_object BLOB,
  request_object BLOB,
  receiver_data BLOB,
  proto_props BLOB,
  user_info BLOB);

sqlite> select * from cfurl_cache_response limit 3;
1|0|1897220634|0|http://..../|2008-01-19 11:10:33
2|0|-662909776|0|http://..../|2008-01-19 11:10:33
```

Wow. Impressionante. Ecco perché adoro i prodotti Apple: sono così ben
strutturati che puoi liberamente ispezionarli e usare le loro risorse per
qualsiasi compito imprevisto tu debba completare... anche per rimediare ai tuoi
stessi errori ;). Ed è anche stimolante, perché devi rimboccarti le maniche e
trovare la soluzione esplorando un prodotto software costruito splendidamente.

Per farla breve, ogni URL nella cache è memorizzato nel campo `request_key`
della tabella `cfurl_cache_response`, mentre nel campo `receiver_data` della
tabella `cfurl_cache_blob_data` ci sono i dati effettivi. Ora possiamo cercare
il foglio di stile CSS del tema bbs che abbiamo sovrascritto:

```
sqlite> select entry_ID, request_key from cfurl_cache_response
   ...> where request_key like '%bbs/style.css';
??1950??|http://sindro.me/sites/all/themes/bbs/style.css
```

Adesso cerchiamo nella tabella `blob_data` l'entry con ID 1950:

```
sqlite> select receiver_data from cfurl_cache_blob_data
   ...> where entry_ID = 1950;
/**
 * Themetastic, for Drupal 5.0
 * Stefan Nagtegaal, iStyledThis [dot] nl
 * Steven Wittens, acko [dot] net`
 *
 * If you use a customized color scheme, you must regenerate it after
 * modifying this file.
[......rest of the stylesheet removed.....]
```

YAY! Trovato! Un rapido copia e incolla... e il tema perduto è tornato! :D
