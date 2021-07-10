#!/usr/bin/env python

from argparse import ArgumentParser
from boto3.session import Session
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
import os
import pytz
import json

__author__ = 'franklinsijo'

SERVICE = 'ec2'


def delete(ec2client, args):
    IDSFILE = os.path.abspath(args.idfile)
    if not os.path.isfile(IDSFILE):
        raise Exception("File '%s' does not exist" % IDSFILE)

    with open(IDSFILE, 'r') as f:
        resources2delete = f.read().splitlines()
    f.close()

    if args.resource == 'instance':
        try:
            ec2client.terminate_instances(InstanceIds=resources2delete)
        except ClientError as e:
            print(e.response['Error']['Code'])
    elif args.resource == 'volume':
        for id in resources2delete:
            try:
                ec2client.delete_volume(VolumeId=id)
            except ClientError as e:
                print("%s :" + e.response['Error']['Code'] % id)
    elif args.resource == 'snapshot':
        for id in resources2delete:
            try:
                ec2client.delete_snapshot(SnapshotId=id)
            except ClientError as e:
                print("%s :" + e.response['Error']['Code'] % id)


def snapshot(ec2client, args):
    if args.INSTANCE_ID:
        instanceId = args.INSTANCE_ID
        try:
            instance_result = ec2client.describe_instances(InstanceIds=[instanceId])
            block_devices = instance_result['Reservations'][0]['Instances'][0]['BlockDeviceMappings']
            volumes = []
            for i in range(len(block_devices)):
                volumes.append({'id':block_devices[i]['Ebs']['VolumeId'], 'device':block_devices[i]['DeviceName']})
        except Exception as e:
            raise e
        if args.EXCLUDE_LIST:
            volumes2exclude = [id.strip() for id in args.EXCLUDE_LIST.split(",")]
            volumes = [id for id in volumes if id not in volumes2exclude]
    elif args.VOLUME_ID:
        volumes = [{'id': args.VOLUME_ID}]
    else:
        raise Exception("Either Instance ID or Volume ID must be provided")

    tags = []
    if args.TAGS_JSON:
        TAGSFILE = os.path.abspath(args.TAGS_JSON)
        if not os.path.isfile(TAGSFILE):
            raise Exception("File '%s' does not exist" % TAGSFILE)
        with open(TAGSFILE, 'r') as t:
            tags = json.load(t)
        t.close()

    def validity(datevalue, daysago):
        deleteable_date = datetime.now(pytz.utc) - timedelta(days=daysago)
        return datevalue < deleteable_date

    def delete_snapshots(vols, DAYS_OLD=7):
        for volume in vols:
            try:
                snapshot_result = ec2client.describe_snapshots(Filters=[{'Name': 'volume-id', 'Values': volume['id']}])
                snapshots = snapshot_result['Snapshots']
                for snapshot in snapshots:
                    snapshot_id, start_time = snapshot['SnapshotId'], snapshot['StartTime']
                    if validity(start_time, DAYS_OLD):
                        try:
                            ec2client.delete_snapshot(SnapshotId=snapshot_id)
                        except ClientError as e:
                            print("%s :" + e.response['Error']['Code'] % volume['id'])
            except Exception as e:
                raise e

    if args.ACTION == 'create':
        snapshot_ids = []
        for volume in volumes:
            description = "Snapshot #" + args.INSTANCE_ID + " #" + volume['id'] + " #" + volume['device'] if args.INSTANCE_ID else "Snapshot #" + volume['id']
            try:
                snapshot_result = ec2client.create_snapshot(VolumeId=volume['id'], Description=description)
                snapshot_ids.append(snapshot_result['SnapshotId'])
            except ClientError as e:
                print("%s :" + e.response['Error']['Code'] % volume['id'])
        if args.TAGS_JSON:
            try:
                ec2client.create_tags(Resources=snapshot_ids, Tags=tags)
            except Exception as e:
                raise e
        if args.DELETE_OLD:
            delete_snapshots(volumes, args.DAYS_OLD)
    elif args.ACTION == 'delete':
        if args.DELETE_OLD:
            # Deletes only the snapshots that are older by DAYS_OLD value
            delete_snapshots(volumes, args.DAYS_OLD)
        else:
            # Deletes all the snapshots
            delete_snapshots(volumes, DAYS_OLD=0)


