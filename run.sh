./bin/bankreport \
  --dedup -f html --sort Date \
  -x "DE35490501010010558849" \
  -x "DE30200411550886249200" \
  -x "DE77200411110519079805" \
  -x "Wertpapiere - Buchungstext" \
  ./Steuer/2019/A1-Kotoauszuege/csv/FGK_2018.ftx.csv \
  ./Steuer/2019/A1-Kotoauszuege/csv/CDP_2018.cd.csv \
  ./Steuer/2019/A1-Kotoauszuege/csv/CDG_2018.cd.csv \
  > table.html

open table.html

exit 0
./bin/bankreport \
  --dedup -f html \
  ./Steuer/2019/A1-Kotoauszuege/csv/FGK_2019.ftx.csv \
  ./Steuer/2019/A1-Kotoauszuege/csv/CDP_2019.cd.csv \
  ./Steuer/2019/A1-Kotoauszuege/csv/CDG_2019.cd.csv \
  > table_2019.html

open table_2019.html

exit 0

