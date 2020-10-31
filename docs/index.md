![Departure](https://user-images.githubusercontent.com/930566/95666191-9da79d00-0b57-11eb-9059-afe446d07ed9.png)

This is the documentation for the Python Departure package.



## Prerequisites

Register for the transport operators you want to get information from (registration is free for all the listed transport operators at the time of writing):

- London Underground (TfL Tube) – Register for a Transport for London (TfL) Unified API application key at https://api-portal.tfl.gov.uk/, and you will receive an application key by email.
- National Rail –  Register for access to the National Rail Enquiries OpenLDBWS at http://realtime.nationalrail.co.uk/OpenLDBWSRegistration/, and you will receive an email containing a token.
- Nederlandse Spoorwegen – Sign up on the NS API portal at https://apiportal.ns.nl/, register for the Ns-App product (https://apiportal.ns.nl/products), and retrieve your API key from your profile page.
- RATP – Fill in the subscription form and send it to RATP's Open Data team as explained on https://data.ratp.fr/page/temps-reel/, under *S'inscrire*. Access to RATP's real-time API doesn't require an API key, but it does require that all calls be made from an authorised IP address.
- SNCF – Register for access to the SNCF real-time API at https://www.digital.sncf.com/startup/api, and you will receive your API authentication key by email.
- Transilien – Submit a request by email (see https://ressources.data.sncf.com/explore/dataset/api-temps-reel-transilien/information/), and you will receive your credentials by email.



Install Python 3.6 or greater.

(Optional, recommended) create a Python virtual environment.



## Installation

Install Python package.


```
$ pip install departure
```

  

## Usage

There are three command line interface tools:

- `departure`, the main CLI, to get station information and departures from public transport operators, and update a virtual or physical departure board with departure information for a station,
- `departure-web`, to run the API web server, optionally with a web front end.
- `departure-server`, to run a Python departure board server, which can receive and display departure information that it has received from the `departure` CLI or the `departure-web` web server.



### Environment variables

Before running `departure` or `departure-web`, set the following environment variables (see below for further instructions) for the public transport operators of interest:

- London Underground (TfL Tube) – Set the `TFL_APP_KEY` environment variable to your TfL Unified API application key.
- National Rail – Set the `LDB_TOKEN` environment variable to your National Rail token.
- Nederlandse Spoorwegen – Set the `NS_API_KEY` environment variable to your NS API key.
- RATP – No environment variable is needed, but all calls must be made from the authorised IP address that you provided when you registered.
- SNCF – Set the `SNCF_KEY` environment variable to your SNCF API authentication key.
- Transilien – Set the `TRANSILIEN_USER` and `TRANSILIEN_PASSWORD` environment variables to your Transilien API credentials.



To set an environment variable with the name `SOME_VAR` and the value `some_value`:

- Windows: open a Command Prompt, and enter `set SOME_VAR=some_value`. The environment variable will be remembered as long as the Command Prompt is open.
- Linux: open a console, and enter `export SOME_VAR=some_value`. The environment variable will be remembered in the current shell as long as it remains open.



Alternatively, you can use the `set_env_vars.bat.template` and `set_env_vars.sh.template` files in the repository to set the environment variables automatically:

- Remove the `.template` extension from the file(s) of interest for your system (`set_env_vars.bat.template` for Windows, `set_env_vars.bat.sh` for Linux).
- Edit the file(s) to set the environment variables as explained above.
- (Windows) In Command Prompt, enter `set_env_vars.bat` to set all defined environment variables.
- (Linux) In a shell, enter `. ./set_env_vars.sh` or `source set_env_vars.sh` to set the environment variables.



### Main CLI

*Make sure you have set the environment variables you need as described above.*

To get started, display the main CLI's help page.

```
$ departure
```

![departure CLI](images/departure-cli.svg)



The following command searches for SNCF (FR) stations containing "Paris".

```
$ departure sncf search paris
```

![departure sncf search paris](images/departure-sncf-search-paris.svg)



The following command shows the next departures at Den Haag Centraal (NL).

```
$ departure ns next gvc
```

![departure ns next gvc](images/departure-ns-next-gvc.svg)



The following command shows the next Westbound departures on Central Line at Oxford Circus.

```
$ departure lu next ce oxc w
```

![departure lu next ce oxc w](images/departure-lu-next.svg)



The following command updates a departure board with SNCF (FR) departures at Paris Montparnasse.

```
$ departure sncf board 87391003
```

The `departure <operator> board` commands require a running a Departure board server on a physical or virtual departure board – see below for Python Departure board servers and https://github.com/spujadas/departure-board-servers-cpp for C++ Departure board servers.



### Web API server

*Make sure you have set the environment variables you need as described above.*

To start the Departure web API server:

```
$ departure-web
```

The server will run on port 8000, e.g. if installed locally browse to http://localhost:8000.



The OpenAPI documentation can be found at `/docs`, e.g. http://localhost:8000/docs.

![Departure OpenAPI documentation page](images/departure-web-fastapi-doc.png)



Here is a sample cURL command to update a board, in this case with departure information for Montparnasse SNCF station (FR):

```
$ curl -X POST http://localhost:8000/sncf/start-client -d "{\"stop_area_id\": \"87391003\"}"
```



Alternatively, you can use a REST GUI client, such as [Insomnia](https://insomnia.rest/) (shown below) or [Postman](https://www.postman.com/).

![Using Insomnia as a client for Departure's web API](images/insomnia-departure-lu.gif)



#### Web front end

To use the Departure web front end:

- Download a release of the front-end from the Releases page of the [Departure front end](https://github.com/spujadas/departure-front-end) repository, and extract it to any directory.
- Point the `DEPARTURE_STATIC_WEBROOT` environment variable to the directory you have just extracted the Departure front end to.
- Start the web API server (`departure-web`, see previous section).
- Browse to the server on port 8000, e.g. http://localhost:8000.

![Departure web front end - SNCF Montparnasse](images/departure-web-sncf-montparnasse.gif)



### Departure board server

To run a Python Departure board server on a virtual or physical departure board, you will first need to install one or several [Python back ends](https://github.com/spujadas/departure-board-servers-python).

Run the following command to list the available back ends.

```
$ departure-server
```

![departure-server CLI](images/departure-server.svg)



## About

Written by [Sébastien Pujadas](https://pujadas.net/), released under the [MIT license](https://github.com/spujadas/departure-python/blob/master/LICENSE), with additional provisions as per below.

All product names, logos, and brands are property of their respective owners. All company, product and service names used in this project are for identification purposes only. Use of these names, logos, and brands does not imply endorsement.

The London Underground (TfL Tube) engine is powered by TfL Open Data. Contains OS data © Crown copyright and database rights 2016' and Geomni UK Map data © and database rights [2019].

The National Rail engine is powered by [National Rail Enquiries](https://www.nationalrail.co.uk/). The built-in list of National Rail station codes was derived from https://www.nationalrail.co.uk/stations_destinations/48541.aspx.

The built-in list of Nederlandse Spoorwegen station codes was retrieved from [Rijden de Treinen](https://www.rijdendetreinen.nl/over/open-data).

The built-in WSDL file used to access RATP's real-time web service was extracted from [RATP's API development kit](https://data.ratp.fr/page/temps-reel/).

The built-in list of SNCF stations (used by the SNCF and Transilien engines) was obtained from the [Gares de voyageurs](https://ressources.data.sncf.com/explore/dataset/referentiel-gares-voyageurs) dataset, which is released under the [ODbL (Open Database License)](https://data.sncf.com/pages/cgu/A1#A1).

The built-in list of Transilien stations and stops was obtained from the [Gares et points d'arrêt du réseau Transilien](https://ressources.data.sncf.com/explore/dataset/sncf-gares-et-arrets-transilien-ile-de-france/) dataset, which is released under the [ODbL (Open Database License)](https://data.sncf.com/pages/cgu/A1#A1).