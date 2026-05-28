/**
 * BullMQ Worker — Main entry point
 * Processes: scrape, embed, apply, gmail_sync, weekly_summary jobs
 */

import { Worker, Job } from "bullmq";
import IORedis from "ioredis";
import { PrismaClient } from "@prisma/client";
import cron from "node-cron";
import dotenv from "dotenv";
import { createTransport } from "nodemailer";
import { sendPushNotification } from "./utils/push";

dotenv.config();

const redis = new IORedis(process.env.REDIS_URL || "redis://localhost:6379", {
  maxRetriesPerRequest: null,
  enableReadyCheck: false,
});

const prisma = new PrismaClient();

// ─── Scrape Worker ──────────────────────────────────────────

const scrapeWorker = new Worker(
  "job-scrape",
  async (job: Job) => {
    const { source } = job.data;
    console.log(`🔄 Processing scrape job: ${source}`);

    // Dynamically import scrapers to avoid heavy deps at startup
    try {
      switch (source) {
        case "remotive": {
          const { scrapeRemotive } = await import("../../apps/web/src/lib/scrapers/remotive.js" as any);
          return { inserted: await scrapeRemotive() };
        }
        case "adzuna": {
          const { scrapeAdzuna } = await import("../../apps/web/src/lib/scrapers/adzuna.js" as any);
          return { inserted: await scrapeAdzuna() };
        }
        default:
          console.warn(`Unknown scrape source: ${source}`);
          return { inserted: 0 };
      }
    } catch (e) {
      console.error(`Scrape failed for ${source}:`, e);
      throw e;
    }
  },
  { connection: redis, concurrency: 2 }
);

// ─── Apply Worker ──────────────────────────────────────────

const applyWorker = new Worker(
  "job-apply",
  async (job: Job) => {
    const { applicationId, userId } = job.data;
    console.log(`🚀 Processing apply job: ${applicationId}`);

    const application = await prisma.application.findUnique({
      where: { id: applicationId },
      include: { job: true },
    });

    if (!application) {
      throw new Error(`Application ${applicationId} not found`);
    }

    const profile = await prisma.profile.findUnique({ where: { userId } });
    if (!profile) throw new Error(`Profile not found for user ${userId}`);

    const user = await prisma.user.findUnique({
      where: { id: userId },
      select: { expoPushToken: true },
    });

    const dryRun = process.env.DRY_RUN_MODE === "true";
    const atsType = application.job.atsType;

    let result;
    const profileData = {
      name: profile.parsedName || "Candidate",
      firstName: (profile.parsedName || "").split(" ")[0],
      lastName: (profile.parsedName || "").split(" ").slice(1).join(" "),
      email: profile.parsedEmail || "",
      phone: profile.parsedPhone || undefined,
      coverLetter: application.coverLetter || undefined,
    };

    try {
      if (atsType === "GREENHOUSE") {
        const { fillGreenhouseForm } = await import("../../apps/web/src/lib/ats/greenhouse.js" as any);
        result = await fillGreenhouseForm(
          application.job.applyUrl,
          profileData,
          applicationId,
          dryRun
        );
      } else {
        // For unknown ATS, log and mark as manual
        result = { success: false, errorMessage: `ATS type ${atsType} not yet supported` };
      }

      // Update audit log
      await prisma.auditLog.create({
        data: {
          applicationId,
          action: dryRun ? "DRY_RUN_COMPLETED" : result.success ? "FORM_SUBMITTED" : "ERROR",
          details: result.errorMessage || (dryRun ? "Dry run completed" : "Form submitted"),
          screenshotUrl: result.screenshotUrl,
          success: result.success,
          dryRun,
        },
      });

      if (result.captchaDetected) {
        // Send notification to user
        console.log(`⚠️ CAPTCHA detected for application ${applicationId}`);
        if (user?.expoPushToken) {
          await sendPushNotification(
            user.expoPushToken,
            "Action Required: CAPTCHA Detected",
            `Please solve the CAPTCHA for your application at ${application.job.company}.`,
            { applicationId }
          );
        }
      }

      if (!dryRun && result.success) {
        await prisma.application.update({
          where: { id: applicationId },
          data: {
            status: "APPLIED",
            appliedAt: new Date(),
            lastActivityAt: new Date(),
          },
        });
        if (user?.expoPushToken) {
          await sendPushNotification(
            user.expoPushToken,
            "Application Submitted!",
            `Successfully submitted your application for ${application.job.title} at ${application.job.company}.`,
            { applicationId }
          );
        }
      }

      return result;
    } catch (e) {
      await prisma.auditLog.create({
        data: {
          applicationId,
          action: "ERROR",
          details: String(e),
          success: false,
          dryRun,
        },
      });
      throw e;
    }
  },
  { connection: redis, concurrency: 1 } // 1 at a time for Playwright
);

// ─── Event listeners ───────────────────────────────────────

scrapeWorker.on("completed", (job) => {
  console.log(`✅ Scrape job ${job.id} completed:`, job.returnvalue);
});

scrapeWorker.on("failed", (job, err) => {
  console.error(`❌ Scrape job ${job?.id} failed:`, err.message);
});

applyWorker.on("completed", (job) => {
  console.log(`✅ Apply job ${job.id} completed`);
});

applyWorker.on("failed", (job, err) => {
  console.error(`❌ Apply job ${job?.id} failed:`, err.message);
});

// ─── Cron Jobs ─────────────────────────────────────────────

// Scrape every 6 hours
cron.schedule("0 */6 * * *", async () => {
  console.log("⏰ Cron: Starting job scrape...");
  const { Queue } = await import("bullmq");
  const q = new Queue("job-scrape", { connection: redis });
  await q.addBulk([
    { name: "scrape-remotive", data: { source: "remotive" } },
    { name: "scrape-adzuna",   data: { source: "adzuna" } },
    { name: "scrape-muse",     data: { source: "muse" } },
    { name: "scrape-jsearch",  data: { source: "jsearch" } },
    { name: "scrape-hn",       data: { source: "hn" } },
  ]);
  console.log("✅ Scrape jobs queued");
});

// Weekly summary every Sunday at 9am
cron.schedule("0 9 * * 0", async () => {
  console.log("⏰ Cron: Generating weekly summaries...");
  // Find all users with weekly summary enabled
  const users = await prisma.preferences.findMany({
    where: { notifyWeeklySummary: true },
    include: { user: true },
  });

  for (const pref of users) {
    try {
      // Generate and send weekly summary
      console.log(`📧 Sending weekly summary to ${pref.user.email}`);
      // TODO: Generate with GPT-4o and send via Nodemailer
    } catch (e) {
      console.error(`Failed weekly summary for user ${pref.userId}:`, e);
    }
  }
});

// Gmail sync every 30 minutes
cron.schedule("*/30 * * * *", async () => {
  console.log("⏰ Cron: Gmail sync...");
  const users = await prisma.user.findMany({
    where: { gmailSyncEnabled: true, gmailAccessToken: { not: null } },
    take: 50,
  });
  console.log(`Gmail sync: ${users.length} users to sync`);
  // TODO: Gmail scanning implementation
});

console.log("🚀 ApplyIQ Worker started");
console.log("  ✓ Scrape worker: job-scrape queue");
console.log("  ✓ Apply worker: job-apply queue");
console.log("  ✓ Cron: scrape every 6h, weekly summary Sundays 9am");
