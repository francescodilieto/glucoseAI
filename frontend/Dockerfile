FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json .npmrc ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80

# API_BASE_URL is baked into config.json at container start (not at image
# build time), so the same image works in docker-compose and Render just by
# setting a different env var -- no rebuild needed.
ENV API_BASE_URL=http://localhost:8080/api
CMD ["/bin/sh", "-c", "envsubst '$API_BASE_URL' < /usr/share/nginx/html/config.template.json > /usr/share/nginx/html/config.json && exec nginx -g 'daemon off;'"]
