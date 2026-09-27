# Stage 1: build the SPA
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN CYPRESS_INSTALL_BINARY=0 npm ci --no-audit --no-fund
COPY . .
RUN npm run build

# Stage 2: Caddy serves the SPA and acts as the API gateway
FROM caddy:2.8-alpine
COPY --from=build /app/dist /srv
EXPOSE 80 443
