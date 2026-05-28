-- CreateEnum
CREATE TYPE "JobType" AS ENUM ('FULL_TIME', 'PART_TIME', 'CONTRACT', 'INTERNSHIP', 'FREELANCE');

-- CreateEnum
CREATE TYPE "WorkMode" AS ENUM ('REMOTE', 'HYBRID', 'ONSITE');

-- CreateEnum
CREATE TYPE "CompanySize" AS ENUM ('STARTUP', 'SMALL', 'MID', 'LARGE', 'ENTERPRISE');

-- CreateEnum
CREATE TYPE "ApplicationStatus" AS ENUM ('SAVED', 'APPLIED', 'SCREENING', 'INTERVIEW', 'OFFER', 'REJECTED', 'WITHDRAWN');

-- CreateEnum
CREATE TYPE "AtsType" AS ENUM ('GREENHOUSE', 'LEVER', 'WORKDAY', 'ASHBY', 'SMARTRECRUITERS', 'UNKNOWN');

-- CreateEnum
CREATE TYPE "JobSource" AS ENUM ('REMOTIVE', 'ADZUNA', 'THE_MUSE', 'JSEARCH', 'HN_HIRING', 'COMPANY_SITE', 'MANUAL');

-- CreateEnum
CREATE TYPE "InteractionType" AS ENUM ('EMAIL_RECEIVED', 'EMAIL_SENT', 'PHONE_CALL', 'VIDEO_INTERVIEW', 'ONSITE_INTERVIEW', 'OFFER_RECEIVED', 'NOTE', 'STATUS_CHANGE');

-- CreateEnum
CREATE TYPE "AuditAction" AS ENUM ('FORM_FILLED', 'FORM_SUBMITTED', 'CAPTCHA_DETECTED', 'SCREENSHOT_TAKEN', 'ERROR', 'DRY_RUN_COMPLETED');

-- CreateTable
CREATE TABLE "users" (
    "id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "name" TEXT,
    "image" TEXT,
    "emailVerified" TIMESTAMP(3),
    "fcmToken" TEXT,
    "expoPushToken" TEXT,
    "gmailAccessToken" TEXT,
    "gmailRefreshToken" TEXT,
    "gmailTokenExpiry" TIMESTAMP(3),
    "gmailSyncEnabled" BOOLEAN NOT NULL DEFAULT false,
    "gmailLastSynced" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "accounts" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "provider" TEXT NOT NULL,
    "providerAccountId" TEXT NOT NULL,
    "refresh_token" TEXT,
    "access_token" TEXT,
    "expires_at" INTEGER,
    "token_type" TEXT,
    "scope" TEXT,
    "id_token" TEXT,
    "session_state" TEXT,

    CONSTRAINT "accounts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "sessions" (
    "id" TEXT NOT NULL,
    "sessionToken" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "expires" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "sessions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "verification_tokens" (
    "identifier" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "expires" TIMESTAMP(3) NOT NULL
);

