/**
 * Dashboard.jsx — Main application page
 *
 * Concepts:
 * - React hooks: useState, useEffect, useCallback
 * - Async data fetching on mount
 * - CRUD operations wired to API methods
 * - Filtering tasks client-side
 * - Modal for task creation form
 * - Lifting state up
 */

import { useState, useEffect, useCallback } from "react";
import toast from "react-hot-toast";
import { authAPI, tasksAPI } from "../api";
import Navbar from "../components/Navbar";
import TaskCard from "../components/TaskCard";

const FILTERS = [
  { label: "All", value: "" },
  { label: "To Do", value: "todo" },
  { label: "In Progress", value: "in_progress" },
  { label: "Done", value: "done" },
];

export default function Dashboard() {
  const [user, setUser]         = useState(null);
  const [tasks, setTasks]       = useState([]);
  const [stats, setStats]       = useState({ todo: 0, in_progress: 0, done: 0, total: 0 });
  const [filter, setFilter]     = useState("");
  const [loading, setLoading]   = useState(true);
  const [showModal, setShowModal] = useState(false);

  // ── New Task Form State ─────────────────────────────────
  const [newTask, setNewTask] = useState({
    title: "", description: "", priority: "medium", due_date: ""
  });
  const [creating, setCreating] = useState(false);

  // ── Fetch current user ───────────────────────────────────
  useEffect(() => {
    authAPI.getMe()
      .then(res => setUser(res.data))
      .catch(() => {});
  }, []);

  // ── Fetch tasks & stats ──────────────────────────────────
  const fetchData = useCallback(async () => {
    try {
      const [tasksRes, statsRes] = await Promise.all([
        tasksAPI.list(1, 50, filter || null),
        tasksAPI.stats(),
      ]);
      setTasks(tasksRes.data.tasks);
      setStats(statsRes.data);
    } catch {
      toast.error("Failed to load tasks");
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    setLoading(true);
    fetchData();
  }, [fetchData]);

  // ── Create Task ──────────────────────────────────────────
  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newTask.title.trim()) return;
    setCreating(true);
    try {
      const payload = { ...newTask };
      if (!payload.due_date) delete payload.due_date;
      await tasksAPI.create(payload);
      toast.success("Task created! ✅");
      setShowModal(false);
      setNewTask({ title: "", description: "", priority: "medium", due_date: "" });
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to create task");
    } finally {
      setCreating(false);
    }
  };

  // ── Update Task ──────────────────────────────────────────
  const handleUpdate = async (id, data) => {
    try {
      await tasksAPI.update(id, data);
      toast.success("Task updated! 🔄");
      fetchData();
    } catch {
      toast.error("Failed to update task");
    }
  };

  // ── Delete Task ──────────────────────────────────────────
  const handleDelete = async (id) => {
    if (!window.confirm("Delete this task?")) return;
    try {
      await tasksAPI.delete(id);
      toast.success("Task deleted");
      fetchData();
    } catch {
      toast.error("Failed to delete task");
    }
  };

  // ── Render ───────────────────────────────────────────────
  return (
    <>
      <Navbar user={user} />

      <main className="dashboard">
        {/* Header */}
        <div className="dashboard-header">
          <div>
            <h2>My Tasks</h2>
            <p>
              Welcome back, <strong>{user?.username}</strong>!
              You have <strong>{stats.todo}</strong> tasks to do.
            </p>
          </div>
          <button
            id="new-task-btn"
            className="btn btn-primary"
            onClick={() => setShowModal(true)}
          >
            + New Task
          </button>
        </div>

        {/* Stats Cards */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon todo">📋</div>
            <div className="stat-info">
              <span>To Do</span>
              <strong>{stats.todo}</strong>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon prog">⚡</div>
            <div className="stat-info">
              <span>In Progress</span>
              <strong>{stats.in_progress}</strong>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon done">✅</div>
            <div className="stat-info">
              <span>Done</span>
              <strong>{stats.done}</strong>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon total">📊</div>
            <div className="stat-info">
              <span>Total</span>
              <strong>{stats.total}</strong>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="filters">
          {FILTERS.map(f => (
            <button
              key={f.value}
              className={`filter-btn ${filter === f.value ? "active" : ""}`}
              onClick={() => setFilter(f.value)}
            >
              {f.label}
            </button>
          ))}
        </div>

        {/* Task Grid */}
        {loading ? (
          <div className="loading-screen" style={{ minHeight: "200px" }}>
            <div className="spinner" style={{ width: 32, height: 32, borderWidth: 3 }} />
            <span>Loading tasks...</span>
          </div>
        ) : tasks.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <h3>No tasks yet</h3>
            <p>Click <strong>"+ New Task"</strong> to get started!</p>
          </div>
        ) : (
          <div className="tasks-grid">
            {tasks.map(task => (
              <TaskCard
                key={task.id}
                task={task}
                onUpdate={handleUpdate}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </main>

      {/* New Task Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={(e) => e.target === e.currentTarget && setShowModal(false)}>
          <div className="modal">
            <div className="modal-header">
              <h3>Create New Task</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => setShowModal(false)}>✕</button>
            </div>

            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label htmlFor="task-title">Title *</label>
                <input
                  id="task-title"
                  type="text"
                  placeholder="What needs to be done?"
                  value={newTask.title}
                  onChange={e => setNewTask({ ...newTask, title: e.target.value })}
                  required
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label htmlFor="task-desc">Description</label>
                <textarea
                  id="task-desc"
                  placeholder="Optional details..."
                  value={newTask.description}
                  onChange={e => setNewTask({ ...newTask, description: e.target.value })}
                />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                <div className="form-group">
                  <label htmlFor="task-priority">Priority</label>
                  <select
                    id="task-priority"
                    value={newTask.priority}
                    onChange={e => setNewTask({ ...newTask, priority: e.target.value })}
                  >
                    <option value="low">🟢 Low</option>
                    <option value="medium">🟡 Medium</option>
                    <option value="high">🔴 High</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="task-due">Due Date</label>
                  <input
                    id="task-due"
                    type="date"
                    value={newTask.due_date}
                    onChange={e => setNewTask({ ...newTask, due_date: e.target.value })}
                    style={{ colorScheme: "dark" }}
                  />
                </div>
              </div>

              <div className="modal-footer">
                <button type="button" className="btn btn-ghost" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button
                  id="create-task-submit"
                  type="submit"
                  className="btn btn-primary"
                  disabled={creating}
                >
                  {creating ? <span className="spinner" /> : "Create Task"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
