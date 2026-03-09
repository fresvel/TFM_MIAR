FROM texlive/texlive:latest

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    fontconfig \
    fonts-liberation \
    fonts-crosextra-carlito \
    fonts-crosextra-caladea \
  && rm -rf /var/lib/apt/lists/*

# Copia fuentes del proyecto (poner .ttf/.otf en docker/fonts)
COPY fonts/ /usr/local/share/fonts/
RUN fc-cache -f -v

WORKDIR /workdir
