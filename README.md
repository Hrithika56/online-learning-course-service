# Online Learning Management System - Course Service

This repository contains the **Course Service** of an Online Learning Management System developed using a microservices architecture.

## My Contribution

I developed the **Course Service**, which is responsible for managing course information.

## Technologies Used

- Python
- Flask
- SQLite
- REST API
- Git & GitHub

## Features

- Create a new course
- Retrieve all courses
- Retrieve a course by ID
- Update course information
- Delete a course
- API versioning
- Separate database for the Course Service

## API Endpoints

### API Version 1

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/courses` | Create a new course |
| GET | `/api/v1/courses` | Retrieve all courses |
| GET | `/api/v1/courses/<course_id>` | Retrieve a course by ID |
| PUT | `/api/v1/courses/<course_id>` | Update a course |
| DELETE | `/api/v1/courses/<course_id>` | Delete a course |

### API Version 2

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v2/courses` | Retrieve courses with total course count |

## Database

The Course Service uses a separate **SQLite database** named `course.db`.

The database contains course information such as:

- Course ID
- Title
- Description
- Instructor
- Category
- Duration
- Price
- Status

The database file is excluded from Git using `.gitignore`.

## How to Run

### 1. Navigate to the Course Service

```powershell
cd course-service
