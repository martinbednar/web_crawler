OpenWPM
=======

OpenWPM je platforma umožňujúca návštevu väčšieho počtu webových stránok
za účelom vykonávania rôznych meraní na webe. V našej práci sme OpenWPM rozšírili
o upravené rozšírenie Web API Manager, pomocou ktorého detegujeme prístup
k rôznym API JavaScriptu vo webovom prehliadači. Dokumentáciu k OpenWPM
je možné nájsť na https://github.com/mozilla/OpenWPM.


Inštalácia
----------
Platformu OpenWPM môžeme nainštalovať podľa oficiálnej dokumentácie.

V našom prípade bola platforma spúšťaná na Ubuntu 18.04.

Hlavnou prerekvizitou pre inštaláciu platformy OpenWPM je prítomnosť
prostredia Conda, ktoré môže byť inštalované z nasledovného odkazu:
https://docs.conda.io/en/latest/miniconda.html

Pre inštaláciu platformy je možné spustiť skript `install.sh`, ktorý
nainštaluje prehliadač Mozilla Firefox a zostaví rozšírenie, ktoré
umožňuje zachytávať JavaScriptové volania.

Po spustení príkazu `$ ./install.sh` je potrebné aktivovať prostredie
`openwpm` spustením príkazu `$ conda activate openwpm`.

Použutie OpenWPM
----------------
V našej práci sme v rámci platformy OpenWPM implementovali dva príkazy,
`GetLinksCommand` v súbore `get_links_command.py` a `InterceptJavaScriptCommand`
v súbore `intercept_javascript_command.py`.

## Rozšírenie zoznamu tranco o podstránky
Pre rozšírenie zoznamu Tranco o podstránky môžeme použiť skript `crawl-links.py`, ktorý
prijíma tri vstupné parametre:

````
--sites={string}
--start={integer}
--length={integer}
````

Parameter `--sites={string}` určuje cestu k vstupnému súboru, ktorý obsahuje zoznam Tranco
vo formáte CSV. Parameter `--start={integer}` potom určuje index počiatku, od ktorého sa má
daný zoznam Tranco rozšíriť o zoznam podstránok. Parameter `--length={integer}` určuje dĺžku
výsledného zoznamu obohateného o podstránky. Výsledky budú zaznamenané v SQLite databáze.



## Spustenie meraní používania JavaScriptu
Pre spustenie meraní používania JavaScriptu je možné spustiť skript `crawl-javascript-apis.py`,
ktorý má nasledovné parametre:

```
--browsers={integer}
--sites={string}
--start={integer}
--offset={integer}
--ghostery
```

Parameter `--browsers={integer}` definuje maximálny počet prehliadačov, ktoré môžu byť počas 
vykonávania meraní spustené súčasne.

Parameter `--sites={string}` definuje cestu k vstupnému súboru, ktorý má štruktúru súboru `sites_to_be_visited.json`.

Parameter `--start={integer}` určuje index počiatku zoznamu webových stránok, ktoré majú byť analyzované.


Parameter `--offset={integer}` určuje počet podstránok, ktoré majú byť analyzované.

Prítomnosť parametra `--ghostery` rozhoduje o tom, či má byť dané meranie vykonávané s aktívnym doplnkom Ghostery.
