FROM mcr.microsoft.com/playwright:v1.65.0-noble
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip ffmpeg && rm -rf /var/lib/apt/lists/* \
 && pip3 install --break-system-packages --no-cache-dir anthropic pillow
WORKDIR /srv
COPY server/package.json server/
RUN cd server && npm install --omit=dev && ln -s /srv/server/node_modules /srv/node_modules
COPY lib lib
# the picture library the template path makes its pictures from (lib/templates/pictures.py looks for /srv/media/library);
# without it every job got `media.library 0` and no made pictures. The server logs "library: N pictures" on boot.
COPY media media
# measured principles of the reference sites (JSON and their reader): what the composer of a first screen is briefed with
COPY design_dna design_dna
COPY experiments/design-patterns experiments/design-patterns
COPY swarm.js swarm.js
COPY server server
ENV NODE_ENV=production PORT=8080
EXPOSE 8080
CMD ["node","server/index.mjs"]
