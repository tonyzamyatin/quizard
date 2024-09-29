# Use official node image as base
FROM node:20.11-alpine AS builder

# Set environment to development to install devDependencies (attempted bugfix)
ENV NODE_ENV=development

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Copy the rest of the application
COPY . .

# Build the frontend
RUN npm run build

# Serve the frontend using a lightweight web server
FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
