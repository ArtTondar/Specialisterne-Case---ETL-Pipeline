import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# Load environment variables from .env file
load_dotenv()

# --- Load environment parameters ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")  # Default PostgreSQL port
DB_NAME = os.getenv("DB_NAME")



# --- Build database URL ---
# This function constructs the database URL in the format expected by SQLAlchemy.
# It uses the environment variables loaded from the .env file. This allows for flexible configuration without hardcoding sensitive information in the code.
# The URL format for PostgreSQL is: postgresql://user:password@host:port/database
# By using a function, we can easily modify the URL construction logic in one place if needed (e.g., to support different database types or additional parameters).
# Note: In a production environment, you might want to add error handling here to ensure that all required environment variables are set and valid.
# For example, you could raise an exception if any of the required variables are missing or if the port is not a valid number.
# Additionally, you might want to consider using a more secure way to handle database credentials, such as using a secrets manager or environment variables set at the system level rather than in a .env file.
# For the purpose of this exercise, we will keep it simple and use the .env file for configuration.
# Using the os.getenv() function allows us to easily access the environment variables and provides a default value for the port if it is not set. This makes our code more robust and adaptable to different environments (e.g., development, testing, production) without requiring changes to the codebase.
# but it makes 7 calls to os.getenv() which is not the most efficient way to build the URL. In a real application, you might want to optimize this by storing the values in variables or using a configuration object.
# If the environment variables are changed after the URL is built, the get_database_url() function will reflect those changes when called, while the DB_URL variable (if we had defined it) would not, since it would be set at the time of module loading.
def get_database_url_from_environment() -> str:
    return (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )

# --- Build database URL with global variables ---
# This is an alternative way to build the database URL using global variables. It achieves the same result as the get_database_url() function but does so by first loading the environment variables into global variables and then constructing the URL using those variables.
# This approach can be more efficient if you need to access the database URL multiple times throughout your application, as it avoids the overhead of calling os.getenv() multiple times. However, it also means that the database URL is constructed at the time the module is loaded, which may not be ideal if you want to allow for dynamic configuration changes at runtime.
# DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
def get_database_url_from_globals() -> str:
    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"



# --- Create engine and sessionmaker ---
engine = create_engine(get_database_url_from_globals(), echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)



# --- Utility function to get a new database session ---
def get_session() -> Session:
    """Returns a new database session. Use with 'with' statement for safe handling and remember to close the session after use."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()



# This line is used to test whether the import of .env is working properly or not. It should be removed in production code, as it is not the intended use of this file.
#print(f"Database connection established successfully with user {DB_USER}.")



# --- TESTING THE CONNECTION ---
# Test the connection and demonstrate different result fetching methods 
# Note: In SQLAlchemy, once you fetch results using one method, the cursor is advanced.
# This means that if you use fetchone() first, the next call to scalar() will return None because there are no more rows to fetch.
# To demonstrate the different methods properly, we will execute the query multiple times to reset the cursor for each method.
# The test should not be exexuted in this file, but rather in a separate test file (or when the connection is actually used eg. main.py in this case), as this is not the intended use of this file. 
# This is just for demonstration and learning purposes.
# the if statement ensures that this code only runs when this file is executed directly, and not when it is imported as a module in another file.
if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            # 1️ Eksekver en simpel query
            result = conn.execute(text("SELECT 1"))
            print("Database connection test successful.\n")
        
            # --- FETCHONE ---
            # fetchone() returnerer næste række som en tuple
            row = result.fetchone()  
            print("1. Using fetchone():", row)  # => (1,)
        
            # --- SCALAR ---
            # scalar() returnerer første kolonne i næste række
            # OBS: cursoren er allerede rykket frem af fetchone(), så her får vi None
            value = result.scalar()
            print("2. Using scalar() after fetchone():", value)  # => None
        
            # --- LØSNING: GEM RESULTATET FØRST ---
            result = conn.execute(text("SELECT 1"))  # gen-eksekver query
            row = result.fetchone()
            print("\n3. Using fetchone() with saved row:", row)      # => (1,)
            print("   Using scalar() on saved row:", row[0])         # => 1

            # --- FETCHALL ---
            # fetchall() returnerer alle rækker som liste af tuples
            result = conn.execute(text("SELECT 1"))
            all_rows = result.fetchall()
            print("\n4. Using fetchall():", all_rows)               # => [(1,)]
            print("   Access first row, first column (scalar style):", all_rows[0][0])  # => 1
        
            # --- FIRST ---
            # first() returnerer første række eller None hvis ingen rækker
            result = conn.execute(text("SELECT 1"))
            first_row = result.first()
            print("\n5. Using first():", first_row)                # => (1,)
            print("   Access first column (scalar style):", first_row[0])  # => 1
        
            # --- ITERATION ---
            result = conn.execute(text("SELECT 1"))
            print("\n6. Using iteration over Result:")
            for r in result:
                print("   Row:", r, "Scalar-style:", r[0])       # => (1,) og 1

            # --- ALL-AT-ONCE (scalar_all) ---
            # scalar_all() henter alle første kolonner som liste
            result = conn.execute(text("SELECT 1"))
            scalars = result.scalars().all()
            print("\n7. Using scalars().all():", scalars)        # => [1]

    except Exception as e:
        print("Database connection test failed.")
        print("Error:", e)
