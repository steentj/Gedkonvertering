# GEDCOM til Markdown Konverter

Dette program konverterer en GEDCOM-fil til en række markdown-filer eller Word-dokumenter, der viser slægtstræer i et tabelformat.

## Installation

1. Sørg for at have Python 3.6 eller nyere installeret
2. Installer de nødvendige pakker:
   ```bash
   pip install -r requirements.txt
   ```

## Brug

Kør programmet ved at angive stien til din GEDCOM-fil:
```bash
python gedcom_processor.py sti/til/din/fil.ged
```

For at generere Word dokumenter i stedet for markdown filer:
```bash
python gedcom_processor.py sti/til/din/fil.ged --format word
```

Du kan valgfrit angive en anden output mappe end standardmappen 'output':
```bash
python gedcom_processor.py sti/til/din/fil.ged --output-dir min_mappe --format word
```

Programmet vil generere en række .md filer i en 'output' mappe. Hver fil indeholder et slægtstræ med følgende struktur:
- Række 1: Rodpersonen
- Række 2: Forældre (2 celler)
- Række 3: Bedsteforældre (4 celler)
- Række 4: Oldeforældre (8 celler)

Personer nummereres efter anetavle-systemet:
- Rodperson: 1
- Far: 2
- Mor: 3
- Farfar: 4
- Farmor: 5
- Morfar: 6
- Mormor: 7
osv.

## Output Format

Hver markdown-fil indeholder en tabel med personoplysninger i følgende format:
```
[Nummer]. [Navn] (f. [Fødselsdato], d. [Dødsdato])
```