# Killer + Thermo Sudoku

Studiju projekts 9x9 Sudoku risināšanai ar paša implementētu Simulated Annealing.
Projektā ir datu modelis, nejauša sākuma kandidāta ģenerēšana pa 3x3 blokiem,
ierobežojumu novērtēšana, JSON ielāde un optimizācijas algoritms.

## Palaišana

Nepieciešams Python 3.10 vai jaunāks. Ārējas bibliotēkas nav vajadzīgas.

```powershell
python main.py instances/classic_demo.json --seed 42
```

Pieejamie algoritma parametri: `--temperature`, `--cooling-rate` un
`--time-limit` (pēc noklusējuma 180 sekundes). Algoritms restartējas, kad
temperatūra nokrītas zem minimuma, un turpina līdz score 0 vai laika beigām.

## Testi

```powershell
python -m unittest discover -s tests -v
```

## JSON formāts

`grid` ir 9x9 skaitļu matrica, kur 0 apzīmē tukšu šūnu. `cages` un `thermos`
ir neobligāti lauki. Šūnu koordinātas ir nulles bāzes formā `[rinda, kolonna]`.

## Atkārtota eksperimentu testēšana

Lai palaistu katru no 20 kategorizētajiem piemēriem piecas reizes un saglabātu
rezultātus:

```powershell
python benchmark.py
```

Pēc noklusējuma katram palaidienam ir 10 sekunžu laika limits, un tiek izmantotas
reproducējamas, bet atšķirīgas nejaušās sēklas. Pilnie palaidienu dati tiek
saglabāti jaunā `results/benchmark_YYYYMMDD_HHMMSS.csv` failā; kopsavilkums par
katru mīklu — blakus esošajā `..._summary.csv` failā. Katrā rindā ir sākuma un
labākais score, optimalitātes atstarpe līdz score 0, izpildes laiks, iterāciju
skaits, restartu skaits un labākais atrastais režģis. CSV fails tiek papildināts
pēc katra palaidiena, tāpēc jau iegūtie dati paliek pieejami arī tad, ja
benchmark tiek pārtraukts.

Piemēri parametru maiņai:

```powershell
python benchmark.py --runs 5 --time-limit 30 --seed 100
python benchmark.py --runs 10 --time-limit 5 --output results/quick_benchmark.csv
```
