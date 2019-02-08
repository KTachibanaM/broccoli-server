var db_names = db.getMongo().getDBNames()
for (var db_name in db_names){
    db = db.getMongo().getDB(db_names[db_name]);
    print("dropping db " + db.getName());
    db.dropDatabase();
}