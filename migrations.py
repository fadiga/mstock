
def make_migrate():
    from Common.models import migrator

    from playhouse.migrate import migrate, CharField, BooleanField

    migrations = [('InvoiceItem', 'detailed', CharField(default=""))]

    for x, y, z in migrations:
        try:
            migrate(migrator.add_column(x, y, z))
            print(x, " : ", y)
        except:
            pass
