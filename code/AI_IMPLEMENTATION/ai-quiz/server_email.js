require("dotenv").config();
const express = require("express");
const nodemailer = require("nodemailer");
const mysql = require("mysql2");

const app = express();

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

// ✅ Setup mail transporter (use your SMTP or Gmail)
const transporter = nodemailer.createTransport({
  service: "gmail", // or your SMTP provider
  auth: {
    user: process.env.EMAIL_USER, // your email
    pass: process.env.EMAIL_PASS, // your email password or app password
  },
});

// ✅ Function to send emails
function sendEmails() {
  db.query("SELECT candidate_name, email, status FROM final_email", (err, results) => {
    if (err) {
      console.error("❌ DB error:", err);
      return;
    }

    results.forEach(row => {
      let subject, message;

      if (row.status === "Selected") {
        subject = "Congratulations! You have been selected 🎉";
        message = `Dear ${row.candidate_name},\n\nWe are pleased to inform you that you have been selected. Our HR team will contact you with the next steps.\n\nBest regards,\nRecruitment Team`;
      } else if (row.status === "Rejected") {
        subject = "Application Update";
        message = `Dear ${row.candidate_name},\n\nWe appreciate your effort and interest in applying. Unfortunately, you were not selected this time. We wish you the best in your future endeavors.\n\nBest regards,\nRecruitment Team`;
      } else {
        console.log(`⚠️ Skipping ${row.candidate_name}, unknown status: ${row.status}`);
        return;
      }

      const mailOptions = {
        from: process.env.EMAIL_USER,
        to: row.email,
        subject: subject,
        text: message,
      };

      transporter.sendMail(mailOptions, (error, info) => {
        if (error) {
          console.error(`❌ Failed to send email to ${row.email}:`, error);
        } else {
          console.log(`✅ Email sent to ${row.email}: ${info.response}`);
        }
      });
    });
  });
}

// ✅ Trigger email sending with GET request
app.get("/send-emails", (req, res) => {
  sendEmails();
  res.send("📨 Emails are being sent. Check logs for status.");
});

app.listen(7000, () => console.log("🚀 Email server running at http://localhost:7000"));
