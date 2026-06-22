import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authApi, getApiError } from "../services/api.js";

export default function Signup() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await authApi.signup(form);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      navigate("/dashboard");
    } catch (err) {
      setError(getApiError(err, "Signup failed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-art">
        <h1>Your personal AI study desk.</h1>
        <p>Extract text from notes, handouts, and images, then save organized summaries for revision.</p>
      </section>
      <form className="auth-card" onSubmit={submit}>
        <h2>Create account</h2>
        <label>
          Name
          <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        </label>
        <label>
          Email
          <input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </label>
        <label>
          Password
          <input type="password" minLength={6} required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="primary wide" disabled={loading}>{loading ? "Creating..." : "Signup"}</button>
        <p className="muted">Already have an account? <Link to="/login">Login</Link></p>
      </form>
    </main>
  );
}
