## Generate the SQL dump file from public dataset

```bash
# setup connection
export VM_ADDR="tournesol-vm"
export VM_USER="$USER"

# nuke database tables
ssh "$VM_USER@$VM_ADDR" -- sudo -u postgres psql -d tournesol <<< "truncate table core_user cascade;"
ssh "$VM_USER@$VM_ADDR" -- sudo -u postgres psql -d tournesol <<< "truncate table tournesol_video cascade;"
ssh "$VM_USER@$VM_ADDR" -- sudo -u postgres psql -d tournesol <<< "truncate table tournesol_comparison cascade;"

# push data and scripts
tar xvf public-dataset.tgz
./fix-csv-files.sh
scp comparison_database.csv contributors_public.csv install-venv-and-dependencies.sh import-contributors-dataset.sh get-users-comparisons-dataset.sh get-videos-comparisons-dataset.sh import-comparisons-dataset.sh "$VM_USER@$VM_ADDR":.
rm comparison_database.csv contributors_public.csv

# run all the scripts
ssh "$VM_USER@$VM_ADDR" -- bash -c "./install-venv-and-dependencies.sh && ./import-contributors-dataset.sh && ./get-users-comparisons-dataset.sh && ./get-videos-comparisons-dataset.sh && ./import-comparisons-dataset.sh"

# dump tables (produces a dump.sql.tgz file)
./dump-tables.sh
```

## Import SQL dump file

If you want to empty your database before:

```bash
# setup connection
VM_ADDR="tournesol-vm"
VM_USER="$USER"

# nuke database tables
ssh "$VM_USER@$VM_ADDR" -- sudo -u postgres psql -d tournesol <<< "truncate table core_user cascade;"
ssh "$VM_USER@$VM_ADDR" -- sudo -u postgres psql -d tournesol <<< "truncate table tournesol_video cascade;"
ssh "$VM_USER@$VM_ADDR" -- sudo -u postgres psql -d tournesol <<< "truncate table tournesol_comparison cascade;"
```

Import the dump:

```bash
# setup connection
VM_ADDR="tournesol-vm"
VM_USER="$USER"

tar xvf dump.sql.tgz
ssh "$VM_USER@$VM_ADDR" -- sudo -u postgres psql -d tournesol < dump.sql
rm dump.sql
```
