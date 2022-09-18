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