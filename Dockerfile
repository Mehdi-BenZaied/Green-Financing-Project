# Étape 1 : Build Angular
FROM node:18-slim AS build

WORKDIR /app

# Copier les fichiers de configuration
COPY package*.json angular.json tsconfig*.json ./
COPY src ./src

RUN npm install
RUN npm run build --prod

# Étape 2 : Serve avec NGINX
FROM nginx:alpine
COPY --from=build /app/dist/financement /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
