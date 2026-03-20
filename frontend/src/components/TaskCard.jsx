/**
 * TaskCard.jsx — Displays a single task with actions
 *
 * Concepts: Props, conditional rendering, event handling, React state
 */

const STATUS_LABELS = {
  todo: "To Do",
  in_progress: "In Progress",
  done: "Done",
};

const STATUS_BADGE = {
  todo: "badge-todo",
  in_progress: "badge-prog",
  done: "badge-done",
};

const PRIORITY_BADGE = {
  high: "badge-high",
  medium: "badge-medium",
  low: "badge-low",
};

const STATUS_NEXT = {
  todo: "in_progress",
  in_progress: "done",
  done: null,
};

const STATUS_NEXT_LABEL = {
  todo: "▶ Start",
  in_progress: "✔ Complete",
};

export default function TaskCard({ task, onUpdate, onDelete }) {
  const isDone = task.status === "done";

  const handleStatusAdvance = () => {
    const nextStatus = STATUS_NEXT[task.status];
    if (nextStatus) onUpdate(task.id, { status: nextStatus });
  };

  return (
    <div className={`task-card priority-${task.priority} ${isDone ? "done-card" : ""}`}>
      {/* Header: title + priority badge */}
      <div className="task-card-header">
        <span className={`task-title ${isDone ? "strikethrough" : ""}`}>
          {task.title}
        </span>
        <span className={`badge ${PRIORITY_BADGE[task.priority]}`}>
          {task.priority}
        </span>
      </div>

      {/* Description */}
      {task.description && (
        <p className="task-desc">{task.description}</p>
      )}

      {/* Status + Due Date badges */}
      <div className="task-meta">
        <span className={`badge ${STATUS_BADGE[task.status]}`}>
          {STATUS_LABELS[task.status]}
        </span>
        {task.due_date && (
          <span style={{ fontSize: "0.75rem", color: "var(--text-dim)" }}>
            📅 {new Date(task.due_date).toLocaleDateString()}
          </span>
        )}
        {task.completed_at && (
          <span style={{ fontSize: "0.75rem", color: "var(--success)" }}>
            ✓ {new Date(task.completed_at).toLocaleDateString()}
          </span>
        )}
      </div>

      {/* Actions */}
      <div className="task-actions">
        {!isDone && (
          <button
            className="btn btn-ghost btn-sm"
            onClick={handleStatusAdvance}
            title="Advance status"
          >
            {STATUS_NEXT_LABEL[task.status]}
          </button>
        )}
        <button
          className="btn btn-danger btn-sm"
          onClick={() => onDelete(task.id)}
          style={{ marginLeft: "auto" }}
          title="Delete task"
        >
          🗑
        </button>
      </div>
    </div>
  );
}
