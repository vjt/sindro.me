(function() {
  var lastBoot = localStorage.getItem('boot-done');
  if (lastBoot && (Date.now() - Number(lastBoot)) < 86400000) {
    var splash = document.getElementById('boot-splash');
    if (splash) splash.remove();
    return;
  }

  var splash = document.getElementById('boot-splash');
  if (!splash) return;

  var hostname = splash.getAttribute('data-hostname') || 'localhost';
  var tagline = splash.getAttribute('data-tagline') || 'ready.';

  var defaultLines = [
    { cls: 'info', text: '[    0.000000] Linux version 6.12.75+rpt-rpi-2712 (gcc 12.2.0)' },
    { cls: '',     text: '[    0.000014] Command line: BOOT_IMAGE=/vmlinuz root=/dev/nvme0n1p2 ro quiet' },
    { cls: 'ok',   text: '[    0.031201] CPU: ARMv8 Cortex-A76 [410fd083] revision 3 (ARMv8), cr=30c5383d' },
    { cls: '',     text: '[    0.068442] Machine model: Raspberry Pi 5 Model B Rev 1.0' },
    { cls: '',     text: '[    0.102887] Memory: 8192MB/8192MB available (16384K kernel code)' },
    { cls: 'ok',   text: '[    0.148201] Calibrating delay loop (skipped), value calculated using timer frequency' },
    { cls: '',     text: '[    0.203118] pid_max: default: 32768 minimum: 301' },
    { cls: '',     text: '[    0.261003] Mount-cache hash table entries: 32768 (order: 6, 262144 bytes)' },
    { cls: 'ok',   text: '[    0.312556] NET: Registered PF_INET protocol family' },
    { cls: '',     text: '[    0.401223] TCP: Hash tables configured (established 65536 bind 65536)' },
    { cls: 'ok',   text: '[    0.468910] clocksource: Switched to clocksource arch_sys_counter' },
    { cls: '',     text: '[    0.521887] EXT4-fs (nvme0n1p2): mounted filesystem with ordered data mode. Quota mode: none.' },
    { cls: 'ok',   text: '[    0.612003] systemd[1]: Detected architecture arm64.' },
    { cls: '',     text: '[    0.681234] systemd[1]: Hostname set to <' + hostname + '>.' },
    { cls: 'ok',   text: '[    0.742891] systemd[1]: Started nginx - high performance web server.' },
    { cls: 'ok',   text: '[    0.801445] hugo[1337]: Building sites...' },
    { cls: '',     text: '[    0.823001] hugo[1337]:                    | EN  | IT' },
    { cls: '',     text: '[    0.824100] hugo[1337]:   -------------------+-----+-----' },
    { cls: '',     text: '[    0.825003] hugo[1337]:   Pages            |  87 |  85' },
    { cls: '',     text: '[    0.825890] hugo[1337]:   Static files     | 142 | 142' },
    { cls: 'ok',   text: '[    0.831002] hugo[1337]: Total in 91 ms' },
    { cls: 'warn', text: '[    0.900000] init: blog ready. ' + tagline },
  ];

  var customLines = splash.getAttribute('data-lines');
  var lines;
  if (customLines) {
    try { lines = JSON.parse(customLines); }
    catch (e) { lines = defaultLines; }
  } else {
    lines = defaultLines;
  }

  var log = document.getElementById('boot-log');
  var brand = document.getElementById('boot-brand');
  if (!log) return;

  var i = 0;
  var interval = 3000 / (lines.length + 8);

  function nextLine() {
    if (i >= lines.length) {
      if (brand) brand.classList.add('visible');
      setTimeout(function() {
        splash.classList.add('fade-out');
        setTimeout(function() {
          splash.remove();
        }, 600);
        localStorage.setItem('boot-done', Date.now());
      }, 500);
      return;
    }
    var line = lines[i];
    var div = document.createElement('div');
    if (line.cls) div.className = line.cls;
    div.textContent = line.text;
    log.appendChild(div);
    i++;
    setTimeout(nextLine, interval + (Math.random() * 40 - 20));
  }

  nextLine();
})();
