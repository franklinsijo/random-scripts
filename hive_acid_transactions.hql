# HiveQL
#
# Configurations required to enable ACID transactions in Hive
# and a simple example to perform ACID operations
#

## Override default Transaction Manager ##
SET hive.txn.manager=org.apache.hadoop.hive.ql.lockmgr.DbTxnManager;

## Configurations for Hive Client ##
SET hive.support.concurrency=true;
SET hive.enforce.bucketing=true;
SET hive.exec.dynamic.partition.mode=nonstrict;

## Configurations for Hive Metastore ##
SET hive.compactor.initiator.on=true;
SET hive.compactor.worker.threads=1;

## DDL ##
CREATE TABLE transactions 
	(
		userid VARCHAR(64), 
		key_id BIGINT,
       	value_id BIGINT,
       	value_name STRING, 
       	value_displayname STRING,
       	value_type STRING,
       	value_status STRING
	) 
	PARTITIONED BY (transaction_date STRING) 
	CLUSTERED BY (userid) INTO 24 BUCKETS 
	STORED AS ORC 
	TBLPROPERTIES ("transactional"="true", "orc.compress"="NONE");

## DML ##
INSERT INTO TABLE transactions 
	PARTITION (transaction_date = '2014-09-23') 
	VALUES 
		('jsmith', 86030895877, 500557, 'FALSE', 'None', 'EXACT', 'ACTIVE'), 
		('jdoe', 86030896837, 500797, 'topmodule', 'None', 'EXACT', 'ACTIVE');
 
INSERT INTO TABLE transactions 
	PARTITION (transaction_date) 
	VALUES 
		('tjohnson', 86030896357, 500797, 'top15', 'None', 'EXACT', 'ACTIVE', '2014-09-23'), 
		('tlee', 86030896477, 500797, 'top25', 'None', 'EXACT', 'INACTIVE', '2014-09-21');
  
SELECT * from transactions where transaction_date='2014-09-23';

UPDATE transactions SET value_name='top100' WHERE userid='jsmith';

DELETE from transactions where userid = 'jdoe';
