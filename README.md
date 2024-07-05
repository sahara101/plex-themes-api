# plex-themes-api
Plex themes API endpoint for Homepage


# DISCLAIMER
I am no programmer! Code is written with help of ChatGPT. Feel free to modify the code as you please. Also open to criticism ;)</big>

This is a docker container which will enable you to create a widget for [Themerr ](https://github.com/LizardByte/Themerr-plex) in [Homepage](https://gethomepage.dev/main/).

<img width="373" alt="image" src="https://github.com/sahara101/plex-themes-api/assets/22507692/c429149b-6b4f-42cb-ae53-71b40089cd5b">

# Docker-compose

```
version: '3.8'

services:
  plex-themes-api:
    image: ghcr.io/sahara101/plex-themes-api:latest
    ports:
      - "7089:80"
    environment:
      PLEX_SERVER_URL: http://IP:32400 #Optional. Default http://localhost:32400
      PLEX_TOKEN: TOKEN
      UPDATE_INTERVAL: 600 #Optional. Default 300
    restart: unless-stopped
```

# Homepage

Edit services.yml and add the following to your Themerr service.
Change the fields according to the API response (your Plex library names).

```
widget:
          type: customapi
          url: http://IP:7089
          method: GET
          mappings:
             - field: combined_value_filme
               label: Themes Movies
             - field: combined_value_seriale
               label: Themes Shows
             - field: combined_value_anime
               label: Themes Anime
```

Thanks to the developers of Homepage, Themerr and ofc ChatGPT 
