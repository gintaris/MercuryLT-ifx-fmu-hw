# IMU kalibravimo kubas

Parametrinis FreeCAD skriptas `calib_cube.py` sukuria kubo formos laikiklį plokštei su IMU. Kubo išorinės sienos plokščios ir tarpusavyje statmenos, o plokštės ašys lygiagrečios sienoms. Taip galima tiksliai atlikti akselerometro kalibravimą 6 padėtimis (NuttX `imucal`) ir palyginti kelis plokščių egzempliorius.

| Variantas | Plokštė | Kubas (su numatytais matmenimis) |
|---|---|---|
| `psc3_rab7` | KIT_PSC3M5_EVK su Rutronik RAB7-SENSORFUSION skydu | 148,3 mm |
| `pse84` | KIT_PSE84_AI | 102,6 mm |

Kubą sudaro dvi dalys:
- **pagrindas** – atvira dėžė su U išpjova USB kabeliui. Dugnas lygus: plokštė stovi ant savo guminių kojelių. Aplink PCB kontūrą yra XY centravimo bėgeliai;
- **dangtis** su centravimo bortu, prisukamas 4 varžtais M3. Po dangčiu nuo sienos iki sienos eina standžios briaunos, kurios nusileidžia iki 3 mm virš plokščių rinkinio viršaus. Iš jų žemyn eina trumpi prispaudimo vamzdeliai (Ø12/8 mm) su putplasčio pagalvėlėmis: jie švelniai prispaudžia plokštę Z kryptimi.

Plokštė **neprisukama**. Jos guminių kojelių vietos nesvarbios: XY padėtį laiko bėgeliai.

Abi dalys spausdinamos be atramų.

## Būsena

- **FreeCAD versija:** 1.0 arba naujesnė; tikslinė versija – naujausia stabili.
- **Naudojami moduliai:** tik standartiniai FreeCAD moduliai `Part` ir `Mesh`. Išorinių Python paketų nereikia.
- **Kas išbandyta:** skriptas paleistas su FreeCAD 1.2.0 (`freecadcmd`, Windows) abiem variantais. Taip pat išbandytas įklijavimas į konsolę (be `__file__`). Visos 4 dalys sugeneruotos kaip taisyklingi vientisi kietieji kūnai, STEP ir STL failai įrašyti.
- **Kas neišbandyta:**
  - FreeCAD GUI (*Macro → Execute*) kitame kompiuteryje;
  - kitos FreeCAD versijos;
  - spausdinimas;
  - `pse84` matmenys – įvertinimai (`MEASURE`), žr. 2 skyrių.

## 1. Paruošimas

