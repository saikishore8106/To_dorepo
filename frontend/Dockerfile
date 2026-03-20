# ── Frontend Dockerfile ──────────────────────────────────
# Multi-stage build:
# Stage 1 (builder): Install deps & build the React app
# Stage 2 (runner): Serve the static build with nginx (lightweight)

# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies first (layer cache optimization)
COPY package*.json ./
RUN npm ci

# Copy source and build for production
COPY . .
RUN npm run build


# Stage 2: Serve with nginx (final image is tiny — no Node.js runtime!)
FROM nginx:alpine

# Copy built static files to nginx's serve directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Custom nginx config to enable React Router (SPA routing)
RUN echo 'server { \
  listen 80; \
  root /usr/share/nginx/html; \
  index index.html; \
  location / { try_files $uri $uri/ /index.html; } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
