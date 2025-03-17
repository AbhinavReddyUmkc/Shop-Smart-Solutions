{\rtf1\ansi\ansicpg1252\cocoartf2761
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import React, \{ useState, useEffect \} from "react";\
import "./ThreatDashboard.css"; // Import CSS file for styling\
\
function ThreatDashboard() \{\
  const [threats, setThreats] = useState([]);\
\
  useEffect(() => \{\
    fetch("/api/threats")\
      .then((res) => res.json())\
      .then((data) => setThreats(data))\
      .catch((error) => console.error("Error fetching threats:", error));\
  \}, []);\
\
  return (\
    <div className="dashboard-container">\
      <h2>Real-Time Threat Intelligence</h2>\
      <table>\
        <thead>\
          <tr>\
            <th>IP Address</th>\
            <th>Threat Type</th>\
            <th>Risk Score</th>\
          </tr>\
        </thead>\
        <tbody>\
          \{threats.map((threat, index) => (\
            <tr key=\{index\} className=\{threat.risk_score > 20 ? "high-risk" : ""\}>\
              <td>\{threat.ip\}</td>\
              <td>\{threat.type\}</td>\
              <td>\{threat.risk_score\}</td>\
            </tr>\
          ))\}\
        </tbody>\
      </table>\
    </div>\
  );\
\}\
\
export default ThreatDashboard;\
}