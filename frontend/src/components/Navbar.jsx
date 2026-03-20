/**
 * Navbar.jsx — Top navigation bar
 * Shows app branding, current user, and logout button.
 */

import { authAPI } from "../api";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

export default function Navbar({ user }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("token");
    toast.success("Logged out successfully");
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        {/* Brand */}
        <div className="navbar-brand">
          <div className="brand-icon">✅</div>
          <span>Task Manager Pro</span>
        </div>

        {/* Right side */}
        <div className="navbar-right">
          {user && (
            <div className="navbar-user">
              <div className="avatar">
                {user.username?.[0]?.toUpperCase()}
              </div>
              <span style={{ fontSize: "0.85rem" }}>{user.username}</span>
            </div>
          )}
          <button className="btn btn-ghost btn-sm" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
