from flask import Flask, render_template, app, session, redirect, url_for, request
from flask_session import Session
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import x
import uuid
import time
import os

from icecream import ic
ic.configureOutput(prefix=f'***** | ', includeContext=True)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

###################################
###################################
def _________GET_________(): pass
###################################
###################################

##############################
# Index / landingpage
##############################
@app.get("/")
def view_index():
    return render_template("view_index.html")

##############################
# Profile
##############################
@app.get("/profile")
@x.no_cache
def view_profile():
    user = session.get("user", "")
    user_role = session.get("role_name", "")
    if not user:
        return redirect(url_for("view_index"))
    return render_template("view_profile.html", user=user, user_role=user_role)

##############################
# Login
##############################
@app.get("/login")
@x.no_cache
def view_login():
    ic(session)
    if session.get("user"):
        if len(session.get("user").get("roles")) > 1:
            return redirect(url_for("view_choose_role"))
        if "admin" in session.get("user").get("roles"):
            return redirect(url_for("view_admin"))
        if "customer" in session.get("user").get("roles"):
            return redirect(url_for("view_customer"))
    return render_template("view_login.html", x=x, title="Login")

##############################
# Signup
##############################
@app.get("/signup")
@x.no_cache
def view_signup():  
    ic(session)
    if session.get("user"):
        if len(session.get("user").get("roles")) > 1:
            return redirect(url_for("view_choose_role")) 
        if "admin" in session.get("user").get("roles"):
            return redirect(url_for("view_admin"))
        if "customer" in session.get("user").get("roles"):
            return redirect(url_for("view_customer")) 
        if "partner" in session.get("user").get("roles"):
            return redirect(url_for("view_partner"))         
    return render_template("view_signup.html", x=x, title="Signup")

##############################
# Customer
##############################
@app.get("/customer")
@x.no_cache
def view_customer():
    if not session.get("user", ""):
        return redirect(url_for("view_login"))
    user = session.get("user")
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))

    try:
        db, cursor = x.db()  # Connect to the database

        # Fetch all restaurants with the restaurant role
        q = """
            SELECT DISTINCT
                u.user_pk, 
                u.user_name AS restaurant_name
            FROM users u
            JOIN users_roles ur ON u.user_pk = ur.user_role_user_fk
            WHERE ur.user_role_role_fk = %s AND u.user_deleted_at = 0
        """
        cursor.execute(q, (x.RESTAURANT_ROLE_PK,))
        restaurants = cursor.fetchall()  # Fetch all restaurants
        ic(restaurants)  # Debugging output
        
        return render_template("view_customer.html", user=user, restaurants=restaurants)
    
    except Exception as ex:
        ic(ex)
        return "Error loading customer page", 500
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()



##############################
# Customer single view page
##############################
@app.get("/customer-single/<user_pk>")
@x.no_cache
def view_customer_single(user_pk):
    try:
        db, cursor = x.db()  # Connect to the database
        user = session.get("user")  # Ensure user is available

        # Fetch restaurant info
        q_restaurant = """
            SELECT 
                u.user_name AS restaurant_name, 
                u.user_email AS restaurant_email, 
                u.user_verified_at AS restaurant_verified_at,
                u.user_created_at AS restaurant_created_at
            FROM users u
            WHERE u.user_pk = %s AND u.user_deleted_at = 0
        """
        cursor.execute(q_restaurant, (user_pk,))
        restaurant = cursor.fetchone()

        if not restaurant:
            return "Restaurant not found", 404

        # Fetch items for the specific restaurant
        q_items = """
            SELECT 
                i.item_title, 
                i.item_description, 
                i.item_price, 
                i.item_image
            FROM items i
            WHERE i.item_deleted_at = 0 AND i.item_user_fk = %s
        """
        cursor.execute(q_items, (user_pk,))
        items = cursor.fetchall()

        return render_template(
            "view_customer_single.html",
            restaurant=restaurant,
            items=items,
            user=user
        )

    except Exception as ex:
        return f"Error loading restaurant details: {ex}", 500

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()






