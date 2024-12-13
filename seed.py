import x
import uuid
import time
import random
from werkzeug.security import generate_password_hash
from faker import Faker

fake = Faker()

from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)

db, cursor = x.db()

def insert_user(user):
    q = f"""
        INSERT INTO users
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
    values = tuple(user.values())
    cursor.execute(q, values)
try:
    ###############################
    ######   Create users table
    ###############################
    cursor.execute("DROP TABLE IF EXISTS item_images")
    cursor.execute("DROP TABLE IF EXISTS items")
    cursor.execute("DROP TABLE IF EXISTS users_roles")
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS roles")
    q = """
        CREATE TABLE users (
            user_pk CHAR(36),
            user_name VARCHAR(20) NOT NULL,
            user_last_name VARCHAR(20) NOT NULL,
            user_email VARCHAR(100) NOT NULL UNIQUE,
            user_password VARCHAR(255) NOT NULL,
            user_created_at INTEGER UNSIGNED,
            user_deleted_at INTEGER UNSIGNED,
            user_blocked_at INTEGER UNSIGNED,
            user_updated_at INTEGER UNSIGNED,
            user_verified_at INTEGER UNSIGNED,
            user_verification_key CHAR(36),
            user_reset_token CHAR(36),
            user_reset_token_expires INTEGER UNSIGNED,
            PRIMARY KEY(user_pk)
        )
        """
    cursor.execute(q)

    ###############################
    ######   Create roles table
    ###############################
    q = """
        CREATE TABLE roles (
            role_pk CHAR(36),
            role_name VARCHAR(10) NOT NULL UNIQUE,
            PRIMARY KEY(role_pk)
        );
        """
    cursor.execute(q)

    ##################################
    ######   Create users_roles table
    ##################################
    q = """
        CREATE TABLE users_roles (
            user_role_user_fk CHAR(36),
            user_role_role_fk CHAR(36),
            PRIMARY KEY(user_role_user_fk, user_role_role_fk)
        );
        """
    cursor.execute(q)
    cursor.execute("ALTER TABLE users_roles ADD FOREIGN KEY (user_role_user_fk) REFERENCES users(user_pk) ON DELETE CASCADE ON UPDATE RESTRICT") 
    cursor.execute("ALTER TABLE users_roles ADD FOREIGN KEY (user_role_role_fk) REFERENCES roles(role_pk) ON DELETE CASCADE ON UPDATE RESTRICT") 

    ##################################
    ######   Create items table
    ##################################
    q = """
        CREATE TABLE items (
            item_pk CHAR(36),
            item_user_fk CHAR(36),
            item_title VARCHAR(50) NOT NULL,
            item_description VARCHAR(50) NOT NULL,
            item_price DECIMAL(5,2) NOT NULL,
            item_image VARCHAR(50),
            item_created_at INTEGER UNSIGNED,
            item_deleted_at INTEGER UNSIGNED,
            item_blocked_at INTEGER UNSIGNED,
            item_updated_at INTEGER UNSIGNED,
            PRIMARY KEY(item_pk)
        );
        """
    cursor.execute(q)
    cursor.execute("ALTER TABLE items ADD FOREIGN KEY (item_user_fk) REFERENCES users(user_pk) ON DELETE CASCADE ON UPDATE RESTRICT")

    ##################################
    ######  Create item_images table
    ##################################
    q = """
        CREATE TABLE item_images (
            image_pk CHAR(36),
            item_fk CHAR(36),
            image_file VARCHAR(50) NOT NULL,
            PRIMARY KEY(image_pk),
            FOREIGN KEY (item_fk) REFERENCES items(item_pk) ON DELETE CASCADE ON UPDATE RESTRICT
        );
        """
    cursor.execute(q)

    ###############################
    ######   Create roles
    ###############################
    q = f"""
        INSERT INTO roles (role_pk, role_name)
        VALUES ("{x.ADMIN_ROLE_PK}", "admin"), ("{x.CUSTOMER_ROLE_PK}", "customer"),
        ("{x.PARTNER_ROLE_PK}", "partner"), ("{x.RESTAURANT_ROLE_PK}", "restaurant")
        """
    cursor.execute(q)

    ###############################
    ######   Create Admin user
    ###############################
    user_pk = str(uuid.uuid4())
    user = {
        "user_pk" : user_pk,
        "user_name" : "John",
        "user_last_name" : "Admin",
        "user_email" : "admin@fulldemo.com",
        "user_password" : generate_password_hash("password"),
        "user_created_at" : int(time.time()),
        "user_deleted_at" : 0,
        "user_blocked_at" : 0,
        "user_updated_at" : 0,
        "user_verified_at" : int(time.time()),
        "user_verification_key" : str(uuid.uuid4()),
        "user_reset_token": 0,
        "user_reset_token_expires": 0
    }
    insert_user(user)
    # Assign role to admin user
    q = f"""
        INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES ("{user_pk}",
        "{x.ADMIN_ROLE_PK}")
        """
    cursor.execute(q)

    ###############################
    ######   Create customer user
    ###############################
    user_pk = "4218788d-03b7-4812-bd7d-31c8859e92d8"
    user = {
        "user_pk" : user_pk,
        "user_name" : "John",
        "user_last_name" : "Customer",
        "user_email" : "customer@fulldemo.com",
        "user_password" : generate_password_hash("password"),
        "user_created_at" : int(time.time()),
        "user_deleted_at" : 0,
        "user_blocked_at" : 0,
        "user_updated_at" : 0,
        "user_verified_at" : int(time.time()),
        "user_verification_key" : str(uuid.uuid4()),
        "user_reset_token": 0,
        "user_reset_token_expires": 0
    }
    insert_user(user)
    # Assign role to customer user
    q = f"""
        INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES ("{user_pk}",
        "{x.CUSTOMER_ROLE_PK}")
        """
    cursor.execute(q)

    ###############################
    ######   Create partner user
    ###############################
    user_pk = str(uuid.uuid4())
    user = {
        "user_pk" : user_pk,
        "user_name" : "John",
        "user_last_name" : "Partner",
        "user_email" : "partner@fulldemo.com",
        "user_password" : generate_password_hash("password"),
        "user_created_at" : int(time.time()),
        "user_deleted_at" : 0,
        "user_blocked_at" : 0,
        "user_updated_at" : 0,
        "user_verified_at" : int(time.time()),
        "user_verification_key" : str(uuid.uuid4()),
        "user_reset_token": 0,
        "user_reset_token_expires": 0
    }
    insert_user(user)
    # Assign role to partner user
    q = f"""
        INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES ("{user_pk}",
        "{x.PARTNER_ROLE_PK}")
        """
    cursor.execute(q)

    #################################
    ######   Create restaurant user
    #################################
    user_pk = str(uuid.uuid4())
    user = {
        "user_pk" : user_pk,
        "user_name" : "Seafood",
        "user_last_name" : "Restaurant",
        "user_email" : "restaurant@fulldemo.com",
        "user_password" : generate_password_hash("password"),
        "user_created_at" : int(time.time()),
        "user_deleted_at" : 0,
        "user_blocked_at" : 0,
        "user_updated_at" : 0,
        "user_verified_at" : int(time.time()),
        "user_verification_key" : str(uuid.uuid4()),
        "user_reset_token": 0,
        "user_reset_token_expires": 0
    }
    insert_user(user)
    # Assign role to restaurant user
    q = f"""
        INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES ("{user_pk}",
        "{x.RESTAURANT_ROLE_PK}")
        """
    cursor.execute(q)

    ###############################
    ######   Create 20 customers
    ###############################
    domains = ["example.com", "testsite.org", "mydomain.net", "website.co", "fakemail.io", "gmail.com", "hotmail.com"]
    user_password = hashed_password = generate_password_hash("password")
    for _ in range(20):
        user_pk = str(uuid.uuid4())
        user_verified_at = random.choice([0,int(time.time())])
        user = {
            "user_pk" : user_pk,
            "user_name" : fake.first_name(),
            "user_last_name" : fake.last_name(),
            "user_email" : fake.unique.user_name() + "@" + random.choice(domains),
            "user_password" : user_password,
            # user_password = hashed_password = generate_password_hash(fake.password(length=20))
            "user_created_at" : int(time.time()),
            "user_deleted_at" : 0,
            "user_blocked_at" : 0,
            "user_updated_at" : 0,
            "user_verified_at" : user_verified_at,
            "user_verification_key" : str(uuid.uuid4()),
            "user_reset_token": 0,
            "user_reset_token_expires": 0
        }
        insert_user(user)
        # assign role to customer users
        cursor.execute("""INSERT INTO users_roles (
            user_role_user_fk,
            user_role_role_fk)
            VALUES (%s, %s)""", (user_pk, x.CUSTOMER_ROLE_PK))
        
    ###############################
    ######   Create 20 partners
    ###############################
    user_password = hashed_password = generate_password_hash("password")
    for _ in range(20):
        user_pk = str(uuid.uuid4())
        user_verified_at = random.choice([0,int(time.time())])
        user = {
            "user_pk" : user_pk,
            "user_name" : fake.first_name(),
            "user_last_name" : fake.last_name(),
            "user_email" : fake.unique.email(),
            "user_password" : user_password,
            "user_created_at" : int(time.time()),
            "user_deleted_at" : 0,
            "user_blocked_at" : 0,
            "user_updated_at" : 0,
            "user_verified_at" : user_verified_at,
            "user_verification_key" : str(uuid.uuid4()),
            "user_reset_token": 0,
            "user_reset_token_expires": 0
        }
        insert_user(user)
        # assign role to partner users
        cursor.execute("""
        INSERT INTO users_roles (
            user_role_user_fk,
            user_role_role_fk)
            VALUES (%s, %s)
        """, (user_pk, x.PARTNER_ROLE_PK))


    ###############################
    ######   Create 20 restaurants
    ###############################

    ##### 20 dishes #####
    dishes = ["Spaghetti Carbonara","Chicken Alfredo","Beef Wellington","Sushi","Pizza Margherita","Tacos","Caesar Salad","Fish and Chips","Pad Thai","Dim Sum","Croissant","Ramen","Lasagna","Burrito","Chicken Parmesan","Tom Yum Soup","Shawarma","Paella","Hamburger","Chicken Tikka Masala"]
    restaurant_names = ["Nordic Bites", "Smørrebrød Haven", "The Danish Plate", "Copenhagen Cuisine", "Aarhus Alchemy", "Viking Feast", "Hygge Dining", "Fjord Flavors", "Rustic Rye", "The Pickled Herring", "New Nordic Table", "Sjømat Bistro", "Little Mermaid Café", "Kronborg Kitchen", "Tivoli Treats", "Baltic Bistro", "Midnight Mackerel", "Friluftsmad", "The Carlsberg Grill", "Copenhagen Comforts"]

    user_password = hashed_password = generate_password_hash("password")
    for _ in range(20):
        user_pk = str(uuid.uuid4())
        user_verified_at = random.choice([0,int(time.time())])
        user = {
            "user_pk" : user_pk,
            "user_name" : random.choice(restaurant_names),
            "user_last_name" : "",
            "user_email" : fake.unique.email(),
            "user_password" : user_password,
            "user_created_at" : int(time.time()),
            "user_deleted_at" : 0,
            "user_blocked_at" : 0,
            "user_updated_at" : 0,
            "user_verified_at" : user_verified_at,
            "user_verification_key" : str(uuid.uuid4()),
            "user_reset_token": 0,
            "user_reset_token_expires": 0
        }
        insert_user(user)
        # assign role to restaurant users
        cursor.execute("""
        INSERT INTO users_roles (
            user_role_user_fk,
            user_role_role_fk)
            VALUES (%s, %s)
        """, (user_pk, x.RESTAURANT_ROLE_PK))

        #### generate 20 random items to the items table ####
        for _ in range(random.randint(5,20)):
            # Generate a random integer between 1 and 100 to represent a unique identifier for a dish
            dish_id = random.randint(1, 100)
            item_description = "description"
            item_created_at = int(time.time())
            item_deleted_at = 0
            item_blocked_at = 0
            item_updated_at = 0
            cursor.execute("""
            INSERT INTO items (
                item_pk, item_user_fk, item_title, item_description, item_price, item_image, item_created_at, item_deleted_at, item_blocked_at, item_updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (str(uuid.uuid4()), user_pk, random.choice(dishes), item_description, round(random.uniform(50, 999), 2), f"dish_{dish_id}.jpg", item_created_at, item_deleted_at, item_blocked_at, item_updated_at))                

    db.commit()

except Exception as ex:
    ic(ex)
    if "db" in locals(): db.rollback()

finally:
    if "cursor" in locals(): cursor.close()
    if "db" in locals(): db.close()