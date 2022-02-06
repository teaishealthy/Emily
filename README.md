# Emily
![](https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square&logo=python)
![](https://img.shields.io/github/license/teaishealthy/emily?style=flat-square) 
![](https://img.shields.io/codefactor/grade/github/teaishealthy/emily?style=flat-square)
![](https://img.shields.io/badge/code%20style-black-black?style=flat-square)
## Fork Notice

This is a fork of [`Emily`](https://github.com/Shiick/Emily) by [`Shiick`](https://github.com/Shiick).

## Installation

### Cloning

```bash
# Clone the repository over https
$ git clone https://github.com/teishealthy/Emily.git
# or over SSH 
$ git clone git@github.com:teaishealthy/Emily.git
```

### Config

Copy .env.example to .env and fill in the values.

Copy config.yaml.example to config.yaml and fill in the values.


### Dependencies

```bash
$ poetry install
```

### Start
A [pm2 config](ecosystem.config.js) is provided, start using pm2:
```
$ pm2 start
```

## License
This Project / Fork is licensed under the [GNU General Public License v3.0](COPYING)