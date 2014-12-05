ec2-cost-tools
==============

Simple tools for EC2 cost analysis

Usage
=====

Install the ec2-costs commandline tool by running

```bash
pip install -e .
```

Expose your AWS credentials in the bash environment.

```bash
export AWS_ACCESS_KEY_ID=<Your aws access key>
export AWS_SECRET_ACCESS_KEY=<Your aws secret key>
```

If you want to see the costs analysis for reserved instances of `us-west-` region, then run

```bash
ec2-costs us-west-1
```

You will see two tables like this

```
+---------------+------+------------+---------+---------+-------------+----------------+
| Instance type | VPC  | Zone       | Tenancy | Covered | Instnace ID | Name           |
+---------------+------+------------+---------+---------+-------------+----------------+
| m3.medium     | None | us-west-1b | default | 4 / 4   |             |                |
|               |      |            |         | True    | i-6ca7f0a4  | foo-api-dev2 |
|               |      |            |         | True    | i-1b2474d3  | bar-api-prod |
|               |      |            |         | True    | i-6c2d7da4  | foo-api-prod |
|               |      |            |         | True    | i-7ca7f0b4  | bar-api-dev2 |
| m3.medium     | None | us-west-1c | default | 2 / 2   |             |                |
|               |      |            |         | True    | i-00f6a3ca  | foo-api-prod |
|               |      |            |         | True    | i-b20b5f78  | bar-api-prod |
+---------------+------+------------+---------+---------+-------------+----------------+
########## Not in-use reserved instances ##########
+---------------+-------+------------+---------+-------+
| Instance type |  VPC  |    Zone    | Tenancy | Count |
+---------------+-------+------------+---------+-------+
|   m3.medium   | False | us-west-1c | default |   0   |
|   m3.medium   | False | us-west-1b | default |   2   |
+---------------+-------+------------+---------+-------+
```

The first table indicates all running instacnes, and shows that whether they are covered by reserved instances. You should notice that actually reserved instances have no one-to-one relationship between EC2 instances, it only affects the billing. The `Covered` is just for you to understand the reserved instance coverage easily.

To understand how many reserved instances are not in use, you can see the second table. In our example, there are two reserved instances with m3.medium type, non-VPC in us-west-1b zone are not used.

With these two tables, you can understand how many reserved instances are in-use, then decide how many more to buy or sell.
