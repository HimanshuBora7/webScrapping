import React, { useState } from "react";
import "./LoginForm.css";

function LoginForm({ onSubmit, loading }) {
  const [formData, setFormData] = useState({
    rollNo: "",
    password: "",
    captcha: "",
    year: "0",
    semester: "0",
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>📊 Attendance Dashboard</h1>
        <p className="subtitle">View your attendance data</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Roll Number</label>
            <input
              type="text"
              name="rollNo"
              value={formData.rollNo}
              onChange={handleChange}
              placeholder="202300123"
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter password"
              required
            />
          </div>

          <div className="form-group">
            <label>CAPTCHA</label>
            <input
              type="text"
              name="captcha"
              value={formData.captcha}
              onChange={handleChange}
              placeholder="Enter CAPTCHA"
              required
            />
            <small>Note: You'll need to run nsu3.py manually for now</small>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Year</label>
              <select name="year" value={formData.year} onChange={handleChange}>
                <option value="0">1st Year</option>
                <option value="1">2nd Year</option>
                <option value="2">3rd Year</option>
                <option value="3">4th Year</option>
              </select>
            </div>

            <div className="form-group">
              <label>Semester</label>
              <select
                name="semester"
                value={formData.semester}
                onChange={handleChange}
              >
                <option value="0">1st Sem</option>
                <option value="1">2nd Sem</option>
                <option value="2">3rd Sem</option>
                <option value="3">4th Sem</option>
                <option value="4">5th Sem</option>
                <option value="5">6th Sem</option>
                <option value="6">7th Sem</option>
                <option value="7">8th Sem</option>
              </select>
            </div>
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? "⏳ Loading..." : "🚀 Get Attendance"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default LoginForm;
