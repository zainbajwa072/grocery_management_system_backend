from .connection import neo4j_db

class GroceryGraphQueries:
    @staticmethod
    def create_grocery_node(grocery_id, name, location):
        query = """
        CREATE (g:Grocery {id: $grocery_id, name: $name, location: $location})
        RETURN g
        """
        return neo4j_db.query(query, {
            'grocery_id': grocery_id,
            'name': name,
            'location': location
        })
    
    @staticmethod
    def create_item_node(item_id, name, item_type, price, grocery_id):
        query = """
        MATCH (g:Grocery {id: $grocery_id})
        CREATE (i:Item {id: $item_id, name: $name, type: $item_type, price: $price})
        CREATE (i)-[:BELONGS_TO]->(g)
        RETURN i, g
        """
        return neo4j_db.query(query, {
            'item_id': item_id,
            'name': name,
            'item_type': item_type,
            'price': price,
            'grocery_id': grocery_id
        })
    
    @staticmethod
    def get_grocery_analytics(grocery_id):
        query = """
        MATCH (g:Grocery {id: $grocery_id})<-[:BELONGS_TO]-(i:Item)
        RETURN g.name as grocery_name, 
               count(i) as total_items,
               avg(i.price) as avg_price,
               collect(DISTINCT i.type) as item_types
        """
        return neo4j_db.query(query, {'grocery_id': grocery_id})