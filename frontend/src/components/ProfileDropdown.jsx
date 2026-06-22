import { Mail, UserRound } from "lucide-react";

export default function ProfileDropdown() {
  const user = JSON.parse(localStorage.getItem("user") || "null");
  return (
    <section className="profile-panel">
      <div className="profile-avatar">
        <UserRound size={30} />
      </div>
      <div>
        <h3>{user?.name || "Student"}</h3>
        <p>
          <Mail size={15} />
          {user?.email || "student@example.com"}
        </p>
      </div>
    </section>
  );
}
