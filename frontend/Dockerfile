# Dockerfile for Node.js-based frontend

# Use an official Node.js image
FROM node:20.11-alpine

# Set working directory
WORKDIR /app

# Copy package.json and install dependencies
COPY package.json package-lock.json ./
RUN npm install --production

# Copy the rest of the app
COPY . .

# Build the app
RUN npm run build

# Expose the port your app runs on (e.g., 3000 for Next.js)
EXPOSE 3000

# Start the app
CMD ["npm", "start"]
