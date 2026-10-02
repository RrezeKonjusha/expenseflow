# ZAP Scanning Report

ZAP by [Checkmarx](https://checkmarx.com/).


## Summary of Alerts

| Risk Level | Number of Alerts |
| --- | --- |
| High | 0 |
| Medium | 0 |
| Low | 3 |
| Informational | 5 |




## Insights

| Level | Reason | Site | Description | Statistic |
| --- | --- | --- | --- | --- |
| Low | Exceeded High | https://ef.localhost | Percentage of responses with status code 4xx | 95 % |
| Info | Informational | https://ef.localhost | Percentage of responses with status code 3xx | 3 % |
| Info | Informational | https://ef.localhost | Percentage of endpoints with content type application/json | 52 % |
| Info | Informational | https://ef.localhost | Percentage of endpoints with content type text/html | 46 % |
| Info | Informational | https://ef.localhost | Percentage of endpoints with method DELETE | 3 % |
| Info | Informational | https://ef.localhost | Percentage of endpoints with method GET | 75 % |
| Info | Informational | https://ef.localhost | Percentage of endpoints with method PATCH | 3 % |
| Info | Informational | https://ef.localhost | Percentage of endpoints with method POST | 15 % |
| Info | Informational | https://ef.localhost | Percentage of endpoints with method PUT | 3 % |
| Info | Informational | https://ef.localhost | Count of total endpoints | 166    |
| Info | Informational | https://ef.localhost | Percentage of slow responses | 1 % |







## Alerts

| Name | Risk Level | Number of Instances |
| --- | --- | --- |
| A Server Error response code was returned by the server | Low | 1 |
| Cross-Origin-Resource-Policy Header Missing or Invalid | Low | 3 |
| Unexpected Content-Type was returned | Low | 79 |
| A Client Error response code was returned by the server | Informational | 129 |
| Authentication Request Identified | Informational | 2 |
| Information Disclosure - Sensitive Information in URL | Informational | 1 |
| Non-Storable Content | Informational | Systemic |
| Re-examine Cache-control Directives | Informational | 1 |




## Alert Detail



### [ A Server Error response code was returned by the server ](https://www.zaproxy.org/docs/alerts/100000/)



##### Low (High)

### Description

A response code of 502 was returned by the server.
This may indicate that the application is failing to handle unexpected input correctly.
Raised by the 'Alert on HTTP Response Code Error' script

* URL: https://ef.localhost/api/v1/projects/10/
  * Node Name: `https://ef.localhost/api/v1/projects/10/ ()({code,name,budget,is_active})`
  * Method: `PATCH`
  * Parameter: ``
  * Attack: ``
  * Evidence: `502`
  * Other Info: ``


Instances: 1

### Solution



### Reference



#### CWE Id: [ 388 ](https://cwe.mitre.org/data/definitions/388.html)


#### WASC Id: 20

#### Source ID: 4

### [ Cross-Origin-Resource-Policy Header Missing or Invalid ](https://www.zaproxy.org/docs/alerts/90004/)



##### Low (Medium)

### Description

Cross-Origin-Resource-Policy header is an opt-in header designed to counter side-channels attacks like Spectre. Resource should be specifically set as shareable amongst different origins.

* URL: https://ef.localhost/api/schema/
  * Node Name: `https://ef.localhost/api/schema/`
  * Method: `GET`
  * Parameter: `Cross-Origin-Resource-Policy`
  * Attack: ``
  * Evidence: ``
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/logout/
  * Node Name: `https://ef.localhost/api/v1/auth/logout/`
  * Method: `POST`
  * Parameter: `Cross-Origin-Resource-Policy`
  * Attack: ``
  * Evidence: ``
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/forgot/
  * Node Name: `https://ef.localhost/api/v1/auth/password/forgot/ ()({email})`
  * Method: `POST`
  * Parameter: `Cross-Origin-Resource-Policy`
  * Attack: ``
  * Evidence: ``
  * Other Info: ``


Instances: 3

### Solution

Ensure that the application/web server sets the Cross-Origin-Resource-Policy header appropriately, and that it sets the Cross-Origin-Resource-Policy header to 'same-origin' for all web pages.
'same-site' is considered as less secured and should be avoided.
If resources must be shared, set the header to 'cross-origin'.
If possible, ensure that the end user uses a standards-compliant and modern web browser that supports the Cross-Origin-Resource-Policy header (https://caniuse.com/mdn-http_headers_cross-origin-resource-policy).

### Reference


* [ https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Embedder-Policy ](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Embedder-Policy)


#### CWE Id: [ 693 ](https://cwe.mitre.org/data/definitions/693.html)


#### WASC Id: 14

#### Source ID: 3

### [ Unexpected Content-Type was returned ](https://www.zaproxy.org/docs/alerts/100001/)



##### Low (High)

### Description

A Content-Type of text/html was returned by the server.
This is not one of the types expected to be returned by an API.
Raised by the 'Alert on Unexpected Content Types' script

* URL: https://ef.localhost
  * Node Name: `https://ef.localhost`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/
  * Node Name: `https://ef.localhost/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/683917621372355556
  * Node Name: `https://ef.localhost/683917621372355556`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/9069654155646023990
  * Node Name: `https://ef.localhost/9069654155646023990`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api
  * Node Name: `https://ef.localhost/api`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/
  * Node Name: `https://ef.localhost/api/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/5146045832073033732
  * Node Name: `https://ef.localhost/api/5146045832073033732`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/schema
  * Node Name: `https://ef.localhost/api/schema`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/schema/350399378520498932
  * Node Name: `https://ef.localhost/api/schema/350399378520498932`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1
  * Node Name: `https://ef.localhost/api/v1`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/
  * Node Name: `https://ef.localhost/api/v1/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/4538732785261108722
  * Node Name: `https://ef.localhost/api/v1/4538732785261108722`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/audit-logs
  * Node Name: `https://ef.localhost/api/v1/audit-logs`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/audit-logs/4524588851527943526
  * Node Name: `https://ef.localhost/api/v1/audit-logs/4524588851527943526`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth
  * Node Name: `https://ef.localhost/api/v1/auth`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/
  * Node Name: `https://ef.localhost/api/v1/auth/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/6623923560847237495
  * Node Name: `https://ef.localhost/api/v1/auth/6623923560847237495`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/activate
  * Node Name: `https://ef.localhost/api/v1/auth/activate`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/activate/314623514249241801
  * Node Name: `https://ef.localhost/api/v1/auth/activate/314623514249241801`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/login
  * Node Name: `https://ef.localhost/api/v1/auth/login`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/login/5612474963994780044
  * Node Name: `https://ef.localhost/api/v1/auth/login/5612474963994780044`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/logout
  * Node Name: `https://ef.localhost/api/v1/auth/logout`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/logout/3215635118597500038
  * Node Name: `https://ef.localhost/api/v1/auth/logout/3215635118597500038`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/me
  * Node Name: `https://ef.localhost/api/v1/auth/me`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/me/5831524790223119500
  * Node Name: `https://ef.localhost/api/v1/auth/me/5831524790223119500`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password
  * Node Name: `https://ef.localhost/api/v1/auth/password`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/
  * Node Name: `https://ef.localhost/api/v1/auth/password/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/8161963513622578225
  * Node Name: `https://ef.localhost/api/v1/auth/password/8161963513622578225`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/change
  * Node Name: `https://ef.localhost/api/v1/auth/password/change`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/change/4516444980462939131
  * Node Name: `https://ef.localhost/api/v1/auth/password/change/4516444980462939131`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/forgot
  * Node Name: `https://ef.localhost/api/v1/auth/password/forgot`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/forgot/1929203966106961536
  * Node Name: `https://ef.localhost/api/v1/auth/password/forgot/1929203966106961536`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/reset
  * Node Name: `https://ef.localhost/api/v1/auth/password/reset`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/reset/7026346226460580200
  * Node Name: `https://ef.localhost/api/v1/auth/password/reset/7026346226460580200`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/refresh
  * Node Name: `https://ef.localhost/api/v1/auth/refresh`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/refresh/8497286395297397451
  * Node Name: `https://ef.localhost/api/v1/auth/refresh/8497286395297397451`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/register
  * Node Name: `https://ef.localhost/api/v1/auth/register`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/register/657702964954647399
  * Node Name: `https://ef.localhost/api/v1/auth/register/657702964954647399`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/departments
  * Node Name: `https://ef.localhost/api/v1/departments`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/departments/10
  * Node Name: `https://ef.localhost/api/v1/departments/10`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/departments/10/4465775975865217490
  * Node Name: `https://ef.localhost/api/v1/departments/10/4465775975865217490`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/departments/6539426557329049922/1914036818998469776
  * Node Name: `https://ef.localhost/api/v1/departments/6539426557329049922/1914036818998469776`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses
  * Node Name: `https://ef.localhost/api/v1/expenses`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10
  * Node Name: `https://ef.localhost/api/v1/expenses/10`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/7372770534415169476
  * Node Name: `https://ef.localhost/api/v1/expenses/10/7372770534415169476`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/approve
  * Node Name: `https://ef.localhost/api/v1/expenses/10/approve`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/approve/7314422081276672619
  * Node Name: `https://ef.localhost/api/v1/expenses/10/approve/7314422081276672619`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/reject
  * Node Name: `https://ef.localhost/api/v1/expenses/10/reject`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/reject/1899637873852493229
  * Node Name: `https://ef.localhost/api/v1/expenses/10/reject/1899637873852493229`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/reopen
  * Node Name: `https://ef.localhost/api/v1/expenses/10/reopen`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/reopen/496837807128629494
  * Node Name: `https://ef.localhost/api/v1/expenses/10/reopen/496837807128629494`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/submit
  * Node Name: `https://ef.localhost/api/v1/expenses/10/submit`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/submit/873366476802880498
  * Node Name: `https://ef.localhost/api/v1/expenses/10/submit/873366476802880498`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/5010658808505598535/6286185090907144888
  * Node Name: `https://ef.localhost/api/v1/expenses/5010658808505598535/6286185090907144888`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/import
  * Node Name: `https://ef.localhost/api/v1/expenses/import`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/import/720521105683869858
  * Node Name: `https://ef.localhost/api/v1/expenses/import/720521105683869858`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/reimburse
  * Node Name: `https://ef.localhost/api/v1/expenses/reimburse`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/reimburse/3452496662621837535
  * Node Name: `https://ef.localhost/api/v1/expenses/reimburse/3452496662621837535`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects
  * Node Name: `https://ef.localhost/api/v1/projects`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/10
  * Node Name: `https://ef.localhost/api/v1/projects/10`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/10/1051680715905155468
  * Node Name: `https://ef.localhost/api/v1/projects/10/1051680715905155468`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/10/members
  * Node Name: `https://ef.localhost/api/v1/projects/10/members`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/10/members/5611879766428101156
  * Node Name: `https://ef.localhost/api/v1/projects/10/members/5611879766428101156`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/8688639862664034344/7485315574320716623
  * Node Name: `https://ef.localhost/api/v1/projects/8688639862664034344/7485315574320716623`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports
  * Node Name: `https://ef.localhost/api/v1/reports`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/1286454067997520980/8951034717702311293
  * Node Name: `https://ef.localhost/api/v1/reports/1286454067997520980/8951034717702311293`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/dashboard
  * Node Name: `https://ef.localhost/api/v1/reports/dashboard`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/dashboard/4828980337191168180
  * Node Name: `https://ef.localhost/api/v1/reports/dashboard/4828980337191168180`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/id
  * Node Name: `https://ef.localhost/api/v1/reports/id`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/id/2530317162818893421
  * Node Name: `https://ef.localhost/api/v1/reports/id/2530317162818893421`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/id/export
  * Node Name: `https://ef.localhost/api/v1/reports/id/export`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/id/export/6974872342007591984
  * Node Name: `https://ef.localhost/api/v1/reports/id/export/6974872342007591984`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/run
  * Node Name: `https://ef.localhost/api/v1/reports/run`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/run/1868458562788549511
  * Node Name: `https://ef.localhost/api/v1/reports/run/1868458562788549511`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users
  * Node Name: `https://ef.localhost/api/v1/users`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users/10
  * Node Name: `https://ef.localhost/api/v1/users/10`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users/10/5590938952322726158
  * Node Name: `https://ef.localhost/api/v1/users/10/5590938952322726158`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users/10/actuator/health
  * Node Name: `https://ef.localhost/api/v1/users/10/actuator/health`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users/4051936027608815282/2245565952079583059
  * Node Name: `https://ef.localhost/api/v1/users/4051936027608815282/2245565952079583059`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `text/html`
  * Other Info: ``


Instances: 79

### Solution



### Reference




#### Source ID: 4

### [ A Client Error response code was returned by the server ](https://www.zaproxy.org/docs/alerts/100000/)



##### Informational (High)

### Description

A response code of 401 was returned by the server.
This may indicate that the application is failing to handle unexpected input correctly.
Raised by the 'Alert on HTTP Response Code Error' script

* URL: https://ef.localhost/api/v1/departments/10/
  * Node Name: `https://ef.localhost/api/v1/departments/10/`
  * Method: `DELETE`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/
  * Node Name: `https://ef.localhost/api/v1/expenses/10/`
  * Method: `DELETE`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/10/
  * Node Name: `https://ef.localhost/api/v1/projects/10/`
  * Method: `DELETE`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/id/
  * Node Name: `https://ef.localhost/api/v1/reports/id/`
  * Method: `DELETE`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users/10/
  * Node Name: `https://ef.localhost/api/v1/users/10/`
  * Method: `DELETE`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/
  * Node Name: `https://ef.localhost/api/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/5146045832073033732
  * Node Name: `https://ef.localhost/api/5146045832073033732`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/schema/350399378520498932
  * Node Name: `https://ef.localhost/api/schema/350399378520498932`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1
  * Node Name: `https://ef.localhost/api/v1`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/
  * Node Name: `https://ef.localhost/api/v1/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/4538732785261108722
  * Node Name: `https://ef.localhost/api/v1/4538732785261108722`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/audit-logs/
  * Node Name: `https://ef.localhost/api/v1/audit-logs/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/audit-logs/%3Faction=action&date_from=date_from&date_to=date_to&page=10&page_size=10&user=10
  * Node Name: `https://ef.localhost/api/v1/audit-logs/ (action,date_from,date_to,page,page_size,user)`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/audit-logs/4524588851527943526
  * Node Name: `https://ef.localhost/api/v1/audit-logs/4524588851527943526`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth
  * Node Name: `https://ef.localhost/api/v1/auth`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/
  * Node Name: `https://ef.localhost/api/v1/auth/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/6623923560847237495
  * Node Name: `https://ef.localhost/api/v1/auth/6623923560847237495`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/activate/
  * Node Name: `https://ef.localhost/api/v1/auth/activate/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `405`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/activate/314623514249241801
  * Node Name: `https://ef.localhost/api/v1/auth/activate/314623514249241801`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/login/
  * Node Name: `https://ef.localhost/api/v1/auth/login/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `405`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/login/5612474963994780044
  * Node Name: `https://ef.localhost/api/v1/auth/login/5612474963994780044`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/logout/
  * Node Name: `https://ef.localhost/api/v1/auth/logout/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `405`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/logout/3215635118597500038
  * Node Name: `https://ef.localhost/api/v1/auth/logout/3215635118597500038`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/me/
  * Node Name: `https://ef.localhost/api/v1/auth/me/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/me/5831524790223119500
  * Node Name: `https://ef.localhost/api/v1/auth/me/5831524790223119500`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password
  * Node Name: `https://ef.localhost/api/v1/auth/password`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/
  * Node Name: `https://ef.localhost/api/v1/auth/password/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/8161963513622578225
  * Node Name: `https://ef.localhost/api/v1/auth/password/8161963513622578225`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/change/
  * Node Name: `https://ef.localhost/api/v1/auth/password/change/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/change/4516444980462939131
  * Node Name: `https://ef.localhost/api/v1/auth/password/change/4516444980462939131`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/forgot/
  * Node Name: `https://ef.localhost/api/v1/auth/password/forgot/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `405`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/forgot/1929203966106961536
  * Node Name: `https://ef.localhost/api/v1/auth/password/forgot/1929203966106961536`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/reset/
  * Node Name: `https://ef.localhost/api/v1/auth/password/reset/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `405`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/reset/7026346226460580200
  * Node Name: `https://ef.localhost/api/v1/auth/password/reset/7026346226460580200`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/refresh/
  * Node Name: `https://ef.localhost/api/v1/auth/refresh/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `405`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/refresh/8497286395297397451
  * Node Name: `https://ef.localhost/api/v1/auth/refresh/8497286395297397451`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/register/
  * Node Name: `https://ef.localhost/api/v1/auth/register/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `405`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/register/657702964954647399
  * Node Name: `https://ef.localhost/api/v1/auth/register/657702964954647399`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/departments/
  * Node Name: `https://ef.localhost/api/v1/departments/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/departments/%3Fordering=ordering
  * Node Name: `https://ef.localhost/api/v1/departments/ (ordering)`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/departments/10/
  * Node Name: `https://ef.localhost/api/v1/departments/10/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/departments/10/4465775975865217490
  * Node Name: `https://ef.localhost/api/v1/departments/10/4465775975865217490`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/departments/6539426557329049922
  * Node Name: `https://ef.localhost/api/v1/departments/6539426557329049922`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/departments/6539426557329049922/
  * Node Name: `https://ef.localhost/api/v1/departments/6539426557329049922/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/departments/6539426557329049922/1914036818998469776
  * Node Name: `https://ef.localhost/api/v1/departments/6539426557329049922/1914036818998469776`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/
  * Node Name: `https://ef.localhost/api/v1/expenses/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/%3Famount_max=1.2&amount_min=1.2&date_from=date_from&date_to=date_to&department=1.2&employee=1.2&mine=true&ordering=ordering&page=10&page_size=10&project=1.2&q=q&status=APPROVED&type=EQUIPMENT
  * Node Name: `https://ef.localhost/api/v1/expenses/ (amount_max,amount_min,date_from,date_to,department,employee,mine,ordering,page,page_size,project,q,status,type)`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/
  * Node Name: `https://ef.localhost/api/v1/expenses/10/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/7372770534415169476
  * Node Name: `https://ef.localhost/api/v1/expenses/10/7372770534415169476`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/approve/
  * Node Name: `https://ef.localhost/api/v1/expenses/10/approve/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/approve/7314422081276672619
  * Node Name: `https://ef.localhost/api/v1/expenses/10/approve/7314422081276672619`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/reject/
  * Node Name: `https://ef.localhost/api/v1/expenses/10/reject/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/reject/1899637873852493229
  * Node Name: `https://ef.localhost/api/v1/expenses/10/reject/1899637873852493229`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/reopen/
  * Node Name: `https://ef.localhost/api/v1/expenses/10/reopen/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/reopen/496837807128629494
  * Node Name: `https://ef.localhost/api/v1/expenses/10/reopen/496837807128629494`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/submit/
  * Node Name: `https://ef.localhost/api/v1/expenses/10/submit/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/submit/873366476802880498
  * Node Name: `https://ef.localhost/api/v1/expenses/10/submit/873366476802880498`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/5010658808505598535
  * Node Name: `https://ef.localhost/api/v1/expenses/5010658808505598535`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/5010658808505598535/
  * Node Name: `https://ef.localhost/api/v1/expenses/5010658808505598535/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/5010658808505598535/6286185090907144888
  * Node Name: `https://ef.localhost/api/v1/expenses/5010658808505598535/6286185090907144888`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/import/
  * Node Name: `https://ef.localhost/api/v1/expenses/import/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/import/720521105683869858
  * Node Name: `https://ef.localhost/api/v1/expenses/import/720521105683869858`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/reimburse/
  * Node Name: `https://ef.localhost/api/v1/expenses/reimburse/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/reimburse/3452496662621837535
  * Node Name: `https://ef.localhost/api/v1/expenses/reimburse/3452496662621837535`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/
  * Node Name: `https://ef.localhost/api/v1/projects/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/%3Fis_active=true&ordering=ordering
  * Node Name: `https://ef.localhost/api/v1/projects/ (is_active,ordering)`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/10/
  * Node Name: `https://ef.localhost/api/v1/projects/10/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/10/1051680715905155468
  * Node Name: `https://ef.localhost/api/v1/projects/10/1051680715905155468`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/10/members/
  * Node Name: `https://ef.localhost/api/v1/projects/10/members/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/10/members/5611879766428101156
  * Node Name: `https://ef.localhost/api/v1/projects/10/members/5611879766428101156`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/8688639862664034344
  * Node Name: `https://ef.localhost/api/v1/projects/8688639862664034344`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/8688639862664034344/
  * Node Name: `https://ef.localhost/api/v1/projects/8688639862664034344/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/8688639862664034344/7485315574320716623
  * Node Name: `https://ef.localhost/api/v1/projects/8688639862664034344/7485315574320716623`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/
  * Node Name: `https://ef.localhost/api/v1/reports/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/1286454067997520980
  * Node Name: `https://ef.localhost/api/v1/reports/1286454067997520980`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/1286454067997520980/
  * Node Name: `https://ef.localhost/api/v1/reports/1286454067997520980/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/1286454067997520980/8951034717702311293
  * Node Name: `https://ef.localhost/api/v1/reports/1286454067997520980/8951034717702311293`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/dashboard/
  * Node Name: `https://ef.localhost/api/v1/reports/dashboard/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/dashboard/4828980337191168180
  * Node Name: `https://ef.localhost/api/v1/reports/dashboard/4828980337191168180`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/id/
  * Node Name: `https://ef.localhost/api/v1/reports/id/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/id/2530317162818893421
  * Node Name: `https://ef.localhost/api/v1/reports/id/2530317162818893421`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/id/export/
  * Node Name: `https://ef.localhost/api/v1/reports/id/export/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `406`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/id/export/%3Fformat=csv
  * Node Name: `https://ef.localhost/api/v1/reports/id/export/ (format)`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `406`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/id/export/6974872342007591984
  * Node Name: `https://ef.localhost/api/v1/reports/id/export/6974872342007591984`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/run/
  * Node Name: `https://ef.localhost/api/v1/reports/run/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/run/1868458562788549511
  * Node Name: `https://ef.localhost/api/v1/reports/run/1868458562788549511`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users/
  * Node Name: `https://ef.localhost/api/v1/users/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users/%3Fdepartment=10&is_active=true&ordering=ordering&page=10&page_size=10&role=ADMIN&search=ZAP
  * Node Name: `https://ef.localhost/api/v1/users/ (department,is_active,ordering,page,page_size,role,search)`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users/10/
  * Node Name: `https://ef.localhost/api/v1/users/10/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users/10/5590938952322726158
  * Node Name: `https://ef.localhost/api/v1/users/10/5590938952322726158`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users/10/actuator/health
  * Node Name: `https://ef.localhost/api/v1/users/10/actuator/health`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users/4051936027608815282
  * Node Name: `https://ef.localhost/api/v1/users/4051936027608815282`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users/4051936027608815282/
  * Node Name: `https://ef.localhost/api/v1/users/4051936027608815282/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users/4051936027608815282/2245565952079583059
  * Node Name: `https://ef.localhost/api/v1/users/4051936027608815282/2245565952079583059`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `404`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/me/
  * Node Name: `https://ef.localhost/api/v1/auth/me/ ()({first_name,last_name})`
  * Method: `PATCH`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/departments/10/
  * Node Name: `https://ef.localhost/api/v1/departments/10/ ()({name,manager})`
  * Method: `PATCH`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/
  * Node Name: `https://ef.localhost/api/v1/expenses/10/ ()({type,amount,expense_date,description,project,distance_km,destination,attendees,item_name,serial_no})`
  * Method: `PATCH`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/10/
  * Node Name: `https://ef.localhost/api/v1/projects/10/ ()({code,name,budget,is_active})`
  * Method: `PATCH`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users/10/
  * Node Name: `https://ef.localhost/api/v1/users/10/ ()({email,first_name,last_name,role,department,is_active,password})`
  * Method: `PATCH`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/activate/
  * Node Name: `https://ef.localhost/api/v1/auth/activate/ ()({uid,token})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `400`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/login/
  * Node Name: `https://ef.localhost/api/v1/auth/login/ ()({email,password})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/change/
  * Node Name: `https://ef.localhost/api/v1/auth/password/change/ ()({current_password,new_password})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/forgot/
  * Node Name: `https://ef.localhost/api/v1/auth/password/forgot/ ()({email})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `400`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/reset/
  * Node Name: `https://ef.localhost/api/v1/auth/password/reset/ ()({uid,token,new_password})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `400`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/refresh/
  * Node Name: `https://ef.localhost/api/v1/auth/refresh/`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/register/
  * Node Name: `https://ef.localhost/api/v1/auth/register/ ()({email,password,first_name,last_name})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `400`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/departments/
  * Node Name: `https://ef.localhost/api/v1/departments/ ()({name,manager})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/
  * Node Name: `https://ef.localhost/api/v1/expenses/ ()({type,amount,expense_date,description,project,distance_km,destination,attendees,item_name,serial_no})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/approve/
  * Node Name: `https://ef.localhost/api/v1/expenses/10/approve/`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/reject/
  * Node Name: `https://ef.localhost/api/v1/expenses/10/reject/ ()({reason})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/reopen/
  * Node Name: `https://ef.localhost/api/v1/expenses/10/reopen/`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/submit/
  * Node Name: `https://ef.localhost/api/v1/expenses/10/submit/`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/import/
  * Node Name: `https://ef.localhost/api/v1/expenses/import/ ()(multipart:file)`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/import/
  * Node Name: `https://ef.localhost/api/v1/expenses/import/ ()(multipart:rtobject)`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/reimburse/
  * Node Name: `https://ef.localhost/api/v1/expenses/reimburse/ ()({until})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/
  * Node Name: `https://ef.localhost/api/v1/projects/ ()({code,name,budget,is_active})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/
  * Node Name: `https://ef.localhost/api/v1/reports/ ()({name,criteria:{date_from,date_to,group_by,statuses:[],types:[],department_ids:[],project_ids:[{}]}})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/
  * Node Name: `https://ef.localhost/api/v1/reports/ ()({name,criteria:{date_from,date_to,group_by,statuses:[],types:[],department_ids:[{}],project_ids:[]}})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/
  * Node Name: `https://ef.localhost/api/v1/reports/ ()({name,criteria:{date_from,date_to,group_by,statuses:[],types:[],department_ids:[{}],project_ids:[{}]}})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/run/
  * Node Name: `https://ef.localhost/api/v1/reports/run/ ()({date_from,date_to,group_by,statuses:[],types:[],department_ids:[],project_ids:[{}]})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/run/
  * Node Name: `https://ef.localhost/api/v1/reports/run/ ()({date_from,date_to,group_by,statuses:[],types:[],department_ids:[{}],project_ids:[]})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/reports/run/
  * Node Name: `https://ef.localhost/api/v1/reports/run/ ()({date_from,date_to,group_by,statuses:[],types:[],department_ids:[{}],project_ids:[{}]})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users/
  * Node Name: `https://ef.localhost/api/v1/users/ ()({email,first_name,last_name,role,department,is_active,password})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/departments/10/
  * Node Name: `https://ef.localhost/api/v1/departments/10/ ()({name,manager})`
  * Method: `PUT`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/expenses/10/
  * Node Name: `https://ef.localhost/api/v1/expenses/10/ ()({type,amount,expense_date,description,project,distance_km,destination,attendees,item_name,serial_no})`
  * Method: `PUT`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/10/
  * Node Name: `https://ef.localhost/api/v1/projects/10/ ()({code,name,budget,is_active})`
  * Method: `PUT`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/10/members/
  * Node Name: `https://ef.localhost/api/v1/projects/10/members/ ()({user_ids:[]})`
  * Method: `PUT`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/projects/10/members/
  * Node Name: `https://ef.localhost/api/v1/projects/10/members/ ()({user_ids:[{}]})`
  * Method: `PUT`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/users/10/
  * Node Name: `https://ef.localhost/api/v1/users/10/ ()({email,first_name,last_name,role,department,is_active,password})`
  * Method: `PUT`
  * Parameter: ``
  * Attack: ``
  * Evidence: `401`
  * Other Info: ``


Instances: 129

### Solution



### Reference



#### CWE Id: [ 388 ](https://cwe.mitre.org/data/definitions/388.html)


#### WASC Id: 20

#### Source ID: 4

### [ Authentication Request Identified ](https://www.zaproxy.org/docs/alerts/10111/)



##### Informational (High)

### Description

The given request has been identified as an authentication request. The 'Other Info' field contains a set of key=value lines which identify any relevant fields. If the request is in a context which has an Authentication Method set to "Auto-Detect" then this rule will change the authentication to match the request identified.

* URL: https://ef.localhost/api/v1/users/
  * Node Name: `https://ef.localhost/api/v1/users/ ()({email,first_name,last_name,role,department,is_active,password})`
  * Method: `POST`
  * Parameter: `email`
  * Attack: ``
  * Evidence: `password`
  * Other Info: `userParam=email
userValue=zaproxy@example.com
passwordParam=password`
* URL: https://ef.localhost/api/v1/auth/login/
  * Node Name: `https://ef.localhost/api/v1/auth/login/ ()({email,password})`
  * Method: `POST`
  * Parameter: `email`
  * Attack: ``
  * Evidence: `password`
  * Other Info: `userParam=email
userValue=zaproxy@example.com
passwordParam=password`


Instances: 2

### Solution

This is an informational alert rather than a vulnerability and so there is nothing to fix.

### Reference


* [ https://www.zaproxy.org/docs/desktop/addons/authentication-helper/auth-req-id/ ](https://www.zaproxy.org/docs/desktop/addons/authentication-helper/auth-req-id/)



#### Source ID: 3

### [ Information Disclosure - Sensitive Information in URL ](https://www.zaproxy.org/docs/alerts/10024/)



##### Informational (Medium)

### Description

The request appeared to contain sensitive information leaked in the URL. This can violate PCI and most organizational compliance policies. You can configure the list of strings for this check to add or remove values specific to your environment.

* URL: https://ef.localhost/api/v1/audit-logs/%3Faction=action&date_from=date_from&date_to=date_to&page=10&page_size=10&user=10
  * Node Name: `https://ef.localhost/api/v1/audit-logs/ (action,date_from,date_to,page,page_size,user)`
  * Method: `GET`
  * Parameter: `user`
  * Attack: ``
  * Evidence: `user`
  * Other Info: `The URL contains potentially sensitive information. The following string was found via the pattern: user
user`


Instances: 1

### Solution

Do not pass sensitive information in URIs.

### Reference



#### CWE Id: [ 598 ](https://cwe.mitre.org/data/definitions/598.html)


#### WASC Id: 13

#### Source ID: 3

### [ Non-Storable Content ](https://www.zaproxy.org/docs/alerts/10049/)



##### Informational (Medium)

### Description

The response contents are not storable by caching components such as proxy servers. If the response does not contain sensitive, personal or user-specific information, it may benefit from being stored and cached, to improve performance.

* URL: https://ef.localhost/api/v1/audit-logs/%3Faction=action&date_from=date_from&date_to=date_to&page=10&page_size=10&user=10
  * Node Name: `https://ef.localhost/api/v1/audit-logs/ (action,date_from,date_to,page,page_size,user)`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/me/
  * Node Name: `https://ef.localhost/api/v1/auth/me/`
  * Method: `GET`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/me/
  * Node Name: `https://ef.localhost/api/v1/auth/me/ ()({first_name,last_name})`
  * Method: `PATCH`
  * Parameter: ``
  * Attack: ``
  * Evidence: `PATCH `
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/forgot/
  * Node Name: `https://ef.localhost/api/v1/auth/password/forgot/ ()({email})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``
* URL: https://ef.localhost/api/v1/auth/password/reset/
  * Node Name: `https://ef.localhost/api/v1/auth/password/reset/ ()({uid,token,new_password})`
  * Method: `POST`
  * Parameter: ``
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``

Instances: Systemic


### Solution

The content may be marked as storable by ensuring that the following conditions are satisfied:
The request method must be understood by the cache and defined as being cacheable ("GET", "HEAD", and "POST" are currently defined as cacheable)
The response status code must be understood by the cache (one of the 1XX, 2XX, 3XX, 4XX, or 5XX response classes are generally understood)
The "no-store" cache directive must not appear in the request or response header fields
For caching by "shared" caches such as "proxy" caches, the "private" response directive must not appear in the response
For caching by "shared" caches such as "proxy" caches, the "Authorization" header field must not appear in the request, unless the response explicitly allows it (using one of the "must-revalidate", "public", or "s-maxage" Cache-Control response directives)
In addition to the conditions above, at least one of the following conditions must also be satisfied by the response:
It must contain an "Expires" header field
It must contain a "max-age" response directive
For "shared" caches such as "proxy" caches, it must contain a "s-maxage" response directive
It must contain a "Cache Control Extension" that allows it to be cached
It must have a status code that is defined as cacheable by default (200, 203, 204, 206, 300, 301, 404, 405, 410, 414, 501).

### Reference


* [ https://datatracker.ietf.org/doc/html/rfc7234 ](https://datatracker.ietf.org/doc/html/rfc7234)
* [ https://datatracker.ietf.org/doc/html/rfc7231 ](https://datatracker.ietf.org/doc/html/rfc7231)
* [ https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html ](https://www.w3.org/Protocols/rfc2616/rfc2616-sec13.html)


#### CWE Id: [ 524 ](https://cwe.mitre.org/data/definitions/524.html)


#### WASC Id: 13

#### Source ID: 3

### [ Re-examine Cache-control Directives ](https://www.zaproxy.org/docs/alerts/10015/)



##### Informational (Low)

### Description

The cache-control header has not been set properly or is missing, allowing the browser and proxies to cache content. For static assets like css, js, or image files this might be intended, however, the resources should be reviewed to ensure that no sensitive content will be cached.

* URL: https://ef.localhost/api/schema/
  * Node Name: `https://ef.localhost/api/schema/`
  * Method: `GET`
  * Parameter: `cache-control`
  * Attack: ``
  * Evidence: `no-store`
  * Other Info: ``


Instances: 1

### Solution

For secure content, ensure the cache-control HTTP header is set with "no-cache, no-store, must-revalidate". If an asset should be cached consider setting the directives "public, max-age, immutable".

### Reference


* [ https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html#web-content-caching ](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html#web-content-caching)
* [ https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control ](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control)
* [ https://grayduck.mn/2021/09/13/cache-control-recommendations/ ](https://grayduck.mn/2021/09/13/cache-control-recommendations/)


#### CWE Id: [ 525 ](https://cwe.mitre.org/data/definitions/525.html)


#### WASC Id: 13

#### Source ID: 3