1. Įdiegti naujausią stabilią FreeCAD versiją (https://www.freecad.org/downloads.php).
2. Nusikopijuoti šį katalogą (`fixtures/calib-cube/`) arba vien failą `calib_cube.py`, pvz., į `C:\calib-cube\`.
3. Atidaryti `calib_cube.py` teksto redaktoriumi (arba FreeCAD makrokomandų redaktoriumi) ir nustatyti parametrus (2 skyrius).

## 2. Parametrai

Visi parametrai yra skripto viršuje.

**Pasirinkimas ir išvestis**

- `VARIANT` – `"psc3_rab7"` arba `"pse84"`.
- `OUTPUT_DIR` – kur rašyti failus:
  - tuščias (`""`) – į aplanką `out` šalia skripto;
  - jei skriptas įklijuotas į Python konsolę – į `calib_cube_out` vartotojo namų kataloge;
  - pilnas kelias (pvz., `"C:/Users/aš/Desktop/kubas"`) naudojamas tiesiogiai.

**Plokštės matmenys (`VARIANTS`).** Visos padėtys pateikiamos plokštės koordinatėmis: pradžia – plokštės kampas (−Xc, −Yc), žiūrint iš detalių pusės; x eina išilgai ilgosios kraštinės.

| Parametras | Kas tai |
|---|---|
| `board_l`, `board_w`, `board_t` | plokštės ilgis (ilgoji kraštinė), plotis, storis, mm |
| `stack_h` | visas aukštis nuo kojelių apačios iki aukščiausio taško (PSC3 – RAB7 lizdų viršus) |
| `foot_h` | guminių kojelių aukštis |
| `press` | prispaudimo taškai (x, y, paviršius): `"pcb"` – EVK PCB viršus (`foot_h` + `board_t`), `"rab7"` – RAB7 PCB viršus (`stack_h` − `rab7_socket_h`); tik plika PCB vieta, ne detalės ar lizdai |
| `rab7_socket_h` | RAB7 lizdų aukštis virš RAB7 PCB (8,50 mm pagal STEP, `MEASURE`) |
| `feet` | kojelių vietos – tik dokumentacijai; kišenės daromos tik jei `foot_pocket_depth` > 0 |
| `rail_skip` | bėgelių atkarpos, kurių nedaryti (pvz., ties išsikišusia jungtimi) |
| `footprint` | už plokštės kontūro išsikišančių dalių (skydo) stačiakampiai (x0, y0, x1, y1) |
| `usb_wall` | siena su KitProg3 USB-C: `"-Xc"`, `"+Xc"`, `"-Yc"`, `"+Yc"` |
| `usb_at` | USB centras išilgai tos sienos (plokštės koordinatėmis) |
| `usb_w` | kabelio kištuko plotis su atsarga |
| `usb_z` | USB jungties centro aukštis virš plokštės |
| `labels` | kokia ašies etiketė graviruojama ant kiekvienos sienos |

**`psc3_rab7` – iš gamintojų projektavimo duomenų.** Šaltinis nurodytas komentaru prie kiekvieno skaičiaus skripte. Patys gamintojų failai į git nededami (licencija; `.gitignore`).

| Dydis | Reikšmė | Šaltinis |
|---|---|---|
| EVK kontūras | 130,00 × 70,00 mm, kampai R2,54 | Infineon `KIT_PSC3M5_EVK_Rev5.0_artwork.pdf` (1:1, silkscreen top); mastelis patikrintas pagal 2,54 mm jungčių žingsnį |
| Viso rinkinio aukštis | `stack_h` = 29 mm nuo kojelių apačios iki RAB7 viršaus | vartotojo matavimas 2026-11-19 |
| Guminės kojelės | 4 vnt., ~Ø8 mm, 5 mm aukščio (`foot_h`), netoli kampų, ne PCB skylėse | vartotojo matavimas ir nuotraukos |
| KitProg3 USB-C (J15) | dešinė trumpoji kraštinė, centras y = 29,85 mm | ten pat, J15 aikštelės; tipas – BOM (Würth 629722000214) |
| Arduino lizdai J1–J4 | 8,5 mm aukščio, eilės 48,30 mm atstumu | BOM (Würth 61300811821 / 61301011821); artwork |
| RAB7 plokštė | 72,30 × 71,78 × 1,64 mm; pagal geometriją ant EVK x 46,19–118,49, y −0,95–70,83 (išsikiša ~0,95 mm už abiejų ilgųjų kraštinių). Nuotraukose atrodo daugiau, todėl `footprint` padidintas +3 mm (`MEASURE`) | Rutronik `RAB7-SENSORFUSION_PCB.step`, Mechanical Drawing; nuotraukos |
| DC jungtis J20 | USB kraštinės kampe, išsikiša už krašto; vieta 3 mm (`MEASURE`), toje vietoje bėgelio nėra | BOM (PJ-102A), nuotraukos |
| Skydo viršus virš EVK | pagal detales 8,5 + 1,64 + 8,50 = 18,64 mm; pagal matavimą 29 − 5 − 1,6 = 22,4 mm. Naudojamas matavimas (skirtumas 3,8 mm – greičiausiai kitokio aukščio lizdai) | BOM, RAB7 STEP, matavimas |
| BMI323 (U6) | RAB7 centre, 3,0 × 2,5 mm, ilgoji pusė išilgai plokštės ilgosios kraštinės | RAB7 STEP |
| Prispaudimo taškai | Vamzdeliai Ø12 mm. 4 ant RAB7 PCB viršaus (`stack_h` − `rab7_socket_h`): ilgųjų kraštinių viduriai (≥ 6,5 mm iki detalės ar lizdo) ir šonų taškai (≥ 16 mm). RAB7 kampuose yra detalės (BMP585, SHT40, kondensatoriai). Dar 2 ant EVK PCB mikroBUS gale, kurio skydas nedengia: (25,0; 35,0) ir (4,5; 32,5), ≥ 6,6 mm iki bet kokios aikštelės ar silkscreen. Potenciometras, DC jungtis ir Arduino lizdų eilės nespaudžiami | RAB7 STEP, EVK artwork |

**Ką išmatuoti (`MEASURE`) prieš spausdinant `psc3_rab7`:**
- `footprint` – kiek RAB7 sparnai (BMP585 ir DPS368 pusėje) ir DC jungtis išsikiša už EVK kraštų. Dabar numatyta +3 mm, su atsarga;
- `rail_skip` – USB sienoje praleistos bėgelio atkarpos: DC jungtis (y 0–13 mm) ir 10 kontaktų derinimo jungtis J11 šalia USB-C (y 38–58 mm). Liko atkarpos y 13–22,85 ir 58–66 mm;
- `rab7_socket_h` – RAB7 lizdų aukštis virš RAB7 PCB (8,50 mm). Nuo jo priklauso, kur remiasi RAB7 vamzdeliai;
- `foot_h` (5 mm) ir `board_t` (1,6 mm).

Aukščiai skaičiuojami nuo kojelių apačios, todėl visas aukštis lieka `stack_h`.

**`pse84` – visi matmenys yra įvertinimai (`MEASURE`).** Turimas Infineon PDF (630-60751-01) yra tik schema, be išdėstymo duomenų. Prieš spausdinant išmatuoti plokštę slankmačiu arba gauti KIT_PSE84_AI PCB design data paketą.

**Bendri (`COMMON`)**

| Parametras | Kas tai |
|---|---|
| `wall` | sienos, dugno ir dangčio storis (numatyta 6 mm) |
| `clearance` | tarpas aplink plokštę |
| `fit_tol` | FDM tolerancija dangčio bortui (0,2–0,3 mm) |
| `rail_w`, `rail_clear`, `rail_above`, `rail_corner_gap` | bėgelių storis (2 mm), tarpas iki PCB krašto (0,3 mm), aukštis virš PCB (1 mm), atstumas nuo PCB kampų (4 mm) |
| `foot_pocket_depth`, `foot_pocket_clear` | neprivalomos kojelių kišenės dugne (numatyta 0 – lygus dugnas) |
| `press_d`, `press_bore` | prispaudimo vamzdelio išorinis ir vidinis skersmuo (12 / 8 mm; 0 – pilnas kaištis) |
| `foam_t` | tarpas putplasčio pagalvėlei vamzdelio gale (3 mm) |
| `rib_t`, `rib_gap` | briaunų storis (4 mm) ir tarpas nuo rinkinio viršaus iki briaunų apačios (3 mm) |
| `lid_*` | dangčio varžtai M3 |
| `label_*` | etikečių dydis ir gylis |
| `fonts` | šriftų failų sąrašas; pirmas rastas naudojamas etiketėms |

## 3. Paleidimas

Galimi trys būdai, visi duoda tą patį rezultatą.

**A. FreeCAD GUI, makrokomanda (rekomenduojama)**

1. *Macro → Macros…*.
2. „User macros location“ nurodyti aplanką su `calib_cube.py` (arba nukopijuoti failą į rodomą aplanką).
3. Pasirinkti `calib_cube.py` ir spausti *Execute*.
4. Po kelių sekundžių atsiranda naujas dokumentas `calib_cube_<variantas>` su objektais `Base` ir `Lid`.

**B. Python konsolė**

1. *View → Panels → Python console*.
2. Įklijuoti visą skripto tekstą ir spausti Enter. Prieš įklijuojant galima pakeisti `VARIANT` ir `OUTPUT_DIR`.

**C. Komandinė eilutė (be GUI)**

```
"C:\Program Files\FreeCAD 1.x\bin\freecadcmd.exe" calib_cube.py psc3_rab7
"C:\Program Files\FreeCAD 1.x\bin\freecadcmd.exe" calib_cube.py pse84
```

Linux ir macOS: `freecadcmd calib_cube.py pse84`.

## 4. Rezultatas ir kaip atpažinti sėkmę

Failai rašomi į `<OUTPUT_DIR arba out>/<variantas>/`:

```
calib_cube_<variantas>_base.step   calib_cube_<variantas>_base.stl
calib_cube_<variantas>_lid.step    calib_cube_<variantas>_lid.stl
```

**Sėkmė.** Report view arba konsolėje (*View → Panels → Report view*) matomos eilutės:

```
KIT_PSC3M5_EVK + RAB7-SENSORFUSION: cube 148.3 mm, inner 136.3 mm; above the outside bottom: feet 6.0, PCB top 12.6, stack top 35.0, lowest tube end 15.6 mm; font C:/Windows/Fonts/arialbd.ttf
written to ...\out\pse84
DONE
```

Aplanke yra 4 failai. STL atidarius slicer'yje matomas kubo pagrindas su graviruotomis etiketėmis šonuose ir apačioje bei plokščias dangtis su etikete „+Z“.

**Nesėkmė**

| Ką matote | Ką tai reiškia, ką daryti |
|---|---|
| `Traceback (most recent call last): ...` | skripto klaida. Nukopijuoti visą tekstą ir perduoti programuotojui; dažniausia priežastis – neteisingas parametras, pvz., skylė už plokštės ribų. |
| `WARNING: no font found, labels are not engraved` | kubas sukurtas be etikečių. Į `fonts` įrašyti esamo `.ttf` failo kelią. |
| `WARNING: base shape is not valid` | geometrija netaisyklinga, dažniausiai dėl persidengiančių elementų. Patikrinti parametrus (pvz., USB išpjova kerta bėgelį). |
| Nėra eilutės `DONE`, failų nėra | skriptas nepasiekė pabaigos; žiūrėti klaidą Report view. |

## 5. Ašys ir etiketės

Kubo koordinatės:
- Xc – išilgai plokštės ilgosios kraštinės;
- Yc – išilgai trumposios kraštinės;
- Zc – aukštyn (detalės ir dangtis viršuje).

Ant kiekvienos sienos išgraviruota sensoriaus ašis, kuri iš tos sienos rodo į išorę. Padėjus kubą ant sienos su etikete A, akselerometras ašyje A rodo −g. Pavyzdžiui, ant „−Z“ (normali padėtis) z ≈ +9,81 m/s².

**PSC3 + RAB7** – etiketės nustatytos pagal BMI323 bandymą 2026-11-19 ir išdėstymą:
- plokštę pastačius ant USB trumposios kraštinės, aukštyn rodo +Y. Taigi sensoriaus +Y eina išilgai **ilgosios** EVK kraštinės, nuo USB kraštinės tolyn; X eina išilgai trumposios.
- +Z rodo aukštyn per skydą.
- Ašys sudaro dešiniąją sistemą (patikrinta ir giroskopo Z ženklu). Todėl +X = Y × Z rodo į ilgąją kraštinę y = 70 mm – tą pusę, kuri, žiūrint iš viršaus su USB dešinėje, yra toliau nuo žiūrinčiojo.
- Etiketės:
  - USB sienoje „−Y“, priešingoje trumpojoje „+Y“;
  - ilgojoje kraštinėje y = 70 „+X“, priešingoje „−X“;
  - dangtyje „+Z“, apačioje „−Z“.

**PSE84** – etiketės yra prielaida (`VERIFY`).

Atspausdinus etiketes patikrinti su `sensortest accel0` ir, jei reikia, pakeisti `labels`.

## 6. Spausdinimas

- **Medžiaga ir nustatymai:** PLA arba PETG, sluoksnis 0,2 mm, 4 perimetrai, užpildas 20–30 % (gyroid).
- **Padėtis spausdintuve:**
  - pagrindas – atvira puse į viršų;
  - dangtis – etikete „+Z“ žemyn (STL failai jau orientuoti taip, kaip kubas surinktas, todėl slicer'yje dangtį reikia apversti).
- **Atramų nereikia.**
- **Po spausdinimo:** patikrinti sienų plokštumą liniuote. Jei kubas ant kurios nors sienos klibina, tą sieną lengvai nušlifuoti.
- **Briaunos ir vamzdeliai** spausdinami kartu su dangčiu, kaip vertikalios sienelės ant dangčio plokštės (atramų nereikia). Vamzdeliai trumpi: PSC3 ~8,5 mm iki RAB7 ir ~22 mm iki EVK. Briaunos yra aukštos (PSC3 ~104 mm), todėl dangtis sunkesnis. Užpildas briaunoms gali būti mažesnis.
- **Tvirtinimas:**
  - plokštė nesukama; ji stovi ant savo kojelių ant lygaus dugno, XY ją laiko bėgeliai, Z – dangčio kaiščiai;
  - ant kiekvieno vamzdelio galo priklijuoti ~3 mm putplasčio (EVA, porolono) pagalvėlę Ø12 mm (`foam_t`); ji turi būti šiek tiek suspausta, uždėjus dangtį;
  - dangtis – 4 × M3 × 12 į kampų skyles.

## 7. Naudojimas

1. Įdėti plokštę su RAB7 skydu tarp bėgelių (DC jungtis – į tarpą bėgelyje USB sienos kampe). Prijungti USB kabelį ir išvesti jį per U išpjovą. Uždėti dangtį (vamzdeliai su putplasčiu remiasi į RAB7 PCB ir EVK mikroBUS galą) ir prisukti. Patikrinti, ar plokštė nejuda.
2. NuttX konsolėje paleisti `imucal` (nuttx-apps `testing/drivers/imucal`, įjungta `kit-psc3m5-evk:sensors`).
3. Dėti kubą ant lygaus, horizontalaus paviršiaus ant programos nurodytos sienos ir spausti Enter. Kubo nejudinti, kabelio netempti.
4. Programa atspausdina:
   - akselerometro poslinkį, mastelį, ašių nesutapimą ir korekcijos matricą;
   - giroskopo poslinkį.
5. Giroskopo mastelis: padėti kubą ant patefono (33⅓ aps./min = 200 °/s) ir paleisti `imucal -t`.
