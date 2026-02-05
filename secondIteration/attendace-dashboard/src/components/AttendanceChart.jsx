import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from "recharts";

function AttendanceChart({ data }) {
  // Transform data for the chart
  const chartData = data.map((subject) => ({
    name: subject.subject_code,
    percentage: subject.attendance_percentage,
    present: subject.classes_present,
    absent: subject.classes_absent,
  }));

  // Color based on percentage
  const getColor = (percentage) => {
    if (percentage >= 85) return "#10b981";
    if (percentage >= 75) return "#3b82f6";
    if (percentage >= 65) return "#f59e0b";
    return "#ef4444";
  };

  return (
    <div
      style={{
        width: "100%",
        height: 400,
        background: "white",
        padding: "20px",
        borderRadius: "12px",
        boxShadow: "0 4px 6px rgba(0,0,0,0.1)",
      }}
    >
      <h2 style={{ marginTop: 0, marginBottom: 20, color: "#333" }}>
        📊 Subject-wise Attendance
      </h2>
      <ResponsiveContainer width="100%" height="90%">
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis
            domain={[0, 100]}
            label={{
              value: "Percentage (%)",
              angle: -90,
              position: "insideLeft",
            }}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                return (
                  <div
                    style={{
                      background: "white",
                      padding: "10px",
                      border: "1px solid #ccc",
                      borderRadius: "8px",
                    }}
                  >
                    <p style={{ margin: 0, fontWeight: "bold" }}>
                      {payload[0].payload.name}
                    </p>
                    <p style={{ margin: "5px 0", color: "#666" }}>
                      Attendance: {payload[0].value.toFixed(1)}%
                    </p>
                    <p style={{ margin: "5px 0", color: "#10b981" }}>
                      Present: {payload[0].payload.present}
                    </p>
                    <p style={{ margin: "5px 0", color: "#ef4444" }}>
                      Absent: {payload[0].payload.absent}
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Bar dataKey="percentage" radius={[8, 8, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.percentage)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default AttendanceChart;
