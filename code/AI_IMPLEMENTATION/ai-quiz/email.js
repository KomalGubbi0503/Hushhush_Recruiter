import express from "express";
import bodyParser from "body-parser";
import nodemailer from "nodemailer";
import dotenv from "dotenv";

dotenv.config({ path: "2.env" }); // Load your 2.env file

const app = express();
app.use(bodyParser.json());

// ✅ Verify env loaded
console.log("📩 Mailer using:", process.env.EMAIL_USER);

// ✅ Setup Nodemailer transporter (Gmail SSL)
const transporter = nodemailer.createTransport({
  host: "smtp.gmail.com",
  port: 465,       // SSL port
  secure: true,    // Use SSL
  auth: {
    user: process.env.EMAIL_USER,  // Gmail email
    pass: process.env.EMAIL_PASS,  // Gmail App Password
  },
});

// ✅ Verify SMTP connection
transporter.verify((error, success) => {
  if (error) {
    console.error("❌ SMTP Connection Error:", error);
  } else {
    console.log("✅ SMTP Server is ready to send emails");
  }
});

// ✅ API endpoint to send invite email
app.post("/send-invite", async (req, res) => {
  const { candidateEmail, candidateName } = req.body;

  if (!candidateEmail || !candidateName) {
    return res.status(400).json({ error: "Missing candidate email or name" });
  }

  const mailOptions = {
    from: `"HR Team" <${process.env.EMAIL_USER}>`, // Must match authenticated user
    to: candidateEmail,
    subject: "Invitation to Coding Round",
    text: `Hello ${candidateName},\n\nYou have been shortlisted! 🎉\nPlease attend the coding round using this link:\n\nhttp://localhost:3000/quiz\n\nGood luck!
    \n "Use the credentials given below to access the Quiz" \n\n "Userrname - candidate1" \n "Password - test123"\n\nHR Team`,
  };

  try {
    await transporter.sendMail(mailOptions);
    console.log(`✅ Email sent to ${candidateEmail}`);
    res.json({ success: true, message: "Email sent successfully" });
  } catch (err) {
    console.error("❌ Failed to send email:", err);
    res.status(500).json({ error: "Failed to send email" });
  }
});

// ✅ Start server
app.listen(4000, () => {
  console.log("📧 Email service running on http://localhost:4000");
});
