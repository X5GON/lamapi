
# Learning Analytics Machine API (LAM API)

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]


<!-- PROJECT LOGO -->
<p align="center">
  <a href="https://platform.x5gon.org">
    <img src="readme/logo.svg" alt="Logo" width="80" height="80">
  </a>
  <p align="center">
    <a href="https://www.x5gon.org/wp-content/uploads/2020/04/D3.3_final.pdf"><strong>Explore the full documentation »</strong></a>
    <br />
    <br />
    <a href="https://wp3.x5gon.org/lamapidoc">View Demo</a>
    ·
    <a href="https://github.com/X5GON/lamapi/issues">Report Bug</a>
    ·
    <a href="https://github.com/X5GON/lamapi/issues">Request Feature</a>
  </p>
</p>


<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
        <li><a href="#troubleshooting">Troubleshooting</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li>
      <a href="#contact">Contact</a>
      <ul>
        <li><a href="#members">Members</a></li>
        <li><a href="#moreupdates">More updates are on going !</a></li>
      </ul>
    </li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<img src="readme/analytics.png"  width="60%" height="60%" style="height:60%; width:60%; max-width:60%" >

The X5GON project stands for easily implemented freely available innovative technology elements that will converge currently scattered Open Educational Resources (OER) available in various modalities across Europe and the globe.

X5GON's Learning Analytics Machine (LAM) is capable of dealing with multi-lingual collections of OER. We can give you insight into the usage of your resources across different languages, make your content seen across the world and see how your resources are being used in different cultures.

The X5GON LAM API (models API) is a REST Flask Python web API strengthened by an auto-generated swagger
documentation which offers the possibility to test the endpoints directly on a nice web page. Through
the different offered endpoints, the users can consult the latest results and findings of the learning
analytics work package.
The endpoints give the possibility to access and fetch the content analytics made on
the OERs based on the AI models implemented and tested on the X5gon corpus composed by the
different OERs collected by the pipeline.

### Built With

