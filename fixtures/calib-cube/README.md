# IMU kalibravimo kubas

Parametrinis FreeCAD skriptas `calib_cube.py` sukuria kubo formos laikiklį plokštei su IMU. Kubo išorinės sienos plokščios ir tarpusavyje statmenos, o plokštės ašys lygiagrečios sienoms. Taip galima tiksliai atlikti akselerometro kalibravimą 6 padėtimis (NuttX `imucal`) ir palyginti kelis plokščių egzempliorius.

| Variantas | Plokštė | Kubas (su numatytais matmenimis) |
|---|---|---|
| `psc3_rab7` | KIT_PSC3M5_EVK su Rutronik RAB7-SENSORFUSION skydu | 147,6 mm |
| `pse84` | KIT_PSE84_AI | 102,6 mm |

Kubą sudaro dvi dalys:
- **pagrindas** – atvira dėžė su U išpjova USB kabeliui. Dugne yra seklios kišenės plokštės guminėms kojelėms, aplink PCB kontūrą – XY centravimo bėgeliai;
- **dangtis** su centravimo bortu, prisukamas 4 varžtais M3. Iš dangčio žemyn eina prispaudimo kaiščiai su putplasčio pagalvėlėmis: jie švelniai prispaudžia plokštę Z kryptimi.

Plokštė **neprisukama**: jos skylėse yra užklijuotos guminės kojelės.

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
| `feet` | guminių kojelių centrai (x, y) |
| `foot_d`, `foot_h` | kojelės skersmuo ir aukštis |
| `press` | prispaudimo taškai (x, y) – tik ant plikos PCB vietos, ne ant detalių ar lizdų |
| `press_z` | prispaudžiamo paviršiaus aukštis nuo kojelių apačios |
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
| Skylės kojelėms | 3 × Ø2,2 mm: (3,97; 59,84), (3,97; 9,45), (114,02; 62,69). Kojelių vietos numatytos ten; 4-oji (114,02; 9,45) – spėjimas | ten pat, soldermask top |
| Viso rinkinio aukštis | `stack_h` = 29 mm nuo kojelių apačios iki RAB7 viršaus | vartotojo matavimas 2026-11-19 |
| KitProg3 USB-C (J15) | dešinė trumpoji kraštinė, centras y = 29,85 mm | ten pat, J15 aikštelės; tipas – BOM (Würth 629722000214) |
| Arduino lizdai J1–J4 | 8,5 mm aukščio, eilės 48,30 mm atstumu | BOM (Würth 61300811821 / 61301011821); artwork |
| RAB7 plokštė | 72,30 × 71,78 × 1,64 mm; ant EVK x 46,19–118,49, y −0,95–70,83 (išsikiša ~0,9 mm už abiejų ilgųjų kraštinių) | Rutronik `RAB7-SENSORFUSION_PCB.step`, Mechanical Drawing |
| Skydo viršus virš EVK | 8,5 + 1,64 + 8,50 = 18,64 mm | BOM ir RAB7 STEP |
| BMI323 (U6) | RAB7 centre, 3,0 × 2,5 mm, ilgoji pusė išilgai plokštės ilgosios kraštinės | RAB7 STEP |
| Prispaudimo taškai | ant RAB7 PCB viršaus (`stack_h` − 8,50): ilgųjų kraštinių viduriai (≥ 6,5 mm iki artimiausios detalės) ir šonų taškai (≥ 16 mm). RAB7 kampuose yra detalės (BMP585, SHT40, kondensatoriai), todėl ten nespaudžiama | RAB7 STEP |

**Ką išmatuoti (`MEASURE`) prieš spausdinant `psc3_rab7`:**
- `foot_d` – guminės kojelės skersmuo (numatyta 8 mm);
- `foot_h` – kojelės aukštis, nuo stalo iki EVK PCB apačios. Numatyta 8,76 mm = 29 − 1,6 − 18,64; tai tik prielaida, kad EVK lizdai 8,5 mm aukščio;
- `feet` – kojelių centrai, ypač 4-osios (jei jos nėra – ištrinti iš sąrašo);
- `board_t` – EVK PCB storis (nominalus 1,6 mm).

Jei kojelės ar plokštė stovi kitaip, užtenka pakeisti šiuos skaičius. Aukščiai skaičiuojami nuo kojelių apačios, todėl visas aukštis lieka `stack_h`.

