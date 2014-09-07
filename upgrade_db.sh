for file in db/migrations/*
do
  python $file $1 upgrade
done
