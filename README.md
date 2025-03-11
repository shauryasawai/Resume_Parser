# Django App README

## Introduction

This README provides a step-by-step guide on how to install and set up a Django application. It also includes instructions on how to create and use a virtual environment, and how to install all necessary dependencies.

## Prerequisites

Before starting, ensure you have the following installed:

- Python (version 3.x)
- pip (Python package installer)
- virtualenv

## Installation Steps

### Step 1: Clone the Repository

Clone the Django application repository to your local machine using the following command:

```bash
git clone <repository-url>
```

Replace `<repository-url>` with the URL of your repository.

### Step 2: Navigate to the Project Directory

Change into the directory of the cloned repository:

```bash
cd <project-directory>
```

Replace `<project-directory>` with the name of your project directory.

### Step 3: Create a Virtual Environment

Create a virtual environment using `virtualenv`:

```bash
virtualenv my_env
```

This will create a virtual environment named `my_env`.

### Step 4: Activate the Virtual Environment

Activate the virtual environment using the following command:

- On Windows:
  ```bash
  my_env\Scripts\activate
  ```
- On macOS and Linux:
  ```bash
  source venv/bin/activate
  ```

### Step 5: Install Dependencies

With the virtual environment activated, install the required dependencies using `pip`:

```bash
pip install -r full-requirement.txt
```

This will install all the dependencies listed in the `full-requirements.txt` file.

### Step 6: Run Migrations

Apply the database migrations:

```bash
python manage.py migrate
```

### Step 7: Start the Development Server

Run the development server to start the application:

```bash
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000/` in your web browser.

## Deactivating the Virtual Environment

To deactivate the virtual environment, simply run:

```bash
deactivate
```

## Additional Notes

- Ensure you have the latest version of `pip` by running `pip install --upgrade pip`.
- If you encounter any issues during the installation process, check the error messages for guidance and ensure all prerequisites are met.
