/**
 * Weekly Email Summary Cron
 * Sends a weekly digest to all users with their application stats
 * Run this with: node-cron or a separate cron service
 */

import * as cron from "node-cron";
import * as nodemailer from "nodemailer";
import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

const transporter = nodemailer.createTransport({
  host: process.env.SMTP_HOST || "smtp.gmail.com",
  port: Number(process.env.SMTP_PORT) || 587,
  secure: false,
  auth: {
    user: process.env.SMTP_USER,
    pass: process.env.SMTP_PASS,
  },
});

interface UserStats {
  total: number;
  applied: number;
  interview: number;
  offer: number;
  rejected: number;
  newThisWeek: number;
}

async function getUserWeeklyStats(userId: string): Promise<UserStats> {
  const oneWeekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);

  const [byStatus, newThisWeek] = await Promise.all([
    prisma.application.groupBy({
      by: ["status"],
      where: { userId },
      _count: { status: true },
    }),
    prisma.application.count({
      where: { userId, createdAt: { gte: oneWeekAgo } },
    }),
  ]);

  const getCount = (status: string) =>
    byStatus.find((s) => s.status === status)?._count.status || 0;

  return {
    total: byStatus.reduce((acc, s) => acc + s._count.status, 0),
    applied: getCount("APPLIED"),
    interview: getCount("INTERVIEW"),
    offer: getCount("OFFER"),
    rejected: getCount("REJECTED"),
    newThisWeek,
  };
}

function buildEmailHtml(
  userName: string,
  stats: UserStats
): string {
  const responseRate =
    stats.applied > 0
      ? Math.round(((stats.interview + stats.offer) / stats.applied) * 100)
      : 0;

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #09090b; color: #fafafa; margin: 0; padding: 0; }
    .container { max-width: 600px; margin: 0 auto; padding: 40px 20px; }
    .header { text-align: center; margin-bottom: 32px; }
    .logo { font-size: 28px; font-weight: 700; color: #7c4dff; }
    .title { font-size: 22px; font-weight: 600; color: #fafafa; margin-top: 8px; }
    .stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 24px 0; }
    .stat-card { background: #18181b; border: 1px solid #27272a; border-radius: 12px; padding: 16px; text-align: center; }
    .stat-value { font-size: 28px; font-weight: 700; color: #7c4dff; }
    .stat-label { font-size: 12px; color: #71717a; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em; }
    .highlight { color: #7c4dff; }
    .btn { display: inline-block; background: #7c4dff; color: #fff; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 16px 0; }
    .footer { text-align: center; color: #52525b; font-size: 12px; margin-top: 40px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <div class="logo">⚡ ApplyIQ</div>
      <div class="title">Your Weekly Job Search Summary</div>
    </div>
    
    <p>Hi ${userName},</p>
    <p>Here's how your job search is going this week:</p>
    
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">${stats.newThisWeek}</div>
        <div class="stat-label">New This Week</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${stats.interview}</div>
        <div class="stat-label">Interviews</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${responseRate}%</div>
        <div class="stat-label">Response Rate</div>
      </div>
    </div>
    
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">${stats.total}</div>
        <div class="stat-label">Total Applied</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${stats.offer}</div>
        <div class="stat-label">Offers</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${stats.rejected}</div>
        <div class="stat-label">Rejected</div>
      </div>
    </div>
    
    ${stats.interview > 0 ? `<p>🎉 You have <span class="highlight">${stats.interview} active interview${stats.interview > 1 ? "s" : ""}</span>! Keep it up!</p>` : ""}
    ${stats.offer > 0 ? `<p>🚀 Congratulations! You have <span class="highlight">${stats.offer} offer${stats.offer > 1 ? "s" : ""}</span> to review!</p>` : ""}
    
    <div style="text-align: center">
      <a href="${process.env.NEXTAUTH_URL}/dashboard" class="btn">View Dashboard →</a>
    </div>
    
    <div class="footer">
      <p>You're receiving this because you enabled weekly summaries in ApplyIQ.</p>
      <p><a href="${process.env.NEXTAUTH_URL}/dashboard/profile" style="color: #52525b;">Unsubscribe</a></p>
    </div>
  </div>
</body>
</html>
  `.trim();
}

async function sendWeeklySummaries() {
  console.log("Starting weekly summary email job...");

  const users = await prisma.user.findMany({
    where: {
      email: { not: null },
      preferencesJson: {
        path: ["emailNotifications"],
        equals: true,
      },
    },
    select: { id: true, name: true, email: true },
  });

  console.log(`Sending weekly summaries to ${users.length} users`);

  for (const user of users) {
    if (!user.email) continue;

    try {
      const stats = await getUserWeeklyStats(user.id);

      // Only send if they have any applications
      if (stats.total === 0) continue;

      const html = buildEmailHtml(user.name || "there", stats);

      await transporter.sendMail({
        from: `"ApplyIQ" <${process.env.SMTP_USER}>`,
        to: user.email,
        subject: `Your weekly job search update — ${stats.newThisWeek} new applications this week`,
        html,
      });

      console.log(`Sent weekly summary to ${user.email}`);
    } catch (err) {
      console.error(`Failed to send email to ${user.email}:`, err);
    }
  }

  console.log("Weekly summary job complete.");
}

// Schedule: Every Monday at 9:00 AM UTC
cron.schedule("0 9 * * 1", sendWeeklySummaries, {
  timezone: "UTC",
});

console.log("Weekly summary cron scheduled (every Monday at 9:00 AM UTC)");

// Export for testing
export { sendWeeklySummaries };
