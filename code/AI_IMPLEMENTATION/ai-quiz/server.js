require("dotenv").config();
const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");
const mysql = require("mysql2");
const { GoogleGenerativeAI } = require("@google/generative-ai");

// ✅ Import question bank
const { questionBank } = require("./questions.js");

const app = express();
app.use(cors());
app.use(bodyParser.json());
app.use(express.static("public"));

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

// ✅ Gemini setup
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

// ✅ Helper function to grade with Gemini
async function gradeAnswer(question, candidateCode) {
  try {
    const model = genAI.getGenerativeModel({ model: "gemini-2.5-flash" });

    const prompt = `
You are a strict programming evaluator.
Question: ${question}
Candidate's Python code:
${candidateCode}

Evaluate the correctness of this code.
Return ONLY a number from 0 to 100.
`;

    const result = await model.generateContent(prompt);
    const output = result.response.text().trim();

    const score = parseInt(output, 10);
    return isNaN(score) ? 0 : Math.max(0, Math.min(score, 100));
  } catch (err) {
    console.error("❌ Error grading with Gemini:", err);
    return 0;
  }
}

// ✅ Hardcoded login credentials
const USERS = [
  { username: "candidate1", password: "test123" },
  { username: "candidate2", password: "pass456" }
];

// ✅ Login endpoint
app.post("/login", (req, res) => {
  const { username, password, candidateName } = req.body;

  const user = USERS.find(u => u.username === username && u.password === password);
  if (!user) {
    return res.status(401).json({ error: "Invalid username or password" });
  }

  // Pick 3 shuffled questions for this session
  const shuffled = [...questionBank].sort(() => 0.5 - Math.random());
  const selected = shuffled.slice(0, 3);

  res.json({
    message: "Login successful",
    candidateName,
    questions: selected,
    startTime: Date.now()
  });
});

// ✅ Endpoint: submit answers
app.post("/submit-answers", async (req, res) => {
  const { candidateName, questions, answers, startTime } = req.body;

  try {
    if (!candidateName || !answers || !questions || answers.length !== 3 || questions.length !== 3) {
      return res.status(400).json({ error: "Invalid submission format" });
    }

    // 🔹 Evaluate each answer
    const scores = [];
    for (let i = 0; i < 3; i++) {
      const score = await gradeAnswer(questions[i].question, answers[i]);
      scores.push(score);
    }

    const totalScore = scores.reduce((a, b) => a + b, 0);

    // 🔹 Calculate time taken
    const timeTakenSeconds = Math.floor((Date.now() - startTime) / 1000);
    const minutes = Math.floor(timeTakenSeconds / 60);
    const seconds = timeTakenSeconds % 60;
    const timeTakenFormatted = `${minutes}m ${seconds}s`;

    // Insert into DB
    const sql = `
      INSERT INTO submissions 
      (candidate_name, q1, q2, q3, q1_code, q2_code, q3_code, q1_score, q2_score, q3_score, total_score, time_taken) 
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `;
    db.query(
      sql,
      [
        candidateName,
        questions[0],
        questions[1],
        questions[2],
        answers[0],
        answers[1],
        answers[2],
        scores[0],
        scores[1],
        scores[2],
        totalScore,
        timeTakenFormatted
     
      ],
      (err) => {
        if (err) {
          console.error("❌ Error inserting into DB:", err);
          return res.status(500).json({ error: "Database error" });
        }
        console.log(`✅ Stored submission for ${candidateName}, total score = ${totalScore}`);
        res.json({ message: "Submission stored successfully!" });
      }
    );
  } catch (err) {
    console.error("❌ Error processing submission:", err);
    res.status(500).json({ error: "Failed to submit answers" });
  }
});

// ✅ Endpoint: fetch submissions (admin view)
app.get("/submissions", (req, res) => {
  db.query("SELECT * FROM submissions ORDER BY submitted_at DESC", (err, results) => {
    if (err) {
      console.error("❌ Error fetching submissions:", err);
      return res.status(500).json({ error: "Database error" });
    }
    res.json(results);
  });
});

app.listen(3000, () => {
  console.log("🚀 Server running at http://localhost:3000");
});
