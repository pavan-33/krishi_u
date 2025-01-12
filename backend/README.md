---

# Land Rental Project

This project is a backend application for managing land rentals. It provides an API for farmers and landlords to connect, manage crops, and handle image uploads.

## Prerequisites

Ensure you have the following tools installed:

- Python 3.8 or above
- pip (Python package manager)
- Git (optional, for version control)

## Getting Started

### 1. Unzip the Project

If you received the project in a ZIP file:

1. Extract the ZIP file to a directory on your computer.
   ```bash
   unzip Land_Rental_Project.zip -d ./Land_Rental_Project
   ```

2. Navigate into the project directory:
   ```bash
   cd Land_Rental_Project
   ```

---

### 2. Install Dependencies

1. **Create a Virtual Environment (optional but recommended)**:

   It's best to use a virtual environment to isolate your project's dependencies.

   ```bash
   python -m venv venv
   ```

2. **Activate the Virtual Environment**:

   - **For Windows**:
     ```bash
     venv\Scripts\activate
     ```

   - **For macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

3. **Navigate to project directory**
    ```bash
   cd backend
   ```


4. **Install Project Dependencies**:

   Install the required packages listed in `requirements.txt` using pip:
   ```bash
   pip install -r requirements.txt
   ```

---

### 3. Database Setup

1. **Run Database Migrations**:

   Alembic is used for database migrations. To apply the migrations, follow these steps:

   - Make sure that your database is set up correctly (SQLite or another DB).

   - Run the following command to upgrade the database schema to the latest version:
     ```bash
     alembic upgrade head
     ```

   This command applies the migration scripts to the database and sets up the required tables.

   If you need to generate a new migration script (after modifying models), use:
   ```bash
   alembic revision --autogenerate -m "Description of the change"
   ```

   Then apply the migration:
   ```bash
   alembic upgrade head
   ```

---

### 4. Running the Application

1. **Run the FastAPI Application**:

   Start the FastAPI server using `uvicorn`:
   
   ```bash
   uvicorn main:app --reload --port=8000
   ```

   This command runs the app in development mode with auto-reload enabled. The FastAPI app will be hosted on `http://localhost:8000`.

---

### 5. Accessing the API

Once the server is running, you can access the API documentation via Swagger.

1. **Swagger UI**: Open your browser and go to:
   ```
   http://localhost:8000/docs
   ```

   This is the interactive Swagger UI where you can view all available endpoints, test API calls, and see request/response examples.

2. **ReDoc UI**: For an alternative API documentation format, you can go to:
   ```
   http://localhost:8000/redoc
   ```

---


### 9. Troubleshooting

- **If `alembic upgrade head` fails**: Ensure your migration files are correct, and try running the migration manually.
- **Image Upload Issues**: Ensure that the `media/` folder is writable and properly served by the web server. If you're using Nginx or Apache, configure static file serving to make uploaded images accessible.


### 10. Development Tips

- **Running in Development Mode**: Use the `--reload` flag with `uvicorn` for automatic code reloading:
  ```bash
  uvicorn main:app --reload
  ```

- **Testing**: Ensure you write unit tests for critical parts of the application. You can use `pytest` for testing.


