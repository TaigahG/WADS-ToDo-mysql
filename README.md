| Endpoint           | Method | Description                           | Request Body                                        | Response Body                                   |
|--------------------|--------|---------------------------------------|-----------------------------------------------------|-------------------------------------------------|
| `/register`        | POST   | Register a new user                   | `{ "firebase_uid": "uid123", "email": "user@example.com", "username": "user" }` | `{ "firebase_uid": "uid123", "email": "user@example.com", "username": "user" }` |
| `/login`           | POST   | Log in a user                         | `{ "firebase_uid": "uid123" }`                       | `{ "firebase_uid": "uid123", "email": "user@example.com", "username": "user" }` |
| `/tasks`           | POST   | Create a new task                     | `{ "title": "New Task", "completed": false, "user_id": 1 }` | `{ "id": 1, "title": "New Task", "completed": false, "user_id": 1 }` |
| `/tasks`           | GET    | Retrieve all tasks                    | None                                                | `[ { "id": 1, "title": "Task One", "completed": false, "user_id": 1 }, ... ]` |
| `/tasks/{task_id}` | GET    | Retrieve a single task by its ID      | None                                                | `{ "id": 1, "title": "Task One", "completed": false, "user_id": 1 }` |
| `/tasks/{task_id}` | PUT    | Update a task's text and completion status | `{ "title": "Updated Task", "completed": true }` | `{ "id": 1, "title": "Updated Task", "completed": true, "user_id": 1 }` |
| `/tasks/{task_id}` | DELETE | Delete a task                         | None                                                | `204 No Content`                                |
