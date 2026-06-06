FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# Build for production if needed, or run dev server
RUN npm run build

EXPOSE 3001

CMD ["npm", "run", "start"]