def tag(ec2client, args):
    RESOURCEIDS = os.path.abspath(args.resourceids)
    if not os.path.isfile(RESOURCEIDS):
        raise Exception("File '%s' does not exist" % RESOURCEIDS)

    TAGSFILE = os.path.abspath(args.tags)
    if not os.path.isfile(TAGSFILE):
        raise Exception("File '%s' does not exist" % TAGSFILE)

    with open(RESOURCEIDS, 'r') as f:
        resources2tag = f.read().splitlines()
    f.close()
    with open(TAGSFILE, 'r') as t:
        tags = json.load(t)
    t.close()

    try:
        ec2client.create_tags(Resources=resources2tag,
                              Tags=tags)
    except Exception as e:
        raise e


def main():
    if args.CREDENTIALS_FILE:
        CREDS_FILE = os.path.abspath(args.CREDENTIALS_FILE)
        if not os.path.isfile(CREDS_FILE):
            raise Exception("File '%s' does not exist" % CREDS_FILE)
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = CREDS_FILE

    session = Session(profile_name=args.AWS_PROFILE)
    ec2client = session.client(SERVICE)

    if args.ACTION == 'delete':
        delete(ec2client, args)
    elif args.ACTION == 'snapshot':
        snapshot(ec2client, args)
    elif args.ACTION == 'tag':
        tag(ec2client, args)
    else:
        raise Exception("Unrecognized action: '%s'" % args.ACTION)

if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument("--credentials",
                           dest="CREDENTIALS_FILE",
                           help="path of the file containing AWS Credentials to use")
    argparser.add_argument("--profile",
                           dest="AWS_PROFILE",
                           default=None,
                           help="profile to select from the credentials file")

    subargparser = argparser.add_subparsers(dest="ACTION")

    delete_argparser = subargparser.add_parser("delete")
    delete_argparser.add_argument("-r", "--resource",
                                  dest="RESOURCE_TYPE",
                                  choices=["instance", "volume", "snapshot"],
                                  help="type of resource to delete")
    delete_argparser.add_argument("--id-file",
                                  dest="ID_FILEPATH",
                                  help="path of the file with the resource ids listed")

    snapshot_argparser = subargparser.add_parser("snapshot")
    snapshot_argparser.add_argument("-i", "--instance",
                                    dest="INSTANCE_ID",
                                    type=str,
                                    help="ID of the instance whose volumes to be snapshotted or snapshots to be deleted")
    snapshot_argparser.add_argument("-v", "--volume",
                                    dest="VOLUME_ID",
                                    type=str,
                                    help="ID of the volume to be snapshotted or snapshots to be deleted")
    snapshot_argparser.add_argument("-a", "--action",
                                    dest="ACTION",
                                    choices=["create", "delete"],
                                    default="create",
                                    help="action to perform. "
                                         "Create EBS Snapshots or Delete EBS Snapshots. "
                                         "If not specified, both will be done (deletes one week older snapshots).")
    snapshot_argparser.add_argument("-t", "--days-old",
                                    dest="DAYS_OLD",
                                    type=int,
                                    action="store",
                                    default=7,
                                    help="snapshots older than this number of days will be deleted. "
                                         "7 by default.")
    snapshot_argparser.add_argument("--exclude",
                                    dest="EXCLUDE_LIST",
                                    type=str,
                                    help="comma separated IDs of volumes to be excluded from the operation. "
                                         "Ignored if volume option is used.")
    snapshot_argparser.add_argument("--delete-old",
                                    dest="DELETE_OLD",
                                    action="store_true",
                                    help="delete the snapshots older than --days-old")
    snapshot_argparser.add_argument("--tags-file",
                                    dest="TAGS_JSON",
                                    help="json file containing an array of Key-Value pairs")

    tag_argparser = subargparser.add_parser("tag")
    tag_argparser.add_argument("--id-file",
                               dest="ID_FILEPATH",
                               help="path of the file with the resource ids listed")
    tag_argparser.add_argument("--tags-file",
                               dest="TAGS_JSON",
                               help="json file containing an array of Key-Value pairs")

    args = argparser.parse_args()
    main()
