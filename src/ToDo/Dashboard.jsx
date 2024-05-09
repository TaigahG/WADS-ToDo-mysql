import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./App.css";

function App() {
  const [todos, setTodos] = useState([]);
  const [newItem, setItem] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [editText, setEditText] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const navigate = useNavigate();

  async function fetchWithAuth(url, options = {}) {
    const token = await firebase.auth().currentUser.getIdToken(true);
    const headers = new Headers(options.headers || {});
    headers.set('Authorization', `Bearer ${token}`);
    return fetch(url, { ...options, headers });
}


  useEffect(() => {
    fetch('http://localhost:8000/tasks')
      .then(response => response.json())
      .then(data => {
        setTodos(data);
      })
      .catch(error => console.error('Error loading the tasks:', error));
  }, []);

  async function handleAddOrUpdateTodo(e) {
    e.preventDefault();
    const url = editingId ? `http://localhost:8000/tasks/${editingId}` : 'http://localhost:8000/tasks';
    const method = editingId ? 'PUT' : 'POST';
    const body = JSON.stringify({
      title: editingId ? editText : newItem,
      completed: false, 
      user_id: 1
    });
    try {
      const response = await fetch(url, {
      method: method,
      headers: {
        'Content-Type': 'application/json'
      },
      body: body
    });

    if (response.ok) {
      const updatedTodo = await response.json();
      setTodos(prev => editingId ? prev.map(todo => todo.id === editingId ? updatedTodo : todo) : [...prev, updatedTodo]);
      setEditingId(null);
      setEditText("");
      setItem("");
    } else {
      console.error('Failed to add or update task');
      const errorResponse = await response.text();  // Additional error handling
      console.error('Error Response:', errorResponse);    }
    } catch (error) {
      console.error('Failed:', error);
    }
    
  }

  async function handleToggleCompleted(taskId) {
    const response = await fetch(`http://localhost:8000/tasks/${taskId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      const data = await response.json();
      setTodos(prevTodos => prevTodos.map(todo => 
        todo.id === taskId ? {...todo, completed: !todo.completed} : todo
      ));
    } else {
      console.error('Failed to toggle task completion status');
    }
  }

  async function handleDelete(id) {
    const response = await fetch(`http://localhost:8000/tasks/${id}`, {
      method: 'DELETE',
    });

    if (response.ok) {
      setTodos(prev => prev.filter(todo => todo.id !== id));
    } else {
      console.error('Failed to delete task');
    }
  }

  function handleEdit(todo) {
    setEditingId(todo.id);
    setEditText(todo.title);
  }

  const handleInputChange = (e) => {
    if (editingId) {
      setEditText(e.target.value);
    } else {
      setItem(e.target.value);
    }
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const filteredTodos = todos.filter((todo) => todo.title.toLowerCase().includes(searchQuery.toLowerCase()));

  return (
    <div className="app-container">
      <header className="header">
        <h1>ToDo List</h1>
        <input type="text" className="search-input" placeholder="Search todos..." value={searchQuery} onChange={handleSearchChange} />
      </header>
      <div className="actions">
        <form className="new-item-form" onSubmit={handleAddOrUpdateTodo}>
          <input type="text" className="new-todo-input" placeholder={editingId ? "Edit todo..." : "Add new item..."} value={editingId ? editText : newItem} onChange={handleInputChange} />
          <button className="btn" type="submit">
            {editingId ? "Update" : "Add"}
          </button>
        </form>
      </div>
      <div className="todo-grid">
        {filteredTodos.map((todo) => (
          <div key={todo.id} className="todo-card">
            <div className="todo-text">{todo.title}</div>
            <input type="checkbox" className="todo-checkbox" checked={todo.completed} onChange={() => handleToggleCompleted(todo.id, todo.completed)} />
            <div className="todo-actions">
              <button className="btn" onClick={() => handleEdit(todo)}>
                Edit
              </button>
              <button className="btn btn-danger" onClick={() => handleDelete(todo.id)}>
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
