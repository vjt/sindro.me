---
title: "Integrare i prodotti OneSpan 2FA in Ruby"
date: 2020-09-11
tags: [ruby, c, security, open-source, ifad]
description: "Due gemme Ruby per integrare il 2FA via token hardware OneSpan: una C extension che wrappa l'SDK proprietario AAL2 e un client SOAP per il OneSpan Authentication Server (ex Identikey)."
image: cover.jpg
featuredImage: cover.jpg
---

Mi è stato affidato il compito di integrare l'autenticazione a due fattori con token hardware di [OneSpan](https://www.onespan.com/) (ex VASCO) in uno stack Ruby — wrappando il loro SDK C proprietario VACMAN Controller per la validazione OTP in locale, e costruendo un client per l'API SOAP del [OneSpan Authentication Server](https://docs.onespan.com/sec/docs/onespan-authentication-server) (originariamente chiamato Identikey Authentication Server, rinominato a metà progetto). Nessuno dei due aveva una libreria Ruby.

Per [vacman_controller](https://github.com/vjt/vacman_controller) c'era un punto di partenza: [una C extension Ruby](https://github.com/mlankenau/vacman_controller) di Marcus Lankenau che wrappava l'SDK AAL2. Un solo commit, nessuna release, parecchio grezza, ma le fondamenta — linking, import dei token e wrapper di base — c'erano. L'ho [forkata in IFAD](https://github.com/ifad/vacman_controller), sistemata, estesa e le ho spinto sopra [97 commit aggiuntivi](https://github.com/vjt/vacman_controller/commits/master). 14 release, dalla v0.1.0 alla v0.9.3.

Per [identikey](https://github.com/vjt/identikey) non c'era nulla — OneSpan distribuisce un SDK Java, nessuna libreria Ruby esiste. L'ho [scritta da zero](https://github.com/vjt/identikey): 123 commit, 18 tag, dalla v0.2.0 alla v0.9.1.

Entrambe sono [su](https://github.com/vjt/vacman_controller) [GitHub](https://github.com/vjt/identikey). Ecco cosa c'è dentro.

<!--more-->

## vacman_controller

La gemma [vacman_controller](https://github.com/vjt/vacman_controller) è una C extension Ruby che wrappa l'SDK AAL2 di OneSpan — una libreria C proprietaria a codice chiuso per gestire i token hardware DIGIPASS. L'SDK viene distribuito come libreria statica con un header file, senza sorgenti, senza simboli di debug, e con una documentazione che sembra tradotta dall'olandese attraverso un fax. Il tuo compito è linkarla e pregare. L'[`extconf.rb`](https://github.com/vjt/vacman_controller/blob/master/ext/vacman_controller/extconf.rb) gestisce la preghiera — auto-scopre l'SDK facendo glob su `/opt/vasco/VACMAN_Controller-*`, sceglie l'ultima versione e linka con `-rpath` in modo che la shared library venga risolta a runtime senza giochi di `LD_LIBRARY_PATH`.

L'Authentication Server gestisce i token internamente ed espone la validazione OTP e l'amministrazione tramite la sua API — ma per un caso d'uso specifico avevamo bisogno di gestire i token direttamente.

Quando gestisci un token in proprio, il requisito centrale è la persistenza dello stato: il blob del token muta ad ogni operazione e va salvato dopo ciascuna di esse. Ho scelto di serializzarlo come un semplice hash Ruby — una struttura piatta chiave-valore che offre massima comodità per la serializzazione e l'interop con qualsiasi storage o trasporto tu decida di usare.

Un blob di token è tutto ciò che serve per generare OTP — l'SDK AAL2 [lo impedisce artificialmente](#la-patch-binaria), ma i seed sono lì dentro. Tratta i blob come chiavi private: mai loggarli, mai esporli fuori dal datastore, mai includerli in una response API. Se un blob trapela, la fiducia 2FA per quel token è compromessa.

La gemma fa da ponte tra il mondo delle struct C dell'SDK e questo mondo di hash Ruby, e il ponte è il luogo in cui vive tutta l'ingegneria interessante.

### Il ponte C-Ruby

{{< figure src="c-ruby-bridge.jpg" alt="Blocchi struct C che si trasformano in cristalli Ruby attraverso un ponte" >}}

La struttura dati centrale dell'SDK AAL2 è `TDigipassBlob` — una struct opaca che contiene il numero seriale del token, il nome dell'applicazione, i flag, e un campo `Blob` da 224 byte che conserva lo stato cifrato del token. Ogni chiamata all'SDK prende un puntatore a questa struct, la muta in place e si aspetta che tu persista le modifiche.

La gemma non wrappa `TDigipassBlob` in un oggetto Ruby — serializza la struct in un hash piatto che può fare round-trip attraverso una colonna del database, una coda di background job o qualunque altro posto in cui lo stato del token debba viaggiare. Il layer di serializzazione in [`serialize.c`](https://github.com/vjt/vacman_controller/blob/master/ext/vacman_controller/serialize.c) converte avanti e indietro:

```c
void vacman_rbhash_to_digipass(VALUE token, TDigipassBlob* dpdata) {
  VALUE blob     = rbhash_get_key(token, "blob",     T_STRING);
  VALUE serial   = rbhash_get_key(token, "serial",   T_STRING);
  VALUE app_name = rbhash_get_key(token, "app_name", T_STRING);
  VALUE flag1    = rbhash_get_key(token, "flags1",   T_FIXNUM);
  VALUE flag2    = rbhash_get_key(token, "flags2",   T_FIXNUM);

  memset(dpdata, 0, sizeof(*dpdata));

  strcpy(dpdata->Blob, rb_string_value_cstr(&blob));
  strncpy(dpdata->Serial, rb_string_value_cstr(&serial), sizeof(dpdata->Serial));
  strncpy(dpdata->AppName, rb_string_value_cstr(&app_name), sizeof(dpdata->AppName));
  dpdata->DPFlags[0] = rb_fix2int(flag1);
  dpdata->DPFlags[1] = rb_fix2int(flag2);
}
```

E la direzione inversa, che impacchetta la struct dentro un hash Ruby:

```c
void vacman_digipass_to_rbhash(TDigipassBlob* dpdata, VALUE hash) {
  char buffer[256];

  memset(buffer, 0, sizeof(buffer));
  strncpy(buffer, dpdata->Serial, 10);
  rb_hash_aset(hash, rb_str_new2("serial"), rb_str_new2(buffer));

  memset(buffer, 0, sizeof(buffer));
  strncpy(buffer, dpdata->AppName, 12);
  rb_hash_aset(hash, rb_str_new2("app_name"), rb_str_new2(buffer));

  memset(buffer, 0, sizeof(buffer));
  strncpy(buffer, dpdata->Blob, 224);
  rb_hash_aset(hash, rb_str_new2("blob"), rb_str_new2(buffer));

  rb_hash_aset(hash, rb_str_new2("flags1"), rb_fix_new(dpdata->DPFlags[0]));
  rb_hash_aset(hash, rb_str_new2("flags2"), rb_fix_new(dpdata->DPFlags[1]));
}
```

Il pattern è: deserializzi l'hash Ruby in una `TDigipassBlob` allocata sullo stack, chiami la funzione SDK (che muta la struct), poi serializzi la struct di ritorno nello *stesso* hash Ruby. L'hash è il token — viaggia da Ruby al C e ritorno, accumulando cambi di stato lungo il cammino. Tutto sta sullo stack, quindi niente grattacapi di memory management e niente preoccupazioni di thread safety da questo lato del recinto.

Esiste anche una variante, [`vacman_rbhash_to_digipass_sv`](https://github.com/vjt/vacman_controller/blob/master/ext/vacman_controller/serialize.c#L53), che gestisce un'ulteriore chiave `"sv"` per lo static vector del token — necessaria per la [generazione offline dell'activation code](https://github.com/vjt/vacman_controller/blob/master/ext/vacman_controller/dpx.c#L92) via `AAL2GenActivationCodeXErc`. Quando si provisiona un nuovo soft token, l'activation code permette al device dell'utente di sincronizzarsi col server senza round-trip. Non tutti i token hanno uno static vector — la chiave `"sv"` è presente solo sui token importati da file DPX che ne includono uno.

### Importazione dei token

{{< figure src="dpx-import.jpg" alt="Una cassaforte metallica aperta che rivela capsule ambra luminose — token DPX cifrati" >}}

I token arrivano come file `.dpx` — container cifrati che contengono i seed dei token e i parametri di inizializzazione. Li decifri con una transport key che OneSpan fornisce separatamente. Il flusso di import in [`dpx.c`](https://github.com/vjt/vacman_controller/blob/master/ext/vacman_controller/dpx.c) apre il DPX e poi itera sul contenuto estraendo i token uno alla volta:

```c
VALUE vacman_dpx_import(VALUE module, VALUE filename, VALUE key) {
  TDPXHandle dpx_handle;
  aat_int16  appl_count;
  aat_ascii  appl_names[13*8];
  aat_int16  token_count;

  aat_int32 result = AAL2DPXInit(&dpx_handle,
                                 rb_string_value_cstr(&filename),
                                 rb_string_value_cstr(&key),
                                 &appl_count,
                                 appl_names,
                                 &token_count);

  if (result != 0) {
    vacman_library_error("AAL2DPXInit", result);
    return Qnil;
  }

  // ...

  VALUE list = rb_ary_new();

  while (1) {
    result = AAL2DPXGetToken(&dpx_handle,
        &g_KernelParms,
        appl_names,
        sw_out_serial_No,
        sw_out_type,
        sw_out_authmode,
        &dpdata);

    if (result < 0) {
      vacman_library_error("AAL2DPXGetToken", result);
      return Qnil;
    }

    if (result == 107) break;

    VALUE hash = rb_hash_new();
    vacman_digipass_to_rbhash_sv(&dpdata, sw_out_static_vector, hash);
    rb_ary_push(list, hash);
  }

  AAL2DPXClose(&dpx_handle);
  return list;
}
```

Nota il `if (result == 107) break;` — è la sentinella di "fine file". Non `EOF`, non `-1`, non una costante nominata: il magic number `107`. La documentazione AAL2 non ne parla. Era già [nel codice originale di Marcus](https://github.com/mlankenau/vacman_controller/blob/master/ext/vacman_controller/vacman_controller.c#L139). I risultati negativi sono errori, lo zero vuol dire "ecco un token" e `107` vuol dire "niente più token".

Un dettaglio sottile: `AAL2DPXInit` non valida la transport key. Se passi la chiave sbagliata non ottieni un errore — ottieni token che generano OTP sbagliati. Scoprirai l'errore solo dopo, quando utenti reali non riusciranno ad autenticarsi. Divertente.

I messaggi d'errore dell'SDK sono altrettanto d'aiuto. Ogni errore SDK passa attraverso [`vacman_library_error`](https://github.com/vjt/vacman_controller/blob/master/ext/vacman_controller/main.c#L48) nel layer C, che crea un'eccezione Ruby con metadata strutturati — `@library_method`, `@error_code`, `@error_message` — attaccati via `rb_iv_set`:

```c
VALUE exc = rb_exc_new2(e_VacmanError, error_message);
rb_iv_set(exc, "@library_method", rb_str_new2(method));
rb_iv_set(exc, "@error_code",     INT2FIX(vacman_error_code));
rb_iv_set(exc, "@error_message",  rb_str_new2(vacman_error_message));
rb_exc_raise(exc);
```

Il wrapper Ruby poi [traduce i codici d'errore non documentati](https://github.com/vjt/vacman_controller/blob/master/lib/vacman_controller.rb#L37): `-15` diventa "invalid transport key", `-20` diventa "cannot open DPX file". Il `AAL2GetErrorMsg` di OneSpan non restituisce nulla di utile per nessuno dei due.

### Verifica OTP

{{< figure src="otp-clockwork.jpg" alt="Meccanismo a orologeria in ottone con anelli rotanti di codici a 6 cifre" >}}

L'operazione core — verificare una one-time password — vive in [`token.c`](https://github.com/vjt/vacman_controller/blob/master/ext/vacman_controller/token.c). La funzione C segue il pattern deserializza-chiama-serializza:

```c
VALUE vacman_token_verify_password(VALUE module, VALUE token, VALUE password) {
  TDigipassBlob dpdata;

  vacman_rbhash_to_digipass(token, &dpdata);

  aat_int32 result = AAL2VerifyPassword(&dpdata, &g_KernelParms,
                                         rb_string_value_cstr(&password), 0);

  vacman_digipass_to_rbhash(&dpdata, token);

  if (result == 0)
    return Qtrue;
  else {
    vacman_library_error("AAL2VerifyPassword", result);
    return Qnil;
  }
}
```

La sottigliezza critica qui: `vacman_digipass_to_rbhash(&dpdata, token)` viene eseguito *indipendentemente dal fatto che l'OTP sia valido o meno*. È intenzionale. `AAL2VerifyPassword` muta la `TDigipassBlob` ad ogni chiamata — incrementa gli error counter in caso di fallimento, aggiusta le finestre di time drift in caso di successo e aggiorna lo stato interno di sequenza. Il blob del token dopo la verifica è *diverso* dal blob prima della verifica, che l'OTP fosse giusto o sbagliato. Se scarti lo stato post-verifica, il token esce di sync col server e diventa inutilizzabile.

Lato Ruby, [`Token#verify`](https://github.com/vjt/vacman_controller/blob/master/lib/vacman_controller/token.rb) wrappa tutto così:

```ruby
def verify(otp)
  verify!(otp)
rescue VacmanController::Error
  false
end

def verify!(otp)
  VacmanController::LowLevel.verify_password(@token_hash, otp.to_s)
end
```

Due sapori: `verify!` solleva in caso di fallimento (per controller che vogliono mostrare un flash d'errore), `verify` ritorna un booleano (per background job che controllano OTP e vanno avanti). Entrambi chiamano la stessa funzione C. Entrambi mutano `@token_hash` in place. Il commento `ATTENTION` nel [sorgente](https://github.com/vjt/vacman_controller/blob/master/lib/vacman_controller/token.rb#L65) lo rende esplicito: *devi* persistere `token.to_h` dopo ogni chiamata di verifica. Salta il passo di persistenza e passerai una settimana a debuggare perché i token funzionano per il primo OTP e poi rifiutano tutto il resto.

Questo si estende a ogni operazione SDK. Settare una proprietà, cambiare il PIN, resettare gli error count — seguono tutti lo stesso pattern in [`token.c`](https://github.com/vjt/vacman_controller/blob/master/ext/vacman_controller/token.c): deserializza, chiama la funzione vendor, serializza di ritorno. L'hash viene sempre mutato e il chiamante è sempre responsabile di salvarlo.

### Parametri del kernel thread-safe

L'SDK AAL2 ha una struct globale `TKernelParms` — `g_KernelParms` — che configura il comportamento runtime: finestre temporali, numero di iterazioni e altri parametri che si applicano a tutte le operazioni sui token. In un'applicazione Ruby multi-thread (Puma, Sidekiq), scritture concorrenti a questa struct la corromperebbero.

Il modulo [`Kernel`](https://github.com/vjt/vacman_controller/blob/master/lib/vacman_controller/kernel.rb) lo gestisce con una Mutex solo sul setter:

```ruby
module VacmanController
  module Kernel
    class << self
      def [](name)
        VacmanController::LowLevel.get_kernel_param(name)
      end

      def []=(name, val)
        Mutex.synchronize do
          VacmanController::LowLevel.set_kernel_param(name, val)
        end
      end

      Mutex = Thread::Mutex.new
    end
  end
end
```

Nessuna mutex sulle letture. I parametri kernel si settano una volta al boot e raramente cambiano dopo — è un pattern di accesso read-heavy, write-almost-never. Bloccare ogni lettura aggiungerebbe contention per zero beneficio. La Mutex protegge contro il caso raro in cui due thread tentino di riconfigurare il kernel simultaneamente, e nient'altro.

### Proprietà del token

L'SDK AAL2 espone oltre 40 proprietà per token — `pin_enabled`, `error_count`, `auth_mode`, `virtual_token_grace_period` e decine d'altre. Ogni proprietà è identificata da una costante numerica nell'header C. Il layer C in [`token.c`](https://github.com/vjt/vacman_controller/blob/master/ext/vacman_controller/token.c) mappa nomi leggibili a questi ID attraverso un [registro statico](https://github.com/vjt/vacman_controller/blob/master/ext/vacman_controller/token.c#L19), con alias in modo che i chiamanti possano usare sia le abbreviazioni criptiche di OneSpan sia i nomi estesi:

```c
static struct token_property vacman_token_properties[] = {
  {"pin_ch_on",          PIN_CH_ON       },
  {"pin_change_enabled", PIN_CH_ON       },
  {"pin_len",            PIN_LEN         },
  {"pin_length",         PIN_LEN         },
  {"response_chk",       RESPONSE_CHK    },
  {"response_checksum",  RESPONSE_CHK    },
  {"use_3des",           TRIPLE_DES_USED },
  {"triple_des_used",    TRIPLE_DES_USED },
  // ...40+ entries
};
```

`pin_ch_on` e `pin_change_enabled` risolvono alla stessa costante `PIN_CH_ON`. La documentazione OneSpan usa le abbreviazioni; la gemma espone anche nomi estesi cosicché i chiamanti scrivano codice auto-documentante invece di indovinare cosa voglia dire `pin_ch_on`.

Lato Ruby, [`Token::Properties`](https://github.com/vjt/vacman_controller/blob/master/lib/vacman_controller/token/properties.rb) wrappa tutto questo con `method_missing` per una sintassi getter/setter naturale — `token.properties.pin_enabled` legge, `token.properties.token_status = :disabled` scrive:

```ruby
def method_missing(name, *args, &block)
  prop, setter = name.to_s.match(/\A(.+?)(=)?\Z/).values_at(1, 2)
  if setter
    self[prop] = args.first
  else
    self[prop]
  end
end
```

La parte interessante è il layer di type casting sotto. L'SDK AAL2 parla solo interi e stringhe. Il lato Ruby traduce in entrambe le direzioni. In lettura, [`read_cast`](https://github.com/vjt/vacman_controller/blob/master/lib/vacman_controller/token/properties.rb#L157) converte `"YES"`/`"NO"` in `true`/`false`, timestamp come `"Wed Jan 01 00:00:00 2020"` in oggetti `Time`, authentication mode in simboli — `:response_only`, `:challenge_response`, `:multi_mode`. In scrittura, [`write_cast!`](https://github.com/vjt/vacman_controller/blob/master/lib/vacman_controller/token/properties.rb#L71) impone vincoli con messaggi d'errore migliori di quelli che ti darebbe l'SDK:

```ruby
when 'pin_change_forced'
  if value
    1
  else
    raise VacmanController::Error,
      "Token property #{property} cannot be set to #{value.inspect}"
  end

when 'token_status'
  case value
  when :disabled     then 0
  when :primary_only then 1
  when :backup_only  then 2
  when :enabled      then 3
  else
    raise VacmanController::Error,
      "Token property #{property} cannot be set to #{value.inspect}"
  end
```

`pin_change_forced` è un flag unidirezionale — puoi forzare un cambio PIN ma non puoi "de-forzarlo", quindi il setter solleva invece di fallire silenziosamente. `token_status` mappa simboli Ruby ai valori interi che l'SDK si aspetta. `pin_enabled` mappa `true` a `1` e `false` a `2` — sì, `2`, non `0`, perché OneSpan. Le proprietà intere limitate come `pin_minimum_length` (3–8) e `virtual_token_grace_period` (1–364) ottengono validazione di range. [Oltre quaranta proprietà](https://github.com/vjt/vacman_controller/blob/master/ext/vacman_controller/token.c#L19), ciascuna con la sua semantica di tipo, tutte dietro un'[interfaccia coerente](https://github.com/vjt/vacman_controller/blob/master/lib/vacman_controller/token/properties.rb) che fa sembrare l'API C ossessionata dagli interi di OneSpan un oggetto Ruby.

### La patch binaria

{{< figure src="binary-patch.jpg" alt="Vista di hex editor scolpita nell'ossidiana — un singolo byte evidenziato in rosso, uno strumento di precisione sospeso sopra" >}}

L'SDK AAL2 sa verificare i codici OTP. Sa anche generarli — ma solo per un piccolo insieme di token demo che OneSpan distribuisce a scopo di sviluppo. Per i token hardware e i token software reali, la generazione è bloccata completamente. Gli passi un seed, lui ti dice sì o no su un OTP sottoposto, ma non ti dice quale *dovrebbe essere* l'OTP.

È una limitazione artificiale imposta a runtime. Ma il codice è lì — *deve* esserci. La verifica dell'OTP non è un semplice confronto tra stringhe; la libreria deve generare internamente l'OTP atteso a partire dal seed del token e dalla finestra temporale corrente per verificare quello inviato dall'utente. La logica di generazione esiste. È lo stesso cammino di codice. L'SDK la espone per i token demo e la blocca per tutto il resto.

Per curiosità di ricerca sono andato a cercare quel check nel binario — e l'ho trovato. Il repo include [`ext/libaal2sdk-3.15.1.so.vtoken.bspatch`](https://github.com/vjt/vacman_controller/blob/master/ext/libaal2sdk-3.15.1.so.vtoken.bspatch) — una patch [bsdiff](https://www.daemonology.net/bsdiff/) che applichi contro il `.so` proprietario per sbloccare la generazione software degli OTP per tutti i tipi di token, purché tu abbia i seed.

Cosa potrebbe sbloccare nella pratica: testing e CI. Immagina di far girare una suite completa di test di verifica dei token senza un DIGIPASS fisico sulla scrivania, senza essere limitati alla manciata di token demo di OneSpan. Ma questa è un'altra storia.

Questo è totalmente non supportato. Invaliderà senz'altro qualsiasi contratto di supporto con OneSpan. Se sai quello che stai facendo, la patch è lì. Regolati di conseguenza.

Questo è anche il motivo per cui i blob dei token vanno trattati come chiavi private. Con la libreria patchata e un blob trapelato, chiunque può generare OTP validi per quel token — nessun device hardware necessario. Tieni i blob nel datastore, tienili fuori dai log e non esporli mai tramite un'API.

## identikey

{{< figure src="soap-labyrinth.jpg" alt="Una cattedrale barocca steampunk di tubi, valvole e planimetrie WSDL XML" >}}

La gemma [identikey](https://github.com/vjt/identikey) è una bestia di tutt'altra specie. Parla con il [OneSpan Authentication Server](https://docs.onespan.com/sec/docs/onespan-authentication-server) — il prodotto enterprise 2FA. Quando ho iniziato questo lavoro si chiamava Identikey Authentication Server; OneSpan l'ha rinominato a metà progetto, ma la gemma porta ancora il vecchio nome. Dove vacman_controller lotta con un SDK C e struct opache, identikey lotta con SOAP — specificatamente, con l'interpretazione che ne dà OneSpan, la quale sta allo standard WS-I come un sogno febbrile sta a un pensiero lucido.

Il server espone tre endpoint SOAP separati: [Authentication](https://github.com/vjt/identikey/blob/master/lib/identikey/authentication.rb), [Administration](https://github.com/vjt/identikey/blob/master/lib/identikey/administration.rb) e [Provisioning](https://github.com/vjt/identikey/blob/master/lib/identikey/provisioning.rb). Ciascuno ha il proprio WSDL, il proprio formato di response, la propria idea di cosa significhi "successo". La gemma usa [Savon](https://www.savonrb.com/) per il lavoro pesante e wrappa i tre endpoint in una classe [`Base`](https://github.com/vjt/identikey/blob/master/lib/identikey/base.rb) condivisa che nasconde le incoerenze.

### Il labirinto SOAP

La prima sorpresa arriva da Savon stesso. Quando riconfiguri il percorso WSDL a runtime — ad esempio, per puntare a una fixture di test invece che al server di produzione — il `client.globals` di Savon aggiorna il percorso ma l'oggetto interno `client.wsdl` continua a puntare a quello vecchio. Il metodo [`configure`](https://github.com/vjt/identikey/blob/master/lib/identikey/base.rb#L6) aggira la cosa così:

```ruby
def self.configure(&block)
  self.client.globals.instance_eval(&block)

  # Work around a sillyness in Savon
  if client.globals[:wsdl] != client.wsdl.document
    client.wsdl.document = client.globals[:wsdl]
  end
end
```

Un fix di due righe per un bug che è costato un'ora di debug. Il commento dice "sillyness" perché come altro vuoi chiamare un'API di configurazione che ignora silenziosamente metà della configurazione?

### Il problema degli attributi

Qui OneSpan passa da "fastidioso" ad "avversariale". In un'API SOAP sana, un oggetto user torna con elementi XML nominati — `<userId>john</userId>`, `<email>john@example.com</email>`. Li parsi, ottieni un hash con chiavi parlanti. Fine.

OneSpan non fa così. Ogni singolo attributo arriva come una coppia di elementi generici — `<attributeID>` che contiene il nome del campo e `<value>` che contiene il valore. Stessa struttura piatta, per ogni attributo, in ogni response. Una query su un utente ritorna una dozzina di coppie `<attributeID>`/`<value>` che devi zippare tu per capire quale valore appartiene a quale campo. I valori tornano come stringhe non tipate — nessuno schema, nessuna annotazione di tipo. Ti arrangi tu a capire se `"1"` è un intero, un booleano o una stringa.

Mandare dati indietro è in realtà meglio — il server si aspetta che ogni `<value>` porti un'annotazione `xsi:type` (`xsd:unsignedInt`, `xsd:dateTime`, `xsd:boolean`). Avere i tipi sul write path è sano. Quello che non è sano è l'asimmetria: niente tipi in ingresso, tipi in uscita. E i tipi stessi non sono nel WSDL — sono definiti solo nella documentazione e nel codice del server. Il WSDL descrive la struttura (una lista di elementi attributo generici) senza dire quale tipo debba avere ciascun attributo. Come dice il [commento-sfogo nel sorgente](https://github.com/vjt/identikey/blob/master/lib/identikey/base.rb#L259): *"This code should not exist, because defining argument types is what WSDL is for."*

Il read path non tipato rompe anche il tooling standard. Il log filtering integrato di Savon funziona sui nomi degli elementi. Gli dici "filtra l'elemento `<password>`" e redige il valore. Ma non c'è nessun elemento `<password>`. C'è un `<attributeID>` con testo `CREDFLD_PASSWORD` e un `<value>` fratello con la password effettiva. I filtri standard non sanno esprimere "trova l'elemento `<value>` che è fratello di un `<attributeID>` il cui testo è questa specifica stringa".

Così la gemma implementa il [filtering basato su XPath](https://github.com/vjt/identikey/blob/master/lib/identikey/base.rb#L60):

```ruby
def self.identikey_filter_proc_for(attribute)
  lambda do |document|
    document.xpath("//attributeID[text()='#{attribute}']/../value").each do |node|
      node.content = '***FILTERED***'
    end
  end
end
```

Sali dall'`<attributeID>` al suo parent, poi riscendi al `<value>` fratello, e lo blanki. I [filtri di default](https://github.com/vjt/identikey/blob/master/lib/identikey/base.rb#L68) usano la convenzione del prefisso `identikey:` per distinguere questi dai filtri standard Savon:

```ruby
filters: [
  'sessionID',
  'staticPassword',
  'identikey:CREDFLD_PASSWORD',
  'identikey:CREDFLD_STATIC_PASSWORD',
  'identikey:CREDFLD_SESSION_ID'
]
```

Filtri Savon standard e filtri XPath custom, coesistenti nella stessa lista. Il metodo [`process_identikey_filters`](https://github.com/vjt/identikey/blob/master/lib/identikey/base.rb#L46) li separa in fase di inizializzazione e converte quelli `identikey:` in lambda proc. Funziona. Non dovrebbe dover esistere.

### Quando il successo non è successo

{{< figure src="soap-paradox.jpg" alt="Una maschera teatrale a due facce, una metà verde con un segno di spunta, l'altra metà rossa con simboli di avvertimento" >}}

L'API di Authentication ha una bellissima trappola per gli incauti. Chiami `auth_user` con username e OTP, ti torna un codice di stato. `STAT_SUCCESS` significa che l'autenticazione è passata, qualsiasi altro codice significa che non lo è. Semplice, no?

No, se stai usando push OTP.

Con le notifiche push, il server manda una challenge al telefono dell'utente. Se l'utente non ha ancora risposto — o se la password è sbagliata — il server ritorna `STAT_SUCCESS` comunque, ma infila un messaggio "password is wrong" nell'attributo `CREDFLD_STATUS_MESSAGE`. Il codice di stato mente. L'errore si nasconde in un campo opzionale che devi sapere di cercare.

Il metodo [`otp_validated_ok?`](https://github.com/vjt/identikey/blob/master/lib/identikey/authentication.rb#L54) codifica questa conoscenza guadagnata a caro prezzo:

```ruby
# For all cases, except where the OTP is "push", Identikey returns a
# status that is != than `STAT_SUCCESS`. But when the OTP is "push",
# then Identikey returns a `STAT_SUCCESS` with a "password is wrong"
# message in the `CREDFLD_STATUS_MESSAGE`.
#
# This method checks for both cases.. Success means a `STAT_SUCCESS`
# and nothing in the `CREDFLD_STATUS_MESSAGE`.
#
def self.otp_validated_ok?(status, result)
  status == 'STAT_SUCCESS' && !result.key?('CREDFLD_STATUS_MESSAGE')
end
```

Successo significa `STAT_SUCCESS` *e l'assenza di un messaggio d'errore*. Non la presenza di un messaggio di successo — l'assenza di un messaggio di fallimento. La distinzione conta. Senza questo check, l'autenticazione push OTP "ha successo" silenziosamente quando non dovrebbe, il tipo di bug di sicurezza che ti tiene sveglio la notte.

L'API pubblica espone questo in due forme — [`valid_otp?`](https://github.com/vjt/identikey/blob/master/lib/identikey/authentication.rb#L27) per check booleani e [`validate!`](https://github.com/vjt/identikey/blob/master/lib/identikey/authentication.rb#L32) per validazione che solleva eccezione. Entrambi passano per lo stesso gate `otp_validated_ok?`.

### Attributi tipati

Il metodo [`typed_attributes_query_list_from`](https://github.com/vjt/identikey/blob/master/lib/identikey/base.rb#L268) lascia che i chiamanti passino valori Ruby semplici — un `Integer`, un `Time`, una `String` — e li serializza nell'XML annotato `xsi:type` che il server si aspetta. Passa il tipo sbagliato e ti torna indietro un SOAP fault:

```ruby
def self.typed_attributes_query_list_from(hash)
  hash.map do |full_name, value|

    parse = /^(not_)?(.*)/i.match(full_name.to_s)
    name  = parse[2]

    options = {}
    options[:negative] = true if !parse[1].nil?

    type, value = case value

    when Unsigned
      [ 'xsd:unsignedInt', value.to_s ]

    when Integer
      [ 'xsd:int', value.to_s ]

    when Time
      [ 'xsd:dateTime', value.utc.iso8601 ]

    when TrueClass, FalseClass
      [ 'xsd:boolean', value.to_s ]

    when Symbol, String
      [ 'xsd:string', value.to_s ]

    when NilClass
      options[:null] = true
      [ 'xsd:string', '' ]

    else
      raise Identikey::UsageError, "#{full_name} type #{value.class} is unsupported"
    end

    { attributeID:      name,
      attributeOptions: options,
      value: { '@xsi:type': type, content!: value } }
  end.compact
end
```

Nota il tipo `Unsigned` nel `case`. L'`Integer` di Ruby mappa a `xsd:int`, ma OneSpan usa `xsd:unsignedInt` per certi campi come `CREDFLD_PASSWORD_FORMAT`. La gemma porta con sé una classe wrapper [`Unsigned`](https://github.com/vjt/identikey/blob/master/lib/identikey/unsigned.rb) che estende `BasicObject` e delega tutto all'intero sottostante, esistendo solo come type tag per il layer di serializzazione. Un'intera classe, affinché `case value; when Unsigned` possa scegliere il tipo XSD giusto.

### Ricerca

Attraverso tutta la gemma mi sono sforzato di presentare un'interfaccia Rubyesca — qualcosa che segua il principio della minima sorpresa e sembri familiare a chiunque abbia lavorato con ActiveRecord o librerie Ruby simili. L'interfaccia di search dell'API Administration è un buon esempio. Sotto il cofano è la stessa machinery `<attributeID>`/`<value>`, ma a livello chiamante si presenta così:

```ruby
# Find locked users in a domain
session.search_users(domain: 'master', locked: true)

# Find expired tokens of a specific type
session.search_digipasses(expired: true, type: 'DP4MOBILE')

# Find users who do NOT have a token assigned
session.search_users(not_has_digipass: true)
```

La gemma traduce questi hash Ruby nel formato attributo di OneSpan. `domain: 'master'` diventa `{attributeID: 'USERFLD_DOMAIN', value: {'@xsi:type': 'xsd:string', content!: 'master'}}`. `locked: true` diventa `{attributeID: 'USERFLD_LOCKED', value: {'@xsi:type': 'xsd:boolean', content!: 'true'}}`. Il metodo [`search_attributes_from`](https://github.com/vjt/identikey/blob/master/lib/identikey/base.rb#L312) mappa chiavi amichevoli a nomi di attributo OneSpan via una [mappa attributi per modello](https://github.com/vjt/identikey/blob/master/lib/identikey/administration/user.rb#L15) (`'domain' => 'USERFLD_DOMAIN'`, `'email' => 'USERFLD_EMAIL'`, ecc.), e il prefisso `NOT_` ti regala la negazione gratis — nessuna API speciale necessaria.

### Stranezze enterprise

La classe [Session](https://github.com/vjt/identikey/blob/master/lib/identikey/administration/session.rb) gestisce l'autenticazione verso l'API Administration, e deve supportare due modalità completamente diverse per due use case diversi.

Modalità classica: un amministratore umano che gestisce token e utenti attraverso l'API. Username e password, chiami `logon`, ottieni un session ID, lo usi per le chiamate successive, chiami `logoff` quando hai finito. Ciclo di vita di sessione standard.

Modalità API key: un service account che esegue verifica OTP in modo programmatico. Quando la tua applicazione deve validare l'OTP di un utente, non ha — e non dovrebbe avere — credenziali interattive. Il session ID è `"Apikey #{username}:#{apikey}"`, un token sintetico che la gemma costruisce localmente. Gli utenti di servizio saltano del tutto la danza logon/logoff:

```ruby
def initialize(username:, password: nil, apikey: nil, domain: 'master')
  if password.nil? && apikey.nil?
    raise Identikey::UsageError, "Either a password or an API Key is required"
  end

  @client = Identikey::Administration.new

  @username = username
  @password = password
  @domain   = domain

  if apikey
    @service_user = true
    @session_id = "Apikey #{username}:#{apikey}"
  end
end
```

Le due modalità richiedono paraurti. Gli utenti classici devono fare logon prima di qualunque cosa; gli utenti di servizio non devono mai chiamare logon (fallirebbe). I metodi [`require_classic_user!`](https://github.com/vjt/identikey/blob/master/lib/identikey/administration/session.rb#L150) e [`require_logged_on!`](https://github.com/vjt/identikey/blob/master/lib/identikey/administration/session.rb#L144) lo impongono ai confini giusti.

Poi ci sono i privilegi. Quando un utente classico fa logon, il server ritorna i suoi privilegi come una stringa separata da virgole: `"PRIV_REPORT true, PRIV_USER_ADMIN true, PRIV_DIGIPASS_ADMIN false"`. Non XML. Non JSON. Neppure coppie chiave-valore in un formato riconoscibile. Solo una stringa piatta con virgole tra le entry di privilegio e spazi tra il nome e il suo valore booleano.

Il [parsing](https://github.com/vjt/identikey/blob/master/lib/identikey/administration/session.rb#L156) è lugubremente lineare:

```ruby
def parse_privileges(privileges)
  privileges.split(', ').inject({}) do |h, priv|
    privilege, status = priv.split(' ')
    h.update(privilege => status == 'true')
  end.freeze
end
```

Split su virgola-spazio, split di ogni pezzo su spazio, confronta la seconda metà con la stringa `"true"`. Questo è il tipo di codice che scrivi quando l'idea che ha il vendor di "dati strutturati" è "concatena qualche stringa e spera per il meglio". Funziona, è testato ed è un monumento alla distanza tra il marketing "enterprise-grade" e l'ingegneria enterprise-grade.

### CRONTO: criptogrammi visivi

L'API [Provisioning](https://github.com/vjt/identikey/blob/master/lib/identikey/provisioning.rb) gestisce l'enrollment dei device — registrare app mobili per autenticazione basata su notifiche push. Wrappa due design di API incompatibili in un solo modulo: il vecchio stile `provisioningExecute` con le stesse coppie generiche `<attributeID>`/`<value>` del resto dell'API, e il più recente `dsappSRPRegister` con response WSDL correttamente tipate. Il [layer di parsing](https://github.com/vjt/identikey/blob/master/lib/identikey/provisioning.rb#L104) rileva quale formato è tornato e li gestisce entrambi in modo trasparente — perché, ovviamente, OneSpan non poteva degnarsi di tenere la propria API consistente tra gli endpoint.

Il premio è l'attivazione [CRONTO](https://www.onespan.com/products/transaction-signing/cronto). CRONTO è la tecnologia di criptogrammi visivi di OneSpan — non un normale QR code in bianco e nero, ma una matrice di pallini colorati che codifica dati cifrati. Rosso, verde, blu — un barcode a colori che l'utente scansiona con la fotocamera del telefono o con un device DIGIPASS dedicato per decodificare i dettagli di una transazione o completare l'enrollment.

{{< figure src="cronto.png" alt="Criptogramma visivo CRONTO — una matrice di pallini colorati" caption="Un criptogramma visivo CRONTO. [Fonte: documentazione Airlock IAM](https://docs.airlock.com/iam/latest/index/1579527945336.html)." >}}

Il class method [`cronto_code_for_srp_registration`](https://github.com/vjt/identikey/blob/master/lib/identikey/provisioning.rb#L67) mette tutto insieme. Chiama la registrazione SRP, compone una stringa di attivazione proprietaria con un header fisso e campi delimitati da punto e virgola, poi la esadecimalizza carattere per carattere nel formato che un renderer di immagini CRONTO si aspetta:

```ruby
def self.cronto_code_for_srp_registration(gateway:, **kwargs)
  status, result, error = new.dsapp_srp_register(**kwargs)

  if status != 'STAT_SUCCESS'
    raise Identikey::OperationFailed,
      "Error while assigning DAL: #{status} - #{[error].flatten.join('; ')}"
  end

  message = '01;01;%s;%s;%s;%s;%s' % [
    result[:user][:user_id],
    result[:user][:domain],
    result[:registration_id],
    result[:activation_password],
    gateway
  ]

  return message.split(//).map {|c| '%x' % c.ord}.join
end
```

La stringa esadecimale alimenta una gemma companion che renderizza la matrice di pallini colorati come PNG, consegnata agli utenti durante l'enrollment via notifica push. Il prefisso `01;01;`, i punto e virgola, la codifica esadecimale per-carattere — niente di tutto questo è nella documentazione pubblica. Il formato CRONTO è proprietario, la codifica è proprietaria, e l'unico modo per farla giusta è matchare l'implementazione di riferimento di OneSpan byte per byte.

[vacman_controller](https://github.com/vjt/vacman_controller) e [identikey](https://github.com/vjt/identikey) sono su GitHub. L'autenticazione 2FA hardware non dovrebbe richiedere un SDK Java o un manuale da fax. Continua a non richiederlo.


---

**Open source dagli anni IFAD:** [ChronoModel](/it/posts/2012-05-07-chronomodel-time-travel-postgresql/) (2012) • [data-confirm-modal](/it/posts/2013-07-02-data-confirm-modal/) (2013) • [Hermes](/it/posts/2013-10-20-hermes-rails-rumble-2013/) (2013) • [Eaco](/it/posts/2015-02-28-eaco-authorization-ruby/) (2015) • [Heathen → Colore](/it/posts/2016-01-15-document-pipeline-heathen-colore/) (2016) • [TM → Pontoon](/it/posts/2018-02-14-translation-memory-pontoon/) (2018) • [ChronoModel 1.0](/it/posts/2019-04-06-chronomodel-one-dot-zero/) (2019) • **OneSpan 2FA (2020)** • [ansible-wsadmin](/it/posts/2026-04-11-ansible-wsadmin/) (2026)
