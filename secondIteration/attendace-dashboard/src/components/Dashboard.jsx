import React from "react";
import AttendanceCard from "./AttendanceCard";
import AttendanceChart from "./AttendanceChart";
import "./Dashboard.css";

function Dashboard({ data, onLogout }) {
  // Calculate overall statistics
  const totalPresent = data.reduce(
    (sum, subject) => sum + subject.classes_present,
    0,
  );
  const totalClasses = data.reduce(
    (sum, subject) => sum + subject.total_classes,
    0,
  );
  const overallPercentage =
    totalClasses > 0 ? ((totalPresent / totalClasses) * 100).toFixed(2) : 0;

  const subjectsBelow75 = data.filter(
    (s) => s.attendance_percentage < 75,
  ).length;

  const getOverallColor = (percentage) => {
    if (percentage >= 85) return "#10b981";
    if (percentage >= 75) return "#3b82f6";
    if (percentage >= 65) return "#f59e0b";
    return "#ef4444";
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>📚 Your Attendance Dashboard</h1>
        <button onClick={onLogout} className="logout-btn">
          ← Back to Login
        </button>
      </div>

      {/* Overall Stats */}
      <div className="stats-container">
        <div
          className="stat-card"
          style={{ borderLeftColor: getOverallColor(overallPercentage) }}
        >
          <div className="stat-icon">📊</div>
          <div className="stat-content">
            <h3>Overall Attendance</h3>
            <p
              className="stat-number"
              style={{ color: getOverallColor(overallPercentage) }}
            >
              {overallPercentage}%
            </p>
            <p className="stat-detail">
              {totalPresent} / {totalClasses} classes
            </p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">📖</div>
          <div className="stat-content">
            <h3>Total Subjects</h3>
            <p className="stat-number">{data.length}</p>
            <p className="stat-detail">This semester</p>
          </div>
        </div>

        <div
          className="stat-card"
          style={{
            borderLeftColor: subjectsBelow75 > 0 ? "#ef4444" : "#10b981",
          }}
        >
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <h3>Below 75%</h3>
            <p
              className="stat-number"
              style={{ color: subjectsBelow75 > 0 ? "#ef4444" : "#10b981" }}
            >
              {subjectsBelow75}
            </p>
            <p className="stat-detail">
              {subjectsBelow75 === 0 ? "Great job!" : "Need attention"}
            </p>
          </div>
        </div>
      </div>

      {/* Chart */}
      <AttendanceChart data={data} />

      {/* Subject Cards */}
      <div className="cards-section">
        <h2>📋 Subject Details</h2>
        <div className="cards-grid">
          {data.map((subject, index) => (
            <AttendanceCard key={index} subject={subject} />
          ))}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
