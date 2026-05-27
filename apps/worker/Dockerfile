# syntax=docker/dockerfile:1
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./
COPY packages/db/package.json ./packages/db/
COPY apps/worker/package.json ./apps/worker/

# Install all dependencies
RUN npm ci --workspace=apps/worker --workspace=packages/db

# Copy source
COPY packages/db ./packages/db
COPY apps/worker ./apps/worker

# Generate Prisma client
RUN npx prisma generate --schema=./packages/db/prisma/schema.prisma

# Build TypeScript
WORKDIR /app/apps/worker
RUN npx tsc --project tsconfig.json

# ── Production image ──
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy built files
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/packages ./packages
COPY --from=builder /app/apps/worker/dist ./apps/worker/dist
COPY --from=builder /app/apps/worker/package.json ./apps/worker/

CMD ["node", "apps/worker/dist/index.js"]
