FROM node:20-alpine

WORKDIR /app

# Install Python and other necessary build tools
RUN apk add --no-cache python3 make g++ 

# Copy package files and install dependencies
COPY package.json ./
RUN npm install -g pnpm && pnpm install

# Copy the source code and configuration files
COPY . .

# If you decide to use `nginx`, remember to configure it properly
# to serve Next.js static files and reverse proxy requests to the Next.js server.
# The following is just an example to get you started:
#
# RUN apk add --no-cache nginx
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Note: Don't expose ports here, Compose will handle that for us
# EXPOSE 3000

# Start the Next.js app
CMD ["pnpm", "run", "dev"]