* [Python](https://www.python.org/downloads/release/python-377/)
* [Flask](https://numpy.org/)
* [Psycopg2](https://pypi.org/project/psycopg2/)
* [Pandas](https://pandas.pydata.org/)
* [Numpy](https://numpy.org/)
* [Gensim](https://pypi.org/project/gensim/)
* [Scikit-learn](https://pypi.org/project/scikit-learn/)
* [Pytorch](https://pytorch.org/)
* [Joblib](https://pypi.org/project/joblib/)
* ...


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple example steps:
* Install the environment python packages.
* Install the X5GON DB.
* Run your API.

Follow the instructions in the following sections:

### Prerequisites

Make sure you install the necessary python packages(and their related dependencies), on your activated environment:
* Create your environment(using conda for example), activate it.
* Run this on your terminal:
    ```sh
      pip3 install -r requirements.txt
      python3 -m spacy download en
    ```

### Installation
1. Clone the repository
    ```sh
    git clone https://github.com/X5GON/lamapi
    ```
2. Install the Python packages
    ```sh
    pip3 install -r requirements.txt
    ```
4. Prepare the DB environment by creating the 'x5gon' database where all the data will be stored and from where the LAM API will source the OERs data (transcriptions, traductions, representations...):
  * Follow the instructions mentioned in the [platform-api, Installation section, 7th point about "creating x5gon DB"](https://github.com/X5GON/platform-api).
  * Create a DB user,  having the select/update previleges (will be used by the API).
  * Create the needed tables if not automatically added. The "x5gon DB schema" can be consulted in the delivrable [D 3.2, section 6](https://www.x5gon.org/wp-content/uploads/2021/02/D3.2-final.pdf). In order to create the missing tables if needed, refer to the simplified [x5gon db schema](components/db/init/x5gon.dmp):
  ```sh
     pg_restore -U dbuser -h localhost -d x5gon -Fc -C components/db/init/x5gon.dmp
  ```
  * Fill up your "x5gon" DB with your OERs corpus.
5. Set up the LAM API and the DB configuration by updating the [configuration file](config.ini)
6. Build the models & update the DB with the needed OERs representations, to do that:
    - Move to the lamapi root folder:
    - Execute the python commands found in the [models updater](components/db/update/updater) file, in the order, in your terminal.
 7. Run your LAM API from the terminal:
    ```sh
    python3 lamapi.py -hs wp3.x5gon.org -p 5000 -ct /etc/letsencrypt/live/blind.x5gon.org/cert.pem -ky /etc/letsencrypt/live/blind.x5gon.org/privkey.pem -bdh 192.168.1.7 -bdn x5gon -bdu wp3lam -bdpw 'mal3pw#51!&#prod' -bdp 5432 -d
    ```
    The API is designed to consider the Proxy and SSL functionnalities, so the arguments are as follows:
    ```
      -hs         localhost                         : The API host/domain name
      -p          5000                              : The API port name
      -ct         /path/to/your/cert.pem            : SSL certificate file
      -ky         /path/to/your/privkey.pem         : SSL private key file
      -bdh        localhost                         : DB host/domain name
      -bdn        x5gon                             : DB name
      -bdu        x5gondbuser                       : DB user name
      -bdpw       'x5gondbuserpassword'             : DB user password
      -bdp        5432                              : DB port
      -d                                            : debug mode or not
    ```

### Troubleshooting
* If there are issues while executing the "models update commands", please run the API with a minimum configuration of models activated, then run the "update endpoints" instead.

* To configure the activated models:
  - Refer to the [modelloader file](x5gonlammodels/modelloader.py)
  - Enable/Disable the needed models by commenting the suitable lines.


<!-- USAGE EXAMPLES -->
## Usage

Once the API is running and all the environment prerequisites are satisfied, you can test your endpoints using one of the following methods:
  * Visit the swagger documentation on : localhost:5000
  * Execute in your terminal one of the requests mentionned on the [lamapi_routes_test file](test/lamapi_routes_test)
  * Execute one of the [Python/Shell scripts](test/lamapi_routes_test.py) to launch a bench of tests.

Here is how it's looking the swagger documentation once the LAM API is up and running, the [Official X5GON LAM API](https://wp3.x5gon.org/lamapidoc.

An example of endpoint execution, the SEARCH SERVICE:

```sh
curl -X POST "https://wp3.x5gon.org/searchengine/v1" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{  \"text\": \"machine learning applied on health sector\",  \"type\": \"pdf\",  \"page\": 1,  \"model_type\": \"doc2vec\",  \"remove_duplicates\": 1,  \"nb_wikiconcepts\": 5,  \"return_wikisupport\": 0}"
```

[![Search service request][search-request]](readme/search_service_request.png)
[![Search service response][search-response]](readme/search_service_response.png)

<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/X5GON/lamapi/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->
## License

Distributed under the [BSD-2-Clause](https://opensource.org/licenses/BSD-2-Clause) License. See [LICENSE](LICENSE) for more information.

<!-- CONTACT -->
## Contact

### Members
* Victor Connes - <victor.connes@gmail.com>
* Walid Ben Romdhane - [@walidbrw](https://github.com/walidbrw) - <walid_benromdhane@hotmail.fr>
* Colin de la Higuera - <cdlh@univ-nantes.fr>


### More updates are on going !
The LAM API is composed essentially from 3 principal components:

#### The Services
Are the endpoints implemented above the Learning Analytics(LA) heureustics and models in order to be able to use them as independant services.
Many services types are implemented to treat many LA problems, [more details >>](https://www.x5gon.org/wp-content/uploads/2020/04/D3.3_final.pdf)

More updated version can be found on [X5GON LAM API repository of the X5GON-University of Nantes team](https://gitlab.univ-nantes.fr/x5gon/lamapi)

#### The X5gonlamtools
Are the algorithms behind the core of the Services that are using the OERs, in their different format (transcriptions, translations, metadata) to be able to compute the LA heurestics/metrics and generate the LA models needed for the Services.
These algorithms designed to solve many intersting Learning Ananlytics problems such as: Difficulty, order, concept continuity within an OER... [more details >>](https://www.x5gon.org/wp-content/uploads/2021/02/D3.2-final.pdf)

More updated version can be found on [X5GON LAM Tools repository of the X5GON-University of Nantes team](https://gitlab.univ-nantes.fr/connes-v/x5gonwp3tools)

#### The X5gonlammodels
Are the AI LA computed models based on the OERs and the X5gonlamtools algorithms. [more details >>](https://www.x5gon.org/wp-content/uploads/2021/02/D3.2-final.pdf)

More updated version can be found on:
* [X5GON LAM Models repository of the X5GON-University of Nantes team](https://gitlab.univ-nantes.fr/x5gon/x5gonwp3models)
* [The Order model](https://gitlab.univ-nantes.fr/connes-v/order_inference)


<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/X5GON/lamapi.svg?style=for-the-badge
[contributors-url]: https://github.com/X5GON/lamapi/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/X5GON/lamapi.svg?style=for-the-badge
[forks-url]: https://github.com/X5GON/lamapi/network/members
[stars-shield]: https://img.shields.io/github/stars/X5GON/lamapi.svg?style=for-the-badge
[stars-url]: https://github.com/X5GON/lamapi/stargazers
[issues-shield]: https://img.shields.io/github/issues/X5GON/lamapi.svg?style=for-the-badge
[issues-url]: https://github.com/X5GON/lamapi/issues
[license-shield]: https://img.shields.io/github/license/X5GON/lamapi.svg?style=for-the-badge
[license-url]: https://github.com/X5GON/lamapi/blob/master/LICENSE
[license]: https://img.shields.io/badge/License-BSD%202--Clause-green.svg
[license-link]: https://opensource.org/licenses/BSD-2-Clause

[project-screenshot]: readme/analytics.png
[search-request]: readme/search_service_request.png
[search-response]: readme/search_service_response.png
