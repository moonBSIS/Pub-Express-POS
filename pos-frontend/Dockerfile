# Stage 1: Build the Vue app
FROM node:23-alpine AS build-stage
WORKDIR /app
COPY . .
RUN npm install && npm run build

# Stage 2: Serve using Nginx
FROM nginx:stable-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
