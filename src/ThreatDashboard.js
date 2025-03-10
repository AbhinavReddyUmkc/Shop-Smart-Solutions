import React, { useEffect, useState } from "react";

function ThreatDashboard() {
  // State to store threat data
  const [threats, setThreats] = useState([]);

  // Fetch TVA data from the backend when the page loads
  useEffect(() => {
    fetch("/api/tva") // API endpoint to get data
      .then((response) => response.json())
      .then((data) => setThreats(data))
      .catch((error) => console.error("Error fetching TVA data:", error));
  }, []);

  return (
    <div>
      <h2>Threat Intelligence Dashboard</h2>
      <table border="1">
        <thead>
          <tr>
            <th>Asset ID</th>
            <th>Threat</th>
            <th>Vulnerability</th>
            <th>Risk Score</th>
          </tr>
        </thead>
        <tbody>
          {threats.map((threat, index) => (
            <tr key={index}>
              <td>{threat.asset_id}</td>
              <td>{threat.threat_name}</td>
              <td>{threat.vulnerability_description}</td>
              <td>{threat.risk_score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ThreatDashboard;
