import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def add_test_doc():
    doc_ref = db.collection(u'users').document(u'alovelace')
    doc_ref.set({
        u'first': u'Ada',
        u'last': u'Lovelace',
        u'born': 1815
    })


def add_second_case():
    doc_ref = db.collection(u'users').document(u'aturing')
    doc_ref.set({
        u'first': u'Alan',
        u'middle': u'Mathison',
        u'last': u'Turing',
        u'born': 1912
    })


def get_stuff():
    users_ref = db.collection(u'devices')
    docs = users_ref.stream()

    for doc in docs:
        print(f'{doc.id} => {doc.to_dict()}')


def add_new_dispenser():
    data = {
        u'deviceID': u'dispenser1',
        u'name': u'Lobby Dispenser',
        u'gateway': u'192.168.1.1'
    }

    db.collection(u'devices').document(u'device1').set(data)


def main():
    # add_test_doc()
    # add_second_case()
    get_stuff()
    # add_new_dispenser()


if __name__ == "__main__":
    main()
