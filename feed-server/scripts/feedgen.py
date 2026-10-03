#!/usr/bin/env python3

import argparse
import getpass
import sys
import datetime

from atproto import Client

CONTENT_MODE_VIDEO = "app.bsky.feed.defs#contentModeVideo"
CONTENT_MODE_UNSPECIFIED = "app.bsky.feed.defs#contentModeUnspecified"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Publish or unpublish a Bluesky custom feed generator"
    )

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--handle", required=True, help="Your Bluesky handle")
    common.add_argument(
        "--service",
        default="https://bsky.social/xrpc",
        help="PDS service URL (default: https://bsky.social/xrpc)",
    )
    common.add_argument(
        "--record-name",
        required=True,
        help="Short name of the feed record (appears in feed URL)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    publish = subparsers.add_parser(
        "publish", parents=[common], help="Publish or update a feed generator"
    )
    publish.add_argument(
        "--hostname",
        required=True,
        help="Hostname of your feed generator (e.g. feedgen.example.com)",
    )
    publish.add_argument("--display-name", required=True, help="Display name for the feed")
    publish.add_argument("--description", default=None, help="Brief description of the feed")
    publish.add_argument("--avatar", default=None, help="Local path to a PNG or JPEG avatar image")
    publish.add_argument(
        "--video-only",
        action="store_true",
        help="Set content mode to video (enables immersive video experience)",
    )
    publish.add_argument(
        "--accept-interactions",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Advertise that this feed wants client interaction events "
            "(likes, reposts, clicks, 'show more/less like this') sent to its "
            "sendInteractions endpoint so it can tune ranking. Sets the record's "
            "acceptsInteractions flag (default: True)"
        ),
    )

    subparsers.add_parser("unpublish", parents=[common], help="Delete a feed generator record")

    return parser.parse_args()


def load_avatar(path: str) -> tuple[bytes, str]:
    if path.endswith(".png"):
        encoding = "image/png"
    elif path.endswith((".jpg", ".jpeg")):
        encoding = "image/jpeg"
    else:
        print("Error: avatar must be a .png or .jpg/.jpeg file.", file=sys.stderr)
        sys.exit(1)
    with open(path, "rb") as f:
        return f.read(), encoding


def confirm_publish(args: argparse.Namespace, feed_gen_did: str) -> None:
    print("\n── Feed details ──────────────────────────────")
    print(f"  Handle       : {args.handle}")
    print(f"  Service      : {args.service}")
    print(f"  Record name  : {args.record_name}")
    print(f"  Display name : {args.display_name}")
    print(f"  Description  : {args.description or '(none)'}")
    print(f"  Avatar       : {args.avatar or '(none)'}")
    print(f"  Video only   : {args.video_only}")
    print(f"  Interactions : {args.accept_interactions}")
    print(f"  Feed DID     : {feed_gen_did}")
    print("──────────────────────────────────────────────\n")
    answer = input("Publish this feed? [y/N] ").strip().lower()
    if answer not in ("y", "yes"):
        print("Aborted.")
        sys.exit(0)


def confirm_unpublish(args: argparse.Namespace) -> None:
    print("\n── Unpublish feed ────────────────────────────")
    print(f"  Handle       : {args.handle}")
    print(f"  Service      : {args.service}")
    print(f"  Record name  : {args.record_name}")
    print("──────────────────────────────────────────────\n")
    answer = input("Delete this feed record? This cannot be undone. [y/N] ").strip().lower()
    if answer not in ("y", "yes"):
        print("Aborted.")
        sys.exit(0)


def cmd_publish(args: argparse.Namespace, client: Client) -> None:
    feed_gen_did = f"did:web:{args.hostname}"
    confirm_publish(args, feed_gen_did)

    password = getpass.getpass(f"Password for {args.handle} (preferably an App Password): ")
    client.login(args.handle, password)

    avatar_blob = None
    if args.avatar:
        img_data, encoding = load_avatar(args.avatar)
        blob_response = client.com.atproto.repo.upload_blob(img_data)
        avatar_blob = blob_response.blob

    content_mode = CONTENT_MODE_VIDEO if args.video_only else CONTENT_MODE_UNSPECIFIED

    resp = client.com.atproto.repo.put_record(
        data={
            "repo": client.me.did,
            "collection": "app.bsky.feed.generator",
            "rkey": args.record_name,
            "record": {
                "$type": "app.bsky.feed.generator",
                "did": feed_gen_did,
                "displayName": args.display_name,
                "description": args.description,
                "avatar": avatar_blob,
                "createdAt": datetime.datetime.utcnow().isoformat() + "Z",
                "contentMode": content_mode,
                "acceptsInteractions": args.accept_interactions,
            },
        }
    )
    print(f"record: {resp}")
    print("All done 🎉")


def cmd_unpublish(args: argparse.Namespace, client: Client) -> None:
    confirm_unpublish(args)

    password = getpass.getpass(f"Password for {args.handle} (preferably an App Password): ")
    client.login(args.handle, password)

    client.com.atproto.repo.delete_record(
        data={
            "repo": client.me.did,
            "collection": "app.bsky.feed.generator",
            "rkey": args.record_name,
        }
    )
    print("Feed deleted 🗑️")


def main():
    args = parse_args()
    client = Client(base_url=args.service)

    if args.command == "publish":
        cmd_publish(args, client)
    elif args.command == "unpublish":
        cmd_unpublish(args, client)


if __name__ == "__main__":
    main()
