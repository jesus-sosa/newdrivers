# Stage: development
FROM node:20-alpine AS development

WORKDIR /app

COPY package.json .npmrc ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Stage: build
FROM node:20-alpine AS build

WORKDIR /app

COPY package.json .npmrc ./
RUN npm install

COPY . .
RUN npm run build

# Stage: production
FROM node:20-alpine AS production

WORKDIR /app

COPY --from=build /app/.output /app/.output

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
