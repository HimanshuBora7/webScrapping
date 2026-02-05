import React from "react";
import "./AttendanceCard.css";

function AttendanceCard({ subject }) {
  const getColorClass = (percentage) => {
    if (percentage >= 85) return "excellent";
    if (percentage >= 75) return "good";
    if (percentage >= 65) return "warning";
    return "danger";
  };

  const calculateNeededClasses = (percentage, total) => {
    if (percentage >= 75) return 0;
    const attended = Math.round((percentage / 100) * total);
    const needed = Math.ceil((0.75 * (total + 1) - attended) / 0.25);
    return Math.max(0, needed);
  };

  const colorClass = getColorClass(subject.attendance_percentage);
  const needed = calculateNeededClasses(
    subject.attendance_percentage,
    subject.total_classes,
  );

  return (
    <div className={`attendance-card ${colorClass}`}>
      <div className="card-header">
        <h3>{subject.subject_code}</h3>
        <span className={`percentage-badge ${colorClass}`}>
          {subject.attendance_percentage.toFixed(1)}%
        </span>
      </div>

      <p className="subject-name">{subject.subject_name}</p>

      <div className="stats">
        <div className="stat">
          <span className="stat-label">Present</span>
          <span className="stat-value">{subject.classes_present}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Absent</span>
          <span className="stat-value">{subject.classes_absent}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Total</span>
          <span className="stat-value">{subject.total_classes}</span>
        </div>
      </div>

      {needed > 0 && (
        <div className="warning-message">
          ⚠️ Need {needed} more classes to reach 75%
        </div>
      )}
    </div>
  );
}

export default AttendanceCard;
