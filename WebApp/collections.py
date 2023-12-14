class CollectionItem:
    def __init__(self, item_id, name, description):
        self.item_id = item_id
        self.name = name
        self.description = description

    def __str__(self):
        return f"ID: {self.item_id}, Name: {self.name}, Description: {self.description}"
    
    def display_collection(collection):
        for item in collection:
            print(item)
    
    def add_to_collection(collection, item):
        collection.append(item)
    
    def delete_from_collection(collection, item_id):
        collection[:] = [item for item in collection if item.item_id != item_id]
    
    def view_other_collection(other_collection):
        display_collection(other_collection)