# ##############################
# # View customer single
# ##############################
# @app.get("/customer-single")
# @x.no_cache
# def view_customer_single():
#     return render_template("view_customer_single.html", x=x)


##############################
# Partner
##############################
@app.get("/partner")
@x.no_cache
def view_partner():
    if not session.get("user", ""):
        return redirect(url_for("view_login"))
    user = session.get("user")
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))
    return render_template("view_partner.html", user=user)

##############################
# Admin
##############################
@app.get("/admin")
@x.no_cache
def view_admin():
    if not session.get("user", ""):
        return redirect(url_for("view_login"))
    user = session.get("user", "")
    if not "admin" in user.get("roles", ""):
        return redirect(url_for("view_login"))

    try:
        db, cursor = x.db()  # Connect to the database
        # Fetch all users
        q = """
            SELECT
                user_pk, user_name, user_last_name, user_email, user_blocked_at
            FROM users
            WHERE user_deleted_at = 0
        """
        cursor.execute(q)
        users = cursor.fetchall()  # Fetch all users as a list 
        ic(users)  # Debugging output to confirm data

        # Fetch all items
        q = """
            SELECT
                i.item_pk, i.item_title, i.item_description, i.item_price, i.item_image, i.item_blocked_at,
                u.user_name AS restaurant_name
            FROM items i
            JOIN users u ON i.item_user_fk = u.user_pk
            WHERE i.item_deleted_at = 0
        """
        cursor.execute(q)
        items = cursor.fetchall()  # Fetch all items as a list
        ic(items)  # Debugging output to confirm data
        
        # Pass data to the template
        return render_template("view_admin.html", user=user, users=users, items=items)
    
    except Exception as ex:
        ic(ex)  # Log the error for debugging
        return "Error loading admin page", 500  # Return an error message if something goes wrong
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
# Restaurant
##############################
@app.get("/restaurant")
@x.no_cache
def view_restaurant():
    if not session.get("user", ""):
        return redirect(url_for("view_login"))
    user = session.get("user")
    
    if len(user.get("roles", "")) > 1:
        return redirect(url_for("view_choose_role"))
    try:
        db, cursor = x.db()  # Connect to the database

        # Fetch all items
        q = """
            SELECT
                i.item_pk, i.item_title, i.item_description, i.item_price, i.item_image,
                u.user_name AS restaurant_name
            FROM items i
            JOIN users u ON i.item_user_fk = u.user_pk
            WHERE i.item_deleted_at = 0
        """
        cursor.execute(q)
        items = cursor.fetchall()  # Fetch all items as a list of dictionaries
        ic(items)  # Debugging output to confirm data
        
        # Pass data to the template
        return render_template("view_restaurant.html", user=user, items=items)
    
    except Exception as ex:
        ic(ex)  # Log the error for debugging
        return "Error loading admin page", 500  # Return an error message if something goes wrong
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
# Choose role
##############################
@app.get("/choose-role")
@x.no_cache
def view_choose_role():
    if not session.get("user", ""):
        return redirect(url_for("view_login"))
    if not len(session.get("user").get("roles")) >= 2:
        return redirect(url_for("view_login"))
    user = session.get("user")
    return render_template("view_choose_role.html", user=user, title="Choose role")

##############################
# View restaurant add an item
##############################
@app.get("/add-item")
@x.no_cache
def view_restaurant_add():
    user = session.get("user", "") # get the user from the session
    if not user:
        return redirect(url_for("view_index")) # redirect if user is not logged in
    return render_template("view_restaurant_add.html", user=user, x=x)

