# README #

Django API to access TVH Servers.

Use the latest patches from https://github.com/ckarrie/tvheadend, i.e.:

* [channel uuid](https://github.com/ckarrie/tvheadend/commit/1f0b59ca37e07ab53910782b5e8302a3d0085645)

## Example API requests ##

Change channel nr.:

```curl 'http://ckarrie2.dyndns.org:9981/api/idnode/save' -H 'Host: ckarrie2.dyndns.org:9981' -H 'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' -H 'Accept-Language: de,en-US;q=0.7,en;q=0.3' --compressed -H 'X-Requested-With: XMLHttpRequest' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' -H 'Referer: http://ckarrie2.dyndns.org:9981/extjs.html?' -H 'Connection: keep-alive' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' --data 'node=%5B%7B%22number%22%3A%225%22%2C%22uuid%22%3A%22cf05419812f2189bbd5355ad21bef25d%22%7D%2C%7B%22number%22%3A%221005%22%2C%22uuid%22%3A%2242894e0da4499edd76bcae882a0f7c52%22%7D%5D'```

Data:

node: [{"number":"5","uuid":"cf05419812f2189bbd5355ad21bef25d"},{"number":"1005","uuid":"42894e0da4499edd76bcae882a0f7c52"}]