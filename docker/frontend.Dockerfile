FROM node:18

WORKDIR /app

COPY frontend/package.json .
COPY frontend/package-lock.json .

RUN npm install

COPY ./frontend /app

CMD ["npm", "start"]
