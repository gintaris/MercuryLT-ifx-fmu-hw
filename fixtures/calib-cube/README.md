# IMU kalibravimo kubas

Parametrinis FreeCAD skriptas `calib_cube.py` sukuria kubo formos laikiklį plokštei su IMU. Kubo išorinės sienos plokščios ir tarpusavyje statmenos, o plokštės ašys lygiagrečios sienoms. Taip galima tiksliai atlikti akselerometro kalibravimą 6 padėtimis (NuttX `imucal`) ir palyginti kelis plokščių egzempliorius.

| Variantas | Plokštė | Kubas (su numatytais matmenimis) |
|---|---|---|
| `psc3_rab7` | KIT_PSC3M5_EVK su Rutronik RAB7-SENSORFUSION skydu | 133 mm |
| `pse84` | KIT_PSE84_AI | 98 mm |

Kubą sudaro dvi dalys:
- **pagrindas** – atvira dėžė su stovais plokštės montavimo skylėms ir U išpjova USB kabeliui;
- **dangtis** su centravimo bortu, prisukamas 4 varžtais M3.

Abi dalys spausdinamos be atramų.

## Būsena

- **FreeCAD versija:** 1.0 arba naujesnė; tikslinė versija – naujausia stabili.
- **Naudojami moduliai:** tik standartiniai FreeCAD moduliai `Part` ir `Mesh`. Išorinių Python paketų nereikia.
- **Kas išbandyta:** skriptas paleistas su FreeCAD 1.2.0 (`freecadcmd`, Windows) abiem variantais. Taip pat išbandytas įklijavimas į konsolę (be `__file__`). Visos 4 dalys sugeneruotos kaip taisyklingi vientisi kietieji kūnai, STEP ir STL failai įrašyti.
- **Kas neišbandyta:**
  - FreeCAD GUI (*Macro → Execute*) kitame kompiuteryje;
  - kitos FreeCAD versijos;
  - spausdinimas;
  - **plokščių matmenys – įvertinimai**, žr. žemiau.

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

**Plokštės matmenys (`VARIANTS`) – žymėti `MEASURE`, išmatuoti slankmačiu.** Gamintojo mechaninio brėžinio gauti nepavyko, todėl visi dabartiniai skaičiai yra įvertinimai.

| Parametras | Kas tai |
|---|---|
| `board_l`, `board_w`, `board_t` | plokštės ilgis (ilgoji kraštinė), plotis, storis, mm |
| `holes` | montavimo skylių centrai (x, y) nuo plokštės kampo (ilgoji kraštinė – x) |
| `below_h` | aukščiausia detalė ar kaištis po plokšte (nustato stovų aukštį) |
| `above_h` | aukščiausia detalė virš plokštės; PSC3 atveju – RAB7 skydo viršus |
| `usb_wall` | siena su KitProg3 USB-C: `"-Xc"`, `"+Xc"`, `"-Yc"`, `"+Yc"` |
| `usb_offset` | USB vieta išilgai tos sienos nuo plokštės centro |
| `usb_w` | kabelio kištuko plotis su atsarga |
| `usb_z` | USB jungties centro aukštis virš plokštės |
| `labels` | kokia ašies etiketė graviruojama ant kiekvienos sienos |

**Bendri (`COMMON`)**

| Parametras | Kas tai |
|---|---|
| `wall` | sienos, dugno ir dangčio storis (numatyta 6 mm) |
| `clearance` | tarpas aplink plokštę |
| `fit_tol` | FDM tolerancija dangčio bortui (0,2–0,3 mm) |
| `board_pilot_d` | skylės stovuose (M2.5 savisriegiams) |
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
KIT_PSE84_AI: cube 98.0 mm, inner 86.0 mm, base height 92.0 mm, board bottom 11.0 mm above the outside bottom, font C:/Windows/Fonts/arialbd.ttf
written to ...\out\pse84
DONE
```

Aplanke yra 4 failai. STL atidarius slicer'yje matomas kubo pagrindas su graviruotomis etiketėmis šonuose ir apačioje bei plokščias dangtis su etikete „+Z“.

**Nesėkmė**

| Ką matote | Ką tai reiškia, ką daryti |
|---|---|
| `Traceback (most recent call last): ...` | skripto klaida. Nukopijuoti visą tekstą ir perduoti programuotojui; dažniausia priežastis – neteisingas parametras, pvz., skylė už plokštės ribų. |
| `WARNING: no font found, labels are not engraved` | kubas sukurtas be etikečių. Į `fonts` įrašyti esamo `.ttf` failo kelią. |
| `WARNING: base shape is not valid` | geometrija netaisyklinga, dažniausiai dėl persidengiančių elementų. Patikrinti parametrus (pvz., USB išpjova kerta stovą). |
| Nėra eilutės `DONE`, failų nėra | skriptas nepasiekė pabaigos; žiūrėti klaidą Report view. |

## 5. Ašys ir etiketės

Kubo koordinatės:
- Xc – išilgai plokštės ilgosios kraštinės;
- Yc – išilgai trumposios kraštinės;
- Zc – aukštyn (detalės ir dangtis viršuje).

Ant kiekvienos sienos išgraviruota sensoriaus ašis, kuri iš tos sienos rodo į išorę. Padėjus kubą ant sienos su etikete A, akselerometras ašyje A rodo −g. Pavyzdžiui, ant „−Z“ (normali padėtis) z ≈ +9,81 m/s².

**PSC3 + RAB7** – etiketės nustatytos pagal BMI323 bandymą 2026-11-19:
- plokštę pastačius ant USB trumposios kraštinės, aukštyn rodo +Y, todėl sensoriaus Y eina išilgai **ilgosios** EVK kraštinės, o X – išilgai trumposios;
- kuri ilgoji kraštinė yra +X, nepatikrinta (`VERIFY`).

**PSE84** – etiketės yra prielaida (`VERIFY`).

Atspausdinus etiketes patikrinti su `sensortest accel0` ir, jei reikia, pakeisti `labels`.

## 6. Spausdinimas

- **Medžiaga ir nustatymai:** PLA arba PETG, sluoksnis 0,2 mm, 4 perimetrai, užpildas 20–30 % (gyroid).
- **Padėtis spausdintuve:**
  - pagrindas – atvira puse į viršų;
  - dangtis – etikete „+Z“ žemyn (STL failai jau orientuoti taip, kaip kubas surinktas, todėl slicer'yje dangtį reikia apversti).
- **Atramų nereikia.**
- **Po spausdinimo:** patikrinti sienų plokštumą liniuote. Jei kubas ant kurios nors sienos klibina, tą sieną lengvai nušlifuoti.
- **Tvirtinimas:**
  - plokštė – M2.5 savisriegiais į stovus;
  - dangtis – 4 × M3 × 12 į kampų skyles.

## 7. Naudojimas

1. Įdėti plokštę, prijungti USB kabelį ir išvesti jį per U išpjovą. Prisukti plokštę, uždėti ir prisukti dangtį.
2. NuttX konsolėje paleisti `imucal` (nuttx-apps `testing/drivers/imucal`, įjungta `kit-psc3m5-evk:sensors`).
3. Dėti kubą ant lygaus, horizontalaus paviršiaus ant programos nurodytos sienos ir spausti Enter. Kubo nejudinti, kabelio netempti.
4. Programa atspausdina:
   - akselerometro poslinkį, mastelį, ašių nesutapimą ir korekcijos matricą;
   - giroskopo poslinkį.
5. Giroskopo mastelis: padėti kubą ant patefono (33⅓ aps./min = 200 °/s) ir paleisti `imucal -t`.
