import mongoengine


def initialise_database():
    db = "glidertest1"
    mongoengine.register_connection(
        alias="core", name=db, uuidRepresentation="standard"
    )
