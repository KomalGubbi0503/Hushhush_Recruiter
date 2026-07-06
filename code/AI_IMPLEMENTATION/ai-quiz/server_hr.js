require("dotenv").config();
const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");
const mysql = require("mysql2");

const app = express();
app.use(cors());
app.use(bodyParser.json());

// ✅ Serve login page first when hitting root
app.get("/", (req, res) => {
  res.sendFile(__dirname + "/public_hr/login.html");
});

// ✅ Serve static files (index.html, technical.html, CSS, JS, etc.)
app.use(express.static("public_hr"));

// ✅ MySQL connection
const db = mysql.createConnection({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
});

db.connect(err => {
  if (err) {
    console.error("❌ MySQL connection failed:", err);
    process.exit(1);
  }
  console.log("✅ Connected to MySQL database");
});

// ✅ Hardcoded users
const users = [
  { username: "hradmin", password: "hrpass123", role: "hr" },
  { username: "tech1", password: "techpass1", role: "technical_interviewer" }
];

// ✅ Login route
app.post("/login", (req, res) => {
  const { username, password } = req.body;
  const user = users.find(u => u.username === username && u.password === password);
  if (!user) return res.json({ success: false, error: "Invalid credentials" });
  res.json({ success: true, role: user.role });
});

// ✅ HR dashboard routes
app.get("/candidates", (req, res) => {
  db.query("SELECT DISTINCT candidate_name FROM submissions", (err, results) => {
    if (err) return res.status(500).json({ error: "DB error" });
    res.json(results);
  });
});

app.get("/candidate-details/:name", (req, res) => {
  const candidateName = req.params.name;

  const sql = `
    SELECT 
      s.candidate_name,
      s.total_score, s.time_taken,
      cb.stars, cb.commits, cb.total_public_repos, cb.pull_requests
    FROM submissions s
    LEFT JOIN candidates_base cb
    ON s.candidate_name = cb.candidate_name
    WHERE s.candidate_name = ?
    ORDER BY s.submitted_at DESC
    LIMIT 1
  `;

  db.query(sql, [candidateName], (err, results) => {
    if (err) return res.status(500).json({ error: "DB error" });
    res.json(results[0] || {});
  });
});

// ✅ Update status (HR action) → fetch email from candidates_base
app.post("/update-status", (req, res) => {
  const { candidate_name, status } = req.body;

  if (!candidate_name || !status) {
    return res.status(400).json({ success: false, error: "Missing fields" });
  }

  // ✅ Fetch email from candidates_base
  const emailQuery = "SELECT email FROM candidates_base WHERE candidate_name = ? LIMIT 1";

  db.query(emailQuery, [candidate_name], (err, results) => {
    if (err) return res.status(500).json({ success: false, error: "DB error" });

    if (results.length === 0) {
      return res.status(404).json({ success: false, error: "Candidate not found in candidates_base" });
    }

    const email = results[0].email;

    // ✅ Insert or update into candidate_status
    const insertQuery = `
      INSERT INTO final_email (candidate_name, email, status)
      VALUES (?, ?, ?)
      ON DUPLICATE KEY UPDATE status = VALUES(status)
    `;

    db.query(insertQuery, [candidate_name, email, status], (err2) => {
      if (err2) return res.status(500).json({ success: false, error: "DB error" });
      res.json({ success: true, message: `Candidate ${status}` });
    });
  });
});

// ✅ Technical dashboard routes
app.get("/technical-dashboard", (req, res) => {
  db.query("SELECT * FROM technical_dashboard", (err, results) => {
    if (err) return res.status(500).json({ error: "DB error" });
    res.json(results);
  });
});

app.post("/update-scores", (req, res) => {
  const { id, q1_score, q2_score, q3_score } = req.body;
  const total_score = Number(q1_score) + Number(q2_score) + Number(q3_score);

  const sql = `
    UPDATE technical_dashboard 
    SET q1_score=?, q2_score=?, q3_score=?, total_score=? 
    WHERE id=?`;

  db.query(sql, [q1_score, q2_score, q3_score, total_score, id], (err) => {
    if (err) return res.status(500).json({ success: false, error: "DB error" });
    res.json({ success: true });
  });
});

app.listen(5000, () => console.log("🚀 Server running on http://localhost:5000"));
