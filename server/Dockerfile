FROM mcr.microsoft.com/playwright:v1.65.0-noble
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip ffmpeg && rm -rf /var/lib/apt/lists/* \
 && pip3 install --break-system-packages --no-cache-dir anthropic pillow
WORKDIR /srv
COPY server/package.json server/
RUN cd server && npm install --omit=dev
COPY lib lib
COPY swarm.js swarm.js
COPY server server
ENV NODE_ENV=production PORT=8080 CHROME_PATH=/ms-playwright/chromium-*/chrome-linux/chrome
EXPOSE 8080
CMD ["node","server/index.mjs"]
