# Execute from root dir as: bash upgrade_db.sh <db_path>
for file in db/migrations/*
do
  python $file $1 upgrade
done
