---
title: "Odissea 10.5.2: un piccolo viaggio tra i servizi e componenti di Mac OS X"
date: 2008-02-15
tags: [apple, backup, macos]
---


Beh, sono davvero contento di OSX 10.5.2. Anche se non sono uno di quelli che
ha insultato Apple per la barra dei menu traslucida che a tutti fa schifo...
anzi, a me piace. Non mi interessa il tool di TM nella barra dei menu, perché
non ho (ancora) comprato la fighissima Time Capsule, mi piace lo spinner nel
menu Airport e, soprattutto, apprezzo molto gli aggiornamenti al
`BluetoothSCOAudioDriver.kext` che pilota il mio auricolare bluetooth.

Spotlight sembra anche più veloce ad ogni aggiornamento, e sono un utente
pesante di Spotlight, quindi questo mi rende davvero felice. Grazie ingegneri
Apple!

Ma torniamo al tema: perché odissea? Perché seguendo i [miei consigli sulla
batteria](/posts/2008-01-31-how-to-keep-your-apple-notebook-battery-healthy/),
sono riuscito a far SPEGNERE il mio MacBook2,1 mentre era al 74% della fase
"Scrittura file" del combo update... risultato: un sistema completamente
distrutto, come ogni geek potrebbe immaginare :). Apple aveva aggiornato
alcune librerie, e al riavvio semplicemente niente funzionava, e la console
Darwin era piena di **tonnellate** di messaggi di errore.

Il tipico fanb^Wutente Apple avrebbe semplicemente archiviato e reinstallato
il sistema, ma ehi, io sono un geek orgoglioso! So per esperienza che le
situazioni di disaster recovery sono le migliori per imparare qualcosa su un
sistema operativo, perché devi aiutare il sistema ad avviarsi, tirando su i
servizi a mano, e trovare un modo per riapplicare il combo update senza usare
la comoda interfaccia Aqua.

Per fortuna, su OSX ogni GUI ha la sua controparte CLI, seguendo le migliori
"linee guida UNIX" di separazione degli interessi e architettura ben
progettata. Inoltre, OSX porta questo approccio un passo avanti, seguendo i
migliori principi di ingegneria del software, dove le funzionalità sono
implementate nei Framework e sia la GUI che la CLI le utilizzano. Ben fatto!

L'odissea è iniziata con un `CMD-S` per avviare in single user mode, un
`/sbin/fsck -fy`, e un `/sbin/mount -uw /` per avere la root in scrittura. Ho
provato direttamente con un `hdiutil attach -noverify -verbose -mount required
/Users/vjt/Downloads/MacOSXUpdCombo10.5.2.dmg` per montare la disk image
dell'aggiornamento, ma è fallito perché il demone `diskarbitrationd` non era
in esecuzione.

Allora ho lanciato `launchctl` e dato `load
/System/Librar/LaunchDaemons/com.apple.diskarbitrationd.plist`, scoprendo che
servivano sia il demone `configd` che il demone `notifyd`, quindi li ho
caricati entrambi via launchctl e... **YAY**! La disk image era montata
correttamente in `/Volumes/Mac OS X Update Combined`!

Qui le cose hanno cominciato a complicarsi un po', perché un compito
apparentemente semplice come lanciare `installer -package
MacOSXUpdCombo10.5.2.pkg -target /` è fallito con

> `NSInvalidArgumentException in [IFRunnerProxy
> requestKeyForRights:askUser:] unrecognized selector sent to instance
> 0x79ac50.`

Beh, qui il metodo Objective-C era piuttosto autoesplicativo: l'installer
stava cercando di chiedere all'utente il permesso di installare il pacchetto.
Abbastanza strano, dato che stavo eseguendo il comando `installer` come root,
quindi nessuna richiesta avrebbe dovuto essere fatta.

Ho iniziato a grattarmi la testa, e ho pensato ai `DirectoryServices`, forse
visto che non erano disponibili stava succedendo "qualcosa di
sbagliato"(tm)?

OK, proviamo a iniettare la property list di `com.apple.DirectoryServices` in
`launchd`... non ha funzionato e `dyld` ha sputato fuori questo illuminante
messaggio di errore:

> `com.apple.DirectoryServices[11980]: dyld: lazy symbol binding failed: Symbol
> not found: _res_interrupt_requests_enable voyager
> com.apple.DirectoryServices[11980]: Referenced from:
> /usr/sbin/DirectoryService com.apple.DirectoryServices[11980]: Expected in:
> /usr/lib/libresolv.9.dylib`

**ARGH**! Qualcosa era cambiato nella libresolv! Avevo i DirectoryServices
della 10.5.1... con la libresolv della 10.5.2! Bisognava ripristinare la
vecchia versione per far funzionare DS. Ho provato prima con una copia di rete
grezza via `netcat` da un'altra macchina 10.5.1, ma con mia sorpresa il
three-way handshake non veniva completato tra i due endpoint, quindi nessun
dato poteva essere trasferito. Pfui.

Ma per fortuna, avendo già avviato il demone `diskarbitration`, potevo
semplicemente mettere la libreria su un dispositivo di storage **USB**,
collegarlo e farlo montare in /Volumes. Ha funzionato e i Directory Services
erano attivi e funzionanti... ma sempre lo stesso maledetto errore
`NSInvalidArgumentException` quando lanciavo il comando `installer`. Sigh. :(

A questo punto ho mollato perché il mio viaggio era stato abbastanza
interessante e avevo un modo molto più comodo per risolvere il problema: un
hard disk collegato via **USB** con un'installazione vanilla di Leopard, da cui
potevo avviare il mio MacBook, fare doppio click sulla disk image dal Finder e
pigramente lanciare un `installer -target /Volumes/disk0 -package /Volumes/Mac
OS X Update Combined/MacOSXUpdCombo10.5.2.pkg` per rieseguire tutte le
procedure di aggiornamento che avrebbero sistemato la mia installazione di
Leopard. Quindi ho seguito questa strada, perché avevo del lavoro da fare e non
potevo perseverare nel mio viaggio geek con la console Darwin, anche se era
stato davvero divertente. :)

Dopo che l'installer ha completato il suo lavoro, ho riavviato e un fiammante
10.5.2 mi ha accolto con la solita finestra di login di Mac **OS X** che sulla
mia macchina sfoggia lo slogan "All your base are belong to us" ;).

Spero che questo viaggio vi sia piaciuto come è piaciuto a me, e se sei un
fanb^Wutente Linux non sottovalutare la pulizia e l'ingegnosità di Mac **OS X**
che ogni geek Apple cerca di condividere con te!