-- CreateTable
CREATE TABLE "preferences" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "desiredRoles" TEXT[],
    "salaryMin" INTEGER,
    "salaryMax" INTEGER,
    "jobTypes" "JobType"[],
    "workModes" "WorkMode"[],
    "preferredLocations" TEXT[],
    "targetIndustries" TEXT[],
    "companySizes" "CompanySize"[],
    "blacklistedCompanies" TEXT[],
    "minMatchScore" INTEGER NOT NULL DEFAULT 70,
    "autoApplyEnabled" BOOLEAN NOT NULL DEFAULT false,
    "autoApplyThreshold" INTEGER NOT NULL DEFAULT 85,
    "maxDailyApplications" INTEGER NOT NULL DEFAULT 10,
    "applyHoursStart" INTEGER NOT NULL DEFAULT 9,
    "applyHoursEnd" INTEGER NOT NULL DEFAULT 17,
    "notifyNewMatches" BOOLEAN NOT NULL DEFAULT true,
    "notifyQueueReady" BOOLEAN NOT NULL DEFAULT true,
    "notifyInterviews" BOOLEAN NOT NULL DEFAULT true,
    "notifyFollowups" BOOLEAN NOT NULL DEFAULT true,
    "notifyWeeklySummary" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "preferences_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "profiles" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "resumeFileName" TEXT,
    "resumeFileUrl" TEXT,
    "resumeText" TEXT,
    "parsedName" TEXT,
    "parsedEmail" TEXT,
    "parsedPhone" TEXT,
    "parsedLocation" TEXT,
    "parsedSummary" TEXT,
    "parsedSkills" TEXT[],
    "parsedJson" JSONB,
    "linkedinUrl" TEXT,
    "linkedinDataJson" JSONB,
    "resumeEmbeddingId" TEXT,
    "embeddingUpdatedAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "profiles_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "jobs" (
    "id" TEXT NOT NULL,
    "title" TEXT NOT NULL,
    "company" TEXT NOT NULL,
    "companyDomain" TEXT,
    "location" TEXT,
    "salaryMin" INTEGER,
    "salaryMax" INTEGER,
    "salaryCurrency" TEXT DEFAULT 'USD',
    "description" TEXT NOT NULL,
    "requirements" TEXT,
    "benefits" TEXT,
    "applyUrl" TEXT NOT NULL,
    "atsType" "AtsType" NOT NULL DEFAULT 'UNKNOWN',
    "source" "JobSource" NOT NULL DEFAULT 'MANUAL',
    "jobType" "JobType",
    "workMode" "WorkMode",
    "companySize" "CompanySize",
    "industry" TEXT,
    "dedupHash" TEXT NOT NULL,
    "embeddingId" TEXT,
    "postedAt" TIMESTAMP(3),
    "scrapedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expiresAt" TIMESTAMP(3),

    CONSTRAINT "jobs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "applications" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "jobId" TEXT NOT NULL,
    "status" "ApplicationStatus" NOT NULL DEFAULT 'SAVED',
    "matchScore" INTEGER,
    "skillsMatch" INTEGER,
    "experienceLevel" INTEGER,
    "domainRelevance" INTEGER,
    "salaryFit" INTEGER,
    "cultureSignals" INTEGER,
    "missingSkills" TEXT[],
    "whyGoodFit" TEXT,
    "potentialConcerns" TEXT,
    "suggestedAngle" TEXT,
    "coverLetter" TEXT,
    "coverLetterTone" TEXT,
    "appliedAt" TIMESTAMP(3),
    "atsType" "AtsType",
    "lastActivityAt" TIMESTAMP(3),
    "reviewStatus" TEXT,
    "reviewedAt" TIMESTAMP(3),
    "notes" TEXT,
    "followUpScheduled" TIMESTAMP(3),
    "followUpSentAt" TIMESTAMP(3),
    "followUpDraft" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "applications_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "contacts" (
    "id" TEXT NOT NULL,
    "applicationId" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "email" TEXT,
    "linkedinUrl" TEXT,
    "role" TEXT,
    "phone" TEXT,
    "notes" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "contacts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "interactions" (
    "id" TEXT NOT NULL,
    "applicationId" TEXT NOT NULL,
    "type" "InteractionType" NOT NULL,
    "content" TEXT,
    "subject" TEXT,
    "direction" TEXT,
    "gmailMessageId" TEXT,
    "happenedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "interactions_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "audit_logs" (
    "id" TEXT NOT NULL,
    "applicationId" TEXT NOT NULL,
    "action" "AuditAction" NOT NULL,
    "details" TEXT,
    "screenshotUrl" TEXT,
    "success" BOOLEAN NOT NULL DEFAULT false,
    "errorMessage" TEXT,
    "dryRun" BOOLEAN NOT NULL DEFAULT true,
    "timestamp" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "audit_logs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "queue_items" (
    "id" TEXT NOT NULL,
    "bullJobId" TEXT,
    "type" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'waiting',
    "payload" JSONB,
    "result" JSONB,
    "errorMessage" TEXT,
    "attempts" INTEGER NOT NULL DEFAULT 0,
    "maxAttempts" INTEGER NOT NULL DEFAULT 3,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "processedAt" TIMESTAMP(3),
    "completedAt" TIMESTAMP(3),

    CONSTRAINT "queue_items_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "weekly_snapshots" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "weekStart" TIMESTAMP(3) NOT NULL,
    "weekEnd" TIMESTAMP(3) NOT NULL,
    "applicationsCount" INTEGER NOT NULL DEFAULT 0,
    "responsesCount" INTEGER NOT NULL DEFAULT 0,
    "interviewsCount" INTEGER NOT NULL DEFAULT 0,
    "offersCount" INTEGER NOT NULL DEFAULT 0,
    "rejectedCount" INTEGER NOT NULL DEFAULT 0,
    "responseRate" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "topSource" TEXT,
    "avgMatchScore" DOUBLE PRECISION,
    "successfulDimensions" JSONB,
    "aiInsight" TEXT,
    "emailSentAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "weekly_snapshots_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "skill_gaps" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "skill" TEXT NOT NULL,
    "frequency" INTEGER NOT NULL DEFAULT 1,
    "courseUrl" TEXT,
    "courseTitle" TEXT,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "skill_gaps_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");

-- CreateIndex
CREATE UNIQUE INDEX "accounts_provider_providerAccountId_key" ON "accounts"("provider", "providerAccountId");

-- CreateIndex
CREATE UNIQUE INDEX "sessions_sessionToken_key" ON "sessions"("sessionToken");

-- CreateIndex
CREATE UNIQUE INDEX "verification_tokens_token_key" ON "verification_tokens"("token");

-- CreateIndex
CREATE UNIQUE INDEX "verification_tokens_identifier_token_key" ON "verification_tokens"("identifier", "token");

-- CreateIndex
CREATE UNIQUE INDEX "preferences_userId_key" ON "preferences"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "profiles_userId_key" ON "profiles"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "jobs_dedupHash_key" ON "jobs"("dedupHash");

-- CreateIndex
CREATE INDEX "jobs_company_idx" ON "jobs"("company");

-- CreateIndex
CREATE INDEX "jobs_source_idx" ON "jobs"("source");

-- CreateIndex
CREATE INDEX "jobs_postedAt_idx" ON "jobs"("postedAt");

-- CreateIndex
CREATE INDEX "jobs_dedupHash_idx" ON "jobs"("dedupHash");

-- CreateIndex
CREATE INDEX "applications_userId_status_idx" ON "applications"("userId", "status");

-- CreateIndex
CREATE INDEX "applications_reviewStatus_idx" ON "applications"("reviewStatus");

-- CreateIndex
CREATE UNIQUE INDEX "applications_userId_jobId_key" ON "applications"("userId", "jobId");

-- CreateIndex
CREATE INDEX "interactions_applicationId_idx" ON "interactions"("applicationId");

-- CreateIndex
CREATE INDEX "interactions_type_idx" ON "interactions"("type");

-- CreateIndex
CREATE INDEX "audit_logs_applicationId_idx" ON "audit_logs"("applicationId");

-- CreateIndex
CREATE INDEX "audit_logs_timestamp_idx" ON "audit_logs"("timestamp");

-- CreateIndex
CREATE UNIQUE INDEX "queue_items_bullJobId_key" ON "queue_items"("bullJobId");

-- CreateIndex
CREATE INDEX "queue_items_type_status_idx" ON "queue_items"("type", "status");

-- CreateIndex
CREATE INDEX "weekly_snapshots_userId_idx" ON "weekly_snapshots"("userId");

-- CreateIndex
CREATE UNIQUE INDEX "weekly_snapshots_userId_weekStart_key" ON "weekly_snapshots"("userId", "weekStart");

-- CreateIndex
CREATE INDEX "skill_gaps_userId_frequency_idx" ON "skill_gaps"("userId", "frequency");

-- CreateIndex
CREATE UNIQUE INDEX "skill_gaps_userId_skill_key" ON "skill_gaps"("userId", "skill");

-- AddForeignKey
ALTER TABLE "accounts" ADD CONSTRAINT "accounts_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "sessions" ADD CONSTRAINT "sessions_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "preferences" ADD CONSTRAINT "preferences_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "profiles" ADD CONSTRAINT "profiles_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "applications" ADD CONSTRAINT "applications_userId_fkey" FOREIGN KEY ("userId") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "applications" ADD CONSTRAINT "applications_jobId_fkey" FOREIGN KEY ("jobId") REFERENCES "jobs"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "contacts" ADD CONSTRAINT "contacts_applicationId_fkey" FOREIGN KEY ("applicationId") REFERENCES "applications"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "interactions" ADD CONSTRAINT "interactions_applicationId_fkey" FOREIGN KEY ("applicationId") REFERENCES "applications"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "audit_logs" ADD CONSTRAINT "audit_logs_applicationId_fkey" FOREIGN KEY ("applicationId") REFERENCES "applications"("id") ON DELETE CASCADE ON UPDATE CASCADE;