##############################
# View restaurant edit an item
##############################
@app.get("/edit-item/<item_pk>")
@x.no_cache
def view_restaurant_edit(item_pk):
    user = session.get("user", "") # get the user from the session
    if not user:
        return redirect(url_for("view_index")) # redirect if user is not logged in
    try:
        db, cursor = x.db()
        # Fetch the specific item data from the database
        q = """
            SELECT
                i.item_pk, i.item_title, i.item_description, i.item_price, i.item_image,
                u.user_name AS restaurant_name
            FROM items i
            JOIN users u ON i.item_user_fk = u.user_pk
            WHERE i.item_pk = %s AND i.item_deleted_at = 0
        """
        cursor.execute(q, (item_pk,))
        item = cursor.fetchone()

        if not item:
            x.raise_custom_exception("Item not found", 404)
        
        # Store the item_pk in the session
        session["item"] = {"item_pk": item_pk}
        
        # Pass item data to the template
        return render_template("view_restaurant_edit.html", user=user, item=item, x=x)
    
    except Exception as ex:
        ic(ex)
        return "Error loading edit page", 500
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


###################################
###################################
def _________POST_________(): pass
###################################
###################################

##############################
# Login
##############################
@app.post("/login")
@x.no_cache
def login():
    try:
        # validate user input
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()

        # Database query for user authentication
        db, cursor = x.db()
        q = """ SELECT * FROM users
                JOIN users_roles
                ON user_pk = user_role_user_fk
                JOIN roles
                ON role_pk = user_role_role_fk
                WHERE user_email = %s"""
        cursor.execute(q, (user_email,))
        rows = cursor.fetchall()

        if not rows:
            toast = render_template("___toast.html", message="User not registered")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400
        if not check_password_hash(rows[0]["user_password"], user_password):
            toast = render_template("___toast.html", message="Invalid credentials")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 401

        # Process user roles and redirect
        roles = []
        for row in rows:
            roles.append(row["role_name"])
        user = {
            "user_pk": rows[0]["user_pk"],
            "user_name": rows[0]["user_name"],
            "user_last_name": rows[0]["user_last_name"],
            "user_email": rows[0]["user_email"],
            "roles": roles
        }
        ic(user)
        session["user"] = user

        # redirect based on roles
        if len(roles) == 1:
            return f"""<template mix-redirect="/{roles[0]}"></template>"""
        return f"""<template mix-redirect="/choose-role"></template>"""

    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrading</template>", 500
        return "<template>System under maintenance</template>", 500
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
# Signup
##############################
@app.post("/users")
@x.no_cache
def create_user():
    try:
        user_name = x.validate_user_name()
        user_last_name = x.validate_user_last_name()
        user_email = x.validate_user_email()
        user_password = x.validate_user_password()
        hashed_password = generate_password_hash(user_password)
        
        user_pk = str(uuid.uuid4())
        user_created_at = int(time.time())
        user_deleted_at = 0
        user_blocked_at = 0
        user_updated_at = 0
        user_verified_at = 0
        user_verification_key = str(uuid.uuid4())

        db, cursor = x.db()
        q = 'INSERT INTO users VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(q, (user_pk, user_name, user_last_name, user_email, 
                        hashed_password, user_created_at, user_deleted_at, user_blocked_at, 
                        user_updated_at, user_verified_at, user_verification_key))
        
        role_fk = x.CUSTOMER_ROLE_PK
        q_roles = 'INSERT INTO users_roles (user_role_user_fk, user_role_role_fk) VALUES (%s, %s)'
        cursor.execute(q_roles, (user_pk, role_fk))
        db.commit()
        return f"""<template mix-redirect="/login"></template>""", 201
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()        
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            if "users.user_email" in str(ex):
                toast = render_template("___toast.html", message="Email not available")
                return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400
            
            return f"""<template mix-target="#toast" mix-bottom>System upgrating</template>""", 500        
        return f"""<template mix-target="#toast" mix-bottom>System under maintenance</template>""", 500    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
# Logout
##############################
@app.post("/logout")
@x.no_cache
def logout():
    session.pop("user", None)
    return redirect(url_for("view_login"))

