![Departure](https://user-images.githubusercontent.com/930566/95666191-9da79d00-0b57-11eb-9059-afe446d07ed9.png)

This Python package provides a CLI, a web API server, and library, to:

- get station information and departures from public transport operators,
- update a virtual or physical departure board with departure information for a station.

Departure has out-of-the-box support for the following operators:

- [London Underground](https://tfl.gov.uk/modes/tube/) (UK),
- [National Rail](https://www.nationalrail.co.uk/) (UK),
- [Nederlandse Spoorwegen](https://www.ns.nl/) (Netherlands)
- [RATP](https://www.ratp.fr/) (France),
- [SNCF](https://www.sncf.com/) (France),
- [Transilien](https://www.transilien.com/) (France).

Departure information can be sent to a departure board server that supports the [Departure protocol buffer message format](https://github.com/spujadas/departure-proto).

As an illustration, the image below was created using the [Python Departure board server](https://github.com/spujadas/departure-board-servers-python) running the Pygame back end.

![Pygame virtual departure board - SNCF (FR) - Paris Montparnasse](https://user-images.githubusercontent.com/930566/95666195-a13b2400-0b57-11eb-841d-c56e0ecbd704.gif)

The video clip below was made using a physical LED matrix board running the [C++ Departure board server](https://github.com/spujadas/departure-board-servers-cpp) on a Raspberry Pi.

![Departure board - National Rail (UK) - Victoria station](https://user-images.githubusercontent.com/930566/95666193-9e403380-0b57-11eb-8edf-2c4be0fe5af5.gif)

The [official web front end](https://github.com/spujadas/departure-front-end) provides a human-friendly way to interact with the web API server.

![Departure web front end - SNCF Montparnasse](https://user-images.githubusercontent.com/930566/95666197-a39d7e00-0b57-11eb-9856-89579708c146.gif)

### Documentation

See the [Departure-Python documentation web page](http://departure-python.readthedocs.io/) for complete instructions on how to use this Python package.



### About

Written by [Sébastien Pujadas](https://pujadas.net/), released under the [MIT license](https://github.com/spujadas/departure-python/blob/master/LICENSE).

All product names, logos, and brands are property of their respective owners. All company, product and service names used in this project are for identification purposes only. Use of these names, logos, and brands does not imply endorsement.

