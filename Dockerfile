FROM python:3.8.6-alpine3.12

# Install les dépendances du projet
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

COPY /src/ .

# Lancement du micro-serveur REST
CMD ["waitress-serve", "--listen=*:80", "MicroServREST:app"]
EXPOSE 80
