import React, { useState } from "react";
import axios from "axios";
import LoginForm from "./components/LoginForm";
import Dashboard from "./components/Dashboard";
import "./App.css";

function App() {
  const [attendanceData, setAttendanceData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLogin = async (formData) => {
    setLoading(true);
    setError(null);

    try {
      // Call your Flask API
      const response = await axios.get("http://localhost:5000/api/attendance");

      if (response.data.success) {
        setAttendanceData(response.data.data);
      } else {
        setError(response.data.error || "Failed to fetch attendance");
      }
    } catch (err) {
      console.error("Error:", err);
      setError(
        "Failed to connect to server. Make sure Flask API is running on port 5000.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setAttendanceData(null);
    setError(null);
  };

  return (
    <div className="App">
      {error && (
        <div className="error-banner">
          ❌ {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {!attendanceData ? (
        <LoginForm onSubmit={handleLogin} loading={loading} />
      ) : (
        <Dashboard data={attendanceData} onLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;
