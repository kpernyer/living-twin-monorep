# Stage 1: Build the application
FROM node:20-slim AS builder

# Set environment variables
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

# Install pnpm
RUN corepack enable

# Set work directory
WORKDIR /app

# Copy workspace files
COPY pnpm-workspace.yaml .
COPY package.json .

# Copy the admin_web package.json
COPY apps/admin_web/package.json ./apps/admin_web/

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy the rest of the application code
COPY apps/admin_web ./apps/admin_web

# Build the application
RUN pnpm --filter admin_web build

# Stage 2: Serve the application with a minimal server
FROM gcr.io/distroless/nodejs20-debian11

# Set work directory
WORKDIR /app

# Copy the built application from the builder stage
COPY --from=builder /app/apps/admin_web/dist .

# Expose the port the app runs on
EXPOSE 4173

# Serve the application
CMD ["./server.js"]
