FROM --platform=linux/amd64 node:20-alpine

WORKDIR /app

RUN apk add --no-cache python3 make g++ 
# Copy package files and install dependencies
COPY package.json pnpm-lock.yaml* ./
RUN npm install -g pnpm && pnpm install

# Copy the source code and configuration files
COPY . .

# Build the Next.js app
RUN pnpm run generate
RUN pnpm run build

# If you decide to use `nginx`, remember to configure it properly 
# to serve Next.js static files and reverse proxy requests to the Next.js server.
# The following is just an example to get you started:
# 
# RUN apk add --no-cache nginx
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose the port the app runs on
EXPOSE 3000

# Start the Next.js app
CMD ["pnpm", "start"]