##############################
# Create item
##############################
@app.post("/items")
@x.no_cache
def create_item():
    try:
        # Check if the user is logged in
        if not session.get("user"):
            toast = render_template("___toast.html", message="Please login to create an item")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 401
            
        # Extract the user ID from the session
        user_pk = session.get("user").get("user_pk")

        # Validate inputs for the item
        item_title = x.validate_item_title()
        item_description = x.validate_item_description()
        item_price = x.validate_item_price()
        file, item_image = x.validate_item_image()  # Validate and process image file
        item_pk = str(uuid.uuid4())  # Generate a unique identifier for the item        
        item_created_at = int(time.time())
        item_deleted_at = 0
        item_blocked_at = 0
        item_updated_at = 0

        # Save the uploaded image to the designated folder
        file.save(os.path.join(x.UPLOAD_ITEM_FOLDER, item_image))

        # Database connection and insertion
        db, cursor = x.db()

        # Insert the new item into the database
        q = """
            INSERT INTO items (item_pk, item_user_fk, item_title, item_description, item_price, item_image, item_created_at, item_deleted_at, item_blocked_at, item_updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(q, (item_pk, user_pk, item_title, item_description, item_price, item_image, item_created_at, item_deleted_at, item_blocked_at, item_updated_at))

        # Commit the transaction to save the item
        db.commit()

        # Success response
        session["item"] = {"item_pk": item_pk}  # Store item_pk in the session

        toast = render_template("___toast.html", message="Item successfully created.", x=x)
        return f"""<template mix-target="#toast" mix-bottom>{toast}</template>"""
    
    except Exception as ex:
        ic(ex)
        # Rollback the database transaction if there's an error
        if "db" in locals(): db.rollback()

        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message, x=x)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    

        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrading</template>", 500

        return "<template>System under maintenance</template>", 500
    finally:
        # Close database resources
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
##############################
##############################
def _________PUT_________(): pass
##############################
##############################
##############################

##############################
# Update user
##############################
@app.put("/users")
@x.no_cache
def user_update():
    try:
        if not session.get("user"):
            toast = render_template("___toast.html", message="Please login")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 401
        
        user_pk = session.get("user").get("user_pk")
        user_name = x.validate_user_name()
        user_last_name = x.validate_user_last_name()
        user_email = x.validate_user_email()

        user_updated_at = int(time.time())

        db, cursor = x.db()
        q = """ UPDATE users
                SET user_name = %s, user_last_name = %s, user_email = %s, user_updated_at = %s
                WHERE user_pk = %s
            """
        cursor.execute(q, (user_name, user_last_name, user_email, user_updated_at, user_pk))
        if cursor.rowcount != 1: 
            toast = render_template("___toast.html", message="Cannot update user")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 401
                    
        db.commit()
        toast = render_template("___toast.html", message="User updated")
        return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 200
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
        if isinstance(ex, x.mysql.connector.Error):
            if "users.user_email" in str(ex): return "<template>email not available</template>", 400
            return "<template>System upgrating</template>", 500        
        return "<template>System under maintenance</template>", 500    
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
# Block user
##############################
@app.put("/users/block/<user_pk>")
@x.no_cache
def user_block(user_pk):
    try:
        # Check admin role
        if not "admin" in session.get("user").get("roles"):
            return redirect(url_for("view_login"))
        
        user_pk = x.validate_uuid4(user_pk)  # Validate UUID
        user_blocked_at = int(time.time())
        
        # Update the user in the database
        db, cursor = x.db()
        cursor.execute('UPDATE users SET user_blocked_at = %s WHERE user_pk = %s', (user_blocked_at, user_pk))
        if cursor.rowcount != 1:
            return "<template>Could not block user</template>", 400
        db.commit()

        # Respond with the new Unblock button
        btn_unblock = render_template("___btn_unblock_user.html", user={"user_pk": user_pk})
        toast = render_template("___toast.html", message="User blocked successfully")
        return f"""
            <template mix-target='#block-unblock-btn-{user_pk}' mix-replace>{btn_unblock}</template>
            <template mix-target="#toast" mix-bottom>{toast}</template>
        """
    
    except Exception as ex:
        # Handle exceptions and roll back if needed
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException): 
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
# Unblock user
##############################
@app.put("/users/unblock/<user_pk>")
@x.no_cache
def user_unblock(user_pk):
    try:
        # Check admin role
        if not "admin" in session.get("user").get("roles"):
            return redirect(url_for("view_login"))
        
        user_pk = x.validate_uuid4(user_pk)  # Validate UUID
        user_blocked_at = 0  # Unblock the user

        # Update the user in the database
        db, cursor = x.db()
        cursor.execute('UPDATE users SET user_blocked_at = %s WHERE user_pk = %s', (user_blocked_at, user_pk))
        if cursor.rowcount != 1:
            return "<template>Could not unblock user</template>", 400
        db.commit()

        # Respond with the new Block button
        btn_block = render_template("___btn_block_user.html", user={"user_pk": user_pk})
        toast = render_template("___toast.html", message="User unblocked successfully")
        return f"""
            <template mix-target='#block-unblock-btn-{user_pk}' mix-replace>{btn_block}</template>
            <template mix-target="#toast" mix-bottom>{toast}</template>
        """
    
    except Exception as ex:
        # Handle exceptions and roll back if needed
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code
                     
        if isinstance(ex, x.mysql.connector.Error):
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  

    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


##############################
# Update item
##############################
@app.put("/items")
@x.no_cache
def item_update():
    try:
        if not session.get("user"):
            toast = render_template("___toast.html", message="Please login")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 401

        # Get the item_pk from the session
        item_pk = session.get("item").get("item_pk")
        if not item_pk:
            ic("item_pk not found in session")
            x.raise_custom_exception("invalid item", 400)
        
        # validate inputs for form data
        item_title = x.validate_item_title()
        item_description = x.validate_item_description()
        item_price = x.validate_item_price()
        item_updated_at = int(time.time())
        
        # Validate and process the new image if provided
        file, item_image = x.validate_item_image()
        # Save the new image file
        file.save(os.path.join(x.UPLOAD_ITEM_FOLDER, item_image))

        db, cursor = x.db()
        q = """ UPDATE items
                SET item_title = %s, item_description = %s, item_price = %s, item_image = %s, item_updated_at = %s
                WHERE item_pk = %s
            """
        cursor.execute(q, (item_title, item_description, item_price, item_image, item_updated_at, item_pk))

        # Ensure exactly one row was updated
        if cursor.rowcount != 1:
            toast = render_template("___toast.html", message="Cannot update item")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 401
                    
        db.commit()
        toast = render_template("___toast.html", message="Item updated")
        return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 200
    
    except Exception as ex:
        ic(ex)
        # Rollback the database transaction if there's an error
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code    

        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>System upgrading</template>", 500

        return "<template>System under maintenance</template>", 500
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
# Block item
##############################
@app.put("/items/block/<item_pk>")
@x.no_cache
def item_block(item_pk):
    try:
        #check admin role
        if not "admin" in session.get("user").get("roles"): return redirect(url_for("view_login"))
        
        item_pk = x.validate_uuid4(item_pk) #validate uuid
        item_blocked_at = int(time.time())

        # Block the user in the db
        db, cursor = x.db()
        q = 'UPDATE items SET item_blocked_at = %s WHERE item_pk = %s'
        cursor.execute(q, (item_blocked_at, item_pk))
        if cursor.rowcount != 1: 
            toast = render_template("___toast.html", message="Cannot block item")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400            
        db.commit()    

        # Respond with the new Unblock button
        btn_unblock = render_template("___btn_unblock_user.html", item={"item_pk": item_pk})
        toast = render_template("___toast.html", message="Item blocked successfully")
        return f"""
            <template mix-target="#block-unblock-btn-{item_pk}" mix-replace>{btn_unblock}</template>
            <template mix-target="#toast" mix-bottom>{toast}</template>
        """
    
    except Exception as ex:
        # Handle exceptions and roll back if needed
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code        
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
# Unblock item
##############################
@app.put("/items/unblock/<item_pk>")
@x.no_cache
def item_unblock(item_pk):
    try:
        # check admin role
        if not "admin" in session.get("user").get("roles"): return redirect(url_for("view_login"))
        
        item_pk = x.validate_uuid4(item_pk) #validate uuid
        item_blocked_at = 0 # unblock item

        #unblock the user in the db
        db, cursor = x.db()
        q = 'UPDATE items SET item_blocked_at = %s WHERE item_pk = %s'
        cursor.execute(q, (item_blocked_at, item_pk))
        if cursor.rowcount != 1: 
            toast = render_template("___toast.html", message="Cannot unblock item")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400              
        db.commit()

        # Respond with the new Block button
        btn_block = render_template("___btn_block_user.html", item={"item_pk": item_pk})
        toast = render_template("___toast.html", message="Item unblocked successfully")
        return f"""
            <template mix-target="#block-unblock-btn-{item_pk}" mix-replace>{btn_block}</template>
            <template mix-target="#toast" mix-bottom>{toast}</template>
        """
    
    except Exception as ex:
        # handle exceptions and rollback if needed
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code      
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()


###################################
###################################
def ________DELETE________(): pass
###################################
###################################

##############################
# Delete user
##############################
@app.delete("/users/<user_pk>")
@x.no_cache
def user_delete(user_pk):
    try:
        # Check if user is logged
        if not session.get("user", ""): return redirect(url_for("view_login"))
        # Check if it is an admin (can delete all users). If its not the admin role then you can only delete your own user.
        if not "admin" in session.get("user").get("roles") and session.get("user").get("user_pk") != user_pk:
            return redirect(url_for("view_login"))
        user_pk = x.validate_uuid4(user_pk)
        user_deleted_at = int(time.time())
        db, cursor = x.db()
        q = 'UPDATE users SET user_deleted_at = %s WHERE user_pk = %s'
        cursor.execute(q, (user_deleted_at, user_pk))
        if cursor.rowcount != 1:
            toast = render_template("___toast.html", message="Cannot delete user")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400  
        db.commit()

        toast = render_template("___toast.html", message="User deleted")
        return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 200
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code       
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##############################
# Delete item
##############################
@app.delete("/items/<item_pk>")
@x.no_cache
def item_delete(item_pk):
    try:
        # Check if user is logged
        if not session.get("user", ""): return redirect(url_for("view_login"))
        # Check if it is an admin (can delete all items). If its not the admin role then you can only delete your own items.
        if not "admin" in session.get("user").get("roles") and session.get("item").get("item_pk") != item_pk:
            return redirect(url_for("view_login"))
        
        item_pk = x.validate_uuid4(item_pk)
        item_deleted_at = int(time.time())

        db, cursor = x.db()
        q = 'UPDATE items SET item_deleted_at = %s WHERE item_pk = %s'
        cursor.execute(q, (item_deleted_at, item_pk))

        if cursor.rowcount != 1: 
            x.raise_custom_exception("cannot delete item", 400)
            toast = render_template("___toast.html", message="Cannot delete item")
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 400  
        db.commit()

        toast = render_template("___toast.html", message="Item deleted")
        return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", 200
    
    except Exception as ex:
        ic(ex)
        if "db" in locals(): db.rollback()
        if isinstance(ex, x.CustomException):
            toast = render_template("___toast.html", message=ex.message)
            return f"""<template mix-target="#toast" mix-bottom>{toast}</template>""", ex.code         
        if isinstance(ex, x.mysql.connector.Error):
            ic(ex)
            return "<template>Database error</template>", 500        
        return "<template>System under maintenance</template>", 500  
    
    finally:
        if "cursor" in locals(): cursor.close()
        if "db" in locals(): db.close()

##########################
if __name__ == "__main__":
    app.run(debug=True)