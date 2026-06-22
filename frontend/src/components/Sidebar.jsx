import { FileUp, LibraryBig, Sparkles } from "lucide-react";
import { NavLink } from "react-router-dom";

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <NavLink to="/dashboard">
        <FileUp size={19} />
        Upload
      </NavLink>
      <NavLink to="/generated">
        <Sparkles size={19} />
        Generated
      </NavLink>
      <NavLink to="/notes">
        <LibraryBig size={19} />
        Profile Notes
      </NavLink>
    </aside>
  );
}
