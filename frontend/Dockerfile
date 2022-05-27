FROM nginx:latest

COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create config.js file with contents replaced with environment variables
ARG FRONTEND_CLIENT_ID
ARG FRONTEND_DOMAIN
ARG GOOGLE_MAPS_API_KEY
COPY ./source/js/config.js /usr/share/nginx/html/js/config.js
RUN mkdir -p /usr/share/nginx/generated \
    && envsubst < /usr/share/nginx/html/js/config.js > /usr/share/nginx/generated/config.js