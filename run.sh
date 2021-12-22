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