**`pse84` – visi matmenys yra įvertinimai (`MEASURE`).** Turimas Infineon PDF (630-60751-01) yra tik schema, be išdėstymo duomenų. Prieš spausdinant išmatuoti plokštę slankmačiu arba gauti KIT_PSE84_AI PCB design data paketą.

**Bendri (`COMMON`)**

| Parametras | Kas tai |
|---|---|
| `wall` | sienos, dugno ir dangčio storis (numatyta 6 mm) |
| `clearance` | tarpas aplink plokštę |
| `fit_tol` | FDM tolerancija dangčio bortui (0,2–0,3 mm) |
| `foot_pocket_depth`, `foot_pocket_clear` | kojelių kišenių gylis (1 mm) ir tarpas aplink kojelę (0,6 mm) |
| `rail_w`, `rail_clear`, `rail_above`, `rail_corner_gap` | bėgelių storis (2 mm), tarpas iki PCB krašto (0,3 mm), aukštis virš PCB (1 mm), atstumas nuo PCB kampų (4 mm) |
| `press_d` | prispaudimo kaiščių skersmuo (8 mm) |
| `foam_t` | tarpas putplasčio pagalvėlei kaiščio gale (3 mm) |
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
KIT_PSC3M5_EVK + RAB7-SENSORFUSION: cube 147.6 mm, inner 135.6 mm; above the outside bottom: feet 5.0, PCB top 15.4, stack top 34.0, pin ends 28.5 mm; font C:/Windows/Fonts/arialbd.ttf
written to ...\out\pse84
DONE
```

Aplanke yra 4 failai. STL atidarius slicer'yje matomas kubo pagrindas su graviruotomis etiketėmis šonuose ir apačioje bei plokščias dangtis su etikete „+Z“.

**Nesėkmė**

| Ką matote | Ką tai reiškia, ką daryti |
|---|---|
| `Traceback (most recent call last): ...` | skripto klaida. Nukopijuoti visą tekstą ir perduoti programuotojui; dažniausia priežastis – neteisingas parametras, pvz., skylė už plokštės ribų. |
| `WARNING: no font found, labels are not engraved` | kubas sukurtas be etikečių. Į `fonts` įrašyti esamo `.ttf` failo kelią. |
| `WARNING: base shape is not valid` | geometrija netaisyklinga, dažniausiai dėl persidengiančių elementų. Patikrinti parametrus (pvz., kojelės kišenė kerta bėgelį). |
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
- **Prispaudimo kaiščiai** dangtyje yra ilgi (PSC3 ~113 mm, Ø8 mm). Jei spausdinant jie svyruoja: padidinti `press_d` iki 10 mm, spausdinti lėčiau arba su „brim“.
- **Tvirtinimas:**
  - plokštė nesukama; ji stovi ant savo kojelių kišenėse, XY ją laiko bėgeliai, Z – dangčio kaiščiai;
  - ant kiekvieno kaiščio galo priklijuoti ~3 mm putplasčio (EVA, porolono) pagalvėlę Ø8 mm (`foam_t`); ji turi būti šiek tiek suspausta, uždėjus dangtį;
  - dangtis – 4 × M3 × 12 į kampų skyles.

## 7. Naudojimas

1. Įdėti plokštę su RAB7 skydu tarp bėgelių taip, kad kojelės įkristų į kišenes. Prijungti USB kabelį ir išvesti jį per U išpjovą. Uždėti dangtį (kaiščiai su putplasčiu remiasi į RAB7 PCB) ir prisukti. Patikrinti, ar plokštė nejuda.
2. NuttX konsolėje paleisti `imucal` (nuttx-apps `testing/drivers/imucal`, įjungta `kit-psc3m5-evk:sensors`).
3. Dėti kubą ant lygaus, horizontalaus paviršiaus ant programos nurodytos sienos ir spausti Enter. Kubo nejudinti, kabelio netempti.
4. Programa atspausdina:
   - akselerometro poslinkį, mastelį, ašių nesutapimą ir korekcijos matricą;
   - giroskopo poslinkį.
5. Giroskopo mastelis: padėti kubą ant patefono (33⅓ aps./min = 200 °/s) ir paleisti `imucal -t`.
