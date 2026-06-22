import { BookOpen, LogOut, UserRound } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem("user") || "null");

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };

  return (
    <header className="navbar">
      <Link className="brand" to="/dashboard">
        <BookOpen size={26} />
        <span>AI Notes</span>
      </Link>
      <nav className="nav-links">
        <Link to="/dashboard">Generate</Link>
        <Link to="/notes">My Notes</Link>
      </nav>
      <div className="nav-user">
        <UserRound size={18} />
        <span>{user?.name || "Student"}</span>
        <button className="icon-button" onClick={logout} title="Logout" aria-label="Logout">
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
