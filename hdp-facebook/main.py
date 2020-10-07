from data.FacebookDataReader import FacebookDataReader

# functions for testing
reader = FacebookDataReader()
# enter directory with unzipped Facebook data
data = reader.load(r"")
# enter directory to save and restore loaded data
data.save(r"")
data.restore(r"")
