import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authApi, getApiError } from "../services/api.js";

export default function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await authApi.login(form);
      localStorage.setItem("token", data.access_token);
      localStorage.setItem("user", JSON.stringify(data.user));
      navigate("/dashboard");
    } catch (err) {
      setError(getApiError(err, "Login failed"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <section className="auth-art">
        <h1>Turn study files into clear notes.</h1>
        <p>Upload documents, generate short or detailed AI notes, and keep every saved note in your profile.</p>
      </section>
      <form className="auth-card" onSubmit={submit}>
        <h2>Welcome back</h2>
        <label>
          Email
          <input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </label>
        <label>
          Password
          <input type="password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="primary wide" disabled={loading}>{loading ? "Signing in..." : "Login"}</button>
        <p className="muted">No account? <Link to="/signup">Create one</Link></p>
      </form>
    </main>
  );
}
