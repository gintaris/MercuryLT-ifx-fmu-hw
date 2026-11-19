# IMU kalibravimo kubas

Parametrinis FreeCAD skriptas `calib_cube.py` sukuria kubo formos laikiklį plokštei su IMU. Kubo išorinės sienos plokščios ir tarpusavyje statmenos, o plokštės ašys lygiagrečios sienoms. Taip galima tiksliai atlikti akselerometro kalibravimą 6 padėtimis (NuttX `imucal`) ir palyginti kelis tos pačios plokštės egzempliorius.

Dvi variantai:

| Variantas | Plokštė | Kubas (numatytieji matmenys) |
|---|---|---|
| `psc3_rab7` | KIT_PSC3M5_EVK su Rutronik RAB7-SENSORFUSION skydu | 133 mm |
| `pse84` | KIT_PSE84_AI | 98 mm |

Kubą sudaro dvi dalys:
- **pagrindas** – atvira dėžė su stovais plokštės montavimo skylėms ir U formos išpjova USB kabeliui;
- **dangtis** su centravimo bortu, prisukamas 4 varžtais M3 kampuose.

Abi dalys spausdinamos be atramų: pagrindas – atvira puse į viršų, dangtis – viršutine puse ant stalo.

## Paleidimas

```
freecadcmd calib_cube.py psc3_rab7
freecadcmd calib_cube.py pse84
```

Taip pat galima FreeCAD GUI: *Macro → Macros… → Execute*; variantas tada imamas iš kintamojo `VARIANT` skripto viršuje.

Rezultatai įrašomi į `out/<variantas>/`: `calib_cube_<variantas>_base.step/.stl` ir `..._lid.step/.stl`. Skriptas patikrintas su FreeCAD 1.2 (`freecadcmd`, Windows): abu variantai sugeneruojami, kiekviena dalis yra vienas taisyklingas kietasis kūnas. Atspausdintas dar nebuvo.

## Ką išmatuoti ir pakeisti (žymė `MEASURE`)

Gamintojo mechaninio brėžinio (plokštės kontūro ir skylių) gauti nepavyko, todėl visi plokščių matmenys yra **įvertinimai**. Prieš spausdinant juos reikia išmatuoti slankmačiu ir pataisyti žodyne `VARIANTS`:

- `board_l`, `board_w`, `board_t` – plokštės ilgis, plotis ir storis;
- `holes` – montavimo skylių centrai (x, y) nuo plokštės kampo (−Xc, −Yc);
- `below_h` – aukščiausia detalė ar kaištis po plokšte (nuo to priklauso stovų aukštis);
- `above_h` – aukščiausia detalė virš plokštės; PSC3 atveju tai RAB7 skydo viršus (jungčių aukštis, skydo PCB, detalės);
- `usb_wall`, `usb_offset`, `usb_w`, `usb_z` – kurioje sienoje yra KitProg3 USB-C, jo vieta išilgai sienos, kabelio kištuko plotis ir jungties centro aukštis virš plokštės.

Bendrieji parametrai (`COMMON`):
- `wall` – sienos storis;
- `clearance` – tarpas aplink plokštę;
- `fit_tol` – FDM tolerancija (0,2–0,3 mm);
- varžtų skylės (stovuose M2.5 savisriegiams, dangtyje M3);
- etikečių dydis ir gylis;
- šriftų sąrašas.

## Ašys ir etiketės

Kubo koordinatės: Xc – išilgai plokštės ilgosios kraštinės, Yc – išilgai trumposios, Zc – aukštyn (detalių pusė ir dangtis viršuje). Ant kiekvienos sienos išgraviruota sensoriaus ašis, kuri rodo iš tos sienos į išorę.

Padėjus kubą ant sienos su etikete A, akselerometras toje ašyje rodo −g. Pavyzdžiui, ant „−Z“ (normali padėtis) z ≈ +9,81 m/s².

- **PSC3 + RAB7** – etiketės nustatytos pagal BMI323 bandymą 2026-11-19.
  - Plokštę pastačius ant USB trumposios kraštinės, aukštyn rodo +Y, todėl sensoriaus Y eina išilgai **ilgosios** EVK kraštinės, o X – išilgai trumposios.
  - Kuri ilgoji kraštinė yra +X, nepatikrinta (`VERIFY`).
- **PSE84** – etiketės yra prielaida (`VERIFY`).

Etiketes galima pakeisti parametru `labels`.

## Spausdinimo nustatymai (rekomendacija)

- PLA arba PETG, sluoksnis 0,2 mm, 4 perimetrai, užpildas 20–30 % (gyroid);
- atramų nereikia; pagrindas – atvira puse į viršų, dangtis – viršumi žemyn;
- po spausdinimo patikrinti, ar sienos plokščios (liniuote ant stiklo). Jei reikia, lengvai nušlifuoti, kol kubas stovi stabiliai ant kiekvienos sienos;
- plokštė tvirtinama varžtais M2.5 (savisriegiais) į stovus, dangtis – 4 varžtais M3 × 12 į kampų skyles.

## Naudojimas

1. Įdėti plokštę (USB kabelis prijungtas, išvestas per U išpjovą), prisukti, uždėti dangtį.
2. NuttX konsolėje paleisti `imucal` (žr. `MercuryLT-ifx-nuttx-apps`, `testing/drivers/imucal`).
3. Programos nurodyta tvarka dėti kubą ant 6 sienų ant lygaus, horizontalaus paviršiaus. Kiekvienoje padėtyje palaukti, kol programa surinks vidurkį. Kubo nejudinti, kabelio netempti.
4. Programa atspausdina:
   - kiekvienos ašies poslinkį, mastelį ir nesutapimą (3×3 matrica);
   - giroskopo poslinkį ramybėje.
5. Giroskopo mastelio patikra: kubą su norima ašimi vertikaliai padėti ant patefono, 33⅓ aps./min = 200 °/s (`imucal -t`).
