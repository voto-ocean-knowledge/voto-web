import mongoengine


def initialise_database():
    db = "glidertest0"
    mongoengine.register_connection(
        alias="core", name=db, uuidRepresentation="standard"
    )
