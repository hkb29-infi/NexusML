FROM node:18

WORKDIR /app

COPY frontend/package.json ./

RUN npm install

COPY frontend/src ./src
COPY frontend/public ./public

CMD ["npx", "react-scripts", "start"]
