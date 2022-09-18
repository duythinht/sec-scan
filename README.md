# Problem 1 - Design 3 tier web application

Note: this design contains solution based on generic concept and does not sticky to any vendor, you can implement it on any cloud provider with specific component which they provide

### Diagram:

![High level design diagram](/diagram.jpg)

### Explain:

* Frontend:
    * We use the object storage to store the static files and assets
    * Deliver assets via CDN network improve the speed and less effort to maintain the bandwidth sensitive and also optimize so much the cost, we could use cloudfront (aws), cloudflare or fastly...
    * The other problem is if we use any ssr solution (like nextjs) we should consider some frontend hosting like vercel (not just execute workloads, it also support CICD and development workflow) or build the executor by our self (run like backend service)

* Backend:
    *  All of endpoint must be access over API gateway (round robin should be consider as first approach, based on some purpose other LB algorithm should be consider)
    * Traffic beetween API gateway and Backend private zone will be manipulate by a firewall and network policy rules
    * Cluster manager depend on team decision, state of application, etc... you can use either kubernetes or ec2 (auto scaling group)
    * Serverless application is not define in this design, so we assume only clasic application was input here
    * For some reason, the instance need to access to the internet (install dependencies, pull docker image...) it should do it by go over the NAT gateway.

* Data:
    * Basiscally only the RDBMS topology was here, caching (redis, memcache) and elasticsearch (for some reason we need to improve the performance) should be design detail based on the workloads.
    * We separate the read and write into 2 lane, write to the master and read from the replication, to easy manage the read/write without modify the backend application, SQL proxy should be consider if need
    * Access beetwen backend and DB should managed by firewall rules

* Observability
    * Metrics, there are 2 model we could use to capture the series
        * pull (prometheus, grafana cloud): easy to scale, easy to store, nice document
        * push (statsd, datadog...): well cloud manage, we will take less effort to manage the stored
    * Logs
        * We could use cloudwatch (aws) or stackdriver (gcp) or whatever if choose cloud managed
        * Otherside, the ELK platform is good and mature for logs without vendor locking
    * We can use the grafana or the dashboard provided by cloud provider
    * Alert management could be choiced: opsgenie, pageduty, betteruptime...

# Problem 2 - Scan instances security group

### Prerequisite
* python 3.7++
* boto3
* moto for mock boto3
* pytest for running test

### Known issue

* This instance scan just modify security group which assign to an instance, should we consider to modify ENI as well?

### How to run it on local

* Set those environment (note it's can be done without set it with aws_credentials which placement on the local machine)
    * AWS_ACCESS_KEY_ID
    * AWS_SECRET_ACCESS_KEY
    * AWS_DEFAULT_REGION

* Install dependencies

```
pip install -r requirements.txt
```

* Run pytest (you don't need aws credential because it using mock)

```
pytest .
```

Example output

```
❯❯❯ pytest -s
======================================================================================== test session starts =========================================================================================
platform linux -- Python 3.8.10, pytest-7.1.3, pluggy-1.0.0
rootdir: /home/duythinht/workspace/github.com/duythinht/sec-scan
collected 1 item

test_instances_scan.py >> list of loose open security groups:  ['sg-a34b24b0e4302602a']
>> skip check for instance i-0f86e3c0d79ecef25 due to specific tag: AllowSSH=true
>> check security group violations for i-7ef22854ab7e11c56
>> instance i-7ef22854ab7e11c56 has violated by loose open security group: sg-a34b24b0e4302602a
>> modify instance security groups for i-7ef22854ab7e11c56: []
>> check security group violations for i-e40e7684dd81a1d6c
>> instance i-e40e7684dd81a1d6c has violated by loose open security group: sg-a34b24b0e4302602a
>> modify instance security groups for i-e40e7684dd81a1d6c: []
>> check security group violations for i-eafeb7b20b225bbf3
>> instance i-eafeb7b20b225bbf3 has violated by loose open security group: sg-a34b24b0e4302602a
>> modify instance security groups for i-eafeb7b20b225bbf3: []
>> check security group violations for i-e98d72d340f8d5a60
>> instance i-e98d72d340f8d5a60 has violated by loose open security group: sg-a34b24b0e4302602a
>> modify instance security groups for i-e98d72d340f8d5a60: []
>> check security group violations for i-e0f67db67d8f96671
>> instance i-e0f67db67d8f96671 has violated by loose open security group: sg-a34b24b0e4302602a
>> modify instance security groups for i-e0f67db67d8f96671: []
==================================================================================== 1 passed ====================================================================================
```

* Running production (you need aws credential above)



```
python main.py
```

Example output

```
❯❯❯ python main.py

>> list of loose open security groups:  ['sg-3b15107256637a2d5']
>> skip check for instance i-56adaddf69e11fc78 due to specific tag: AllowSSH=true
>> check security group violations for i-7d105d125d72b99d7
>> instance i-7d105d125d72b99d7 has violated by loose open security group: sg-3b15107256637a2d5
>> modify instance security groups for i-7d105d125d72b99d7: []
>> check security group violations for i-9cd7cde32b147d290
>> instance i-9cd7cde32b147d290 has violated by loose open security group: sg-3b15107256637a2d5
>> modify instance security groups for i-9cd7cde32b147d290: []
>> check security group violations for i-7d670ead8d87928fb
>> instance i-7d670ead8d87928fb has violated by loose open security group: sg-3b15107256637a2d5
>> modify instance security groups for i-7d670ead8d87928fb: []
>> check security group violations for i-b43a2900885ea6415
>> instance i-b43a2900885ea6415 has violated by loose open security group: sg-3b15107256637a2d5
>> modify instance security groups for i-b43a2900885ea6415: []
>> check security group violations for i-9a38dcc914ce97841
>> instance i-9a38dcc914ce97841 has violated by loose open security group: sg-3b15107256637a2d5
>> modify instance security groups for i-9a38dcc914ce97841: []
```